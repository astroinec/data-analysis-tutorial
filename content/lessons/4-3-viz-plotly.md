---
summary: 为同一个月度指标增加悬停交互，并导出不依赖网络的独立 HTML 图表。
prereq: 已完成 4-1、4-2，能按月汇总并解释图表口径
---

## 本课的可检验目标

:::goal
- 用 `plotly.express` 创建一张按月份排序的折线图。
- 在悬停中展示日期、金额和已完成订单数。
- 导出自带 JavaScript 的 HTML，在本机断网打开。
- 区分数据计算、美化展示和文件交付，不让“交互”替代解释。
:::

打开 [4-3 练习本](../../notebooks/4-3_viz_plotly.ipynb)。本课只显示一张 Plotly 交互图，避免每格重复嵌入较大的离线脚本。数据仍是随包的虚构文创店订单，金额口径为 2025 年已完成订单实付金额总和，不含退款，不代表利润。

## 1. 交互解决什么问题

静态 PNG 像报告照片，打开就能看，适合文档和邮件。交互 HTML 像带放大镜的图：鼠标悬停能读准确数值、拖动能局部查看、双击能恢复视野。交互不意味着自动分析，也不会在浏览器里执行你的 pandas 代码。

:::df
| 交付形式 | 优点 | 需要注意 |
|---|---|---|
| PNG / SVG 静态图 | 便于文档嵌入，轻量 | 细节要提前标注 |
| 独立交互 HTML | 可悬停、缩放，不要求收件人安装 Python | 文件更大，含嵌入的数据，要检查是否适合分享 |
| Notebook 输出 | 方便边算边看 | 运行需要课程环境，不等于对方拿到可直接查看的报告 |
:::

Plotly 是图形库，`plotly.express` 是常见快速入口，通常缩写 `px`。matplotlib 中常叫 `fig` 的画布与这里的 Plotly Figure 不是同一种对象，不能混着调用 `set_ylabel()`。Plotly 常用 `update_layout()` 和 `update_traces()`。

## 2. 汇总表比图更早完成

```python
import pandas as pd
orders = pd.read_csv("../data/shop/orders.csv")
completed = orders.loc[orders["status"].eq("已完成")].copy()
completed["order_time"] = pd.to_datetime(completed["order_time"])
completed["month"] = completed["order_time"].dt.to_period("M").dt.to_timestamp()
monthly = (completed.groupby("month", as_index=False)
           .agg(pay_amount=("pay_amount", "sum"),
                order_count=("order_id", "count"))
           .sort_values("month"))
print(monthly)
```

`agg()` 里左侧是结果列名，括号中的两个字符串依次表示源列与统计方法。每行是一个月份，不是一笔订单。订单数按本表一行一个订单的粒度计数，现实明细表则需要重新定义。画图前检查月份有无缺口、金额汇总是否回到已完成订单总额；图不会替你修复漏月和重复订单。

额外放入 `order_count` 是帮助读者理解规模，不意味着金额上升一定由订单数导致。客单价、退款状态和商品结构等也可能影响金额。不要为了悬停字段好看加入未计算过的“增长率”。

## 3. 用 px.line 画第一张交互图

```python
import plotly.express as px
fig = px.line(
    monthly, x="month", y="pay_amount", markers=True,
    hover_data={"order_count": True},
    labels={"month": "月份", "pay_amount": "实付金额（元）",
            "order_count": "已完成订单数（笔）"},
    title="2025年月度已完成订单实付金额（模拟）"
)
fig.update_layout(template="plotly_white",
                  font={"family": "Microsoft YaHei, Arial, sans-serif"},
                  hovermode="x unified")
fig.update_xaxes(tickformat="%Y-%m")
fig.update_yaxes(rangemode="tozero")
fig.show(renderer="notebook")
```

`x`、`y` 使用表中的列名；`labels` 更改显示给读者的文字，不修改实际列名。`markers=True` 给每月加点，悬停更容易定位。`hovermode="x unified"` 把同一横轴位置的信息放在一个提示框，本课只有一条金额线，先不引入多指标双轴。

Plotly 默认用浏览器字体显示文字，`setup_chinese_font()` 主要影响 matplotlib/seaborn，不会自动给 HTML 打包字体。这里写微软雅黑等系统字体候选；在自己的浏览器检查中文。不要因为设置了一个字体名就声称所有收件人机器都有这款字体。

:::note 本教程选择离线 Notebook 渲染
`renderer="notebook"` 会嵌入本地 Plotly 脚本，输出体积会更大。不要换成 `notebook_connected` 并假设断网仍能运行。若 JupyterLab 中空白，可重新运行此格；仍空白时先用下一节导出的独立 HTML 验证，不必安装静态导出引擎。本课不需要 Kaleido，也不使用另行安装的数据框适配 API。
:::

## 4. 悬停写得清楚，不是写得越多越好

日期显示到月份足够，不要让月份标签看起来像真实月初的一天。金额保留两位小数，并让读者知道单位；订单数保留整数。需要严格控制提示文字时，使用 `hovertemplate`。

```python
fig.update_traces(
    hovertemplate="月份：%{x|%Y-%m}<br>实付金额：%{y:,.2f} 元"
                  "<br>已完成订单数：%{customdata[0]:,.0f} 笔<extra></extra>"
)
```

