---
summary: 用标准库可启动的离线体检脚本与 Notebook 核对解释器、课程包、数据读写和中文字体。
prereq: 已完成安装课；da-course 已激活，依赖清单已安装；保持整套教材完整目录。
---

:::goal 本课目标
- 用证据确认 Prompt 和 Notebook 是否正在使用同一个课程 Python。
- 运行 `tools/check_env.py`，区分通过、警告和关键失败，并采取明确下一步。
- 保存一份可脱敏的 JSON 报告，不让体检覆盖原数据。
- 打开环境练习本，完成三个不依赖真实 Windows 路径的简单练习。
:::

## 1. 什么叫“体检”，为什么要看多个证据

网页能打开、安装器已关闭、Prompt 有 `(da-course)`，各自只能证明一部分。课程运行需要**解释器对、包可用、文件可达、读写正常、内核一致**。同一台电脑可以有多个 Python；在正确终端装了包，但 Notebook 用了另一个内核，仍会显示找不到包。

:::analogy 收到办公室钥匙不等于坐在正确工位
Anaconda 是楼入口；da-course 是你的课程工位；包是工位里的工具；Notebook 内核是实际干活的人。入口正常不证明工具到齐，标牌写对也要看干活的人在哪里。
:::

:::flow 本课检查顺序
1. Prompt：激活环境并定位课程根目录。
2. 查看解释器与 pip 归属。
3. 运行离线检查脚本，先解决关键失败。
4. JupyterLab：检查内核与 Notebook 工作目录。
5. 做三个独立练习，保存后进入下一课。
:::

## 2. 在哪里运行：先找 Prompt，不要粘到网页或代码格

若上一课的 Jupyter 服务器仍在运行，它的 Prompt 正显示日志，不能当普通命令输入窗口。另开一个 **Anaconda Prompt**，正常权限打开，每次新窗口先激活。下面都在 Prompt 输入；第一条路径替换为自己真实根目录：

```terminal
conda activate da-course
cd /d "D:\da-course\data-analysis-tutorial"
dir
python --version
python -c "import sys; print(sys.executable)"
python -m pip --version
```

预期：版本 `3.12.x`；解释器路径指向安装位置里的 `envs\da-course\python.exe`；pip 的输出也位于该环境，而不是系统 Python、WindowsApps 或用户级第三方目录。`dir` 里有 `requirements.txt`、`tools`、`data`、`dacheck`、`notebooks`。

`python -m pip` 之所以可靠，是它明确要求**当前解释器**执行 pip，而不是依赖裸 `pip` 的搜索顺序。Notebook 里更进一步用 `sys.executable` 绑定解释器；稍后在 Python 格可以用 `subprocess.run([sys.executable, "-m", "pip", "--version"])` 查看，不在代码格里直接粘 Prompt 命令。

:::window Prompt 检查位置（界面示意，不是实机截图）
| 部分 | 正常观察 | 异常时做什么 |
| --- | --- | --- |
| 左侧环境 | `(da-course)` | 先 activate，不继续安装 |
| 当前目录 | 你的真实课程根目录 | `cd /d "实际路径"`，再 dir |
| Python 版本 | `3.12.x` | 查解释器归属，不随意升级旧项目 |
| sys.executable | da-course 下的 python.exe | 回 A-1 环境分流 |
| pip 路径 | da-course 下的包目录 | 先确认 Python，再解决 pip 归属 |
:::

## 3. 运行离线体检脚本

仍在课程根目录的 Prompt 中运行：

```terminal
python tools/check_env.py
```

该脚本入口只依赖 Python 标准库，可以在课程包缺失时启动并报告缺包；它按需导入清单里的包，而不是先因为没有 pandas 就崩掉。**它不会联网，不修改系统 PATH，不安装/卸载软件，不自动删除你的文件或环境。** 它会在自己新建的临时目录写入小样本后读回，并只清理这些临时测试文件；不读写覆盖课程原始数据。字体缓存也放在临时位置。若运行时系统提示目录权限问题，先记录并换合规可写位置，不以管理员长期绕过。

输出是一串带中文标签的检查项，例如：

```output
【通过】Python 位数: 64 位
【通过】Python 版本: 3.12.13
【通过】当前解释器属于 da-course: 解释器环境目录：D:\Anaconda3\envs\da-course
【通过】pandas CSV 读写: 临时目录中写入并读回 2 行中文数据；结果一致，临时文件已清理。
...
共 ... 项；关键失败 0 项。
```

这是**输出示例**，不是 Windows 实机验证记录，也不是你一定得到的完整清单。路径、补丁版本和项目数可以不同；清单中的包版本以你这套教材 `requirements.txt` 为准，不由课文复制一份容易过期的版本号。

### 输出各项在检查什么

