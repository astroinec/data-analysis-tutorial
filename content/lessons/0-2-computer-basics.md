---
summary: 能找到真实文件、识别完整路径、解压整套课程，并区分命令、提示符和输出。
prereq: 一台 Windows 11 电脑；尚不需要安装 Python。
---

:::goal 本课目标
- 在文件资源管理器显示扩展名，并读出一个文件的完整路径。
- 完整解压课程 ZIP，确认根目录和 notebooks/data 的相对位置。
- 理解地址栏不是搜索框、目录不是文件、Prompt 不是浏览器。
- 在稍后使用 Anaconda Prompt 时，会用 `cd /d` 与带引号的路径定位。
:::

## 1. 文件、文件夹、磁盘：先把东西放得找得到

文件是一个具体对象，例如表格 `books.csv` 或练习本 `0-5_env_check.ipynb`；文件夹（目录）是容纳它们的位置。`D:` 是一个磁盘盘符，不是人人都有 D 盘。课程示例路径是 `D:\da-course\data-analysis-tutorial`，**必须换成你实际解压的位置**。没有 D 盘可以选你有写权限的 `C:\da-course\data-analysis-tutorial`；若这条路径无权限，选自己的有权限目录，不要长期用管理员运行来绕过。

:::window 文件资源管理器（界面示意，不是实机截图）
| 区域 | 示例内容 | 你要做什么 |
| --- | --- | --- |
| 顶部地址栏 | `D:\da-course\data-analysis-tutorial` | 点空白处或按 `Alt+D` 显示路径，复制实际地址 |
| 右上搜索框 | 搜索 data-analysis-tutorial | 用来找名字，不是切换路径；不要把命令粘进这里 |
| 主区域 | `content`、`data`、`notebooks`、`requirements.txt` | 找到课程根目录的这些同级对象 |
| 菜单 | [[查看]] → [[显示]] → [[+文件扩展名]] | 勾选后，文件名末尾显示 `.csv`、`.ipynb` 等 |
:::

按 `Win+E` 打开文件资源管理器。进入你保存下载文件的文件夹。在 Windows 11 的“查看 → 显示”中打开“文件扩展名”；菜单名称可能因系统更新稍变，目标是让完整文件名可见。

### 扩展名告诉软件怎样读取，不保证内容正确

| 名字 | 类型 | 本教程如何使用 |
| --- | --- | --- |
| `books.csv` | 逗号分隔文本表格 | 用 pandas 读取；双击可能交给 Excel，但双击不是运行课程 |
| `sample.xlsx` | Excel 工作簿 | 由 pandas + openpyxl 读写 |
| `0-5_env_check.ipynb` | Jupyter 练习本 | 从 JupyterLab 文件栏双击打开 |
| `check_env.py` | Python 脚本 | 在 Prompt 中用 Python 运行 |
| `requirements.txt` | 课程包与版本清单 | 让 pip 按此清单安装，不需要改成 `.py` |
| `index.html` | 网页 | 用浏览器阅读课程 |
| `course.zip` | 压缩包 | 必须先完整解压；里面的文件尚不等于正常工作目录 |

把 `表格.txt` 重命名为 `表格.xlsx` 并不会把文本变成 Excel 工作簿。隐藏扩展名时容易出现 `check_env.py.txt`，所以先打开扩展名显示。不知道文件格式时保留原文件，不批量重命名。

## 2. 完整解压：不要只拿走一个练习本

:::steps 解压课程
:::step 找到 ZIP
在下载位置查看扩展名，确认压缩包是整套课程。不是安装器 `.exe`，也不是只含一个 Notebook 的附件。
:::
:::step 选择全部提取
右键 ZIP，选择 [[全部提取]]。在目标位置填入你有写权限的课程存放父目录，例如 `D:\da-course`；完成后打开提取出来的普通文件夹。
:::
:::step 识别真正的根目录
若下载包外面多套了一层同名文件夹，继续进入，直到同时看到 `requirements.txt`、`data`、`dacheck`、`notebooks`、`tools` 和 `site`。这一级才是教程根目录。
:::
:::step 验证不是在 ZIP 内
看地址栏与文件类型：不应仍显示 ZIP 内部路径或“压缩文件夹工具”。进入 `data` 能看到 `books.csv`，回上一级后仍能看到 `notebooks`。
:::
:::

:::danger 先停止的情况
如果只找到 `.ipynb`，或 `data`/`tools`/`dacheck` 缺失，不继续安装课程依赖；回到 ZIP 完整提取。不要通过另建一个空 data 文件夹假装补齐，也不要下载网上同名 `dacheck`。
:::

