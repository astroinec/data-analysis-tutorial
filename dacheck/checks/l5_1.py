"""5-1 描述统计：平均数会骗人。"""
import pandas as pd

from dacheck.core import register, load, expect, expect_type, expect_equal, expect_close, expect_df


def _completed():
    orders = load("shop/orders.csv")
    return orders.loc[orders["status"].eq("已完成")].copy()


@register("5-1.1", title="已完成订单金额的核心描述统计", hint="先筛已完成订单，对 pay_amount 分别求 mean、median、std（默认 ddof=1）以及 Q3 - Q1。")
def check_desc_dict(answer):
    expect_type(answer, dict)
    s = _completed()["pay_amount"]
    expected = {
        "mean": s.mean(),
        "median": s.median(),
        "std": s.std(),
        "iqr": s.quantile(0.75) - s.quantile(0.25),
    }
    expect(set(answer) == set(expected), "字典需要且只需要 mean、median、std、iqr 四个键。")
    for k, v in expected.items():
        expect_close(answer[k], v, what=k)


@register("5-1.2", title="订单金额分位数", hint="对已完成订单的 pay_amount 调用 quantile([0.5, 0.75, 0.9, 0.95])，填入 p50、p75、p90、p95 四个键。")
def check_quantiles(answer):
    expect_type(answer, dict)
    s = _completed()["pay_amount"]
    expected = {
        "p50": s.quantile(0.50),
        "p75": s.quantile(0.75),
        "p90": s.quantile(0.90),
        "p95": s.quantile(0.95),
    }
    expect(set(answer) == set(expected), "字典需要且只需要 p50、p75、p90、p95 四个键。")
    for k, v in expected.items():
        expect_close(answer[k], v, what=k)


@register("5-1.3", title="各平台实付金额均值、中位数与标准差", hint="对已完成订单按 platform 分组（as_index=False），用 agg 计算 mean、median、std，按 platform 升序。")
def check_platform_stats(answer):
    expected = (
        _completed()
        .groupby("platform", as_index=False)
        .agg(
            mean=("pay_amount", "mean"),
            median=("pay_amount", "median"),
            std=("pay_amount", "std"),
        )
        .sort_values("platform")
        .reset_index(drop=True)
    )
    expect_df(answer, expected, "各平台描述统计表")


@register("5-1.4", title="用 IQR 规则识别图书评价人数上侧离群数", hint="对 books['rating_count'] 计算 Q1、Q3 与 IQR=Q3-Q1，统计大于 Q3 + 1.5 * IQR 的行数。")
def check_iqr_outliers(answer):
    s = load("books.csv")["rating_count"]
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    upper = q3 + 1.5 * (q3 - q1)
    expected = int((s > upper).sum())
    expect_equal(answer, expected, "上侧统计离群图书数量")
