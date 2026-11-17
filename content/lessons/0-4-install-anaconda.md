---
summary: 按官方安装选项装好 Anaconda，在独立 da-course 环境安装课程清单并注册 Jupyter 内核。
prereq: 已完成安装前体检；整套教程已完整解压，知道实际根目录；联网安装阶段需可用网络。
---

:::goal 本课可检验目标
- 从官方说明进入官方下载，选择适合目标电脑的 Windows x86_64 安装器。
- 解释为什么选择 Just Me、为什么不永久添加 PATH。
- 创建并激活 `da-course`，在它里面安装课程依赖，不把课程包放进 `base`。
- 注册 `Python (da-course)` 内核，从正确目录启动 JupyterLab。
:::

## 1. 先分清四层工具

:::cards 不把软件名字当作同一个东西
:::card Anaconda：工具的入口与管理器
安装包提供 conda 与基础 Python 等。这里把它看作管理学习环境的入口，而不是每课都使用 Navigator。
:::
:::card conda 环境：独立工具箱
`base` 是基础环境。课程另建 `da-course`，不把课程依赖安装进 base。环境名和文件夹名不是随便混用的同义词。
:::
:::card Python 与 pip：执行与装包
环境里指定 Python 3.12。`python -m pip` 使用当前这个 Python 的 pip，按 `requirements.txt` 固定版本安装课程包。
:::
:::card JupyterLab 与内核：界面与执行者
浏览器里的 JupyterLab 是编辑界面；`Python (da-course)` 内核才负责执行代码。界面打开并不能证明内核正确。
:::
:::

本课沿用一条路线：**Anaconda → Anaconda Prompt → da-course → requirements.txt → Python (da-course) → JupyterLab**。暂时不引入 VS Code、系统 Python、Miniconda 或多个镜像路线，以免在不同窗口来回混用。已有可用 Anaconda 时不重复装，直接从第 4 节检查环境开始。

## 2. 官方下载与安装前确认

