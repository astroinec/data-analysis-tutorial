"""8-2 面试高频题（SQL + 业务排查 + 实验分析演练）。"""
import sqlite3
import pandas as pd

from dacheck.core import DATA_DIR, register, load, expect, expect_type, expect_equal, expect_close, expect_df


def _query(sql: str) -> pd.DataFrame:
    with sqlite3.connect(DATA_DIR / "shop" / "shop.db") as conn:
        return pd.read_sql_query(sql, conn)


@register("8-2.1", title="面试 SQL 1：各获客渠道注册到下单转化率", hint="customers c LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status = '已完成'，按 c.channel 分组统计 COUNT(DISTINCT c.customer_id) AS registered、COUNT(DISTINCT o.customer_id) AS buyers、buyers * 1.0 / registered AS conv_rate，按 conv_rate 降序。")
def check_interview_sql1(answer):
    expected = _query(
        "SELECT c.channel, "
        "COUNT(DISTINCT c.customer_id) AS registered, "
        "COUNT(DISTINCT o.customer_id) AS buyers, "
        "COUNT(DISTINCT o.customer_id) * 1.0 / COUNT(DISTINCT c.customer_id) AS conv_rate "
        "FROM customers c "
        "LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status = '已完成' "
        "GROUP BY c.channel ORDER BY conv_rate DESC"
    )
    expect_df(answer, expected, "各渠道下单转化率")


@register("8-2.2", title="面试 SQL 2：月度销售额与年内累计销售额", hint="先用 CTE 算每月已完成 revenue，再用 SUM(revenue) OVER (ORDER BY month) AS cum_revenue，按 month 升序。")
def check_interview_sql2(answer):
    expected = _query(
        "WITH m AS ("
        "  SELECT substr(order_time, 1, 7) AS month, SUM(pay_amount) AS revenue "
        "  FROM orders WHERE status = '已完成' GROUP BY month"
        ") "
        "SELECT month, revenue, SUM(revenue) OVER (ORDER BY month) AS cum_revenue "
        "FROM m ORDER BY month ASC"
    )
    expect_df(answer, expected, "月度累计销售额")


@register("8-2.3", title="面试业务题：定位试看到点击付费转化最低的渠道", hint="将 app_events 与 app_users 合并，按 channel 计算 click_pay 唯一用户数 / start_trial 唯一用户数，找出最低渠道名 lowest_channel 和转化率 lowest_rate。")
def check_interview_biz(answer):
    expect_type(answer, dict)
    eu = load("app/app_events.csv").merge(load("app/app_users.csv")[["user_id", "channel"]], on="user_id", how="left")
    rates = {}
    for ch, g in eu.groupby("channel"):
        t = g.loc[g["event_name"].eq("start_trial"), "user_id"].nunique()
        c = g.loc[g["event_name"].eq("click_pay"), "user_id"].nunique()
        rates[ch] = c / t
    worst_ch = min(rates, key=rates.get)
    expect(set(answer) == {"lowest_channel", "lowest_rate"}, "字典需要且只需要 lowest_channel、lowest_rate 两个键。")
    expect_equal(answer["lowest_channel"], worst_ch, "lowest_channel")
    expect_close(answer["lowest_rate"], rates[worst_ch], tol=1e-5, what="lowest_rate")


@register("8-2.4", title="面试实验题：新客与老客转化率绝对提升", hint="在 ab_experiment.csv 中分别对 is_new_user == 1 和 0 计算 treatment 转化率减去 control 转化率，填入 new_lift 和 old_lift。")
def check_interview_ab(answer):
    expect_type(answer, dict)
    ab = load("abtest/ab_experiment.csv")
    g = ab.groupby(["is_new_user", "group"])["converted"].mean().unstack()
    expected = {
        "new_lift": float(g.loc[1, "treatment"] - g.loc[1, "control"]),
        "old_lift": float(g.loc[0, "treatment"] - g.loc[0, "control"]),
    }
    expect(set(answer) == set(expected), "字典需要且只需要 new_lift、old_lift 两个键。")
    for k, v in expected.items():
        expect_close(answer[k], v, tol=1e-5, what=k)
