"""7-1 指标体系与拆解思路。"""
import pandas as pd

from dacheck.core import register, load, expect, expect_type, expect_close, expect_df


def _completed():
    orders = load("shop/orders.csv", parse_dates=["order_time"])
    done = orders.loc[orders["status"].eq("已完成")].copy()
    done["month"] = done["order_time"].dt.strftime("%Y-%m")
    return done


@register("7-1.1", title="月度销售额三因子拆解", hint="按 month 分组计算 revenue、orders、buyers，再算 orders_per_buyer = orders / buyers 和 aov = revenue / orders，输出 month、buyers、orders_per_buyer、aov、revenue 五列并按 month 升序。")
def check_monthly_decomp(answer):
    done = _completed()
    m = done.groupby("month", as_index=False).agg(
        revenue=("pay_amount", "sum"),
        orders=("order_id", "nunique"),
        buyers=("customer_id", "nunique"),
    )
    m["orders_per_buyer"] = m["orders"] / m["buyers"]
    m["aov"] = m["revenue"] / m["orders"]
    expected = m[["month", "buyers", "orders_per_buyer", "aov", "revenue"]].sort_values("month").reset_index(drop=True)
    expect_df(answer, expected, "月度三因子拆解表")


@register("7-1.2", title="11 月到 12 月环比变化拆解", hint="分别取出 2025-11 和 2025-12 的 revenue、buyers、orders_per_buyer、aov，用 (12月 - 11月) / 11月 计算变化率（小数）。")
def check_nov_dec_mom(answer):
    expect_type(answer, dict)
    done = _completed()
    m = done.groupby("month").agg(
        revenue=("pay_amount", "sum"),
        orders=("order_id", "nunique"),
        buyers=("customer_id", "nunique"),
    )
    m["orders_per_buyer"] = m["orders"] / m["buyers"]
    m["aov"] = m["revenue"] / m["orders"]
    nov, dec = m.loc["2025-11"], m.loc["2025-12"]
    expected = {
        "revenue_mom": (dec["revenue"] - nov["revenue"]) / nov["revenue"],
        "buyers_mom": (dec["buyers"] - nov["buyers"]) / nov["buyers"],
        "opb_mom": (dec["orders_per_buyer"] - nov["orders_per_buyer"]) / nov["orders_per_buyer"],
        "aov_mom": (dec["aov"] - nov["aov"]) / nov["aov"],
    }
    expect(set(answer) == set(expected), "字典需要且只需要 revenue_mom、buyers_mom、opb_mom、aov_mom 四个键。")
    for k, v in expected.items():
        expect_close(answer[k], v, tol=1e-5, what=k)


@register("7-1.3", title="按城市层级下钻拆解", hint="已完成订单左连接 customers[['customer_id', 'city_tier']]，按 city_tier 分组算 buyers、orders、revenue、aov，按 revenue 降序。")
def check_city_tier_decomp(answer):
    done = _completed().merge(
        load("shop/customers.csv")[["customer_id", "city_tier"]],
        on="customer_id", how="left", validate="many_to_one",
    )
    expected = done.groupby("city_tier", as_index=False).agg(
        buyers=("customer_id", "nunique"),
        orders=("order_id", "nunique"),
        revenue=("pay_amount", "sum"),
    )
    expected["aov"] = expected["revenue"] / expected["orders"]
    expected = expected.sort_values("revenue", ascending=False).reset_index(drop=True)
    expect_df(answer, expected, "城市层级拆解表")


@register("7-1.4", title="客单价再拆解：品类平均件数与件单价", hint="已完成订单左连接 products[['product_id', 'category']]，按 category 计算 avg_qty = sum(quantity)/nunique(order_id) 与 price_per_item = sum(pay_amount)/sum(quantity)，按 category 升序。")
def check_category_aov_decomp(answer):
    done = _completed().merge(
        load("shop/products.csv")[["product_id", "category"]],
        on="product_id", how="left", validate="many_to_one",
    )
    g = done.groupby("category", as_index=False).agg(
        orders=("order_id", "nunique"),
        total_qty=("quantity", "sum"),
        revenue=("pay_amount", "sum"),
    )
    g["avg_qty"] = g["total_qty"] / g["orders"]
    g["price_per_item"] = g["revenue"] / g["total_qty"]
    expected = g[["category", "avg_qty", "price_per_item"]].sort_values("category").reset_index(drop=True)
    expect_df(answer, expected, "品类件数与件单价表")
