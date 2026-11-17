"""P-1：按随包订单动态检查年度分析的口径与结果。"""
import pandas as pd

from dacheck.core import register, load, expect, expect_type, expect_equal, expect_close, expect_df


def _orders():
    orders = load("shop/orders.csv", parse_dates=["order_time"])
    return orders.loc[orders["order_time"].between("2025-01-01", "2026-01-01", inclusive="left")].copy()


def _completed():
    return _orders().loc[lambda d: d["status"].eq("已完成")].copy()


@register("P-1.1", title="全年指标", hint="收入、购买人数、客单价用已完成订单；退款率分母用全年全部订单。比率交小数，不乘100。")
def check_kpi(answer):
    expect_type(answer, dict)
    orders = _orders()
    completed = _completed()
    expected = {
        "all_orders": len(orders),
        "completed_orders": len(completed),
        "revenue": completed["pay_amount"].sum(),
        "buyers": completed["customer_id"].nunique(),
        "aov": completed["pay_amount"].sum() / len(completed),
        "refund_rate": orders["status"].eq("已退款").mean(),
    }
    expect(set(answer) == set(expected), "字典需要且只需要题目列出的六个键。")
    for key, value in expected.items():
        expect_close(answer[key], value, what=key)


@register("P-1.2", title="月度趋势", hint="只筛已完成，dt.strftime('%Y-%m')，groupby后agg；month、revenue、orders三列，按月份升序。")
def check_monthly(answer):
    completed = _completed()
    completed["month"] = completed["order_time"].dt.strftime("%Y-%m")
    expected = completed.groupby("month", as_index=False).agg(revenue=("pay_amount", "sum"), orders=("order_id", "nunique"))
    expect_df(answer, expected)


@register("P-1.3", title="平台退款率", hint="不能先删退款行。全年订单新增is_refund，分平台求订单数与退款数，最后相除。按platform升序。")
def check_platform(answer):
    orders = _orders().assign(is_refund=lambda d: d["status"].eq("已退款"))
    expected = orders.groupby("platform", as_index=False).agg(all_orders=("order_id", "nunique"), refunds=("is_refund", "sum"))
    expected["refund_rate"] = expected["refunds"] / expected["all_orders"]
    expect_df(answer, expected)


@register("P-1.4", title="品类收入贡献", hint="已完成订单左连接商品表，validate='many_to_one'；分组金额/已完成金额总和。按收入降序。")
def check_category(answer):
    completed = _completed().merge(load("shop/products.csv")[["product_id", "category"]], on="product_id", how="left", validate="many_to_one")
    expected = completed.groupby("category", as_index=False).agg(revenue=("pay_amount", "sum"))
    expected["share"] = expected["revenue"] / expected["revenue"].sum()
    expected = expected.sort_values("revenue", ascending=False).reset_index(drop=True)
    expect_df(answer, expected)


@register("P-1.5", title="月目标达成", hint="月收入和目标都用YYYY-MM字符串，按month合并。达成率是revenue/target_gmv，不是相差金额。")
def check_targets(answer):
    completed = _completed().assign(month=lambda d: d["order_time"].dt.strftime("%Y-%m"))
    monthly = completed.groupby("month", as_index=False).agg(revenue=("pay_amount", "sum"))
    expected = monthly.merge(load("shop/monthly_targets.csv"), on="month", how="left", validate="one_to_one")
    expected["achievement"] = expected["revenue"] / expected["target_gmv"]
    expect_df(answer, expected.sort_values("month").reset_index(drop=True))


@register("P-1.6", title="观察窗口复购率", hint="已完成订单按customer_id统计唯一order_id，至少2笔的客户数/有已完成购买的客户数。不要除以3000。")
def check_repeat(answer):
    counts = _completed().groupby("customer_id")["order_id"].nunique()
    expect_close(answer, counts.ge(2).mean(), what="观察窗口复购率")


@register("P-1.7", title="多表连接不丢不增订单", hint="交order_id、product_name、category、city四列，保留全年全部订单；两个left merge都要验证many_to_one。")
def check_join(answer):
    orders = _orders()
    expected = orders.merge(load("shop/products.csv")[["product_id", "product_name", "category"]], on="product_id", how="left", validate="many_to_one")
    expected = expected.merge(load("shop/customers.csv")[["customer_id", "city"]], on="customer_id", how="left", validate="many_to_one")
    expect_type(answer, pd.DataFrame)
    expect("order_id" in answer.columns, "请保留order_id，以便检查订单是否丢失或重复。")
    expect_equal(answer["order_id"].nunique(), len(orders), "连接后的唯一订单数")
    expect_df(answer, expected[["order_id", "product_name", "category", "city"]], check_order=False)
