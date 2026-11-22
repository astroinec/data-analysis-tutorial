"""7-3 RFM 用户分层。"""
import pandas as pd

from dacheck.core import register, load, expect, expect_type, expect_close, expect_df


REF_DATE = pd.Timestamp("2026-01-01")
SEG_MAP = {
    (True, True, True): "重要价值客户",
    (False, True, True): "重要保持客户",
    (True, False, True): "重要发展客户",
    (False, False, True): "重要挽留客户",
    (True, True, False): "一般价值客户",
    (False, True, False): "一般保持客户",
    (True, False, False): "一般发展客户",
    (False, False, False): "一般挽留客户",
}


def _rfm():
    orders = load("shop/orders.csv", parse_dates=["order_time"])
    done = orders.loc[orders["status"].eq("已完成")].copy()
    rfm = done.groupby("customer_id", as_index=False).agg(
        last_time=("order_time", "max"),
        F=("order_id", "nunique"),
        M=("pay_amount", "sum"),
    )
    rfm["R"] = (REF_DATE - rfm["last_time"]).dt.days
    return rfm[["customer_id", "R", "F", "M"]].sort_values("customer_id").reset_index(drop=True)


@register("7-3.1", title="计算每位购买客户的 R、F、M 原始值", hint="仅用已完成订单，基准日 pd.Timestamp('2026-01-01')，R=(ref_date - max_order_time).dt.days，F 为唯一订单数，M 为实付金额之和，按 customer_id 升序。")
def check_rfm_base(answer):
    expect_df(answer, _rfm(), "RFM 原始指标表")


@register("7-3.2", title="计算 R、F、M 的中位数阈值", hint="对 RFM 表的 R、F、M 三列分别取 median()，放进 R_med、F_med、M_med 三个键。")
def check_rfm_medians(answer):
    expect_type(answer, dict)
    rfm = _rfm()
    expected = {
        "R_med": float(rfm["R"].median()),
        "F_med": float(rfm["F"].median()),
        "M_med": float(rfm["M"].median()),
    }
    expect(set(answer) == set(expected), "字典需要且只需要 R_med、F_med、M_med 三个键。")
    for k, v in expected.items():
        expect_close(answer[k], v, what=k)


@register("7-3.3", title="RFM 八类客户分层汇总", hint="R_high = R <= R_med（注意 R 越小越近！），F_high = F >= F_med，M_high = M >= M_med，映射 8 类分层名后按 segment 汇总 customers 和 total_m，按 total_m 降序。")
def check_rfm_segments(answer):
    rfm = _rfm()
    r_m, f_m, m_m = rfm["R"].median(), rfm["F"].median(), rfm["M"].median()
    rfm["segment"] = [
        SEG_MAP[(r <= r_m, f >= f_m, m >= m_m)]
        for r, f, m in zip(rfm["R"], rfm["F"], rfm["M"])
    ]
    expected = (
        rfm.groupby("segment", as_index=False)
        .agg(customers=("customer_id", "nunique"), total_m=("M", "sum"))
        .sort_values("total_m", ascending=False)
        .reset_index(drop=True)
    )
    expect_df(answer, expected, "RFM 分层汇总表")


@register("7-3.4", title="重要价值客户的占比与金额贡献", hint="在 RFM 分层结果中计算 segment == '重要价值客户' 的人数占比 customer_share 与金额占比 revenue_share（小数）。")
def check_rfm_vip_share(answer):
    expect_type(answer, dict)
    rfm = _rfm()
    r_m, f_m, m_m = rfm["R"].median(), rfm["F"].median(), rfm["M"].median()
    vip = rfm.loc[(rfm["R"] <= r_m) & (rfm["F"] >= f_m) & (rfm["M"] >= m_m)]
    expected = {
        "customer_share": len(vip) / len(rfm),
        "revenue_share": vip["M"].sum() / rfm["M"].sum(),
    }
    expect(set(answer) == set(expected), "字典需要且只需要 customer_share、revenue_share 两个键。")
    for k, v in expected.items():
        expect_close(answer[k], v, tol=1e-5, what=k)
