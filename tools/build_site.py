"""
把 content/ 里的 Markdown 课程生成为 site/ 里的网页。

用法（在教程根目录运行）：
    python tools/build_site.py

依赖：markdown、pymdown-extensions（见 tools/requirements-build.txt）

扩展语法（容器块）说明见 content/AUTHORING.md。
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

import markdown
from markdown.extensions.toc import slugify_unicode

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
SITE = ROOT / "site"
TEMPLATE = (ROOT / "tools" / "templates" / "page.html").read_text(encoding="utf-8")

MD_EXTENSIONS = [
    "abbr", "attr_list", "def_list", "footnotes", "md_in_html", "tables", "sane_lists",
    "pymdownx.superfences", "pymdownx.highlight",
]
MD_CONFIG = {"pymdownx.highlight": {"use_pygments": False}}

CALLOUT_DEFAULTS = {
    "tip": "小贴士", "note": "说明", "warn": "注意", "danger": "千万别这样",
    "job": "求职加分", "analogy": "打个比方", "try": "动手试试",
    "goal": "本课目标", "recap": "本课小结",
}

WARNINGS: list[str] = []


def warn(msg: str) -> None:
    WARNINGS.append(msg)


# ---------------------------------------------------------------- Markdown 工具
def md_to_html(text: str, with_toc: bool = False):
    exts = list(MD_EXTENSIONS)
    cfg = dict(MD_CONFIG)
    if with_toc:
        exts.append("toc")
        cfg["toc"] = {"slugify": slugify_unicode, "toc_depth": "2-3"}
    md = markdown.Markdown(extensions=exts, extension_configs=cfg)
    out = md.convert(text)
    return (out, md.toc_tokens) if with_toc else out


def md_inline(text: str) -> str:
    out = md_to_html(text.strip())
    m = re.fullmatch(r"<p>(.*)</p>", out.strip(), flags=re.S)
    return m.group(1) if m else out


# ---------------------------------------------------------------- 容器块解析
OPEN_RE = re.compile(r"^ {0,3}(:{3,})\s*([A-Za-z][\w-]*)\s*(.*?)\s*$")
CLOSE_RE = re.compile(r"^ {0,3}(:{3,})\s*$")
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")


class Ctx:
    def __init__(self, lesson_id: str):
        self.lesson_id = lesson_id
        self.stash: dict[str, str] = {}
        self.widgets: set[str] = set()
        self.counter = 0

    def put(self, html_text: str) -> str:
        self.counter += 1
        key = f"DAPLACEHOLDER{self.counter:05d}X"
        self.stash[key] = html_text
        return key


def process_containers(text: str, ctx: Ctx) -> str:
    """把 ::: 容器替换成占位符，容器内部递归渲染为 HTML。"""
    lines = text.split("\n")
    out: list[str] = []
    i = 0
    fence = None
    while i < len(lines):
        line = lines[i]
        fm = FENCE_RE.match(line)
        if fence:
            out.append(line)
            if fm and fm.group(1)[0] == fence[0] and len(fm.group(1)) >= len(fence):
                fence = None
            i += 1
            continue
        if fm:
            fence = fm.group(1)
            out.append(line)
            i += 1
            continue
        om = OPEN_RE.match(line)
        if om:
            colons, name, title = len(om.group(1)), om.group(2), om.group(3)
            # 找到对应的结束行
            depth_fence = None
            j = i + 1
            inner: list[str] = []
            closed = False
            nest = 0
            while j < len(lines):
                l2 = lines[j]
                f2 = FENCE_RE.match(l2)
                if depth_fence:
                    if f2 and f2.group(1)[0] == depth_fence[0] and len(f2.group(1)) >= len(depth_fence):
                        depth_fence = None
                    inner.append(l2); j += 1; continue
                if f2:
                    depth_fence = f2.group(1); inner.append(l2); j += 1; continue
                o2 = OPEN_RE.match(l2)
                c2 = CLOSE_RE.match(l2)
                if o2 and len(o2.group(1)) >= colons:
                    nest += 1
                elif c2 and len(c2.group(1)) >= colons:
                    if nest == 0:
                        closed = True
                        break
                    nest -= 1
                inner.append(l2)
                j += 1
            if not closed:
                warn(f"[{ctx.lesson_id}] 容器 :::{name} 没有结束标记（第 {i + 1} 行）")
            rendered = render_container(name, title, "\n".join(inner), ctx)
            out.append("")
            out.append(ctx.put(rendered))
            out.append("")
            i = j + 1
            continue
        out.append(line)
        i += 1
    return "\n".join(out)


def render_md_block(text: str, ctx: Ctx) -> str:
    return md_to_html(process_containers(text, ctx))


def render_container(name: str, title: str, inner: str, ctx: Ctx) -> str:
    name = name.lower()
    if name in CALLOUT_DEFAULTS:
        t = title or CALLOUT_DEFAULTS[name]
        return (f'<div class="callout {name}"><p class="callout-title">{md_inline(t)}</p>'
                f"{render_md_block(inner, ctx)}</div>")
    if name == "steps":
        body = render_md_block(inner, ctx)
        has_step = any((m := OPEN_RE.match(l)) and m.group(2).lower() == "step" for l in inner.split("\n"))
        if has_step:
            return f'<div class="steps"><ol>{body}</ol></div>'
        return f'<div class="steps">{body}</div>'
    if name == "step":
        t = f'<p class="step-title">{md_inline(title)}</p>' if title else ""
        return f'<li class="step">{t}{render_md_block(inner, ctx)}</li>'
    if name == "flow":
        return f'<div class="flow">{render_md_block(inner, ctx)}</div>'
    if name == "cards":
        return f'<div class="cards">{render_md_block(inner, ctx)}</div>'
    if name == "card":
        t = f'<p class="card-title">{md_inline(title)}</p>' if title else ""
        return f'<div class="card">{t}{render_md_block(inner, ctx)}</div>'
    if name == "compare":
        return f'<div class="compare">{render_md_block(inner, ctx)}</div>'
    if name in ("bad", "good"):
        t = title or ("错误做法" if name == "bad" else "正确做法")
        return (f'<div class="compare-col {name}"><p class="compare-title">{md_inline(t)}</p>'
                f"{render_md_block(inner, ctx)}</div>")
    if name == "tabs":
        return f'<div class="tabs">{render_md_block(inner, ctx)}</div>'
    if name == "tab":
        return (f'<div class="tab-panel" data-label="{html.escape(title, quote=True)}">'
                f"{render_md_block(inner, ctx)}</div>")
    if name == "fold":
        t = title or "展开查看"
        return f'<details class="fold"><summary>{md_inline(t)}</summary>{render_md_block(inner, ctx)}</details>'
    if name == "window":
        t = html.escape(title or "安装向导")
        return (f'<div class="window"><div class="window-title">{t}</div>'
                f'<div class="window-body">{render_md_block(inner, ctx)}</div></div>')
    if name == "buttons":
        return f'<div class="ui-btn-row">{md_inline(inner)}</div>'
    if name == "df":
        return f'<div class="dataframe-wrap">{render_md_block(inner, ctx)}</div>'
    if name == "quiz":
        return render_quiz((title + "\n" if title else "") + inner, ctx)
    if name == "checklist":
        return render_checklist(title, inner, ctx)
    if name == "widget":
        return render_widget(title, inner, ctx)
    if name == "html":
        return inner
    warn(f"[{ctx.lesson_id}] 未知容器 :::{name}")
    return render_md_block(inner, ctx)


def render_quiz(inner: str, ctx: Ctx) -> str:
    parts = re.split(r"^\s*---\s*$", inner, maxsplit=1, flags=re.M)
    head = parts[0]
    explain = parts[1] if len(parts) > 1 else ""
    q_lines, options = [], []
    for line in head.strip("\n").split("\n"):
        m = re.match(r"^\s*[-*]\s+\[( |x|X)\]\s+(.*)$", line)
        if m:
            options.append((m.group(1).lower() == "x", m.group(2)))
        elif options and line.strip():
            ok, txt = options[-1]
            options[-1] = (ok, txt + " " + line.strip())
        else:
            q_lines.append(line)
    if not options:
        warn(f"[{ctx.lesson_id}] 小测验没有选项")
    if sum(1 for ok, _ in options if ok) != 1:
        warn(f"[{ctx.lesson_id}] 小测验应当恰好有 1 个正确选项：{' '.join(q_lines)[:30]}")
    opts = "".join(
        f'<li><button type="button" data-correct="{1 if ok else 0}">{md_inline(t)}</button></li>'
        for ok, t in options
    )
    q_html = render_md_block("\n".join(q_lines), ctx)
    q_html = re.sub(r"^<p>", '<p class="quiz-q">', q_html.strip(), count=1)
    if 'class="quiz-q"' not in q_html:
        q_html = f'<p class="quiz-q"></p>{q_html}'
    exp = f'<div class="quiz-explain">{render_md_block(explain, ctx)}</div>' if explain.strip() else ""
    return f'<div class="quiz">{q_html}<ul class="quiz-options">{opts}</ul>{exp}</div>'


def render_checklist(title: str, inner: str, ctx: Ctx) -> str:
    items: list[str] = []
    for line in inner.split("\n"):
        m = re.match(r"^\s*[-*]\s+(?:\[[ xX]\]\s+)?(.*)$", line)
        if m:
            items.append(m.group(1))
        elif items and line.strip():
            items[-1] += "\n" + line.strip()
    lis = []
    for k, txt in enumerate(items):
        cid = f"{ctx.lesson_id}:{ctx.counter}:{k}"
        lis.append(f'<li><label><input type="checkbox" data-id="{cid}">'
                   f'<span class="cl-text">{md_inline(txt)}</span></label></li>')
    t = f'<p class="checklist-title">{md_inline(title)}</p>' if title else ""
    return f'<div class="checklist">{t}<ul>{"".join(lis)}</ul></div>'


def render_widget(title: str, inner: str, ctx: Ctx) -> str:
    parts = title.split(None, 1)
    if not parts:
        warn(f"[{ctx.lesson_id}] :::widget 缺少组件名")
        return ""
    wname = parts[0]
    wtitle = parts[1] if len(parts) > 1 else ""
    ctx.widgets.add(wname)
    if not (SITE / "assets" / "js" / "widgets" / f"{wname}.js").exists():
        warn(f"[{ctx.lesson_id}] 组件脚本不存在：assets/js/widgets/{wname}.js")
    cfg = inner.strip()
    if cfg:
        try:
            json.loads(cfg)
        except json.JSONDecodeError as e:
            warn(f"[{ctx.lesson_id}] 组件 {wname} 的 JSON 配置有误：{e}")
        safe = cfg.replace("</", "<\\/")
        cfg_html = '<script type="application/json">' + safe + "</script>"
    else:
        cfg_html = ""
    t = f'<p class="widget-title">{md_inline(wtitle)}</p>' if wtitle else ""
    return f'<div class="widget" data-widget="{wname}">{t}<div class="widget-body"></div>{cfg_html}</div>'


# ---------------------------------------------------------------- HTML 后处理
UI_TOKEN_RE = re.compile(r"\[\[([*!+]?)([^\[\]\n]{1,40}?)\]\]")


def postprocess(body: str, outline_index: dict, ctx: Ctx, root: str) -> str:
    # 逐个展开占位符（可能嵌套）
    for _ in range(20):
        changed = False
        for key, val in list(ctx.stash.items()):
            if key in body:
                body = body.replace(f"<p>{key}</p>", val).replace(key, val)
                changed = True
        if not changed:
            break

    segments = re.split(r"(<pre[\s\S]*?</pre>)", body)
    for n, seg in enumerate(segments):
        if seg.startswith("<pre"):
            continue
        # 界面按钮 [[下一步]]、主按钮 [[*安装]]、红色标注 [[!这里]]、绿色标注 [[+对]]
        def ui(m):
            kind, label = m.group(1), m.group(2)
            if kind == "*":
                return f'<span class="ui-btn primary">{label}</span>'
            if kind == "!":
                return f'<span class="annot">{label}</span>'
            if kind == "+":
                return f'<span class="annot ok">{label}</span>'
            return f'<span class="ui-btn">{label}</span>'
        seg = UI_TOKEN_RE.sub(ui, seg)
        # 勾选框
        seg = re.sub(r"<li>\s*\[(x|X)\]\s*", '<li class="task checked"><span class="box"></span>', seg)
        seg = re.sub(r"<li>\s*\[ \]\s*", '<li class="task"><span class="box"></span>', seg)
        # 单独成段的图片 -> figure
        seg = re.sub(
            r'<p>\s*<img alt="([^"]*)" src="([^"]+)"(?: title="([^"]*)")?\s*/?>\s*</p>',
            lambda m: (f'<figure><img alt="{m.group(1)}" src="{m.group(2)}" loading="lazy">'
                       + (f"<figcaption>{m.group(3) or m.group(1)}</figcaption>" if (m.group(3) or m.group(1)) else "")
                       + "</figure>"),
            seg,
        )
        segments[n] = seg
    body = "".join(segments)

    # 课程链接 lesson:2-1 与图片 img:0-2/x.svg
    def lesson_link(m):
        lid, anchor = m.group(1), m.group(2) or ""
        info = outline_index.get(lid)
        if not info:
            warn(f"[{ctx.lesson_id}] 链接到不存在的课程 lesson:{lid}")
            return 'href="#"'
        if info["status"] != "ready":
            return f'href="{root}index.html#roadmap" class="link-soon" title="后续内容，本批未交付"'
        return f'href="{root}lessons/{lesson_file(info)}{anchor}"'
    body = re.sub(r'href="lesson:([\w-]+)(#[^"]*)?"', lesson_link, body)

    def img_src(m):
        rel = m.group(1)
        if not (SITE / "assets" / "img" / rel).exists():
            warn(f"[{ctx.lesson_id}] 图片不存在：assets/img/{rel}")
        return f'src="{root}assets/img/{rel}"'
    body = re.sub(r'src="img:([^"]+)"', img_src, body)

    # 包裹表格，窄屏可横向滚动
    body = re.sub(r"(<table(?:\s[^>]*)?>[\s\S]*?</table>)", r'<div class="table-wrap">\1</div>', body)
    return body


# ---------------------------------------------------------------- 页面组件
def lesson_file(info: dict) -> str:
    return f'{info["id"]}-{info["slug"]}.html'


def parse_front_matter(text: str):
    meta = {}
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end > 0:
            for line in text[4:end].split("\n"):
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
            text = text[end + 4:].lstrip("\n")
    return meta, text


def build_sidebar(outline: dict, current: str | None, root: str) -> str:
    parts = []
    for st in outline["stages"]:
        items = []
        for l in st["lessons"]:
            if l["status"] == "ready":
                cls = ' class="active"' if l["id"] == current else ""
                items.append(f'<li><a href="{root}lessons/{lesson_file(l)}" data-lid="{l["id"]}"{cls}>'
                             f'<span class="nid">{l["id"]}</span><span>{html.escape(l["title"])}</span></a></li>')
            else:
                items.append(f'<li><span class="soon"><span class="nid">{l["id"]}</span>'
                             f'<span>{html.escape(l["title"])}</span></span></li>')
        parts.append(
            f'<div class="nav-stage" style="--c:{st["color"]}"><div class="nav-stage-title"><span class="dot"></span>'
            f'阶段 {st["id"]} · {html.escape(st["name"])}</div><ol>{"".join(items)}</ol></div>'
        )
    return "\n".join(parts)


def build_toc(tokens: list) -> str:
    if not tokens:
        return ""

    def walk(ts):
        lis = []
        for t in ts:
            sub = f"<ul>{walk(t['children'])}</ul>" if t.get("children") else ""
            lis.append(f'<li><a href="#{t["id"]}">{html.escape(t["name"])}</a>{sub}</li>')
        return "".join(lis)
    return f'<div class="toc-title">本页目录</div><ul>{walk(tokens)}</ul>'


def render_page(**kw) -> str:
    def rep(m):
        return kw.get(m.group(1), "")
    return re.sub(r"\{\{(\w+)\}\}", rep, TEMPLATE)


def stars(level: int) -> str:
    return "★" * level + "☆" * (3 - level)


def build_lesson(info, stage, outline, index, ready_list):
    lid = info["id"]
    src = CONTENT / "lessons" / f"{lid}-{info['slug']}.md"
    if not src.exists():
        warn(f"[{lid}] 缺少源文件 {src.relative_to(ROOT)}")
        return
    meta, text = parse_front_matter(src.read_text(encoding="utf-8"))
    ctx = Ctx(lid)
    root = "../"
    processed = process_containers(text, ctx)
    body, toc_tokens = md_to_html(processed, with_toc=True)
    body = postprocess(body, index, ctx, root)

    nb = info.get("notebook")
    meta_items = [f"约 {info['minutes']} 分钟", f"难度 {stars(info['level'])}"]
    if nb:
        meta_items.append(f"配套练习本 <code>notebooks/{nb}</code>")
    if meta.get("prereq"):
        meta_items.append("前置：" + md_inline(meta["prereq"]))
    hero = (
        f'<header class="lesson-hero"><div class="crumb">阶段 {stage["id"]} · {html.escape(stage["name"])}</div>'
        f'<h1><span class="lid">{lid}</span>{html.escape(info["title"])}</h1>'
        + (f'<p class="lesson-summary">{md_inline(meta["summary"])}</p>' if meta.get("summary") else "")
        + f'<ul class="lesson-meta">{"".join(f"<li>{x}</li>" for x in meta_items)}</ul></header>'
    )
    cta = ""
    if nb:
        for folder in ("notebooks", "solutions"):
            if not (ROOT / folder / nb).exists():
                warn(f"[{lid}] 缺少配套练习本 {folder}/{nb}")
        cta = (
            f'<div class="nb-cta"><div class="nb-icon">.ipynb</div><div class="nb-text">'
            f'<b>读完了？打开练习本动手做一遍</b><br>在 JupyterLab 左侧文件栏打开 <code>notebooks/{nb}</code>，'
            f'从上到下逐格运行，完成里面的练习。卡住了再对照 <code>solutions/</code> 同名答案。'
            f'<p><a href="../../notebooks/{nb}" download>学生练习本</a> · '
            f'<a href="../../solutions/{nb}" download>参考答案本</a>（仍需保留教程完整目录）</p></div></div>'
        )
    pos = ready_list.index(lid)
    prev_info = index[ready_list[pos - 1]] if pos > 0 else None
    next_info = index[ready_list[pos + 1]] if pos + 1 < len(ready_list) else None
    pager = '<nav class="pager">'
    if prev_info:
        pager += (f'<a class="prev" href="{lesson_file(prev_info)}"><small>← 上一课</small>'
                  f'{prev_info["id"]} {html.escape(prev_info["title"])}</a>')
    if next_info:
        pager += (f'<a class="next" href="{lesson_file(next_info)}"><small>下一课 →</small>'
                  f'{next_info["id"]} {html.escape(next_info["title"])}</a>')
    pager += "</nav>"
    footer = (f'<footer class="lesson-footer"><div class="done-box"><span>学完这一课了吗？标记后首页会记录你的进度（只保存在本机浏览器）。</span>'
              f'<button type="button" class="done-btn">标记本课已学完</button></div>{pager}</footer>')
    main = f'{hero}<article class="lesson-body">{body}{cta}</article>{footer}'
    scripts = [f'<script src="../assets/js/widgets/{w}.js"></script>' for w in sorted(ctx.widgets)]
    page = render_page(
        page_title=f"{lid} {info['title']}", site_title=outline["site_title"], root=root,
        body_class="page-lesson", lesson_id=lid, stage_color=stage["color"],
        sidebar=build_sidebar(outline, lid, root), toc=build_toc(toc_tokens), main=main,
        scripts="\n".join(scripts),
    )
    page = page.replace('<script src="../assets/js/app.js"></script>',
                        '<script src="../assets/js/outline.js"></script>\n<script src="../assets/js/app.js"></script>')
    (SITE / "lessons" / lesson_file(info)).write_text(page, encoding="utf-8")


def build_roadmap(outline: dict, root: str) -> str:
    cards = []
    for st in outline["stages"]:
        ready = [l for l in st["lessons"] if l["status"] == "ready"]
        lis = []
        for l in st["lessons"]:
            if l["status"] == "ready":
                lis.append(f'<li data-lid="{l["id"]}"><span class="nid">{l["id"]}</span>'
                           f'<a href="{root}lessons/{lesson_file(l)}">{html.escape(l["title"])}</a></li>')
            else:
                lis.append(f'<li class="soon"><span class="nid">{l["id"]}</span>{html.escape(l["title"])}</li>')
        mins = sum(l["minutes"] for l in st["lessons"])
        soon = "" if ready else " is-soon"
        cards.append(
            f'<section class="stage-card{soon}" data-sid="{st["id"]}" style="--c:{st["color"]}">'
            f'<h3><span class="sid">{st["id"]}</span>{html.escape(st["name"])}</h3>'
            f'<p class="stage-desc">{html.escape(st["desc"])} · 约 {round(mins / 60, 1)} 小时</p>'
            f'<ol>{"".join(lis)}</ol><div class="stage-bar"><i></i></div></section>'
        )
    return f'<div class="roadmap">{"".join(cards)}</div>'


def build_home(outline: dict, index: dict):
    src = CONTENT / "home.md"
    meta, text = parse_front_matter(src.read_text(encoding="utf-8"))
    ctx = Ctx("home")
    root = ""
    ready = [l for s in outline["stages"] for l in s["lessons"] if l["status"] == "ready"]
    replacements = {
        "{{READY_COUNT}}": str(len(ready)),
        "{{NOTEBOOK_COUNT}}": str(sum(bool(l.get("notebook")) for l in ready)),
        "{{STUDY_HOURS}}": str(round(sum(l["minutes"] for l in ready) / 60, 1)),
    }
    for token, value in replacements.items():
        text = text.replace(token, value)
    text = text.replace("{{ROADMAP}}", ctx.put(build_roadmap(outline, root)))
    body = md_to_html(process_containers(text, ctx))
    body = postprocess(body, index, ctx, root)
    first = next(l for s in outline["stages"] for l in s["lessons"] if l["status"] == "ready")
    hero = (
        f'<section class="home-hero"><h1>{html.escape(outline["site_title"])}</h1>'
        f'<p>{md_inline(meta.get("hero", outline["site_subtitle"]))}</p><div class="hero-actions">'
        f'<a class="hero-btn resume-link" href="lessons/{lesson_file(first)}">从第一课开始</a>'
        f'<a class="hero-btn ghost" href="lessons/{lesson_file(index["0-3"])}">直接去装环境</a></div></section>'
    )
    main = f'{hero}<div class="home-body lesson-body">{body}</div>'
    scripts = "\n".join(f'<script src="assets/js/widgets/{w}.js"></script>' for w in sorted(ctx.widgets))
    page = render_page(
        page_title="首页", site_title=outline["site_title"], root=root, body_class="page-home",
        lesson_id="", stage_color="#4f46e5", sidebar="", toc="", main=main, scripts=scripts,
    )
    page = page.replace('<script src="assets/js/app.js"></script>',
                        '<script src="assets/js/outline.js"></script>\n<script src="assets/js/app.js"></script>')
    (SITE / "index.html").write_text(page, encoding="utf-8")


def check_links():
    for page in list(SITE.glob("*.html")) + list((SITE / "lessons").glob("*.html")):
        text = page.read_text(encoding="utf-8")
        for m in re.finditer(r'(?:href|src)="([^"#:]+?)(?:#[^"]*)?"', text):
            target = m.group(1)
            if target.startswith(("http", "mailto", "javascript", "data")) or not target:
                continue
            if not (page.parent / target).resolve().exists():
                warn(f"[链接检查] {page.relative_to(SITE)} -> {target} 不存在")


def main():
    WARNINGS.clear()
    outline = json.loads((CONTENT / "outline.json").read_text(encoding="utf-8"))
    index = {}
    ready_list = []
    for st in outline["stages"]:
        for l in st["lessons"]:
            index[l["id"]] = l
            if l["status"] == "ready":
                ready_list.append(l["id"])
    if not (SITE / "lessons").exists():
        (SITE / "lessons").mkdir(parents=True)
    slim = {"stages": [{"id": s["id"], "lessons": [{k: l[k] for k in ("id", "slug", "title", "status")} for l in s["lessons"]]}
                       for s in outline["stages"]]}
    (SITE / "assets" / "js" / "outline.js").write_text(
        "/* 由 tools/build_site.py 自动生成，请勿手改 */\nwindow.DA_OUTLINE = " + json.dumps(slim, ensure_ascii=False) + ";\n",
        encoding="utf-8")

    only = {a for a in sys.argv[1:] if not a.startswith("--")}
    for st in outline["stages"]:
        for l in st["lessons"]:
            if l["status"] == "ready" and (not only or l["id"] in only):
                build_lesson(l, st, outline, index, ready_list)
    build_home(outline, index)
    check_links()
    print(f"生成完成：{len(ready_list)} 课 + 首页 -> {SITE.relative_to(ROOT)}/")
    if WARNINGS:
        print(f"\n共有 {len(WARNINGS)} 条警告：")
        for w in WARNINGS:
            print("  - " + w)
        sys.exit(1 if "--strict" in sys.argv else 0)


if __name__ == "__main__":
    main()