这里 `customdata[0]` 是本图 `hover_data` 中第一个附加字段，即订单数。若以后调整了附加字段顺序，必须一起调整模板。`<extra></extra>` 隐藏附加图例框，不是删除数据。`<br>` 表示换行，这是提示框里的固定文本格式，不要拼接未经检查的外部用户输入。

在练习本里，先设置完悬停再调用一次 `fig.show()`，不要每修改一行就重新输出整份离线脚本。图的美化最后完成，数据口径与排序不因字体和配色变化而改变。

## 5. 导出一个断网也能打开的文件

```python
from pathlib import Path
import tempfile
with tempfile.TemporaryDirectory() as folder:
    output = Path(folder) / "monthly_sales.html"
    fig.write_html(output, include_plotlyjs=True, full_html=True)
    print("临时导出存在：", output.exists())
    print("文件大小（字节）：", output.stat().st_size)
```

`include_plotlyjs=True` 把 Plotly 的脚本带进 HTML；如果写 `"cdn"`，打开时还要下载网络脚本，不能称为独立离线交付。`full_html=True` 生成完整页面。文件通常比静态图大，具体大小随版本与数据变化，不需要背一个固定数字。

:::warn 临时文件用于练习，不是最终交付
退出 `with` 后临时目录自动清理。所以这段代码用于测试，不该打印路径后要求学生去找一个已消失文件。要在个人电脑保留成品，请另建自己有写权限的 `outputs` 文件夹，再用下面代码。不要覆盖源订单。
:::

```python
from pathlib import Path
folder = Path("../outputs")
if not folder.exists():
    folder.mkdir()
output = folder / "monthly_sales.html"
fig.write_html(output, include_plotlyjs=True, full_html=True)
print(output.resolve())
```

这一段在个人环境中手动执行：从文件管理器双击 `monthly_sales.html`，用本地浏览器打开，断开网络后刷新，再试悬停和缩放。Windows 浏览器若提示下载而非展示，先确认扩展名是 `.html`，不是隐藏后缀导致的 `.html.txt`。这只是本机文件，不需要发布到网站，也不需要上传第三方平台。

:::danger 分享前看数据，而不只是看图
HTML 里会嵌入绘图用的数据，隐藏某个图例并不等于删除数据。公开作品优先使用本模拟数据或获准公开的汇总数据；不要把个人标识、内部订单和敏感字段顺手打包发出去。本课不自动发送或上传任何文件。
:::

## 6. 四个练习

:::try 练习 1：月度金额与订单数
生成 `month`、`pay_amount`、`order_count` 三列并升序排列。说明 `order_count` 的粒度依据。
:::fold 提示与答案
使用上文 `groupby(...).agg(...)`。本订单主表一行一单，所以行数可计订单；若换成多商品明细，不能照搬 `count()`。
:::
:::

:::try 练习 2：图的结构
创建一张新的月度折线 Figure，不重复显示；轴标签用“月份”“实付金额（元）”，标题“月度实付金额”。
:::fold 参考答案
`px.line(monthly, x="month", y="pay_amount", labels={...}, title="月度实付金额")`。检查对照线的数据、日期顺序与标签，不要求一模一样的像素。
:::
:::

:::try 练习 3：验证离线导出
在临时目录导出 HTML，提交完整 HTML 文本供检查，不使用 CDN。
:::fold 参考答案
`fig.write_html(path, include_plotlyjs=True, full_html=True)` 后在 `with` 内 `html_answer = path.read_text(encoding="utf-8")`。不要把退出后已经失效的路径当答案；检查不接收外部网址，也不上传文件。
:::
:::

:::try 练习 4：交付决策
对方没有 Python、可能断网，但需要悬停查看数值，你应该选择什么交付形式？
:::fold 参考答案
“内嵌脚本的HTML”。收件人在浏览器本地查看，无须安装 Python；同时需要说明文件较大、数据已嵌入，分享前审查。
:::
:::

:::quiz
哪一个参数符合独立离线 HTML 交付？
- [ ] `include_plotlyjs="cdn"`
- [x] `include_plotlyjs=True`
- [ ] `include_plotlyjs=False` 且没有其他脚本来源
---
True 内嵌脚本。CDN 需要网络，False 要依赖页面外部另行提供脚本。
:::

## 7. 报错与验收

| 问题 | 纠正路径 |
|---|---|
| `ModuleNotFoundError: plotly` | 检查课程内核和 requirements，不在 base 随机安装 |
| HTML 断网空白 | 确认 True 内嵌脚本，重新导出完整 HTML |
| 找不到临时文件 | 临时目录退出后会消失；个人保存时用 `outputs` |
| 月份顺序异常 | 绘图前按日期升序，不靠悬停格式修正数据顺序 |
| 想导出 PNG 被要求装引擎 | 本课仅做 HTML；静态 PNG 继续用 matplotlib |

:::job
作品集可以同时提供静态总览与离线交互附件，并写清数据来源、指标定义和可公开范围。你的亮点是“交付可复核、无需联网的分析图”，不是虚构某公司用它提升多少收益。互动图同样需要一句有限度的文字结论。
:::

:::checklist 本课验收
- [ ] 折线数据已汇总，月份按真实日期升序。
- [ ] 悬停日期、金额和订单数的单位与精度正确。
- [ ] Notebook 一次展示即可，独立 HTML 内嵌脚本。
- [ ] 个人环境已本地打开 HTML 并断网检查交互。
- [ ] 不覆盖原数据、不上传敏感数据，不把趋势包装成因果。
:::
