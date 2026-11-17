"""
把 tools/nbsrc/ 里的练习本源文件（Markdown 格式）生成为 Jupyter 练习本。

每个源文件会生成两份：
    notebooks/<名字>.ipynb   学生版：答案被挖空，没有运行结果
    solutions/<名字>.ipynb   答案版：包含完整答案，并且已经运行过，带有全部输出

用法（在教程根目录运行）：
    python tools/build_notebooks.py               # 生成全部并运行检查
    python tools/build_notebooks.py 2-1_pandas_intro   # 只生成某一个
    python tools/build_notebooks.py --no-exec     # 只生成，不运行
    python tools/build_notebooks.py --kernel 内核名  # 指定运行时使用的 Jupyter 内核

源文件格式见 content/AUTHORING.md 的“练习本”一节。
"""
from __future__ import annotations

import argparse
import os
import re
import time
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "tools" / "nbsrc"
OUT_STUDENT = ROOT / "notebooks"
OUT_SOLUTION = ROOT / "solutions"

FENCE_OPEN = re.compile(r"^```python(?:\s+([\w\s-]+))?\s*$")
FENCE_ANY = re.compile(r"^(`{3,}|~{3,})")

KERNELSPEC = {"name": "da-course", "display_name": "Python (da-course)", "language": "python"}


def parse(text: str):
    """返回 [(类型, 内容, 标签集合)]，类型为 markdown 或 code。"""
    cells = []
    md: list[str] = []
    lines = text.split("\n")
    i = 0
    other_fence = None

    def flush_md():
        chunk = "\n".join(md).strip("\n")
        if chunk.strip():
            cells.append(("markdown", chunk, set()))
        md.clear()

    while i < len(lines):
        line = lines[i]
        if other_fence:
            md.append(line)
            if line.startswith(other_fence):
                other_fence = None
            i += 1
            continue
        m = FENCE_OPEN.match(line)
        if m:
            flush_md()
            tags = set((m.group(1) or "").split())
            code: list[str] = []
            i += 1
            while i < len(lines) and not re.match(r"^```\s*$", lines[i]):
                code.append(lines[i])
                i += 1
            cells.append(("code", "\n".join(code), tags))
            i += 1
            continue
        fm = FENCE_ANY.match(line)
        if fm:
            other_fence = fm.group(1)
            md.append(line)
            i += 1
            continue
        if line.strip() == "+++":
            flush_md()
            i += 1
            continue
        md.append(line)
        i += 1
    flush_md()
    return cells


SOL_BEGIN = re.compile(r"^(\s*)### BEGIN SOLUTION\s*$")
SOL_STUDENT = re.compile(r"^\s*### STUDENT\s*$")
SOL_END = re.compile(r"^\s*### END SOLUTION\s*$")


def split_solution(code: str):
    """返回 (学生版代码, 答案版代码, 是否含答案块)。"""
    student, solution = [], []
    mode = None
    indent = ""
    had_student = False
    has_block = False
    for line in code.split("\n"):
        mb = SOL_BEGIN.match(line)
        if mb:
            mode, indent, had_student, has_block = "sol", mb.group(1), False, True
            continue
        if mode and SOL_STUDENT.match(line):
            mode, had_student = "stu", True
            continue
        if mode and SOL_END.match(line):
            if not had_student:
                student.append(f"{indent}# 在这里写你的代码")
            mode = None
            continue
        if mode == "sol":
            solution.append(line)
        elif mode == "stu":
            student.append(line)
        else:
            student.append(line)
            solution.append(line)
    if mode:
        raise ValueError("### BEGIN SOLUTION 没有对应的 ### END SOLUTION")
    return "\n".join(student), "\n".join(solution), has_block


SOLUTION_BANNER = ("> **这是参考答案版**，保留完整示例与解法。代码格下方的输出会在运行后出现。\n"
                   "> 建议先在 `notebooks/` 文件夹里的学生版自己做一遍，卡住了再来这里对照。")


