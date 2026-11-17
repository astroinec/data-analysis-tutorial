# 0-6 JupyterLab 上手

前置：环境体检关键失败为 0；本子位于完整教材的 `notebooks/` 或 `solutions/` 原目录；内核是 **Python (da-course)**。每个格子的实际执行顺序取决于你运行它的顺序，不取决于屏幕上排在哪里。代码格按 `Shift+Enter` 运行；Markdown 格用同一键渲染说明。

每题独立，只需先运行初始化。不要把下面 Python 粘贴到 Anaconda Prompt。

```python
import sys
sys.path.insert(0, "..")
from dacheck import check, hint, setup_chinese_font
import pandas as pd
```

+++

## 最小示范：一句中文输出

`print` 明确打印。下面应该出现“你好，数据分析”。只改这段文字，再重新运行，观察输出更新。

```python
print("你好，数据分析")
```

+++

## 有些正常代码没有输出

赋值、注释和 import 本来可以不产生输出。左侧数字更新表示运行过，保存文件则不代表运行。下一格在自身定义变量后再显示，不依赖练习答案。

```python
sample_total = 12
print("示范数值：", sample_total)
```

+++

## 最后一个表达式会自动展示

这格的结果为 `5`，不是终端命令。代码格下方的输出来自计算，编辑输出文字不能改变变量。

```python
2 + 3
```

+++

## 练习 0-6.1：计算一个简单结果

把省略号换成 `2 + 3`，保留 `result` 和 `check` 编号。可以先预测数值，再运行这格。

```python
### BEGIN SOLUTION
result = 2 + 3
### STUDENT
result = ...
### END SOLUTION
check("0-6.1", result)
```

+++

## 练习 0-6.2：一段中文字符串

给 `message` 赋值为 `"我能运行代码"`。使用英文直引号，中文内容放在引号里。此题不使用上一题的变量。

```python
### BEGIN SOLUTION
message = "我能运行代码"
### STUDENT
message = ...
### END SOLUTION
check("0-6.2", message)
```

+++

## 练习 0-6.3：三项任务有几行

把省略号换成 `pd.DataFrame({"任务": ["读取", "检查", "保存"]}).shape[0]`。不用记完整表格语法，当前先观察一项任务对应一行。检查器从这一小样本计算期望，题目不依赖前两题。

```python
### BEGIN SOLUTION
task_rows = pd.DataFrame({"任务": ["读取", "检查", "保存"]}).shape[0]
### STUDENT
task_rows = ...
### END SOLUTION
check("0-6.3", task_rows)
```

+++

## 提示与常见状态

下面只显示提示，不依赖你完成练习。`...` 仍在时检查器显示“还没作答”，不是系统安装失败。`[*]` 表示正在执行；没有输出但序号变数字可能是正常赋值。运行一直不结束时，先看有没有等待输入，再用 Kernel → Interrupt Kernel 中断当前内核，不结束别的项目。

```python
hint("0-6.2")
```

+++

## 查看中文字体候选

这段不依赖练习答案。没有候选字体或返回 `None` 时，回网页 A-2 处理；不要屏蔽缺字警告。检测字体不需要在这课画图。

```python
font_name = setup_chinese_font(verbose=True)
print("候选字体：", font_name)
```

+++

## 最后做一次可复现验收

1. 按 `Ctrl+S` 保存；保存记录文件，不更新内存变量。
2. 在 Kernel 菜单重启当前内核，再从第一格顺序运行全部。空白练习本显示“还没作答”正常，完成版应三题通过。
3. 重启只清空内存，不删除已保存本子；如果有 NameError，先检查初始化与顺序。
4. 再保存；退出时正常停止当前 Jupyter 服务器，仅关浏览器不保证服务器退出。

不要单独移动本子，避免下一课相对数据路径失效。分享之前查看输出是否含用户名或敏感内容。下一课从变量与数据类型开始。
