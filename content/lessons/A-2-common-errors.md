---
summary: 从错误最后一行识别类别，按最小修正恢复，并保留能复现的错误信息。
prereq: 会区分 Prompt 命令与 Notebook Python 格；不确定环境时先用 A-1。
---

:::goal 本课目标
- 看懂 traceback 的末行错误类型与被指向的代码位置。
- 分清语法、变量、路径、包/内核、字体/编码和网络错误。
- 避免把错误“隐藏”当修复；只改与证据对应的局部问题。
- 修复后重新运行并检查结果，而不只以无红字为目标。
:::

## 1. 先读最后一行，再向上找具体位置

Notebook 的 traceback 是“执行经过哪些位置才失败”的记录。初次阅读先看最后一行的错误类型，再找你自己格子的文件/行号与代码箭头，不用把所有库内部代码读懂。不要把报错粘到新格重新执行。

:::window Python 错误阅读（界面示意，不是实机截图）
```error
Cell In[4], line 1
----> 1 print(total)
NameError: name 'total' is not defined
```
- `Cell In[4]`：执行记录中的格子，不等于当前屏幕第 4 格。
- `line 1`：该格代码的第 1 行。
- 箭头：执行到这里遇错。
- 末行：变量 total 当前不存在；先检查拼写/运行顺序，不安装新包。
:::

下面出现的错误块仅供观察，**不是要你复制执行**。需要示范运行的异常都用 try/except 捕获，避免练习本“运行全部”故意崩掉。

## 2. 高频错误速查

| 最后一行或终端症状 | 常见原因 | 第一检查 | 最小修正 |
| --- | --- | --- | --- |
| `SyntaxError` | 引号、括号、冒号，或错窗口语言 | 指向的代码与前一行 | 改语法/切回正确窗口 |
| `IndentationError` | Python 缩进层级不对 | if/for/def 后面的行 | 同层统一空格，不混 Tab |
| `NameError` | 变量未定义、错拼、未运行初始化 | 当前变量与执行顺序 | 先定义、从第一格运行 |
| `ModuleNotFoundError` | 包不在当前解释器/内核，或教材没完整解压 | sys.executable/文件位置 | 正确内核/安装清单/完整解压 |
| `FileNotFoundError` | cwd 错、文件名错、扩展名隐藏 | Path.cwd() 与真实文件名 | 修正路径，不创建空文件凑数 |
| `PermissionError` | 无写权限或 Excel/其他软件锁文件 | 目标目录与打开的文件 | 另用可写位置/新文件名，或正常关闭占用 |
| `KeyError` | 列名/字典键不存在 | df.columns / 实际键 | 按真实名字更正，不猜字段 |
| `TypeError` | 类型不适合操作 | type(value) 与题目类型 | 转换有依据的类型，先保留原值 |
| `ValueError` | 值格式无法转换/日期不合法等 | 原始值和转换规则 | 定位无效值，不盲填 0 |
| `UnicodeDecodeError` | 文件编码与解码方式不符 | 文件来源与已知编码 | 按明确编码读取，保留原件 |
| `ImportError / DLL load failed` | 二进制依赖、架构或安装损坏等 | 环境路径、版本、完整错误 | 保存诊断，不盲复制 DLL |

不要把“常见原因”当作已确认原因；错误有多种来源，先查第一证据。下一阶段会详细讲类型、列名和转换，本课重点是识别与安全恢复。

## 3. SyntaxError：输入法与错窗口最常见

:::compare 引号要是 Python 认识的符号
:::bad 弯引号是文字排版，不是 Python 引号
```text
print(“你好”)
```
或者在 Python 格写 `conda activate da-course`。这都不是缺包问题。
:::
:::good 英文直引号，中文放里面
```python
print("你好")
```
conda 命令回 Anaconda Prompt；代码格只运行本课标为 Python 的代码。
:::
:::

中文逗号 `，`、中文冒号 `：`、全角括号也不能替代语法符号。语法错误指向下一行时，上一行可能少了闭合引号或括号。一次只修一处，再运行。不要为了输入方便把正常中文数据全部改成英文。

`IndentationError` 多出现在 `if`、`for`、`def` 后，下一行通常缩进四个空格；同层必须一致。复制代码时不要把 Markdown 列表的缩进、行号或提示符带进去，具体语法见[控制流程](lesson:1-3)。

## 4. NameError 与输出不出现：不一定是软件坏

重启内核后所有内存变量消失；保存文件不会恢复变量。先运行初始化，再运行定义变量的格，最后运行使用它的格。`total` 和 `Total` 不同，拼写要一致。

```python
total = 12
print(total)
```

结果应为 `12`。只执行 `total = 12` 没输出正常；加 `print(total)` 或把 `total` 作为最后一行表达式。若 Markdown 格只渲染了文字，切为 Code 后再执行。`[*]` 长时间不结束先看是否等待输入，再 Interrupt 当前内核，不直接杀所有 Python。

