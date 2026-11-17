---
summary: 从症状分流，按窗口、路径、解释器、依赖、内核的顺序定位，不用重装作为第一反应。
prereq: 保留完整课程目录；能找到实际错误所在窗口。可在安装未成功时使用。
---

:::goal 用完这张向导，你能做什么
- 根据出错位置选择第一条检查，不把所有异常都叫“Python 坏了”。
- 收集 Prompt、解释器、pip、内核和目录证据，知道何时停止继续安装。
- 区分自己可逆的局部修正与需要单位支持的权限/网络问题。
- 准备一份脱敏而可复现的提问。
:::

## 先记录四件事，再选症状

1. **在哪个窗口**：普通 CMD、Anaconda Prompt、浏览器、Notebook Python 格？
2. **刚执行的命令/代码**：不要只说“运行一下”。
3. **真实路径与环境**：Prompt 当前目录、sys.executable、Notebook 内核名。
4. **完整错误**：终端从出错行附近到末尾；Notebook 至少保留相关格子与最后一行类型。

:::widget env-doctor 环境故障分流
:::

网页只提供症状分流，不读取你电脑，也不自动执行、安装或修复。不要把交互的建议当成检测通过证明。

:::flow 固定诊断顺序
- 先窗口：课程命令是否在 Anaconda Prompt？
- 再路径：ZIP 是否完整提取？根目录是否真的有 requirements.txt？
- 再 Python：sys.executable 是否属于 da-course？
- 再包：python -m pip 是否绑定当前解释器？
- 最后内核与状态：Notebook 是否同一解释器，是否从第一格运行？
:::

## 1. 找不到 conda，或点 Python 弹出应用商店

### 普通 CMD 找不到 conda

这是可能正常的：本课程安装时不永久添加 PATH。先关闭普通 CMD，从 Windows 开始菜单搜索 **Anaconda Prompt** 并打开普通权限窗口，然后：

```terminal
conda --version
conda info --envs
```

有版本和环境列表就回[安装课第 5 节](lesson:0-4)，不编辑系统 PATH。Prompt 里仍找不到时，记录窗口标题与实际安装位置。

### 开始菜单也没有 Prompt

先在设置的“已安装的应用”与你记录的安装目录确认是否真的完成安装。快捷方式可能没创建，不能仅凭没快捷方式断言软件缺失。若你确认这是完整 Anaconda 安装、实际目录中**确有** `Scripts\activate.bat`，可在普通命令提示符（CMD）运行：

```cmd
call "D:\Anaconda3\Scripts\activate.bat"
conda --version
```

第一条路径**必须换成真实安装路径**，且先在资源管理器确认文件存在；不是让你在 D 盘自建空脚本。它只激活当前 CMD 会话，不永久改 PATH。若文件缺失、来源不明或激活仍失败，停止复制命令，保留安装错误并按官方安装/单位支持流程处理，不卸载所有旧环境。

### `python` 打开商店或 where python 里有 WindowsApps

WindowsApps 中可能是应用执行别名，不是课程解释器。关闭商店，回 Anaconda Prompt 激活，再看实际执行者：

```terminal
conda activate da-course
where python
python -c "import sys; print(sys.executable)"
```

`where` 可以多行，**真实执行路径**应在 da-course。设置 → 应用 → 高级应用设置 → 应用执行别名可用于观察；本课不要求先禁用所有别名，更不删除 WindowsApps 文件夹。若 Prompt 激活正确无需修改系统别名。

## 2. 环境没激活、已有同名环境、误把课程包装进 base

在 Anaconda Prompt 运行：

```terminal
conda info --envs
```

`*` 是当前环境。只有 base 时，需要按安装课创建 da-course；已经有 da-course 时只激活，不重复 create。创建时显示“prefix already exists”或同名冲突，先列表与核对，不能删除未知环境。

```terminal
conda activate da-course
python --version
python -c "import sys; print(sys.executable); print(sys.prefix)"
```

