"""Offline environment checks. Run in the course root: python tools/check_env.py.

run_checks() returns check dictionaries and writes no permanent files. Only the
explicit --json option saves a report. Smoke tests use a disposable temporary
directory; no course data is changed. No network, installation or PATH changes.
"""
from __future__ import annotations

import argparse
import contextlib
import importlib
import importlib.metadata
import importlib.util
import io
import json
import os
import platform
import re
import sqlite3
import struct
import subprocess
import sys
import tempfile
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONT_CANDIDATES = (
    "Microsoft YaHei", "SimHei", "PingFang SC", "Heiti SC",
    "Arial Unicode MS", "Noto Sans CJK SC", "WenQuanYi Micro Hei",
)
IMPORT_NAMES = {"jupyterlab": "jupyterlab", "ipykernel": "ipykernel"}


def run_checks() -> list[dict]:
    """Return structured entries without saving reports, bytecode or new font caches."""
    previous_bytecode = sys.dont_write_bytecode
    previous_config = os.environ.get("MPLCONFIGDIR")
    with tempfile.TemporaryDirectory(prefix="da-course-mpl-") as directory:
        sys.dont_write_bytecode = True
        os.environ["MPLCONFIGDIR"] = directory
        try:
            return _run_checks()
        finally:
            sys.dont_write_bytecode = previous_bytecode
            if previous_config is None:
                os.environ.pop("MPLCONFIGDIR", None)
            else:
                os.environ["MPLCONFIGDIR"] = previous_config
            matplotlib = sys.modules.get("matplotlib")
            if matplotlib is not None:
                for name in ("get_cachedir", "get_configdir"):
                    getter = getattr(matplotlib, name, None)
                    if hasattr(getter, "cache_clear"):
                        getter.cache_clear()


