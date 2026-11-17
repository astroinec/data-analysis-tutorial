# 零基础数据分析 · 第一批教程

面向想增加量化能力的文科求职者。阅读页面不需要编程环境；真正运行练习时，按 Windows 环境课逐步安装。

## 从这里开始

1. **把整个教程压缩包完整解压**，不要在压缩软件里运行。
2. 双击 `site/index.html`，用 Edge / Chrome 等现代浏览器阅读。
3. 从第 `0-1` 课开始；电脑基础不熟时，不跳过 `0-2`。
4. 按 `0-3 → 0-4 → 0-5 → 0-6` 这条路线准备环境，不同时照多份安装教程。
5. 在 JupyterLab 中从 `notebooks/` 打开学生练习本；同名参考答案在 `solutions/`。不要把单个 Notebook 搬到别处。

**HTML 中的互动只是教学模拟，不执行 Python。** 运行代码在本地 JupyterLab 完成。代码框区分 Python、Anaconda Prompt 命令、输出和错误；输出文字不需要复制执行。

## 本批已经提供什么

| 产物 | 内容与位置 |
|---|---|
| 24 篇 HTML 讲义 + 首页 | `site/`；目标、白话解释、示意、代码、练习、答案、排错、验收 |
| 15 套学生练习本 | `notebooks/`；示例可运行，练习答案为 `...` |
| 15 套参考答案 | `solutions/`；与学生本同名，含完整解法。3-1～4-3 这 5 套已保存运行输出；其余 10 套未保存输出，在自己电脑上运行后才会出现 |
| 自动检查与提示 | `dacheck/`；练习中调用 `check(...)`、`hint(...)` |
| Windows 环境准备和排错 | 阶段 0 的 6 课及 `A-1/A-2`；路径、解释器、pip、conda、内核、编码、字体 |
| 独立离线体检脚本 | `tools/check_env.py`；不会联网、改 PATH、安装或卸载软件 |
| 模拟数据 | `data/books.csv`、`data/shop/`；完整订单、多表维度、目标、脏数据、GBK 和 Excel 样本 |
| 公开历史数据 | `data/public/`；tips、titanic、penguins、Gapminder；来源与许可核实状态见 A-3 |
| 项目与报告 | P-1 文创店年度分析；`report/analysis-report-template.md` 和 `report/project-reference-report.md` |
| 速查与术语 | A-4、A-5 |
| 可修改的原稿 | `content/lessons/`、`tools/nbsrc/` |
| 样式重设计交接 | `tools/templates/COMPONENTS.md`；组件约定和给 GPT/Kimi 的重设计提示 |

学习主线共 19 课，另有 5 篇工具箱。每课时间是初次阅读/操作估计，不含反复练习与排错。

**尚未交付的后续内容**：统计推断、SQL、漏斗与留存、A/B 测试、RFM 和求职冲刺。首页的灰色项只表示规划，不是可点击的完整课程。本批不承诺学完即获得职位，也不把模拟分析当作真实工作业绩。

## 环境路线摘要（不替代详细安装课）

目标：Windows 11、x64、Python 3.12，使用 **Anaconda + 独立 conda 环境 `da-course`**。课程包不装进 `base`；不永久修改系统 PATH；不用 pip 的 `--user`。

安装器和 Anaconda Prompt 操作请看 `site/lessons/0-4-install-anaconda.html`。安装界面是明确标记的 HTML 示意，**不是 Windows 实机截图**。只有软件来源、权限、条款和系统架构确认后才继续。

课程根目录例子是 `D:\da-course\data-analysis-tutorial`。没有 D 盘时用自己有写权限的实际目录；命令中的路径必须改成实际路径，其他名称保持课程约定。

每次重新开 Anaconda Prompt：激活 `da-course` → 定位教程根目录 → 启动 JupyterLab。**环境只创建一次，不是每次学习都重新装包。** Notebook 右上角选择 `Python (da-course)`；浏览器界面打开不代表内核正确。

体检报告含解释器/模块/本机路径，分享前隐藏用户名等信息。`--json` 只在你显式指定时保存报告，而且不覆盖已有文件。关键失败解决前，不进入后续代码课；出现中文/空格警告不等于必须改 Windows 用户名。