应为 Python 3.12，路径指向该环境。Python 补丁号不必和课文示例完全相同。若已有 da-course 是其他项目在用、版本不是 3.12，先备份/确认用途并向维护者求助，不以新课覆盖它。

**误装进 base 的最小纠正**：先停止继续改 base，不批量卸载或清理。保留其他项目，确认/创建课程环境，再激活 da-course，在真实根目录用 `python -m pip install -r requirements.txt` 安装。以后所有练习都用它。base 若已受依赖冲突影响，再依据真实日志制定修复方案，不把“删掉 base”当教学步骤。

## 3. pip 模块缺失，或包明明安装却找不到

先核对解释器，不先装包：

```terminal
python -c "import sys; print(sys.executable)"
python -m pip --version
```

如果是 da-course 且出现 `No module named pip`，在 Anaconda Prompt 运行：

```terminal
conda install -n da-course pip
conda activate da-course
python -m pip --version
```

这里 conda 常规确认可根据实际方案操作；出现服务条款须阅读按用途确认。没有 da-course 时先创建，不把 `-n` 换成 base 凑合。`conda` 本身也不能运行则回第 1 节，不下载不明 pip 引导脚本。

确认 pip 路径属于课程环境后，在实际根目录安装清单。不要用裸 `pip`，不加 pip 的 `--user`，不把“Requirement already satisfied”当内核必定正确。若包元数据存在但 `import` 报 DLL、二进制或依赖错误，保存具体错误去[A-2](lesson:A-2)，不强行升级/降级所有包。

### Notebook 缺包但 Prompt 正常

Notebook Python 格运行：

```python
import sys
print(sys.executable)
```

与 Prompt 实际路径比。若不一致，选择内核 **Python (da-course)**，重启并从第一格运行。没有该内核时，从正确 Prompt 注册：

```terminal
python -m ipykernel install --user --name da-course --display-name "Python (da-course)"
```

这个 `--user` 注册用户内核描述，不是 pip 用户级安装。已注册同名时先确认当前路径正确，不覆盖其他用途内核。改内核后不保证旧内存变量仍在，必须从头运行。

## 4. 路径找不到、requirements 缺失、Jupyter 打开错误位置

按 `Win+E` 进入完整解压的普通目录，点地址栏复制。根目录应同时有 requirements.txt、data、notebooks、dacheck、tools、site。ZIP 内可以预览文件，但不能当正常工作目录；只复制 Notebook 也不足。

在 Prompt：

```terminal
cd /d "D:\da-course\data-analysis-tutorial"
dir
```

路径换成自己的，双引号保留。缺 D 盘不是故障；文件找不到先看扩展名是否多了 `.txt`、文件夹是否多套一层。不要修改原数据扩展名来“解决”读取错误。

Jupyter 左侧显示桌面/Downloads/其他项目，说明服务器从那里启动了。保存当前文件，正常停止服务器，再从正确根目录运行 `python -m jupyter lab`。Notebook 内默认 cwd 在 notebooks/，此时 `../data/books.csv` 正常；不要把 Notebook cwd 强求为根目录。

## 5. 浏览器没打开、端口占用、连接失败

看 Jupyter **服务器窗口日志**。浏览器未自动启动时，复制日志给出的本机地址与当前 token 自己使用；不从教材猜端口/token，不公开分享。只关浏览器可能服务器还在；正常恢复已有服务器比再开一堆更好。

若日志表示常用端口被占用，Jupyter 可能自动选择下一个可用端口，以**日志实际地址**为准。确认确需另起当前课程服务器时，可以指定另一个端口：

```terminal
python -m jupyter lab --port=8890
```

8890 只是端口示例，也可能被占用。不要杀未知进程、不开放防火墙、不绑定到 `0.0.0.0`、不关闭 token 校验；本课只需本机访问。连接失败时先看服务器是否已停止、当前地址是否旧的、单位浏览器/代理是否拦截本机访问；单位问题先问支持人员。