def _run_checks() -> list[dict]:
    checks = []

    def add(key, title, status, detail, action="", critical=False):
        checks.append({"id": key, "title": title, "status": status,
                       "detail": str(detail), "action": action, "critical": critical})

    def probe(key, title, operation, action, critical=True):
        try:
            detail = operation()
        except Exception as exc:
            add(key, title, "fail", f"{type(exc).__name__}: {exc}", action, critical)
        else:
            add(key, title, "pass", detail, critical=critical)

    target_platform = sys.platform == "win32" and platform.machine().casefold() in {"amd64", "x86_64"}
    add("platform", "运行平台", "pass" if target_platform else "warn",
        f"{platform.system()} {platform.release()} / {platform.machine()}",
        "本教程以 Windows 11 x86_64 为目标；ARM 或其他系统不是目标路线，运行不等于 Windows 实机验证。")
    probe("python_path", "当前 Python 路径", lambda: str(Path(sys.executable).resolve()),
          "回 Anaconda Prompt 激活 da-course；Notebook 选择 Python (da-course)。")
    bits = struct.calcsize("P") * 8
    add("python_bits", "Python 位数", "pass" if bits == 64 else "fail", f"{bits} 位",
        "课程需要 64 位 Python；检查下载的是 Windows x86_64 安装包。", True)
    add("python_version", "Python 版本", "pass" if sys.version_info[:2] == (3, 12) else "fail",
        sys.version.split()[0], "使用 conda create -n da-course python=3.12 pip -y 创建课程环境。", True)
    probe("cwd", "当前工作目录 cwd", lambda: str(Path.cwd()),
          "回到有写权限且已完整解压的课程目录。")
    add("root", "教程根目录 root", "pass", ROOT)
    cwd_text = next((c["detail"] for c in checks if c["id"] == "cwd"), "")
    unusual = [p for p in (str(ROOT), str(sys.executable), cwd_text)
               if " " in p or re.search(r"[\u3400-\u9fff]", p)]
    add("path_characters", "路径中的中文或空格", "warn" if unusual else "pass",
        "；".join(unusual) if unusual else "上述路径没有中文或空格。",
        "中文或空格不是必然错误；先给路径加双引号，检查实际读写。不要重命名 Windows 用户目录。")
    prefix = os.environ.get("CONDA_PREFIX")
    actual_prefix = Path(sys.prefix).resolve()
    add("conda_prefix", "CONDA_PREFIX / sys.prefix", "pass" if prefix else "warn",
        f"CONDA_PREFIX={prefix or '(未设置)'}; sys.prefix={actual_prefix}",
        "Prompt 先 conda activate da-course；Notebook 子进程可没有此变量，实际解释器路径优先。")
    target_name = actual_prefix.name.casefold() == "da-course"
    add("environment_name", "当前解释器属于 da-course", "pass" if target_name else "fail",
        f"解释器环境目录：{actual_prefix}",
        "在 Prompt 激活 da-course；已有 da-course 时不要重复创建。Notebook 改内核后从头运行。", True)
    if prefix:
        same = os.path.normcase(str(Path(prefix).resolve())) == os.path.normcase(str(actual_prefix))
        add("environment_match", "终端环境与解释器匹配", "pass" if same else "fail",
            f"CONDA_PREFIX={prefix}; sys.prefix={actual_prefix}",
            "终端重新激活；Notebook 若继承了旧变量，先核对 sys.executable 再从正确环境重启 Jupyter。", True)

    def check_pip():
        result = subprocess.run([sys.executable, "-m", "pip", "--version"],
                                capture_output=True, text=True, errors="replace", timeout=30,
                                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1",
                                     "PIP_DISABLE_PIP_VERSION_CHECK": "1"})
        if result.returncode != 0:
            raise RuntimeError((result.stderr or result.stdout).strip())
        spec = importlib.util.find_spec("pip")
        if spec is None or spec.origin is None:
            raise RuntimeError("pip 命令返回成功，但无法定位当前 Python 的 pip 模块。")
        origin = Path(spec.origin).resolve()
        try:
            origin.relative_to(actual_prefix)
        except ValueError:
            raise RuntimeError(f"pip 来自环境外：{origin}; 当前 sys.prefix={actual_prefix}")
        return f"{sys.executable} -m pip: {result.stdout.strip()}; 模块路径：{origin}"

    probe("pip", "绑定当前 Python 的 pip", check_pip,
          "在 Anaconda Prompt 用 conda install -n da-course pip，再激活环境；不要运行不明来源 pip。")
    requirements_path = ROOT / "requirements.txt"
    requirements = []
    try:
        for raw in requirements_path.read_text(encoding="utf-8").splitlines():
            line = raw.split("#", 1)[0].strip()
            if not line:
                continue
            match = re.fullmatch(r"([A-Za-z0-9_.-]+)==([^\s;]+)", line)
            if not match:
                raise ValueError(f"无法识别版本行：{line}")
            requirements.append(match.groups())
        if not requirements:
            raise ValueError("requirements.txt 中没有固定版本。")
    except Exception as exc:
        add("requirements", "课程版本清单", "fail", f"{type(exc).__name__}: {exc}",
            "完整解压课程 ZIP，确认根目录有 requirements.txt。", True)
    else:
        add("requirements", "课程版本清单", "pass", requirements_path, critical=True)

    modules = {}
    for name, expected in requirements:
        try:
            installed = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            installed = "未安装"
        except Exception as exc:
            installed = f"读取版本失败：{exc}"
        add(f"version_{name}", f"{name} 版本", "pass" if installed == expected else "fail",
            f"已安装 {installed} / requirements.txt 要求 {expected}",
            "确认 da-course 激活，在教程根目录 python -m pip install -r requirements.txt。", True)
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                module = importlib.import_module(IMPORT_NAMES.get(name, name))
        except Exception as exc:
            add(f"import_{name}", f"{name} 可导入", "fail", f"{type(exc).__name__}: {exc}",
                "版本存在但导入失败也需排查。保存完整错误，勿关闭杀毒/SSL 校验。", True)
        else:
            modules[name] = module
            add(f"import_{name}", f"{name} 可导入", "pass",
                getattr(module, "__file__", "模块导入成功"), critical=True)

    def data_check():
        path = ROOT / "data" / "books.csv"
        with path.open("r", encoding="utf-8-sig") as stream:
            header = stream.readline().strip()
        if not header:
            raise ValueError("books.csv 是空文件。")
        return f"{path}; 首行可读取：{header}"

    probe("data", "课程数据可达", data_check,
          "ZIP 必须完整解压，data/books.csv 与 notebooks 保持原相对位置。")

    def dacheck_check():
        # A script launched from tools/ does not automatically search its parent.
        inserted = str(ROOT) not in sys.path
        if inserted:
            sys.path.insert(0, str(ROOT))
        try:
            module = importlib.import_module("dacheck")
            if Path(module.__file__).resolve().parent != ROOT / "dacheck":
                raise RuntimeError(f"导入了其他目录的 dacheck：{module.__file__}")
            for attribute in ("check", "hint", "setup_chinese_font"):
                if not callable(getattr(module, attribute, None)):
                    raise RuntimeError(f"dacheck 缺少 {attribute}")
            return module.__file__
        finally:
            if inserted:
                sys.path.remove(str(ROOT))

    probe("dacheck", "本教程检查工具可达", dacheck_check,
          "完整解压整个教程；不要到网上安装同名包。")
    pd = modules.get("pandas")
    if pd is None:
        for key, title in (("csv_io", "pandas CSV 读写"), ("excel_io", "Excel 读写"),
                           ("sqlite_io", "SQLite 读写")):
            add(key, title, "fail", "pandas 未能导入，未执行读写测试。",
                "先解决 pandas 导入项，再重新运行。", True)
    else:
        sample = pd.DataFrame({"名称": ["书签", "明信片"], "数量": [2, 3]})

        def roundtrip(kind):
            with tempfile.TemporaryDirectory(prefix="da-course-check-") as directory:
                tmp = Path(directory)
                if kind == "csv":
                    sample.to_csv(tmp / "sample.csv", index=False, encoding="utf-8-sig")
                    restored = pd.read_csv(tmp / "sample.csv", encoding="utf-8-sig")
                elif kind == "excel":
                    sample.to_excel(tmp / "sample.xlsx", index=False, engine="openpyxl")
                    restored = pd.read_excel(tmp / "sample.xlsx", engine="openpyxl")
                else:
                    with sqlite3.connect(tmp / "sample.sqlite") as connection:
                        sample.to_sql("sample", connection, index=False, if_exists="fail")
                        restored = pd.read_sql_query('SELECT "名称", "数量" FROM sample ORDER BY rowid', connection)
                pd.testing.assert_frame_equal(sample, restored)
            return "临时目录中写入并读回 2 行中文数据；结果一致，临时文件已清理。"

        for kind, key, title in (("csv", "csv_io", "pandas CSV 读写"),
                                 ("excel", "excel_io", "Excel 读写"),
                                 ("sqlite", "sqlite_io", "SQLite 读写")):
            probe(key, title, lambda k=kind: roundtrip(k),
                  "看前面的 pandas/openpyxl 导入项；权限错误检查临时目录，禁止用管理员长期绕过。")

    if "matplotlib" not in modules:
        add("font", "matplotlib 中文字体", "warn", "matplotlib 未导入，未执行字体检查。",
            "先解决 matplotlib 导入，再检查中文。")
    else:
        try:
            # Keep the font cache in a temporary folder, not in the user's profile.
            with tempfile.TemporaryDirectory(prefix="da-course-font-") as directory:
                previous_config = os.environ.get("MPLCONFIGDIR")
                os.environ["MPLCONFIGDIR"] = directory
                try:
                    from matplotlib import font_manager
                    manager = font_manager.FontManager()
                    available = {font.name: font.fname for font in manager.ttflist}
                    selected = next((name for name in FONT_CANDIDATES if name in available), None)
                    if selected is None:
                        add("font", "matplotlib 中文字体", "warn", "没有找到课程候选中文字体。",
                            "到 A-2 字体小节检查已安装字体；别屏蔽 Glyph missing 警告。")
                    else:
                        from matplotlib.backends.backend_agg import FigureCanvasAgg
                        from matplotlib.figure import Figure
                        fig = Figure(figsize=(2, 1))
                        canvas = FigureCanvasAgg(fig)
                        ax = fig.subplots()
                        prop = font_manager.FontProperties(fname=available[selected])
                        ax.set_title("销售数量", fontproperties=prop)
                        ax.plot([1, 2], [2, 3])
                        with warnings.catch_warnings(record=True) as caught:
                            warnings.simplefilter("always")
                            canvas.draw()
                        missing = [str(w.message) for w in caught if "Glyph" in str(w.message)]
                        add("font", "matplotlib 中文字体", "warn" if missing else "pass",
                            f"候选字体：{selected}; " + ("；".join(missing) if missing else "中文样例无缺字警告。"),
                            "此检查只验证样例字，不保证所有字符。图表课仍需 setup_chinese_font()。")
                finally:
                    if previous_config is None:
                        os.environ.pop("MPLCONFIGDIR", None)
                    else:
                        os.environ["MPLCONFIGDIR"] = previous_config
        except Exception as exc:
            add("font", "matplotlib 中文字体", "warn", f"{type(exc).__name__}: {exc}",
                "保存信息，到 A-2 检查字体与缓存权限；不删除用户目录。")
    return checks


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="离线课程环境体检，不联网、不改 PATH、不安装/卸载软件。")
    parser.add_argument("--json", metavar="路径", type=Path,
                        help="明确保存 UTF-8 JSON 报告；不覆盖已有文件，可能包含本机路径，请脱敏后分享。")
    args = parser.parse_args(argv)
    checks = run_checks()
    labels = {"pass": "通过", "warn": "警告", "fail": "失败"}
    for item in checks:
        print(f"【{labels[item['status']]}】{item['title']}: {item['detail']}")
        if item["status"] != "pass" and item["action"]:
            print(f"  下一步：{item['action']}")
    failed = [item for item in checks if item["critical"] and item["status"] == "fail"]
    print(f"\n共 {len(checks)} 项；关键失败 {len(failed)} 项。")
    print("本检查不联网、不改 PATH、不安装或卸载；仅清理自己新建的临时测试目录。")
    if args.json:
        try:
            with args.json.open("x", encoding="utf-8") as stream:
                json.dump({"checks": checks, "critical_failures": len(failed)}, stream,
                          ensure_ascii=False, indent=2)
                stream.write("\n")
        except (OSError, ValueError) as exc:
            print(f"【失败】无法保存报告：{exc}。选择已存在且有写权限的目录与新的文件名。")
            return 1
        print(f"报告已保存：{args.json.resolve()}（分享前隐藏用户名等本机信息）。")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