## 学习与进度

- 建议顺序：阶段 0 → 1 → 2 → 3 → 4 → P-1，工具箱随用随查。
- 学生本里替换 `...` 后重新运行该题。空白题显示“还没作答”是正常行为。
- 每个练习独立；遇错先确认窗口、文件、环境、变量运行顺序，再看 A-1/A-2，不先重装全部。
- 网页进度/勾选保存在当前浏览器，不上传；Notebook 练习进度存在 `dacheck/progress.json`。两种进度**不自动同步**。
- `file://` 网页的本地存储在不同浏览器可能不同；无痕/清缓存/换浏览器可能丢失进度。以保存的 Notebook 和报告为学习证据。

如已装好环境，想让网页共享同一来源的进度，可在根目录的 Prompt 使用 Python 本地静态服务，**只绑定 `127.0.0.1`**，然后从它给出的本机地址进入 `/site/`。具体可选操作在首页；这不是开始阅读前必须做的事。

## 数据与求职作品边界

- 文创店数据完全虚构；订单全集 `orders.csv` 是 **15115 笔**，一行一订单、一个商品。Excel 订单只有前 3000 行；GBK 只有 300 行；清洗表是抽样加脏数据，不能互换成年度全集。
- 已退款订单的 `pay_amount` 保留原支付。本项目只把已完成金额汇总为约定的“已完成净销售额”，不是财务确认收入，也不是净利润。
- 评分缺失是未评价，不填成 0；原始表保留，清洗规则和隔离记录需要说明。
- 公开数据是历史教学版本，不是实时数据；**公开下载不等于任何用途都可再发布**。逐项来源、改编和已确认/未确认许可见 `A-3`。对外分发或商用前继续核实未确认项，不拿软件许可证代替数据许可证。
- 作品集可说明“独立完成模拟订单分析与可复现报告”；不要虚构任职、真实收入提升或实施效果。

## 给内容维护者与视觉重设计者

学习者不必运行以下构建工具：成品网页和本子已经在包内。

- 讲义原稿：`content/lessons/*.md`；路线：`content/outline.json`；首页：`content/home.md`。
- 外观入口：`site/assets/css/style.css` 和 `tools/templates/page.html`。
- 主交互：`site/assets/js/app.js`；教学组件：`site/assets/js/widgets/`。没有第三方网页 CDN，离线可使用。
- Notebook 原稿：`tools/nbsrc/*.md`；学生/答案分离标记与组件语法见 `content/AUTHORING.md`。
- 维护依赖：`tools/requirements-build.txt`，包含课程依赖与 Markdown/Notebook 构建工具。使用课程 Python 3.12 环境安装。
- 生成并运行本子：`python tools/build_notebooks.py --kernel da-course`。
- 生成网页并严格查链接：`python tools/build_site.py --strict`。
- 单元测试：`python -m unittest discover -s tests -v`。

只改成品 HTML 会在下一次构建时被覆盖；重设计应改 CSS/模板，保持功能用的类名、ID、`data-*` 和相对路径。不要删课程、答案或检查题来简化视觉。

## 验证边界

作者验证机是 macOS ARM64、Python 3.12.13；依赖版本固定在 `requirements.txt`。这可验证数据、Python 逻辑与 Notebook，**不能替代 Windows 安装的实机验收**。

15 套练习本的学生版和答案版都已在作者机上用普通 Python 按顺序逐格执行，全部通过：答案版的检查全部判对，学生版留空的题只提示“还没作答”，不会报错。作者机上通过 Jupyter 内核自动执行时会卡住，所以有 10 套答案版没有保存输出。网页尚未整体检查，交由其他人完成。Windows 安装步骤对照官方资料，未来页面/安装器可能变化；本包不会冒称已完成 Windows 全流程实测。

参考答案的环境体检输出来自作者机，可能显示非目标平台/非 `da-course` 环境；这是实际检查结果，不是读者应照抄的路径，也不能凭答案本输出认定自己的电脑健康。读者要在自己的目标环境重新运行体检。