检查器的“还没作答”说明 `...` 尚未替换；“还不对”说明答案与期望不一致；“出错了”可能是答案类型或检查过程错误。这三者都不等于要重装 Anaconda。保留 `check("课号.题号", variable)` 的编号和变量名，只按题目改答题表达式。

## 5. ModuleNotFoundError、pip 缺失与 DLL 错误

### 包名找不到

Notebook 先查看：

```python
import sys
print(sys.executable)
```

如果不是 da-course，换正确内核，重启并从第一格跑。Prompt 里确认 da-course 后用 `python -m pip --version`，再在根目录 `python -m pip install -r requirements.txt`。不在 base 安装，不用 pip `--user`，不靠裸 pip 的搜索顺序。`No module named pip` 用[A-1 pip 缺失](lesson:A-1)里的 conda 命令补到指定环境。

`No module named dacheck`：这是随包工具，不是本课让你网上找的库。确认 ZIP 完整提取、Notebook 在原目录、第一格 `sys.path.insert(0, "..")` 已运行。不要安装网上同名包。

### 包有版本信息，却导入时报错

`DLL load failed`、`numpy.dtype size changed`、无法导入某符号等，可能涉及架构、二进制兼容、版本不一致或安装损坏。先运行离线体检（它会分别检查版本与导入），记录 Python 位数、真实路径、要求/实装版本、完整错误。不要下载散装 DLL 到系统目录，不把版本清单改成任意“最新”，不关闭杀毒以求通过。若是正确环境但依赖仍异常，拿证据求助维护者再做针对性修复；不要删除 base 或所有环境。

## 6. FileNotFoundError、扩展名与 PermissionError

在 Notebook 使用：

```python
from pathlib import Path
print(Path.cwd())
print(Path("../data/books.csv").resolve())
print(Path("../data/books.csv").is_file())
```

这是观察代码，不删除/修改文件。`resolve()` 展示候选绝对位置，**不证明文件存在**；`is_file()` 返回 True 才说明对应文件可见。Notebook 正常在 notebooks/，数据在上一层 data；移动本子会改变路径。根目录路径、ZIP 未完整解压、多一层目录、`books.csv.txt` 都需要从资源管理器核实。

Prompt 的 `cd /d "实际根目录"` 可同时切盘，路径含空格要引号。Python 手写 Windows 绝对路径可用 `r"D:\da-course\data-analysis-tutorial\data\books.csv"`；这里 D 盘是示例，必须换自己的；本课仍优先相对路径。

PermissionError 写 Excel 时可能是工作簿仍在 Excel 中打开。先保存并正常关闭自己打开的该文件，或用新输出名；目录本身无权限就换合规可写位置。不要改系统目录权限、不常驻管理员、不覆盖原始数据。

## 7. 中文编码：乱码与字体方框是两类问题

| 现象 | 属于哪一层 | 先处理什么 |
| --- | --- | --- |
| `UnicodeDecodeError` | 文本字节如何变成字符 | 确认源文件编码 |
| 表格中文看起来像“ä…” | 曾用错误编码读/存 | 保留原件，从正确来源重新读，不对乱码猜测修复 |
| 表格中文正常，图上方框 | 字体是否含这些字形 | 设置实际中文字体 |
| Prompt 输出中文乱码，Notebook 正常 | 终端编码/字体显示 | 先区分文件数据是否正常，按单位/系统支持流程调整显示 |

本套 CSV 按其数据说明读取，通常用 UTF-8，带 BOM 的文件可用 `utf-8-sig`。如果来源明确是 GBK，才用 `encoding="gbk"`；不要一轮试所有编码到“不报错”为止，因为读得出不等于文字正确。

```python
import pandas as pd
books = pd.read_csv("../data/books.csv", encoding="utf-8-sig")
books.head()
```

导出给 Excel 打开的 CSV 常用 `encoding="utf-8-sig"`，并 `index=False`；导出新文件名，别覆盖原始数据。`errors="ignore"` 会丢字符，不是安全修复。仅终端显示异常时，可先以 Notebook 中值与 UTF-8 JSON 报告查看信息；确认是终端编码再按支持流程处理，不改整台机器地区设置作为第一步。

## 8. matplotlib 方框与 Glyph missing

后续图表先：

```python
from dacheck import setup_chinese_font
font_name = setup_chinese_font(verbose=True)
```

Windows 常见候选是 Microsoft YaHei/SimHei；其他系统候选不同。返回 `None` 表示没有找到课程候选，不是“没有中文数据”。先查看实际注册字体：

```python
from matplotlib import font_manager
available_names = sorted({font.name for font in font_manager.fontManager.ttflist})
[name for name in available_names if "YaHei" in name or "SimHei" in name or "CJK" in name]
```

