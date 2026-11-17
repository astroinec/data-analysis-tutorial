# 内容与练习本编写约定

这份说明面向教程维护者与后续视觉重设计者。学习者从 `site/index.html` 开始，不需要运行构建脚本。

## 教学范围与统一路线

- 第一批：阶段 0～4、项目 P-1、工具箱 A-1～A-5。阶段 5～8、P-2/P-3 只展示路线，不冒充已完成课程。
- 读者：零编程基础、想增加量化能力的文科求职者；Windows 11 64 位电脑从零开始。其他系统不冒充实机验证。
- 环境统一为 Anaconda + 独立 conda 环境 `da-course` + Python 3.12；不在 `base` 安装课程包，不要求改系统 PATH。
- 教程根目录例子：`D:\da-course\data-analysis-tutorial`；没有 D 盘时可用当前用户有写权限的 `C:\da-course\data-analysis-tutorial`，不能因为权限错误建议用管理员终端长期运行。
- 安装命令：`conda create -n da-course python=3.12 pip -y` → `conda activate da-course` → 在教程根目录 `python -m pip install -r requirements.txt` → `python -m ipykernel install --user --name da-course --display-name "Python (da-course)"` → `python -m jupyter lab`。
- 明确区分 Anaconda Prompt 中的命令、Notebook 中的 Python、只供观察的输出。不要把 `(da-course) D:\...>` 提示符当作命令。
- 模拟数据全部虚构；公开数据是历史教学数据。项目不写“真实公司经营结果”，不虚构真实简历业绩，不将相关性当成因果。
- 先保留原始数据。缺失评分不等于差评；订单一行一个订单、一个商品，不把金额汇总重复算。
- 版本统一见根目录 `requirements.txt`，作者实际验证环境为 Python 3.12.13。不要换成不同的 pandas/Plotly 写法。

## HTML 讲义源

路径：`content/lessons/<编号>-<slug>.md`，编号/slug 以 `content/outline.json` 为准。

文件开头可以有简单元信息：

```text
---
summary: 本课用一句话说清楚要解决什么问题。
prereq: 已完成第 0-6 课
---
```

网页模板会生成标题，不要在源文件重复写一级标题。正文用二级/三级标题。每课至少包含：

1. 可检验的学习目标与前置条件。
2. 白话解释 → 小样例 → 结果 → 为什么。
3. 一项视觉辅助（示意表、对照、流程、窗口示意或交互）。
4. 3～5 个练习或理解检查（长课可更多），提示与折叠参考答案。
5. 常见错误、纠正路径、求职中的用途与本课验收清单。

时间只是阅读/初次操作估计；练习、排错可能需要更多时间。Windows 安装截图如果未实际采集，只能叫“界面示意”，不能声称是真实截图。

## 容器语法

所有容器以 `:::名字 可选标题` 开始、单独一行 `:::` 结束。嵌套容器保持相同的三个冒号即可；不要缩进整个代码块。普通 Markdown、表格、代码围栏可放在容器中。

支持：

- `goal / note / tip / warn / danger / job / analogy / try / recap`：语义提示框。
- `cards` 中放多个 `card 标题`：概念卡片。
- `compare` 中放 `bad` 与 `good`：正误对照。
- `steps` 中放 `step 标题`：有序操作流程。
- `flow`：简短流程，适合用普通列表表示。
- `tabs` 中放 `tab 标题`：标签切换。
- `fold 标题`：折叠答案或补充说明。
- `window 标题（界面示意）`：安装、文件管理等界面示意。
- `df`：普通 Markdown 表格的强调版。
- `checklist 标题`：使用 `- [ ] 可验证的操作`，浏览器本地保存勾选。
- `quiz`：单选小测验，恰好一个 `- [x]` 正确项，其他用 `- [ ]`。`---` 后为解释。
- `html`：必要的语义化 HTML；不写行内脚本、行内 CSS 或 CDN。

示例：

```text
:::quiz
为什么缺失评分不能填成 0？
- [ ] 缺失值都必须删除
- [x] 未评价和评价为零不是同一件事
- [ ] Python 不认识数字 0
---
填 0 会制造原本没有的低评分，改变平均评分。
:::
```

课程跳转：`[回到筛选](lesson:2-2)`。图片：`![示意说明](img:filename.svg)`，对应 `site/assets/img/filename.svg`。文件下载从课程页指向 `../../data/...` 或 `../../notebooks/...`。