| 检查 | 通过条件/含义 | 失败或警告的下一步 |
| --- | --- | --- |
| 平台与位数 | 目标是 Windows x86_64、64 位 Python | macOS/Linux 只提示非目标平台，不把跨平台通过写成 Windows 已验证 |
| Python 版本/路径 | 3.12，属于 da-course | Prompt 重新激活；Notebook 选择课程内核 |
| cwd 与 root | cwd 是当前目录；root 从脚本自身位置推导 | root 应是完整教材根目录；cwd 可以不同，但启动 Jupyter 要在根目录 |
| 中文/空格路径 | 无则通过，有则警告 | 只是兼容性提醒；先给路径加引号并核对读写，不改 Windows 用户目录 |
| CONDA_PREFIX/sys.prefix | 终端激活变量与实际解释器环境 | 不同则先核对 sys.executable；Notebook 可继承旧变量，实际路径优先 |
| python -m pip | 当前解释器的 pip 可运行，打印其路径 | 缺 pip 时在 Prompt 用 conda 为 da-course 补 pip |
| 包版本与导入 | 每个包匹配 requirements.txt，且能实际导入 | 在正确环境重跑清单安装；有元数据但导入失败也不能算正常 |
| 数据与 dacheck | 能读 data/books.csv，能导入本教程检查工具 | 完整解压，不单独搬走 Notebook，不安装网上同名包 |
| CSV/Excel/SQLite | 临时样本写入读回一致 | 先解决 pandas/openpyxl 导入与权限；SQLite 由 Python 标准库提供 |
| matplotlib 字体 | 找到候选中文字体，样例无缺字警告 | 到 A-2 检查字体；此项只验证样例，不保证所有生僻字 |

### 通过、警告、失败不是同一种结果

:::compare 怎么决定继续
:::bad 不可靠的判断
“最后没看到红色就可以。”终端颜色因系统而异；某些错误也不是红色。或者：“只有字体警告，我以后把警告隐藏掉。”隐藏不会修好中文。
:::
:::good 用标签和关键失败计数
- **通过**：这一项有实际检查证据。
- **警告**：需要理解/跟进，不一定阻止基础练习。例如路径含中文或非目标平台说明。
- **失败**：有问题。关键失败不为 0 时先停止进入后续计算课。
- **字体警告**：可以先做文字练习，但图表课前必须解决，不假称所有图表正常。
:::
:::

关键失败会使脚本以退出码 `1` 结束；关键项全部通过是退出码 `0`。这不是要你记新知识，在 Prompt 若需要核对，可以在脚本运行完**立即**输入 `echo %ERRORLEVEL%`。中途执行别的命令可能改变这个值；主要还是阅读检查条目。

## 4. 保存报告：只有明确要求才写永久文件

需要给自己留记录时，在 Prompt 运行：

```terminal
python tools/check_env.py --json "env-report.json"
```

示例把报告保存到当前根目录，文件名可替换为一个**尚不存在**的新名字。脚本不覆盖已有报告；已经有同名文件时换 `env-report-2.json`。使用绝对路径时双引号保留、路径换成自己的、父文件夹必须真实存在且可写。脚本不替你创建一串新目录。

JSON 是结构化文本，记录每项的 `id`、`title`、`status`、`detail`、`action`、`critical` 与关键失败数。你可以用文本编辑器查看，不需要把它改成 `.xlsx`。保存成功不是环境正常的证明，报告可以忠实记录失败。

:::warn 分享前脱敏
报告包括 Python 路径、用户目录、工作位置等本机信息。发给别人前遮盖用户名、邮箱和敏感项目名称，不发浏览器 token、代理密码或整个系统信息转储。用于定位的目录层级与错误类型尽量保留。
:::

## 5. 打开练习本，再验证 Notebook 自己的内核

若没有服务器运行，回到已激活且定位根目录的 Prompt：

```terminal
python -m jupyter lab
```

如果已有正常服务器，不再重复启动一份。从 JupyterLab 左侧文件栏进入 `notebooks`，双击 `0-5_env_check.ipynb`。需要完整练习本时可从[原位置打开环境练习本](../../notebooks/0-5_env_check.ipynb)对应文件；浏览器直接下载的副本不应单独搬到桌面运行。

在 JupyterLab 的内核选择中选择 **Python (da-course)**。上方显示的执行者要和 Prompt 的环境一致。先读第一说明格，再选第一代码格，按 `Shift+Enter` 执行；下一课会更详细介绍界面。

练习本会查看 `sys.executable`、Python 版本、`Path.cwd()`、根目录和数据。Notebook 正常工作目录通常为课程中的 `notebooks`，所以 `../data/books.csv` 能读到同级 data。Prompt 刚才的 cwd 是根目录，与 Notebook cwd 不同是正常的相对关系，不要要求两者文字完全相同。

在 Notebook 中也可以运行：

```python
from tools.check_env import run_checks
checks = run_checks()
[(item["title"], item["status"]) for item in checks]
```