若存在候选但图未更新，重跑字体设置和绘图格，最后 `plt.show()`；旧输出不会自动更新。若系统中确无合适字体，使用自己获授权的字体文件，按 Windows 提供的“为当前用户安装”或单位软件管理流程安装合适中文字体，再关闭/重启当前 Jupyter 内核或服务器，重新检测。不下载不明“字体修复包”，不删除整段 matplotlib 缓存/用户目录。

新装字体实际内部名称可能与文件名不同；课程工具仅自动选候选列表。若使用其他合法字体，应根据 `font_manager` 显示的**真实内部名称**针对当前图设置，而不是从文件名猜名称。例如已经确认存在 `Noto Sans CJK SC`，可对当前绘图设置：

```python
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC"]
plt.rcParams["axes.unicode_minus"] = False
```

这一名称只是**已确认存在时**的例子，没有它不能复制后声称修好。Glyph 警告说某个字形缺失，可能是生僻字、符号或选错字体；体检样例通过不保证所有字符。检查真实图标题与文字，换确有相应字形的合法字体；不全局屏蔽 warnings。

## 9. 网络、证书、代理与端口

| 安装/启动错误 | 检查路线 | 停止条件 |
| --- | --- | --- |
| `ProxyError` / 代理认证失败 | 是否在单位网络，代理配置来源是否合规 | 需要账号/单位配置时问支持人员，不公开密码 |
| `SSLError` / certificate verify failed | 系统时间、官方来源、单位 CA/证书审查要求 | 不能确认受信任证书时停，不关闭 SSL 校验 |
| `ReadTimeout` / 连接超时 | 网络是否可用、官方服务是否能正常访问 | 保留失败日志，再按正规网络支持排查 |
| `No matching distribution found` | Python 版本/位数、包索引、完整固定清单 | 不立即改清单或追最新，先核对 da-course 的 3.12/64 位 |
| 服务条款提示 | 阅读当前条款，按真实用途与单位规定判断 | 不确定或不同意时停，课程不代接受 |
| 本机 Jupyter 端口占用 | 看日志是否自动选择其他端口 | 不杀未知进程，按 A-1 使用日志实际地址 |

**不要**关闭 SSL 验证、加随意 trusted-host、改成 HTTP、关闭杀毒或长期管理员运行。企业代理若需 CA 文件，应由单位提供并按其安全流程配置，不从聊天附件装根证书。浏览器连接 Jupyter 失败先看服务器是否在运行、日志地址是否当前，不开放远程访问或移除 token。

## 10. 报错怎样提问

用[A-1 提问模板](lesson:A-1)，附目标、窗口、命令、相关格子、末行类型、环境与目录证据、已做动作与结果。JSON 报告包含本机路径，分享前遮盖用户名/项目机密；不发送 token、代理密码和真实业务数据。你不需要一次解释全部错误，只需要让别人能复现最小失败。

:::job 复核能力比“没报错”更重要
表格成功读出来后还要看中文是否正常、行数/列名是否合理；图生成后还要看字体与标签；错误消失后要回到原问题验证结果。工作里的分析质量不是以警告隐藏得多干净来衡量。
:::

## 理解检查

:::try 练习 1：看末行
报 `NameError: name 'total' is not defined`，列出两个应先检查的点。
:::
:::fold 参考答案
变量是否拼写一致；定义 total 的格是否在当前内核运行过（重启后是否从头运行）。通常不需要安装新包。
:::

:::try 练习 2：读取与显示区分
CSV 表格里的中文正常，图上标题方框。应改 CSV 编码还是检查字体？
:::
:::fold 参考答案
检查字体。字符已正确读入，问题在字形显示；先 setup_chinese_font 并观察返回值/警告，不重新保存原 CSV。
:::

:::quiz 练习 3：证书失败怎样处理？
- [ ] 加 trusted-host 让验证绕过去
- [x] 保留报错，检查系统时间与单位代理/证书要求，不关闭 SSL 校验
- [ ] 安装任意聊天附件中的根证书
---
成功下载不能建立在绕开验证上。证书与代理需要可信配置，单位设备先咨询支持人员。
:::

:::try 练习 4：resolve 的局限
`Path("../data/books.csv").resolve()` 打印出一个地址，就能确认文件存在吗？
:::
:::fold 参考答案
不能。resolve 只计算位置；还要 is_file() 和实际读取。若不存在，检查完整解压、cwd、真实文件名与扩展名，不创建空文件伪造通过。
:::

:::checklist 修复验收
- [ ] 我能指出错误类型、相关格子和发生窗口，不把输出当命令。
- [ ] 我只做与证据对应的局部修改，没丢弃原数据/隐去警告。
- [ ] 修正后重新执行，从头运行需要的初始化，并复核数值、文字与图表。
- [ ] 遇未知依赖/许可/权限/证书问题我知道停止并准备脱敏求助。
:::

环境相关修正后重跑[0-5 体检](lesson:0-5)。具体计算问题再回相应课，不把这张表当所有错误的自动处方。
