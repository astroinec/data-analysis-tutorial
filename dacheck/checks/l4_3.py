"""Plotly 图结构和离线 HTML 检查，不执行提交的HTML。"""
import re
import numpy as np
import pandas as pd
from dacheck.core import register, expect, expect_type, expect_equal, expect_df, load


def monthly_summary():
    orders = load("shop/orders.csv")
    completed = orders.loc[orders["status"].eq("已完成")].copy()
    completed["month"] = pd.to_datetime(completed["order_time"]).dt.to_period("M").dt.to_timestamp()
    return (completed.groupby("month", as_index=False)
            .agg(pay_amount=("pay_amount", "sum"), order_count=("order_id", "count"))
            .sort_values("month"))


@register("4-3.1", hint="月份日期升序；agg 命名汇总 pay_amount sum 与 order_id count。", title="月度金额与订单数")
def check_monthly(answer):
    expect(isinstance(answer, pd.DataFrame), "请提交月度汇总表。")
    expect("month" in answer and pd.api.types.is_datetime64_any_dtype(answer["month"]), "月份需为日期类型。")
    expect_df(answer, monthly_summary(), "月度汇总")


@register("4-3.2", hint="px.line 使用示范 monthly；标题和 labels 按题目，不调用 matplotlib 的 set_ylabel。", title="交互折线结构")
def check_figure(answer):
    from plotly.graph_objs import Figure
    expect(isinstance(answer, Figure), "请提交 Plotly Figure，不是 matplotlib Axes。")
    expect_equal(len(answer.data), 1, "图中线条数")
    trace = answer.data[0]
    expect_equal(trace.type, "scatter", "折线轨迹类型")
    expect("lines" in (trace.mode or ""), "需要折线模式，不能只有散点。")
    expected = monthly_summary()
    actual_dates = pd.to_datetime(np.asarray(trace.x))
    expect_equal(len(actual_dates), len(expected), "月份数")
    expect(np.array_equal(actual_dates.to_numpy(dtype="datetime64[ns]"),
                          expected["month"].to_numpy(dtype="datetime64[ns]")), "折线横轴月份或顺序不正确。")
    expect(np.allclose(np.asarray(trace.y, dtype=float), expected["pay_amount"].to_numpy()), "折线金额与已完成订单月度汇总不一致。")
    expect_equal(answer.layout.title.text, "月度实付金额", "标题")
    expect_equal(answer.layout.xaxis.title.text, "月份", "横轴标签")
    expect_equal(answer.layout.yaxis.title.text, "实付金额（元）", "纵轴标签")


@register("4-3.3", hint="write_html(include_plotlyjs=True, full_html=True)，在临时目录退出前 read_text 取完整文本。", title="独立离线HTML")
def check_html(answer):
    expect_type(answer, str, "HTML文本")
    lower = answer.lower()
    expect("<html>" in lower and "</html>" in lower, "需要完整 HTML，而不是片段或文件路径。")
    expect("plotly.newplot" in lower, "未找到 Plotly 图初始化，确认导出的是交互图。")
    expect("plotly.js v" in lower and len(answer) > 500_000, "未找到内嵌 Plotly 脚本；请设置 include_plotlyjs=True。")
    expect(not re.search(r'<script\b[^>]*\bsrc\s*=\s*["\'](?:https?:)?//', answer, re.I),
           "HTML 仍引用网络脚本，不符合本题离线交付要求。")


@register("4-3.4", hint="对方用浏览器打开；脚本随文件内嵌，不能依赖CDN。", title="无需Python的交付")
def check_delivery(answer):
    expect_equal(answer, "内嵌脚本的HTML", "交付形式")
