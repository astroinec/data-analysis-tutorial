"""dacheck 核心：注册练习、检查答案、显示结果。"""
from __future__ import annotations

import html
import importlib
import json
import math
import os
import pkgutil
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
PROGRESS_FILE = Path(__file__).resolve().parent / "progress.json"

_REGISTRY: dict[str, dict] = {}
_LOADED = False


class CheckFail(Exception):
    """答案不正确时抛出，消息会直接展示给学习者。"""


# ------------------------------------------------------------------ 注册
def register(ex_id: str, hint: str | None = None, title: str | None = None):
    """把一个函数注册为某道练习的检查函数。

    检查函数接收学习者的答案，答案正确时什么都不用做；
    不正确时调用 fail("提示信息") 或使用 expect_xxx 系列函数。
    """
    def deco(fn):
        _REGISTRY[ex_id] = {"fn": fn, "hint": hint, "title": title}
        return fn
    return deco


def _ensure_loaded():
    global _LOADED
    if _LOADED:
        return
    from . import checks
    for mod in pkgutil.iter_modules(checks.__path__):
        importlib.import_module(f"{checks.__name__}.{mod.name}")
    _LOADED = True


# ------------------------------------------------------------------ 显示
def _in_notebook() -> bool:
    try:
        from IPython import get_ipython
        ip = get_ipython()
        return ip is not None and ip.__class__.__name__ == "ZMQInteractiveShell"
    except Exception:  # noqa: BLE001
        return False


_STYLE = {
    "pass": ("#ecfdf3", "#16a34a", "通过"),
    "fail": ("#fef3f2", "#dc2626", "还不对"),
    "todo": ("#fffaeb", "#d97706", "还没作答"),
    "info": ("#f0f9ff", "#0284c7", "提示"),
    "error": ("#fef3f2", "#b42318", "出错了"),
}


def _show(kind: str, title: str, msg: str = ""):
    bg, fg, label = _STYLE[kind]
    if _in_notebook():
        from IPython.display import HTML, display
        body = html.escape(msg).replace("\n", "<br>")
        display(HTML(
            f'<div style="background:{bg};border-left:5px solid {fg};padding:10px 14px;border-radius:6px;'
            f'margin:6px 0;font-family:-apple-system,Segoe UI,Microsoft YaHei,sans-serif;line-height:1.7;color:#1f2430">'
            f'<b style="color:{fg}">【{label}】</b> <b>{html.escape(title)}</b>'
            + (f'<div style="margin-top:4px">{body}</div>' if msg else "") + "</div>"))
    else:
        print(f"【{label}】{title}")
        if msg:
            print("    " + msg.replace("\n", "\n    "))


# ------------------------------------------------------------------ 进度
def _load_progress() -> dict:
    if os.environ.get("DACHECK_NO_PROGRESS") == "1":
        return {}
    try:
        data = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:  # noqa: BLE001
        return {}


