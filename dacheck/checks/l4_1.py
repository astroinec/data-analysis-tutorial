"""基础图形检查：验证数据、结构与标签，不比较像素。"""
import pandas as pd
from dacheck.core import register, expect, expect_equal, expect_close, expect_df, expect_series, load


def category_sales():
    orders = load("shop/orders.csv")
    joined = orders.loc[orders["status"].eq("已完成")].merge(
        load("shop/products.csv")[["product_id", "category"]],
        on="product_id", how="left", validate="many_to_one")
    return joined.groupby("category")["pay_amount"].sum().sort_values(ascending=False)


@register("4-1.1", hint="先已完成订单关联品类，再按 category 分组对 pay_amount 求和并降序。", title="品类金额汇总")
def check_category_sales(answer):
    expect_series(answer, category_sales(), "品类金额")


@register("4-1.2", hint="日期转换后生成月份标签，groupby(as_index=False) 求和，再按月份排序。", title="日期排序的月度表")
def check_monthly(answer):
    orders = load("shop/orders.csv")
    completed = orders.loc[orders["status"].eq("已完成")].copy()
    completed["month"] = pd.to_datetime(completed["order_time"]).dt.to_period("M").dt.to_timestamp()
    expected = completed.groupby("month", as_index=False)["pay_amount"].sum().sort_values("month")
    expect(isinstance(answer, pd.DataFrame), "请提交包含 month 和 pay_amount 的表格。")
    expect("month" in answer and pd.api.types.is_datetime64_any_dtype(answer["month"]), "month 需要日期类型。")
    expect_df(answer, expected, "月度金额表")


@register("4-1.3", hint="提交 ax；bar 使用已排序汇总；标题与轴名按题目，set_ylim(bottom=0)。", title="柱形图数据与标签")
def check_bar(answer):
    from matplotlib.axes import Axes
    from matplotlib.container import BarContainer
    expect(isinstance(answer, Axes), "请提交 matplotlib 的 Axes 绘图区对象。")
    expected = category_sales()
    bars = [c for c in answer.containers if isinstance(c, BarContainer)]
    expect_equal(len(bars), 1, "柱形组数")
    expect_equal(len(bars[0].patches), len(expected), "柱子数")
    for i, (patch, value) in enumerate(zip(bars[0].patches, expected)):
        expect_close(patch.get_height(), value, what=f"第{i + 1}根柱的金额")
    expect_equal([t.get_text() for t in answer.get_xticklabels()], list(expected.index), "品类顺序")
    expect_equal(answer.get_title(), "品类实付金额", "标题")
    expect_equal(answer.get_xlabel(), "品类", "横轴标签")
    expect_equal(answer.get_ylabel(), "实付金额（元）", "纵轴标签")
    expect_close(answer.get_ylim()[0], 0, what="柱图纵轴基线")


@register("4-1.4", hint="趋势沿时间连接相邻点，先按真实日期排序。", title="趋势问题选图")
def check_chart(answer):
    expect_equal(answer, "折线图", "图名")