先打开[Anaconda 官方 Windows 安装说明](https://www.anaconda.com/docs/getting-started/anaconda/install/windows-cli-install)，从页面的官方下载入口获取当前 Windows 安装器。该页标题为“Windows shell installer for Anaconda Distribution”，但在 **2026-11-12 本教程核对时**确有图形安装步骤。本课不把某个固定安装器说成“最新”；版本与界面文案可变化。

选择 **Windows、64 位 x86_64**，前提是[系统体检](lesson:0-3)确认基于 x64 的处理器。ARM 电脑不被这条教程自动视为已支持或已实测；不确定时停止并核对官方系统要求。下载完成后在资源管理器中确认文件来自官方下载、扩展名为 `.exe`；不要运行不明重新打包的安装器。单位电脑遵循单位软件安装流程。

:::note 许可与条款由你按真实用途确认
安装器中的 Terms of Service，以及 conda 使用服务时的条款提示，需要阅读后依据个人学习、商业或单位使用情况决定是否同意。课程不是法律意见，不代你接受，也不把任何商业使用一概说成免费。不同意或无法判断时停止，向单位支持/相关负责人确认后再继续。
:::

## 3. 图形安装：逐步界面示意

**下面全部是 HTML 文字界面示意，不是作者采集的 Windows 实机截图，也不是真安装器。** 标记按钮仅帮助你对照。实际安装器出现不同标题或额外页时，读清内容，不凭示意盲点。

:::steps 安装顺序
:::step 双击官方安装器
在下载文件夹双击安装器，正常权限运行。不是把安装器放在压缩包内执行，不使用“以管理员身份运行”作为默认路线。若单位策略或安全软件阻止，记录提示并确认来源/支持流程；不关闭杀毒。
:::
:::step 阅读欢迎与条款页
阅读欢迎说明和许可，只有在理解并愿意接受时选择下一步。取消安装并不算学习失败。
:::
:::step 选择当前用户安装
选择官方推荐的 Just Me；All Users 通常需要管理员权限，不是本课程默认路线。
:::
:::step 选择目录和高级选项
记录真实安装目录，确认无已有安装冲突且自己有写权限；按下表选择，不编辑系统 PATH。
:::
:::step 安装完成后打开 Prompt 验证
安装进度结束后点 Finish，再从 Windows 搜索打开 Anaconda Prompt，不靠“安装器关闭了”判断成功。
:::
:::

:::window 安装范围页（界面示意）
- [[+Just Me (Recommended)]]：为当前用户安装，本教程选择。
- All Users：不是本教程默认；可能需要设备管理员参与。
- [[Next]]：确认范围后继续。
:::

:::window 安装目录页（界面示意）
Destination Folder：`D:\Anaconda3` **仅示例，换成你的实际可写安装目录**。

官方建议目录不含空格/特殊字符，以降低工具兼容问题。中文用户名无需改名；如果默认安装路径含中文/空格，可选择其他合适的可写目录。没有 D 盘就不填写 D 盘，不把权限错误改为常驻管理员。

[[Next]]：确认路径后继续。教程本身仍放在独立的课程目录，不放在这里。
:::

:::window Advanced Installation Options（界面示意）
| 选项 | 本教程选择 | 原因 |
| --- | --- | --- |
| Create shortcuts | [[+保持勾选]] | 官方默认勾选；便于从开始菜单打开 Anaconda Prompt |
| Add Anaconda3 to my PATH environment variable | [[!不勾选]] | 官方不建议默认永久加入 PATH；Prompt 激活会为当前窗口处理环境 |
| Register Anaconda3 as my default Python ... | [[!本教程可不勾选]] | 避免改变其他软件默认解释器；不是不能运行 Anaconda，始终在 Prompt 工作 |
| Clear the package cache upon completion（若有） | 本课不要求勾选 | 这是缓存管理选项，不是成功安装必须项；不把清理当作修复 |

[[*Install]]：确认你的真实选项与条款后安装。
:::

“Register ... Python 3.12”等文案会带安装器自带版本；**那不是课程环境一定使用的版本**。无论 base 附带什么版本，后面另建 Python 3.12 的 `da-course`。本教程“不勾选 Register”是课程的隔离选择，不是假称官方要求每个人不勾选。

安装时可以查看 Show details，等待完成，不在进度过程中强行关闭。报权限、路径冲突或安全软件提示时，先停下保存错误；不删除看不懂的文件，不关闭杀毒，不反复覆盖安装。安装结束后若 Navigator 自动打开，可以关闭 Navigator，本课统一用 Prompt。

## 4. 打开 Anaconda Prompt，先确认入口

点 Windows 开始菜单，输入 **Anaconda Prompt**，打开普通权限的应用。看到类似下行：

```output
(base) C:\Users\你的账户名>
```

这是提示符示例，不是命令。初次显示 `(base)` 正常，说明入口的基础环境已激活，但还没有进入课程环境。在这个窗口逐行输入：

```terminal
conda --version
conda info --envs
```

第一条应输出一个 conda 版本；第二条列出环境。版本可以不同，不把本页示例版本当最新版本。环境列表的 `*` 表示当前激活的环境。没有 `da-course` 时进入第 5 节；已有 `da-course` 时先激活、核对 Python 路径与版本，不重复创建。

如果显示“conda 不是内部或外部命令”，先检查你开的是否真的 Anaconda Prompt；普通 CMD 中找不到 conda 并不说明安装失败。开始菜单也找不到入口时看[A-1](lesson:A-1)，不要先加一串路径到系统 PATH。

## 5. 创建独立课程环境

确认环境列表没有名为 `da-course` 的环境后，在 Anaconda Prompt 运行：

```terminal
conda create -n da-course python=3.12 pip -y
```

逐词解释：`create` 新建环境；`-n da-course` 指定名称；`python=3.12` 指定 Python 主/次版本；`pip` 一同准备包安装工具；`-y` 对常规包方案确认使用 yes。**`-y` 不替你阅读或授权服务条款**；若出现条款、证书、代理或单位政策提示，应根据真实情况处理，不能凭教程默认接受。

输出会包含将下载/安装的包和进度。只有过程正常结束、重新出现提示符后，再运行：

```terminal
conda activate da-course
conda info --envs
python --version
python -c "import sys; print(sys.executable)"
where python
```

正常观察：Prompt 左侧变成 `(da-course)`；列表中的 `*` 在 `da-course`；Python 版本为 `3.12.x`，补丁号可随创建时间变化；解释器路径指向你安装位置下 `envs\da-course\python.exe`。`where python` 可有多行，第一项通常是已激活环境的 Python；最终以实际执行的 `sys.executable` 为证据。

```output
(da-course) C:\Users\你的账户名>
Python 3.12.x
D:\Anaconda3\envs\da-course\python.exe
```

上面的 `x`、用户名、D 盘路径都是输出示意，不能输入成命令。如果仍是 base 或版本不对，停止安装依赖，先按[A-1 环境不一致](lesson:A-1)确认当前窗口与解释器。

:::warn 新窗口需要重新激活
`conda activate` 主要改变当前终端会话，不代表以后每个窗口自动进 da-course。下次打开 Anaconda Prompt 先运行 `conda activate da-course`，不重复 create，也不重新 pip 安装所有包作为每次启动步骤。
:::

## 6. 在正确根目录安装课程清单

保留已激活的 Prompt。打开资源管理器复制真正课程根目录，回 Prompt 运行下面第一行；**只替换双引号内部路径**：

```terminal
cd /d "D:\da-course\data-analysis-tutorial"
dir
```

确认 `dir` 里同时有 `requirements.txt`、`data`、`dacheck`、`notebooks`、`tools`。找不到时停止，回[完整解压与根目录](lesson:0-2)；不要创建空文件凑数。

```terminal
python -m pip --version
python -m pip install -r requirements.txt
```

`-r` 表示从清单读取，文件由课程维护者提供，不要先改成自己猜的版本。输出可能显示下载进度、安装完成、已经满足要求（Requirement already satisfied）。后者可能正常，前提是**当前解释器属于 da-course 且版本清单一致**。看到 `ERROR`、依赖冲突、证书失败或进程退出就先记录，不仅凭末尾有文字判断成功；下一课用体检核对。

本课程先 conda 建独立环境与 Python/pip，再在环境中用 pip 安装课程固定清单，遵循官方关于隔离环境、先 conda 后 pip 的建议。不要加 pip 的 `--user`；它可能把课程包装到环境外。不要用裸 `pip`，也不要在 base 装课包。错误装进 base 时先回[A-1](lesson:A-1)隔离，不自动批量卸载基础包。

### 网络错误的停止条件

出现 `ProxyError`、`SSLError`、证书验证失败或超时：先检查系统日期/时间、正常联网、单位代理与官方证书要求。用[A-2 网络错误](lesson:A-2)整理信息。**不关闭 SSL 校验、不设置随意 trusted-host、不关杀毒、不把下载改为 HTTP**。不随机换不明镜像或一键修复脚本。单位网络要按支持人员提供的合规配置操作；无权限时先求助。

## 7. 注册课程内核并启动 JupyterLab

只有安装命令正常完成后，在同一个 `(da-course)` Prompt、教程根目录运行：

```terminal
python -m ipykernel install --user --name da-course --display-name "Python (da-course)"
python -m jupyter lab
```

这里 ipykernel 的 `--user` 是在当前用户目录注册**内核描述文件**，不是 pip 的 `--user` 装包，两者不同。若以前注册过同名内核，应先确认这次确实要把课程内核指到当前 da-course；不把其他项目内核改名覆盖。

Jupyter 通常自动打开浏览器。服务器日志中可有一个本机地址与 token，这是当前本机运行日志，不是让你贴到公开作业的内容。浏览器未打开时，复制**你自己日志中的本机地址**到浏览器地址栏；不从教材猜端口或 token。浏览器访问本机也不意味着已下载的新包被装对，下一课要验证。

服务器窗口不再显示普通提示符，这是正常的“正在运行”。不要在该窗口日志中继续安装命令。需要另一个命令时开新的 Anaconda Prompt，重新激活 da-course 并定位根目录。退出时保存 Notebook，在服务窗口按 `Ctrl+C`，按它实际提示确认关闭；不通过强制结束未知进程释放端口。

:::window JupyterLab 初次入口（界面示意）
| 区域 | 应看见什么 |
| --- | --- |
| 左侧文件栏 | 根目录中的 data、notebooks、solutions 等 |
| Launcher 或内核选择 | Python (da-course) |
| 浏览器页 | 本机服务器页面，不是 Python 安装器 |
:::

如果只显示 Downloads、桌面或另一项目的文件，启动目录不对；保存后正常关闭服务器，从真正根目录重启。没有 `Python (da-course)` 就回内核注册步骤，不随便选一个名称看起来像 Python 的内核。

## 8. 理解检查与实际验收

:::try 练习 1：哪个选项不需要改系统 PATH？
说出本课三项关键安装选择与原因：范围、PATH、默认 Python 注册。
:::
:::fold 参考答案
Just Me 为当前用户安装；不勾选永久 Add to PATH，改用 Prompt 激活；默认 Python 注册本课可不勾选以减少对其他软件的影响。Create shortcuts 保持勾选方便打开 Prompt。
:::

:::quiz 练习 2：哪个步骤应该每次新开窗口都做？
- [ ] conda create -n da-course python=3.12 pip -y
- [x] conda activate da-course
- [ ] 删除 base 再安装课程
---
环境只创建一次；新窗口重新激活。发现已有 da-course 时先检查，不能反复创建覆盖。
:::

:::try 练习 3：两个 --user 一样吗？
解释为什么内核注册命令带 `--user`，pip 安装却不带。
:::
:::fold 参考答案
ipykernel --user 注册用户可见的内核描述，Python 与包仍在 da-course。pip --user 把包装入用户级目录，可能绕过环境隔离，课程不用它。
:::

:::try 练习 4：判定下一步
Prompt 仍显示 `(base)`，但你已定位课程根目录。现在能执行 pip 安装吗？提示：目录和环境是两件事。
:::
:::fold 参考答案
不能。先 `conda activate da-course`，核对 `sys.executable` 与 Python 3.12，确认后再装清单。目录正确不意味着环境正确。
:::

:::job 可复现比“终于装上”更重要
你现在应该能向别人交代：环境名字、Python 主次版本、依赖清单在哪里、用什么内核、从哪里启动。后续项目交付可以沿用这些信息，不需要给别人你的整个 Anaconda 文件夹。
:::

:::checklist 本课验收
- [ ] 下载来自官方说明的官方下载入口，系统/架构匹配，不冒称 ARM 验证。
- [ ] 保留旧软件与用户目录，使用 Just Me 和 Prompt，不永久改系统 PATH。
- [ ] `conda info --envs` 的星号在 da-course，Python 版本为 3.12，路径指向该环境。
- [ ] 在真实教程根目录运行 `python -m pip install -r requirements.txt`，未忽略错误。
- [ ] 完成内核注册，JupyterLab 能从根目录启动并看见 notebooks。
:::

**停止条件**：任何创建/安装失败、错误环境、缺文件或来源不明时先排查，不继续复制下一条命令。下一步[环境体检](lesson:0-5)。

## 官方资料与核对说明

- [Anaconda 官方 Windows 安装说明](https://www.anaconda.com/docs/getting-started/anaconda/install/windows-cli-install)：2026-11-12 核对范围、目录、快捷方式与高级选项；本课采用界面示意，不宣称真实截图。
- [conda 官方环境管理](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)：核对创建/激活、星号、独立环境与 pip 使用建议。旧的 conda.io/docs 地址在该日返回 404，使用此官方路径。
- 官方页面未来可能更新；本课固定 Python 3.12 与随包 `requirements.txt` 是课程路线，不是“所有包的最新版本”。