def _save_progress(p: dict):
    if os.environ.get("DACHECK_NO_PROGRESS") == "1":
        return
    try:
        PROGRESS_FILE.write_text(json.dumps(p, ensure_ascii=False, indent=1), encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass


def progress(lesson: str | None = None):
    """查看练习完成情况。progress() 看全部，progress("2-1") 只看某一课。"""
    _ensure_loaded()
    done = _load_progress()
    ids = sorted(_REGISTRY, key=_sort_key)
    if lesson:
        ids = [i for i in ids if i.split(".")[0] == lesson]
    if not ids:
        _show("info", "没有找到练习", f"没有编号以 {lesson} 开头的练习。")
        return
    groups: dict[str, list[str]] = {}
    for i in ids:
        groups.setdefault(i.split(".")[0], []).append(i)
    lines = []
    total_done = 0
    for les, items in groups.items():
        n = sum(1 for i in items if i in done)
        total_done += n
        marks = " ".join(("●" if i in done else "○") for i in items)
        lines.append(f"第 {les} 课：{marks}  {n}/{len(items)}")
    _show("info", f"练习进度：已通过 {total_done} / {len(ids)} 题", "\n".join(lines))


def reset_progress():
    """清空练习进度记录。"""
    _save_progress({})
    _show("info", "进度已清空")


def _sort_key(ex_id: str):
    parts = ex_id.replace("-", ".").split(".")
    return [(0, int(p)) if p.isdigit() else (1, p) for p in parts]


# ------------------------------------------------------------------ 检查入口
def _contains_blank(answer, seen=None):
    if answer is Ellipsis:
        return True
    if not isinstance(answer, (list, tuple, dict, set)):
        return False
    seen = set() if seen is None else seen
    if id(answer) in seen:
        return False
    seen.add(id(answer))
    values = answer.values() if isinstance(answer, dict) else answer
    return any(_contains_blank(value, seen) for value in values)


def _reject(kind, title, msg):
    _show(kind, title, msg)
    if os.environ.get("DACHECK_STRICT") == "1":
        raise CheckFail(f"{title}：{msg}")
    return False


def check(ex_id: str, *answers):
    """检查练习答案。用法：check("2-1.1", answer)"""
    _ensure_loaded()
    item = _REGISTRY.get(ex_id)
    title = f"练习 {ex_id}" + (f"：{item['title']}" if item and item.get("title") else "")
    if item is None:
        return _reject("error", f"找不到练习 {ex_id}", "请检查练习编号有没有写错（注意是英文的点和减号）。")
    if any(_contains_blank(a) for a in answers):
        return _reject("todo", title, "把代码里的 ... 换成你的答案，然后重新运行这个格子。")
    try:
        item["fn"](*answers)
    except (CheckFail, AssertionError) as e:
        msg = str(e) or "结果和预期不一致。"
        if item.get("hint"):
            msg += f'\n需要提示可以运行：hint("{ex_id}")'
        return _reject("fail", title, msg)
    except Exception as e:  # noqa: BLE001
        return _reject("error", title, f"检查时遇到了错误：{type(e).__name__}: {e}\n"
                                      "通常是答案的类型不对（比如应该是表格，你给的是数字），对照题目再看看。")
    p = _load_progress()
    p[ex_id] = int(time.time())
    _save_progress(p)
    _show("pass", title, "做得好！")
    return True


def hint(ex_id: str):
    """查看某道练习的提示。"""
    _ensure_loaded()
    item = _REGISTRY.get(ex_id)
    if not item:
        _show("error", f"找不到练习 {ex_id}")
    elif not item.get("hint"):
        _show("info", f"练习 {ex_id} 没有额外提示", "回头看看本节上方的示例代码，答案的写法和它很像。")
    else:
        _show("info", f"练习 {ex_id} 的提示", item["hint"])


# ------------------------------------------------------------------ 写检查函数用的工具
def fail(msg: str):
    raise CheckFail(msg)


def expect(cond, msg: str):
    if not cond:
        fail(msg)


def _type_name(x) -> str:
    names = {int: "整数 int", float: "小数 float", str: "字符串 str", bool: "布尔值 bool",
             list: "列表 list", dict: "字典 dict", tuple: "元组 tuple", type(None): "空值 None"}
    if type(x) in names:
        return names[type(x)]
    mod = type(x).__module__
    if mod.startswith("pandas"):
        return {"DataFrame": "表格 DataFrame", "Series": "一列数据 Series"}.get(type(x).__name__, type(x).__name__)
    return type(x).__name__


def expect_type(x, types, what: str = "答案"):
    if not isinstance(types, tuple):
        types = (types,)
    if not isinstance(x, types):
        want = " 或 ".join(_type_name(t()) if t in (int, float, str, bool, list, dict, tuple) else t.__name__
                           for t in types)
        fail(f"{what}应该是 {want}，你给的是 {_type_name(x)}：{_short(x)}")


def _short(x, n: int = 80) -> str:
    s = repr(x)
    return s if len(s) <= n else s[:n] + "…"


def _is_number(x) -> bool:
    try:
        import numpy as np
        if isinstance(x, np.generic):
            x = x.item()
    except ImportError:
        pass
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def expect_close(actual, expected, tol: float = 1e-6, what: str = "结果"):
    if not _is_number(actual):
        fail(f"{what}应该是一个数字，你给的是 {_type_name(actual)}：{_short(actual)}")
    if not math.isclose(float(actual), float(expected), rel_tol=tol, abs_tol=tol):
        fail(f"{what}应该是 {expected!r}，你得到的是 {actual!r}")


def expect_equal(actual, expected, what: str = "结果"):
    if _is_number(expected) and _is_number(actual):
        return expect_close(actual, expected, what=what)
    if type(expected) in (list, tuple) and type(actual) in (list, tuple):
        if list(actual) != list(expected):
            fail(f"{what}应该是 {_short(list(expected))}，你得到的是 {_short(list(actual))}")
        return
    if actual != expected:
        if isinstance(expected, str) and isinstance(actual, str) and actual.strip() == expected.strip():
            fail(f"{what}前后多了空格。应该是 {expected!r}，你得到的是 {actual!r}")
        fail(f"{what}应该是 {_short(expected)}，你得到的是 {_short(actual)}")


def expect_series(actual, expected, what: str = "结果", check_order: bool = True, tol: float = 1e-6):
    import pandas as pd
    if isinstance(actual, pd.DataFrame) and actual.shape[1] == 1:
        actual = actual.iloc[:, 0]
    if not isinstance(actual, pd.Series):
        fail(f"{what}应该是一列数据 Series，你给的是 {_type_name(actual)}")
    if len(actual) != len(expected):
        fail(f"{what}应该有 {len(expected)} 个值，你的有 {len(actual)} 个")
    a, e = actual, expected
    if not check_order:
        a, e = a.sort_index(), e.sort_index()
    if list(map(str, a.index)) != list(map(str, e.index)):
        if set(map(str, a.index)) == set(map(str, e.index)):
            fail(f"{what}的内容对了，但顺序不对。期望的顺序是：{_short(list(e.index))}")
        fail(f"{what}的索引（最左边那列标签）不对。期望：{_short(list(e.index))}\n你的：{_short(list(a.index))}")
    _compare_values(list(a), list(e), what, tol)


def _compare_values(a: list, e: list, what: str, tol: float, labels=None):
    import pandas as pd
    for k, (x, y) in enumerate(zip(a, e)):
        if pd.isna(y) and pd.isna(x):
            continue
        if _is_number(x) and _is_number(y):
            if math.isclose(float(x), float(y), rel_tol=tol, abs_tol=tol):
                continue
        elif str(x) == str(y):
            continue
        where = labels[k] if labels else f"第 {k + 1} 个值"
        fail(f"{what}的{where}不对：期望 {y!r}，你的是 {x!r}")


def expect_df(actual, expected, what: str = "结果表格", check_order: bool = True,
              check_index: bool = False, check_columns_order: bool = False, tol: float = 1e-6):
    """比较两个 DataFrame。默认不比较索引、不要求列顺序一致，但要求行顺序一致。"""
    import pandas as pd
    if isinstance(actual, pd.Series) and isinstance(expected, pd.DataFrame):
        fail(f"{what}应该是表格 DataFrame，你给的是一列数据 Series。提示：用两层方括号 df[['列名']] 可以得到表格。")
    if not isinstance(actual, pd.DataFrame):
        fail(f"{what}应该是表格 DataFrame，你给的是 {_type_name(actual)}")
    ac, ec = [str(c) for c in actual.columns], [str(c) for c in expected.columns]
    if len(ac) != len(set(ac)):
        fail(f"{what}有重名列。先检查合并、重命名或选列步骤。")
    if set(ac) != set(ec):
        missing = [c for c in ec if c not in ac]
        extra = [c for c in ac if c not in ec]
        msg = f"{what}的列不对。"
        if missing:
            msg += f"\n少了这些列：{missing}"
        if extra:
            msg += f"\n多了这些列：{extra}"
        fail(msg)
    if check_columns_order and ac != ec:
        fail(f"{what}的列顺序不对。期望：{ec}，你的：{ac}")
    if actual.shape[0] != expected.shape[0]:
        fail(f"{what}应该有 {expected.shape[0]} 行，你的有 {actual.shape[0]} 行")
    a = actual.copy()
    e = expected.copy()
    a.columns, e.columns = ac, ec
    a = a[ec]
    if check_index:
        if list(map(str, a.index)) != list(map(str, e.index)):
            fail(f"{what}的索引（最左边的行标签）不对。期望前几个是：{_short(list(e.index[:5]))}\n"
                 f"你的前几个是：{_short(list(a.index[:5]))}")
    if not check_order:
        a = a.sort_values(ec).reset_index(drop=True)
        e = e.sort_values(ec).reset_index(drop=True)
    try:
        _compare_frames(a, e, ec, what, tol)
    except CheckFail:
        if check_order:
            aa = a.sort_values(ec).reset_index(drop=True)
            ee = e.sort_values(ec).reset_index(drop=True)
            try:
                _compare_frames(aa, ee, ec, what, tol)
            except CheckFail:
                raise
            else:
                fail(f"{what}的内容对了，但行的顺序不对。检查一下排序（sort_values）的列和方向。")
        raise


def _compare_frames(a, e, cols, what, tol):
    for c in cols:
        av, evs = list(a[c]), list(e[c])
        _compare_values(av, evs, f"{what}「{c}」列", tol, labels=[f"第 {i + 1} 行" for i in range(len(av))])


def load(name: str, **kwargs):
    """按文件名读取 data/ 下的数据，供检查函数计算标准答案。"""
    import pandas as pd
    path = DATA_DIR / name
    if name.endswith(".xlsx"):
        return pd.read_excel(path, **kwargs)
    return pd.read_csv(path, **kwargs)


# ------------------------------------------------------------------ 中文字体
_FONT_CANDIDATES = [
    "Microsoft YaHei",   # Windows 微软雅黑
    "SimHei",            # Windows 黑体
    "PingFang SC",       # macOS
    "Heiti SC",          # macOS
    "Arial Unicode MS",  # macOS
    "Noto Sans CJK SC",  # Linux
    "WenQuanYi Micro Hei",
]


def setup_chinese_font(verbose: bool = False):
    """让 matplotlib / seaborn 图表正常显示中文。返回实际使用的字体名。"""
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    have = {f.name for f in font_manager.fontManager.ttflist}
    found = [f for f in _FONT_CANDIDATES if f in have]
    if not found:
        _show("error", "没有找到中文字体", "图表里的中文可能显示成方框。Windows 一般自带微软雅黑，"
                                           "请到第 A-2 课“常见报错速查”查看中文方框问题的解决办法。")
        return None
    plt.rcParams["font.sans-serif"] = found + list(plt.rcParams["font.sans-serif"])
    plt.rcParams["axes.unicode_minus"] = False
    if verbose:
        _show("info", f"已设置中文字体：{found[0]}")
    return found[0]