从根目录看，数据路径是 `data\books.csv`；从 `notebooks` 看，要先回上一层，所以 Python 里常写 `../data/books.csv`。`..` 表示上一级目录，`.` 表示当前目录，不是要替换的占位符。斜杠写法会随语言有差异：Windows 命令路径常用 `\`，Python 的相对数据路径可用 `/`。

:::flow 文件位置示意
- `data-analysis-tutorial/`：教程根目录
  - `requirements.txt`：安装清单
  - `data/books.csv`：读取数据
  - `dacheck/`：练习检查工具
  - `tools/check_env.py`：环境体检脚本
  - `notebooks/`：练习本原位置
  - `solutions/`：答案本原位置
  - `site/index.html`：从浏览器阅读
:::

## 3. 什么是命令行：给程序发一条明确指令

命令行是接受文字指令的窗口；不是聊天输入框。之后统一使用 Windows 开始菜单中的 **Anaconda Prompt**，不是随手打开普通 CMD、PowerShell 或浏览器开发者工具。本课未安装 Anaconda，可先看懂示例，等[安装课](lesson:0-4)再操作。

:::window Anaconda Prompt（界面示意，不是实机截图）
```text
(da-course) D:\da-course\data-analysis-tutorial>
```
这是“提示符”：`(da-course)` 是当前环境，后面是当前目录，`>` 后才是输入命令的位置。你不会键入这整行；复制课程的 `terminal` 代码块中命令即可。
:::

命令按一次回车才提交。提交后文字滚动是**输出**，包括正常结果、进度和错误；输出不是要求你重新输入。重新出现提示符通常表示上一条命令结束，可以输入下一条；Jupyter 服务器是例外，它一直运行并占用窗口，不能在它的日志中继续输入安装命令。

### 切换到课程目录

以下在 Anaconda Prompt 中运行。第一行换成你的实际课程根目录，双引号要保留：

```terminal
cd /d "D:\da-course\data-analysis-tutorial"
dir
```

`cd` 是切换目录；`/d` 允许同时切换磁盘。如果你在 C 盘只用 `cd D:\...`，可能未真正把当前盘切到 D 盘。`dir` 列出当前目录内容，不会安装或删除东西。路径含空格时双引号防止被拆成多段；中文路径不等于必然有问题。

```output
... data
... dacheck
... notebooks
... requirements.txt
... tools
```

这是省略了日期等字段的**输出示例**。你电脑上的日期、大小、目录顺序可以不同；应出现所需对象。如果出现“系统找不到指定的路径”，回文件资源管理器地址栏复制真实路径，别继续运行安装命令。

:::compare 三种文字不要混淆
:::bad 不要键入
```text
(da-course) D:\da-course\data-analysis-tutorial> python --version
Python 3.12.x
```
把提示符和输出全部当命令会报错。`x` 也不是让你输入的版本字符。
:::
:::good 只提交命令
```terminal
python --version
```
然后观察程序返回的版本；输出位置不可当作输入框。
:::
:::

### Python 里的路径与 Prompt 命令不是一种语言

在 Notebook 代码格中写 `cd /d ...` 不是本课程的操作路线；在 Prompt 中直接写 `import pandas` 也不对。课程的代码块标了 `terminal` 或 `python`，先看窗口再粘贴。以后在 Python 中手写 Windows 绝对路径，可用原始字符串 `r"D:\da-course\data-analysis-tutorial"`；本教程优先相对路径，不要求记住这个语法。

## 4. 文件保存与隐私

浏览器“另存为”网页不能替代下载整套教程。Notebook 的保存是把代码、文字与可能的输出写入 `.ipynb`；关闭浏览器之前要保存，但保存不等于代码执行过。重要原始表格留一份不修改的副本，后续导出使用新文件名。

截图可能包含用户名、浏览器 token、邮箱、工作文件名。求助时保留错误与操作信息，遮盖这些个人内容；不要把整台电脑目录上传。

:::job 文件管理也是交付能力
分析交付给别人时，对方需要知道数据在哪里、哪个文件是结果、从哪里运行。保留明确目录结构与文件扩展名，比“我电脑能打开”更接近可复现的作品。
:::

## 练习与参考

:::try 练习 1：写完整路径
假设根目录为 `D:\da-course\data-analysis-tutorial`，写出 books.csv 的绝对路径和从 notebooks 出发的相对路径。
:::
:::fold 参考答案
绝对路径是 `D:\da-course\data-analysis-tutorial\data\books.csv`。Notebook 中相对路径是 `../data/books.csv`。自己的根目录不同，绝对路径要改变，相对目录关系不变。
:::

:::quiz 练习 2：哪一项才表示根目录找到对了？
- [ ] 双击 ZIP 看到了一个 Notebook
- [x] 提取后的普通文件夹中同时看到 requirements.txt、data、notebooks、tools、dacheck
- [ ] 在桌面新建一个叫 data 的空文件夹
---
相对路径需要整套文件保持结构，单独移动 Notebook 会导致数据和检查工具不可达。
:::

:::try 练习 3：识别输入与输出
看到 `(da-course) C:\Users\某用户>` 后，需要运行 `python --version`。你输入哪些文字？返回 `Python 3.12.13` 后，是否再输入这一行？
:::
:::fold 参考答案
只输入 `python --version` 并按回车；版本是输出，不需要再输入。用户目录是示例，不是让你把 Windows 用户目录改名。
:::

:::try 练习 4：你的实际目录
打开文件资源管理器显示扩展名，在完整解压的根目录复制地址，记下地址和 requirements.txt 的真实完整名字。尚未拿到完整教程包时，只写“等待整包”，不要自造空结构。
:::
:::fold 验收参考
地址不在 ZIP 内部；根目录有真实课程对象；文件是 `requirements.txt` 而不是 `requirements.txt.txt`。没有 D 盘不算错误，路径用自己有权限的目录。
:::

:::checklist 本课验收
- [ ] 我打开了文件扩展名显示，能分清 `.ipynb`、`.py` 与 `.txt`。
- [ ] 我能找到普通文件夹形式的课程根目录，且整套文件完整。
- [ ] 我知道示例 D 盘路径必须替换，提示符和输出不能复制为命令。
- [ ] 我能解释 `cd /d`、双引号、`..` 的作用。
:::

常见错误是仍在 ZIP 内、进入多一层文件夹、把搜索框当地址栏、复制了提示符。修正目录后再进入[安装前体检](lesson:0-3)。
