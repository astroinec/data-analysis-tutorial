# 4-3 Plotly 交互与离线 HTML

目标：月度折线包含明确单位与悬停，导出自带脚本的完整 HTML。只显示一次交互图，控制离线 Notebook 体积。数据全为虚构，指标是已完成订单实付金额，不含退款、不代表利润。

```python
import sys
sys.path.insert(0, "..")
from dacheck import check, hint, setup_chinese_font
import pandas as pd
```

```python
import plotly.express as px
from pathlib import Path
import tempfile
orders = pd.read_csv("../data/shop/orders.csv")
completed = orders.loc[orders["status"].eq("已完成")].copy()
completed["order_time"] = pd.to_datetime(completed["order_time"])
completed["month"] = completed["order_time"].dt.to_period("M").dt.to_timestamp()
monthly = (completed.groupby("month", as_index=False)
           .agg(pay_amount=("pay_amount", "sum"), order_count=("order_id", "count"))
           .sort_values("month"))
print(monthly)
print("月度金额合计：", monthly["pay_amount"].sum())
```

## 示范：一次显示离线交互图

`px.line` 按表内顺序连线，先按月份排序。`labels` 改展示文字，不改列名；`hover_data` 提供订单数。`customdata[0]` 对应这一附加字段，调整顺序时也要调整悬停模板。

```python
fig = px.line(
    monthly, x="month", y="pay_amount", markers=True,
    hover_data={"order_count": True},
    labels={"month": "月份", "pay_amount": "实付金额（元）", "order_count": "已完成订单数（笔）"},
    title="2025年月度已完成订单实付金额（模拟）"
)
fig.update_layout(template="plotly_white", hovermode="x unified",
                  font={"family": "Microsoft YaHei, Arial, sans-serif"})
fig.update_xaxes(tickformat="%Y-%m")
fig.update_yaxes(rangemode="tozero")
fig.update_traces(hovertemplate="月份：%{x|%Y-%m}<br>实付金额：%{y:,.2f} 元"
                  "<br>已完成订单数：%{customdata[0]:,.0f} 笔<extra></extra>")
fig.show(renderer="notebook")
```

在 Notebook 或最终 HTML 中实际悬停查看。`notebook` 内嵌离线脚本，不要换成需要联网的 `notebook_connected`。浏览器字体独立于 matplotlib 字体工具，需自己核对中文。若输出空白，先验证导出的 HTML，不必安装 Kaleido；本课不做 Plotly 静态图片导出。

## 示范：临时离线导出，不覆盖原文件

```python
with tempfile.TemporaryDirectory() as folder:
    output = Path(folder) / "monthly_sales.html"
    fig.write_html(output, include_plotlyjs=True, full_html=True)
    print("导出存在：", output.exists())
    print("文件大小（字节）：", output.stat().st_size)
```

临时目录在退出 `with` 后清理，这是验证而非永久保存。个人环境需要成品时：在自己有写权限的位置建 `outputs` 文件夹，使用同样 `write_html` 参数另行保存，再从文件管理器双击 HTML，用本地浏览器断网刷新并检查悬停。本练习不自动打开浏览器、不上传、不发送文件。文件会包含图中的数据，分享前先检查可公开范围。

## 练习 1：月度结果表

独立生成月份、金额、订单数三列，按月份日期升序。订单数定义依赖本模拟主表一行一单的粒度。

```python
### BEGIN SOLUTION
monthly_answer = (completed.groupby("month", as_index=False)
                  .agg(pay_amount=("pay_amount", "sum"), order_count=("order_id", "count"))
                  .sort_values("month"))
### STUDENT
monthly_answer = ...
### END SOLUTION
check("4-3.1", monthly_answer)
```

## 练习 2：一条线的 Figure

独立创建 Figure，使用示范 `monthly`，标题“月度实付金额”，横轴“月份”，纵轴“实付金额（元）”。不用再次 show，检查会看结构和数据。

```python
### BEGIN SOLUTION
figure_answer = px.line(
    monthly, x="month", y="pay_amount",
    labels={"month": "月份", "pay_amount": "实付金额（元）"}, title="月度实付金额"
)
### STUDENT
figure_answer = ...
### END SOLUTION
check("4-3.2", figure_answer)
```

## 练习 3：提交独立 HTML 文本

使用示范 `fig`，在临时目录导出内嵌脚本的完整 HTML，退出目录前读出文本赋给 `html_answer`。不要提交临时路径，也不要使用 CDN。检查不会上传内容。

```python
### BEGIN SOLUTION
with tempfile.TemporaryDirectory() as export_folder:
    export_path = Path(export_folder) / "exercise.html"
    fig.write_html(export_path, include_plotlyjs=True, full_html=True)
    html_answer = export_path.read_text(encoding="utf-8")
### STUDENT
html_answer = ...
### END SOLUTION
check("4-3.3", html_answer)
```

## 练习 4：交付形式

对方没有 Python、可能断网，但需要悬停，提交交付形式“内嵌脚本的HTML”。不是依赖网络的网页链接。

```python
### BEGIN SOLUTION
delivery_answer = "内嵌脚本的HTML"
### STUDENT
delivery_answer = ...
### END SOLUTION
check("4-3.4", delivery_answer)
```

## 小测与验收

为什么不写 `include_plotlyjs="cdn"`？

<details><summary>参考答案</summary>CDN 会让浏览器额外请求网络脚本，不符合断网交付。True 将脚本内嵌，文件更大但可独立查看。</details>

验收：月份升序、单位清楚、悬停有金额和订单数；HTML 完整且内嵌脚本；个人环境能断网本地打开；未覆盖原数据。模拟作品展示可复核交付能力，不把趋势当因果、不写真实公司业绩。
