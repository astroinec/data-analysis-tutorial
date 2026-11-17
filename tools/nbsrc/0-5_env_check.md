# 0-5 环境体检

先完成网页安装课，在课程根目录的 Anaconda Prompt 激活 `da-course` 并启动 JupyterLab。请从完整教材 `notebooks/` 或 `solutions/` 的原位置打开本子，不单独移动。选择 **Python (da-course)** 内核。这里是 Notebook：Python 代码在代码格运行，终端命令仍在 Anaconda Prompt。

点击第一代码格，按 `Shift+Enter`。说明格的文字不是需要复制的代码。出现错误时先读最后一行并回网页 A-1/A-2，不在错误内核中盲目安装包。

```python
import sys
sys.path.insert(0, "..")
from dacheck import check, hint, setup_chinese_font
import pandas as pd
```

+++

## 观察解释器与目录

下面是示范，不是练习。`sys.executable` 是正在执行本子的 Python。应该指向课程 `da-course` 环境。Notebook cwd 通常在 `notebooks/` 或 `solutions/`，不是 Prompt 的教程根目录。中文/空格不是必然故障。

```python
from pathlib import Path
from dacheck import ROOT_DIR, DATA_DIR
print("Python 路径：", sys.executable)
print("Python 版本：", sys.version.split()[0])
print("Notebook 当前目录：", Path.cwd())
print("课程根目录：", ROOT_DIR)
print("课程数据目录：", DATA_DIR)
```

+++

## 调用离线体检

`run_checks()` 返回结构化列表，不联网、不装包、不改系统 PATH，也不保存永久报告。它仅在自建临时目录做读写和字体检测，之后清理自身临时文件。需要保存 JSON 的操作请看网页课，在 Prompt 明确使用 `--json`。下列代码只展示状态；关键失败未解决时停止进入后续代码课。

如果版本/环境名称失败，查看 `sys.executable` 后回网页排错。作者跨平台运行会显示非 Windows 提示，并不代表真实 Windows 已验证。缺中文字体可先做文字练习，图表课前解决。

```python
from tools.check_env import run_checks
checks = run_checks()
status_table = pd.DataFrame(checks)[["title", "status", "detail", "action"]]
status_table
```

+++

## 练习 0-5.1：确认当前内核路径

把 `python_path = ...` 中的省略号换成 `sys.executable`，不要抄网页上的 D 盘路径，不给变量表达式加引号。检查器比较当前真实解释器，所以不要求这道理解题必须在 Windows 运行。

```python
### BEGIN SOLUTION
python_path = sys.executable
### STUDENT
python_path = ...
### END SOLUTION
check("0-5.1", python_path)
```

+++

## 练习 0-5.2：记住 pip 绑定方法

给 `pip_command` 赋值为字符串 `"python -m pip"`。英文引号要保留。这是一道理解题，不执行网络安装，不需要终端状态，独立于上一题。

```python
### BEGIN SOLUTION
pip_command = "python -m pip"
### STUDENT
pip_command = ...
### END SOLUTION
check("0-5.2", pip_command)
```

+++

## 练习 0-5.3：读到本套数据

给 `book_rows` 赋值为 `pd.read_csv("../data/books.csv").shape[0]`。`shape[0]` 是表格行数；下一阶段细讲。不要猜一个数字，不依赖前两题答案。路径中的 `..` 不需要替换；必须保留本子原位置。

```python
### BEGIN SOLUTION
book_rows = pd.read_csv("../data/books.csv").shape[0]
### STUDENT
book_rows = ...
### END SOLUTION
check("0-5.3", book_rows)
```

+++

## 怎么拿提示与验收

独立运行下一格只显示提示，不影响答案。填好某题后重新运行对应题格；空白 `...` 显示“还没作答”是正常行为。每题互不依赖。

```python
hint("0-5.3")
```

+++

完成后按 `Ctrl+S` 保存。验收：三个练习显示“通过”；体检关键失败为 0；你能解释警告；Notebook 与 Prompt 解释器一致；数据文件与 dacheck 可达。参考答案只用于对照，不把它的执行序号当自己已经做过的证明。下一课学习运行顺序、保存与重启。
