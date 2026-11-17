# HTML 视觉重设计交接

这是供教程维护者及 GPT/Kimi 等重设计工具使用的接口说明。教学内容与视觉外观分开保存；可以重做视觉，但不要破坏逐步学习、练习检查和路径约定。

## 优先改哪些文件

| 文件 | 职责 | 改动原则 |
|---|---|---|
| `site/assets/css/style.css` | 全站视觉、排版、主题、响应式、教学组件 | 优先在这里重设计；不要把样式散落进每课 |
| `tools/templates/page.html` | 全站页面壳 | 可改布局语义，保留模板占位符与功能挂载点 |
| `content/home.md` | 首页正文 | 保留范围声明、路线和入口，不把后续灰色课包装为完成品 |
| `content/lessons/*.md` | 教学内容 | 不为视觉删讲解、练习、答案、数据来源和风险提示 |
| `site/assets/js/app.js` | 复制、高亮、小测、标签页、勾选、进度、主题、目录、图片放大、搜索 | 一般不改；如改功能，需重新验收 |
| `site/assets/js/widgets/*.js` | 小样本教学互动 | 一般不改计算或真实数据口径 |
| `tools/build_site.py` | Markdown/容器转网页与链接检查 | 构建入口，不逐页手改生成结果 |

`site/index.html` 与 `site/lessons/*.html` 是生成文件，下一次构建会覆盖。页面无在线字体、JS/CSS CDN，也不用前端框架；保持完整解压后双击即可阅读。

## 模板占位符

`page.html` 使用 `{{page_title}}`、`{{site_title}}`、`{{root}}`、`{{body_class}}`、`{{lesson_id}}`、`{{stage_color}}`、`{{sidebar}}`、`{{toc}}`、`{{main}}`、`{{scripts}}`。

- `{{root}}` 在首页为空、课程页为 `../`；不要替换为机器绝对路径。
- `{{scripts}}` 是本课需要的组件脚本，必须在主 `app.js` 之后加载。
- `body` 的 `data-lesson` 用于学习进度；`--stage-color` 和导航 `--c` 是阶段颜色数据，而不是应复制到每课的整套行内样式。
- `<html lang="zh-CN">`、UTF-8、viewport 和内容的标题层级应保留。

## 必须保留的功能接口

| 组件/功能 | JS 使用的接口 |
|---|---|
| 主题 | `.theme-btn`、根元素 `data-theme`，深浅主题变量 |
| 手机课程目录 | `.menu-btn`、`.sidebar`、`.sidebar-mask`、`body.nav-open` |
| 总进度/阅读进度 | `.op-bar i`、`.op-text`、`.read-progress` |
| 单课完成/首页续学 | `body[data-lesson]`、`.done-btn`、`.resume-link`、`[data-lid]` |
| 阶段进度 | `.stage-card[data-sid]`、`.stage-bar i` |
| 首页搜索 | `#course-search`、`.search-summary`、阶段卡片与其中 `li` 的 `hidden` 状态 |
| 页内目录 | `.toc a[href^='#']`、正文标题的对应 `id` |
| 代码 | `pre > code.language-*`；增强后 `.code-wrap/.code-head/.copy-btn`；不要把代码渲染成图片 |
| 小测 | `.quiz`、`.quiz-options button[data-correct]`、`.quiz-explain`、`.right/.wrong/.answered` |
| 标签页 | `.tabs > .tab-panel[data-label]`、`.tab-bar`、`hidden` 和 ARIA selected/tabIndex |
| 勾选清单 | `.checklist input[type=checkbox][data-id]`、`.cl-text`、`.cl-count`、`.all-done` |
| 图片放大 | `.lesson-body figure img`、`.lightbox`；Escape关闭 |
| 教学互动 | `.widget[data-widget]`、`.widget-body`、`script[type='application/json']`、`data-mounted` |

`hidden` 元素必须真的不占布局空间；不要用泛化的 `display:block !important` 覆盖标签页、搜索或隐藏目录。按钮和输入保持键盘可操作、焦点可见、文字对比充分。

## 教学语义组件

- `.lesson-hero`：课号、标题、前置和预计时间。
- `.callout` 与 `goal/note/tip/warn/danger/job/analogy/try/recap`：按语义区分提示；别只靠颜色区分危险和一般说明。
- `.steps > ol > li.step`：分步操作，用编号和留白帮助零基础读者。
- `.flow`：问题→整理→计算→解释流程。
- `.cards/.card/.card-title`：概念卡片。
- `.compare/.compare-col.bad/.compare-col.good`：正误对照，窄屏堆叠。
- `details.fold > summary`：答案折叠，不能因美化把答案内容丢掉。
- `.window/.window-title/.window-body`：**明确标为界面示意**的安装对照；不是模拟可执行的安装器，不新增“官方截图”字样。
- `.ui-btn/.annot`：说明文中的示意标签，不是真按钮。
- `.table-wrap/.dataframe-wrap`：横向滚动表格，不让整页横溢出。
- `.nb-cta`、`.lesson-footer/.pager`：练习本入口与前后课。
- `.home-hero/.roadmap/.stage-card/.is-soon`：已交付和后续课程要区分。

### 已实现的离线互动

- `table-lab`：筛选门槛、排序、按品类/平台分组；独立6行样本。
- `cleaning-lab`：去重复、隔离异常、反例“全部删缺失”。
- `chart-picker`：按问题选择图与解释；小图是示意而非业务结果。
- `env-doctor`：环境问题分流，**不读电脑、不替代检查脚本**。

保留组件的“小样本模拟、不执行 Python”声明。不能通过添加貌似在线运行按钮暗示已有 Pyodide/后端内核。

## 可直接给 GPT/Kimi 的提示

> 请对这份“写给文科求职者的零基础数据分析教程”做视觉重设计。目标是阅读清楚、逐步学习、低认知负担，不是炫技仪表盘。
>
> 优先修改 `site/assets/css/style.css`，必要时修改 `tools/templates/page.html`。教程内容在 `content/`，不要删改课程、练习、折叠答案、环境步骤、模拟声明、数据来源或指标口径。保持这里列出的功能类名、ID、模板占位符与 `data-*` 接口；保持脚本顺序、相对路径和页面离线可用，不引入框架、在线字体或 CDN。
>
> 请重点优化中文长文阅读、字号与行距、标题层次、代码/命令/输出区分、Windows安装示意、表格溢出、正误对照、课程导航与手机布局。浅色/深色都要有足够对比度，按钮键盘焦点可见；不要靠颜色独自传达信息。不要把代码变成图片；互动是小样本模拟，不执行Python。
>
> 修改后运行 `python tools/build_site.py --strict`，检查：首页、安装课0-4、筛选课2-2、清洗课3-1、图表课4-1和项目P-1。测试代码复制、小测、折叠、标签页、进度、搜索、互动、图片与相对链接，分别查看桌面和约390px窄屏。不要手改每个生成HTML来规避构建。

## 重设计后的验收

1. 首页仍明确24篇本批讲义、15套本子；后续阶段不假装完成。
2. 课号、前置、学习目标、下一课和本子链接齐全。
3. 代码块可选中、复制，输出块不误导为待执行命令。
4. 小测题干、选项、反馈与答案解释可见；清单、进度保存行为不变。
5. 表格只在自己的容器内横向滚动，390px宽页面不整体溢出。
6. 深色安装示意仍可读；图片、折叠和交互不用联网。
7. 修改模板/CSS后重建，无缺文件、无组件警告、无断链。