代码语言标记：`python`、`terminal`（Anaconda Prompt）、`cmd`、`powershell`、`output`、`error`、`text`、`csv`。终端块如果带提示符，复制按钮只复制命令行。

界面标签支持 `[[下一步]]`、`[[*安装]]`、`[[!不要勾选]]`、`[[+选择这里]]`。这些是示意标签，不是假安装器，也不是真正按钮。

## 离线教学交互

使用 `:::widget 名字 标题`，内部可放 JSON 对象。所有交互仅模拟小数据，**不执行 Python**。可用组件：

- `table-lab`：筛选、排序、分组的示意。配置 `{"mode":"filter"}`、`{"mode":"groupby"}` 或 `{"mode":"sort"}`，固定内置小样本，无需传数据。
- `cleaning-lab`：重复与缺失示意，配置留空。
- `chart-picker`：按问题选图表，配置留空。
- `env-doctor`：环境故障分流，配置留空。不会读取读者电脑，不替代检查脚本。

配置只使用上面的键。不要发明未实现的组件名。交互脚本只放在 `site/assets/js/widgets/`；主模板保留 `data-widget`、`.widget-body` 等挂载约定。

## Notebook 源

路径：`tools/nbsrc/<outline 中 notebook 文件名去掉 .ipynb>.md`。

普通 Markdown 成为说明格，`python` 围栏成为代码格；单独一行 `+++` 分隔说明格。其他语言围栏留在说明里。

每份 Notebook 是独立的，不能依赖上一份运行结果。第一格统一：

```python
import sys
sys.path.insert(0, "..")
from dacheck import check, hint, setup_chinese_font
import pandas as pd
```

数据从 `../data/...` 读取；Notebook 默认工作目录就是 `notebooks/` 或 `solutions/`。提醒学习者从原位置打开，不要单独移动文件。可用 `dacheck.DATA_DIR` 等绝对根路径辅助。

练习格使用标记，生成时挖空学生代码：

````text
```python
### BEGIN SOLUTION
row_count = pd.read_csv("../data/books.csv").shape[0]
### STUDENT
row_count = ...
### END SOLUTION
check("2-1.1", row_count)
```
````

必须显式写 `### STUDENT` 并给变量赋 `...`。这样学生按“运行全部”时显示“还没作答”，而不是 NameError。所有练习相互独立；不要在后续普通代码格对这个 `...` 变量运算。示范报错必须用 `try/except` 捕获，或只写在 Markdown 中。

- `python solution-only`：只出现在答案本（如完整报告导出）。
- `python student-only`：只出现在练习本（避免依赖被挖空变量）。
- 图表用 `setup_chinese_font()`，绘完 `plt.show()`；不能忽略字体缺字警告。
- Plotly Notebook 静态预览可用 `fig.show(renderer="notebook")`；导出用 `fig.write_html(..., include_plotlyjs=True)`，不要依赖 CDN。
- 导出练习优先使用 `tempfile.TemporaryDirectory()`，不覆盖原始数据或污染作者验证目录。

构建：`python tools/build_notebooks.py --kernel da-course`。生成 `notebooks/` 的学生版和 `solutions/` 的执行过的答案版。作者验证时使用 `da-venv` 内核，不写进最终内核元信息。

## 自动检查函数

路径：`dacheck/checks/l1_1.py` 等（一课一个文件），不能和其他作者改同一个文件。编号用 `"1-1.1"` 这样的格式。

```python
from dacheck.core import register, expect_equal, load

@register("2-1.1", hint="shape 的第一个数是行数。", title="查看行数")
def check_rows(answer):
    expect_equal(answer, load("books.csv").shape[0], "图书数量")
```

可用 `expect_close / expect_equal / expect_df / expect_series / expect_type / expect / fail`。优先从随包数据动态计算期望，不写猜测的硬编码数字。`expect_df` 默认要求行顺序一致，但不比较原索引/列顺序。若题目不要求行序，用 `check_order=False`。

作者构建使用严格检查模式：错误答案会使构建失败。学习者的未作答/错误答案显示中文指导，不抛长串内部错误。不要通过 `assert check(...)` 让空白学生版崩溃。

## 多人协作边界

每位作者只修改分配的课、Notebook 源和检查模块；不改全局模板/CSS/outline/构建脚本。主维护者统一集成。最终链接检查、Notebook 运行与浏览器验收由主维护者完成。
