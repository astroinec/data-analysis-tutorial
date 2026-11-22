"""P-2 项目二：App 转化漏斗与用户留存。"""
import pandas as pd

from dacheck.core import register, load, expect, expect_type, expect_equal, expect_close, expect_df


STEPS = ["app_open", "view_course", "start_trial", "click_pay", "pay_success"]


def _app_tables():
    u = load("app/app_users.csv", parse_dates=["register_date"])
    e = load("app/app_events.csv", parse_dates=["event_time"])
    a = load("app/app_active.csv", parse_dates=["active_date"])
    return u, e, a


@register("P-2.1", title="全量五步转化漏斗", hint="按 app_open→view_course→start_trial→click_pay→pay_success 统计唯一 user_id 数，计算 step_rate 与 overall_rate。")
def check_p2_funnel(answer):
    _, e, _ = _app_tables()
    counts = [e.loc[e["event_name"].eq(st), "user_id"].nunique() for st in STEPS]
    expected = pd.DataFrame([
        {
            "step": st,
            "users": u,
            "step_rate": 1.0 if i == 0 else u / counts[i - 1],
            "overall_rate": u / counts[0],
        }
        for i, (st, u) in enumerate(zip(STEPS, counts))
    ])
    expect_df(answer, expected, "全量五步漏斗表")


@register("P-2.2", title="分渠道核心漏斗转化对比", hint="合并 app_events 与 app_users，按 channel 统计 open_users、trial_users、click_users、pay_users，再算 trial_to_click 与 overall_pay_rate，按 overall_pay_rate 降序。")
def check_p2_channel_funnel(answer):
    u, e, _ = _app_tables()
    eu = e.merge(u[["user_id", "channel"]], on="user_id", how="left", validate="many_to_one")
    rows = []
    for ch, g in eu.groupby("channel"):
        o = g.loc[g["event_name"].eq("app_open"), "user_id"].nunique()
        t = g.loc[g["event_name"].eq("start_trial"), "user_id"].nunique()
        c = g.loc[g["event_name"].eq("click_pay"), "user_id"].nunique()
        p = g.loc[g["event_name"].eq("pay_success"), "user_id"].nunique()
        rows.append({
            "channel": ch,
            "open_users": o,
            "trial_users": t,
            "click_users": c,
            "pay_users": p,
            "trial_to_click": c / t,
            "overall_pay_rate": p / o,
        })
    expected = pd.DataFrame(rows).sort_values("overall_pay_rate", ascending=False).reset_index(drop=True)
    expect_df(answer, expected, "分渠道漏斗转化表")


@register("P-2.3", title="分设备支付成功率对比", hint="合并 app_events 与 app_users，按 device 统计 click_users、pay_users 和 pay_rate = pay_users / click_users，按 device 升序。")
def check_p2_device_pay(answer):
    u, e, _ = _app_tables()
    eu = e.merge(u[["user_id", "device"]], on="user_id", how="left", validate="many_to_one")
    rows = []
    for dev, g in eu.groupby("device"):
        c = g.loc[g["event_name"].eq("click_pay"), "user_id"].nunique()
        p = g.loc[g["event_name"].eq("pay_success"), "user_id"].nunique()
        rows.append({"device": dev, "click_users": c, "pay_users": p, "pay_rate": p / c})
    expected = pd.DataFrame(rows).sort_values("device").reset_index(drop=True)
    expect_df(answer, expected, "分设备支付成功率表")


@register("P-2.4", title="分渠道 D1/D7/D30 留存率对比", hint="合并 app_active 与 app_users，算 day_diff=(active_date-register_date).dt.days，按 channel 计算 users 及 d1、d7、d30 留存率，按 d7 降序。")
def check_p2_channel_ret(answer):
    u, _, a = _app_tables()
    au = a.merge(u[["user_id", "register_date", "channel"]], on="user_id", how="left", validate="many_to_one")
    au["day_diff"] = (au["active_date"] - au["register_date"]).dt.days
    base = u.groupby("channel", as_index=False).agg(users=("user_id", "nunique"))
    for d in (1, 7, 30):
        sub = au.loc[au["day_diff"].eq(d)].groupby("channel", as_index=False).agg(**{f"n{d}": ("user_id", "nunique")})
        base = base.merge(sub, on="channel", how="left")
        base[f"d{d}"] = base[f"n{d}"].fillna(0) / base["users"]
    expected = base[["channel", "users", "d1", "d7", "d30"]].sort_values("d7", ascending=False).reset_index(drop=True)
    expect_df(answer, expected, "分渠道留存对比表")


@register("P-2.5", title="按周同期群 7 日留存趋势", hint="把 register_date 对齐到所在周的周一：cohort_week = (register_date - pd.to_timedelta(register_date.dt.day_of_week, unit='D')).dt.strftime('%Y-%m-%d')，按 cohort_week 统计 users 和 d7_rate，按 cohort_week 升序。")
def check_p2_weekly_cohort(answer):
    u, _, a = _app_tables()
    u["cohort_week"] = (u["register_date"] - pd.to_timedelta(u["register_date"].dt.day_of_week, unit="D")).dt.strftime("%Y-%m-%d")
    au = a.merge(u[["user_id", "register_date", "cohort_week"]], on="user_id", how="left", validate="many_to_one")
    au["day_diff"] = (au["active_date"] - au["register_date"]).dt.days
    base = u.groupby("cohort_week", as_index=False).agg(users=("user_id", "nunique"))
    d7 = au.loc[au["day_diff"].eq(7)].groupby("cohort_week", as_index=False).agg(n7=("user_id", "nunique"))
    expected = base.merge(d7, on="cohort_week", how="left")
    expected["d7_rate"] = expected["n7"].fillna(0) / expected["users"]
    expected = expected[["cohort_week", "users", "d7_rate"]].sort_values("cohort_week").reset_index(drop=True)
    expect_df(answer, expected, "周同期群7日留存表")


@register("P-2.6", title="项目二核心指标卡", hint="返回 6 键字典：total_users、overall_pay_rate、best_channel、worst_channel（按整体付费转化率）、ios_pay_step_rate、android_pay_step_rate。")
def check_p2_kpi(answer):
    expect_type(answer, dict)
    u, e, _ = _app_tables()
    eu = e.merge(u[["user_id", "channel", "device"]], on="user_id", how="left", validate="many_to_one")
    ch_rates = {}
    for ch, g in eu.groupby("channel"):
        o = g.loc[g["event_name"].eq("app_open"), "user_id"].nunique()
        p = g.loc[g["event_name"].eq("pay_success"), "user_id"].nunique()
        ch_rates[ch] = p / o
    dev_rates = {}
    for dev, g in eu.groupby("device"):
        c = g.loc[g["event_name"].eq("click_pay"), "user_id"].nunique()
        p = g.loc[g["event_name"].eq("pay_success"), "user_id"].nunique()
        dev_rates[dev] = p / c
    expected = {
        "total_users": len(u),
        "overall_pay_rate": e.loc[e["event_name"].eq("pay_success"), "user_id"].nunique() / len(u),
        "best_channel": max(ch_rates, key=ch_rates.get),
        "worst_channel": min(ch_rates, key=ch_rates.get),
        "ios_pay_step_rate": dev_rates["iOS"],
        "android_pay_step_rate": dev_rates["Android"],
    }
    expect(set(answer) == set(expected), "字典需要且只需要题目列出的六个键。")
    for k, v in expected.items():
        if isinstance(v, str):
            expect_equal(answer[k], v, what=k)
        else:
            expect_close(answer[k], v, tol=1e-5, what=k)