这是 **Python 格代码**，不是 Prompt 命令。第一初始化格已经把教程上一层加入导入搜索路径。`run_checks()` 返回结构化检查项，不打印整页报告也不保存永久报告；最后一行表达式让 Notebook 展示标题与状态。按需查看某项 `detail` 与 `action`。本练习本不要求 Windows 特定路径通过判断题，但你自己的实际环境仍应按本课检查。

### 为什么 terminal 正常，Notebook 还报缺包？

Notebook 内核可能指向 base、系统 Python 或旧环境。先在代码格运行：

```python
import sys
print(sys.executable)
```

比较**真实路径**，不是只看 Python 名字。若内核不对，选择 Kernel → Change Kernel（或点击内核名称），改为 Python (da-course)，再从上至下运行。若没有此选项，回 Prompt 从正确环境注册内核；不要在错误 Notebook 里反复安装包。切换内核会丢掉当前内存变量，但已保存代码还在。

:::widget env-doctor 不确定是哪一类问题？
:::

这个网页交互只是故障分流，不读取电脑、不执行 Python，也不替代脚本。选择最接近自己症状的选项后，按[A-1](lesson:A-1)或[A-2](lesson:A-2)中的步骤操作。

## 6. 理解检查与三个 Notebook 练习

:::try 练习 1：你是否知道执行者
在环境练习本完成 `0-5.1`：给 `python_path` 赋值为 `sys.executable`，检查的是你当前内核真实路径，而不是让你抄 D 盘示例。提示：使用变量的名字，不加引号。
:::
:::fold 参考答案
```python
python_path = sys.executable
check("0-5.1", python_path)
```
检查器与当前 Python 动态比较，所以 macOS/Linux 上也能验证理解，不等于 Windows 平台验证。
:::

:::try 练习 2：认得 pip 的绑定方法
完成 `0-5.2`：给 `pip_command` 赋值为字符串 `"python -m pip"`。这是一道理解题，不会执行安装。
:::
:::fold 参考答案
```python
pip_command = "python -m pip"
check("0-5.2", pip_command)
```
字符串带英文引号；不把它当一条 Notebook 内安装命令。
:::

:::try 练习 3：数据是否真的可读
完成 `0-5.3`：用 `pd.read_csv("../data/books.csv").shape[0]` 得到行数。提示：`shape[0]` 是行数，下一阶段会细讲；只需要按示例填写，不猜数字。
:::
:::fold 参考答案
```python
book_rows = pd.read_csv("../data/books.csv").shape[0]
check("0-5.3", book_rows)
```
每题独立；第三题不依赖前两题答案。检查器动态从随包数据计算期望，不要求你硬背行数。
:::

:::quiz 补充判断：脚本提示路径含中文，所有读写通过，应当怎么办？
- [ ] 马上重命名 Windows 用户配置目录
- [x] 理解为兼容性警告，保留路径并留意后续实际错误
- [ ] 删除警告代码，保证全绿
---
检查区分警告与关键失败。中文本身不等于故障，删除提示也不修复问题。
:::

## 常见异常与下一步

| 症状 | 先做的一件事 | 不要做 |
| --- | --- | --- |
| can't open file tools/check_env.py | `dir` 确认当前是真实根目录 | 在别处新建同名空脚本 |
| No module named pandas/openpyxl | 查 sys.executable，再在正确 Prompt 安装清单 | 在 base 或任意内核盲装 |
| 版本不匹配 | 对照本套 requirements.txt，保留安装日志 | 为“追最新”改清单 |
| 文件或 dacheck 不可达 | 确认 ZIP 完整解压、未移动练习本 | 网上找同名检查包 |
| 关键失败 0，字体 warn | 可先做文字练习，图表前按 A-2 处理 | 屏蔽所有 Glyph 警告 |
| 平台提示 macOS/Linux | 仅说明非目标系统，命令用各系统适配路线 | 把输出说成 Windows 实机通过 |

:::job 以后怎样描述环境
作品说明可写“按随包 requirements.txt，在独立 da-course 环境运行，附离线体检结果”。这是复现条件，不是业务成绩；不要把“装了 Anaconda”当分析项目贡献。
:::

:::checklist 本课验收
- [ ] Prompt 的 Python 是 da-course 中的 64 位 Python 3.12，pip 也属于它。
- [ ] 体检所有关键失败为 0；警告原因我能解释，字体问题有后续计划。
- [ ] Notebook 的 sys.executable 与 Prompt 指向同一课程解释器。
- [ ] 我能说明 cwd 与 root 的区别，Notebook 仍保留在原 notebooks 文件夹。
- [ ] 我完成三个独立练习并保存，没有把参考路径抄成自己机器的路径。
- [ ] 如果保存/分享报告，我使用新文件名并完成脱敏。
:::

**关键失败未解决时停止进入后续代码课**；先保留日志与复现步骤求助。通过后进入[JupyterLab 上手](lesson:0-6)。