## 6. 输出没出现、一直星号、字体或编码不对

- 赋值、注释和 import 没输出常是正常的；运行序号变化后用 `print(...)` 或最后一个表达式查看。
- `[ ]` 仍空：可能只编辑未执行；选中 Code 格后 Shift+Enter。
- 文字变成段落而非执行：当前是 Markdown 格，先切为 Code。
- `[*]` 一直不结束：看是否在等 `input()`，再 Interrupt 当前内核；不要终止所有 Python。
- 重启后 NameError：内存清空，按第一格起的顺序运行。
- 图中文字是方框或 Glyph 警告：回[A-2 字体](lesson:A-2)，不屏蔽警告。
- CSV 中文乱码：保留原文件，用已知编码正确读取/导出，见[A-2 编码](lesson:A-2)，不要随意忽略错误。

## 7. 网络/权限：不要为了“成功”关闭保护

代理、证书、TLS、连接超时等看[A-2](lesson:A-2)具体分类。先确认系统时间、官方来源、正常网络与单位 CA/代理规定。**不关闭 SSL 校验，不关杀毒，不长期管理员运行，不发送密码**。无权限写课程目录就用合规可写位置；条款与单位策略不确定时停止，课程不替你接受。

## 8. 怎样提问才容易得到有效帮助

:::window 提问模板（文字示意）
**目标**：我想在 da-course 中打开 0-5 环境练习本。

**系统**：Windows 11，64 位 x64；不是 ARM。（填真实情况）

**窗口/位置**：Anaconda Prompt，当前目录 `[教程根目录，用户名已遮盖]`。

**操作**：复制实际运行的命令/相关代码格。

**现象**：期望看到什么、实际看到什么；附错误上下文与末行类型。

**证据**：conda info --envs 星号、sys.executable、python -m pip --version、Notebook 内核/cwd；若有报告附脱敏检查项。

**已尝试**：写具体动作和结果，不写“网上方法都试过”。
:::

不要发“无法运行”四个字配整屏看不清的照片；也不用上传全部电脑文件。错误行和路径层级重要，用户名、邮箱、真实业务资料、token、代理密码不需要。

:::job 工作里也适用这个顺序
把问题缩小到“哪个窗口、哪个解释器、哪条命令、哪份数据”，体现可复现与沟通能力，比盲重装更接近分析工作方式。
:::

## 三个理解检查

:::try 练习 1：普通 CMD 找不到 conda
写出第一步，而不是完整重装计划。
:::
:::fold 参考答案
从开始菜单打开 Anaconda Prompt，运行 conda --version。因为安装时未永久添加 PATH，普通 CMD 找不到可能正常。
:::

:::try 练习 2：base 误装之后
现在知道安装课包时 Prompt 是 base。是否应该批量卸载所有包？
:::
:::fold 参考答案
不应该。先停止改 base，保留已有项目，创建/激活正确课程环境再按清单安装。基础环境若真有冲突，留日志另行制定修复方案。
:::

:::quiz 练习 3：浏览器没有打开怎么办？
- [ ] 从别人的截图复制 token
- [x] 先看自己 Jupyter 日志，使用它实际给出的本机地址
- [ ] 关闭所有 Python 进程并开放防火墙
---
地址与 token 属于当前服务器。不要猜测、公开分享或破坏其他项目进程。
:::

:::checklist 排错验收与停止条件
- [ ] 我能说出错误发生的窗口与具体命令/格子。
- [ ] 我确认目录完整，解释器属于 da-course，pip 与内核指向正确位置。
- [ ] 我没有删除未知环境、改用户目录、关闭 SSL/杀毒或长期管理员运行。
- [ ] 仍有关键失败、权限/许可未确认或未知二进制错误时，我已停止并准备脱敏提问。
:::

修正后重跑[环境体检](lesson:0-5)，不要只凭一次命令不报错宣布全部正常。
