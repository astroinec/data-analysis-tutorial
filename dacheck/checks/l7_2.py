"""7-2 漏斗、留存与同期群。"""
import pandas as pd

from dacheck.core import register, load, expect, expect_type, expect_close, expect_df


STEPS = ["app_open", "view_course", "start_trial", "click_pay", "pay_success"]


@register("7-2.1", title="App 五步转化漏斗", hint="按 STEPS 顺序统计每步唯一 user_id 数，step_rate = 当前步 / 上一步（第一步为 1.0），overall_rate = 当前步 / 第一步。")
def check_app_funnel(answer):
    ev = load("app/app_events.csv")
    counts = [ev.loc[ev["event_name"].eq(st), "user_id"].nunique() for st in STEPS]
    rows = []
    for i, (st, u) in enumerate(zip(STEPS, counts)):
        rows.append({
            "step": st,
            "users": u,
            "step_rate": 1.0 if i == 0 else u / counts[i - 1],
            "overall_rate": u / counts[0],
        })
    expected = pd.DataFrame(rows)
    expect_df(answer, expected, "五步转化漏斗表")


@register("7-2.2", title="全量用户 D1/D7/D14/D30 留存率", hint="把 app_active 与 app_users 按 user_id 左连接，计算 day_diff = (active_date - register_date).dt.days，分别算 day_diff == 1/7/14/30 的唯一用户数除以总注册用户数。")
def check_overall_retention(answer):
    expect_type(answer, dict)
    users = load("app/app_users.csv", parse_dates=["register_date"])
    active = load("app/app_active.csv", parse_dates=["active_date"])
    merged = active.merge(users[["user_id", "register_date"]], on="user_id", how="left", validate="many_to_one")
    merged["day_diff"] = (merged["active_date"] - merged["register_date"]).dt.days
    n = len(users)
    expected = {
        f"d{d}": merged.loc[merged["day_diff"].eq(d), "user_id"].nunique() / n
        for d in (1, 7, 14, 30)
    }
    expect(set(answer) == set(expected), "字典需要且只需要 d1、d7、d14、d30 四个键。")
    for k, v in expected.items():
        expect_close(answer[k], v, tol=1e-5, what=k)


@register("7-2.3", title="各渠道 7 日留存率对比", hint="先算每个渠道的注册人数 users，再算 day_diff == 7 的唯一活跃用户数 d7_retained，d7_rate = d7_retained / users，按 d7_rate 降序。")
def check_channel_d7(answer):
    users = load("app/app_users.csv", parse_dates=["register_date"])
    active = load("app/app_active.csv", parse_dates=["active_date"])
    merged = active.merge(users[["user_id", "register_date", "channel"]], on="user_id", how="left", validate="many_to_one")
    merged["day_diff"] = (merged["active_date"] - merged["register_date"]).dt.days
    base = users.groupby("channel", as_index=False).agg(users=("user_id", "nunique"))
    d7 = merged.loc[merged["day_diff"].eq(7)].groupby("channel", as_index=False).agg(d7_retained=("user_id", "nunique"))
    expected = base.merge(d7, on="channel", how="left")
    expected["d7_retained"] = expected["d7_retained"].fillna(0).astype(int)
    expected["d7_rate"] = expected["d7_retained"] / expected["users"]
    expected = expected.sort_values("d7_rate", ascending=False).reset_index(drop=True)
    expect_df(answer, expected, "各渠道7日留存表")


@register("7-2.4", title="按注册月份制作同期群留存表", hint="提取 register_month = register_date.dt.strftime('%Y-%m')，按月统计 users 以及 d1、d7、d30 留存率，按 register_month 升序。")
def check_monthly_cohort(answer):
    users = load("app/app_users.csv", parse_dates=["register_date"])
    users["register_month"] = users["register_date"].dt.strftime("%Y-%m")
    active = load("app/app_active.csv", parse_dates=["active_date"])
    merged = active.merge(users[["user_id", "register_date", "register_month"]], on="user_id", how="left", validate="many_to_one")
    merged["day_diff"] = (merged["active_date"] - merged["register_date"]).dt.days
    base = users.groupby("register_month", as_index=False).agg(users=("user_id", "nunique"))
    for d in (1, 7, 30):
        sub = merged.loc[merged["day_diff"].eq(d)].groupby("register_month", as_index=False).agg(**{f"n{d}": ("user_id", "nunique")})
        base = base.merge(sub, on="register_month", how="left")
        base[f"d{d}"] = base[f"n{d}"].fillna(0) / base["users"]
    expected = base[["register_month", "users", "d1", "d7", "d30"]].sort_values("register_month").reset_index(drop=True)
    expect_df(answer, expected, "月度同期群留存表")