def build(src: Path):
    cells = parse(src.read_text(encoding="utf-8"))
    stu_nb = new_notebook(metadata={"kernelspec": KERNELSPEC, "language_info": {"name": "python"}})
    sol_nb = new_notebook(metadata={"kernelspec": KERNELSPEC, "language_info": {"name": "python"}})
    n_ex = 0
    for kind, content, tags in cells:
        if kind == "markdown":
            stu_nb.cells.append(new_markdown_cell(content))
            sol_nb.cells.append(new_markdown_cell(content))
            if len(sol_nb.cells) == 1:
                sol_nb.cells.append(new_markdown_cell(SOLUTION_BANNER))
            continue
        stu, sol, has_block = split_solution(content)
        n_ex += has_block
        if "solution-only" not in tags:
            stu_nb.cells.append(new_code_cell(stu))
        if "student-only" not in tags:
            sol_nb.cells.append(new_code_cell(sol))
    return stu_nb, sol_nb, n_ex


def execute(nb, cwd: Path, kernel: str, label: str):
    from nbclient import NotebookClient
    client = NotebookClient(nb, timeout=180, kernel_name=kernel, allow_errors=True,
                            resources={"metadata": {"path": str(cwd)}})
    env = dict(os.environ)
    env["DACHECK_NO_PROGRESS"] = "1"
    env["DACHECK_STRICT"] = "1" if label.startswith("答案") else "0"
    client.execute(env=env)
    errors = []
    for k, c in enumerate(nb.cells):
        if c.cell_type != "code":
            continue
        for o in c.get("outputs", []):
            if o.get("output_type") == "error":
                errors.append(f"{label} 第 {k + 1} 格：{o.get('ename')}: {o.get('evalue')}"[:300])
            if o.get("output_type") == "stream" and o.get("name") == "stderr":
                txt = o.get("text", "")
                if "Warning" in txt:
                    errors.append(f"{label} 第 {k + 1} 格 有警告：{txt.strip()[:200]}")
    nb.metadata["kernelspec"] = KERNELSPEC
    nb.metadata["da_build"] = {"executed": True, "checks_passed": not errors}
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("names", nargs="*", help="Notebook 源文件名（不含 .md）")
    parser.add_argument("--no-exec", action="store_true", help="只生成，不验证或保存运行结果")
    parser.add_argument("--kernel", default="da-course", help="作者验证所用 Jupyter 内核")
    args = parser.parse_args()
    srcs = sorted(SRC.glob("*.md"))
    available = {s.stem for s in srcs}
    unknown = set(args.names) - available
    if unknown:
        parser.error(f"找不到源文件：{', '.join(sorted(unknown))}")
    if args.names:
        srcs = [s for s in srcs if s.stem in args.names]
    if not srcs:
        parser.error("tools/nbsrc/ 中没有 Notebook 源文件")
    for d in (OUT_STUDENT, OUT_SOLUTION):
        if not d.exists():
            d.mkdir()
    all_problems = []
    exercise_count = 0
    for src in srcs:
        t0 = time.time()
        stu, sol, n_ex = build(src)
        exercise_count += n_ex
        problems = []
        if not args.no_exec:
            problems += execute(sol, OUT_SOLUTION, args.kernel, "答案版")
            stu_run = nbformat.reads(nbformat.writes(stu), as_version=4)
            problems += execute(stu_run, OUT_STUDENT, args.kernel, "学生版")
        else:
            sol.metadata["da_build"] = {"executed": False, "checks_passed": False}
        nbformat.validate(stu)
        nbformat.validate(sol)
        if not problems:
            nbformat.write(stu, OUT_STUDENT / f"{src.stem}.ipynb")
            nbformat.write(sol, OUT_SOLUTION / f"{src.stem}.ipynb")
        status = "未执行" if args.no_exec else "OK"
        if problems:
            status = f"{len(problems)} 个问题（未写入交付文件）"
        print(f"[{status}] {src.stem}：{len(stu.cells)} 格，{n_ex} 道练习，用时 {time.time() - t0:.1f}s", flush=True)
        for p in problems:
            print("    - " + p, flush=True)
        all_problems += problems
    if all_problems:
        print(f"\n共 {len(all_problems)} 个问题需要处理。")
        return 1
    print(f"\n完成：{len(srcs)} 对练习本、{exercise_count} 个练习格。构建不会改写学习者的进度。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
