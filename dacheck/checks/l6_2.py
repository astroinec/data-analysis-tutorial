"""6-2 SQL 分组聚合。"""
import sqlite3
import pandas as pd

from dacheck.core import DATA_DIR, register, expect_df


def _query(sql: str) -> pd.DataFrame:
    with sqlite3.connect(DATA_DIR / "shop" / "shop.db") as conn:
        return pd.read_sql_query(sql, conn)


@register("6-2.1", title="各平台已完成订单汇总", hint="WHERE status = '已完成'，按 platform 分组，COUNT(*) AS order_count, SUM(pay_amount) AS revenue, AVG(pay_amount) AS aov，按 revenue DESC。")
def check_platform_agg(answer):
    expected = _query(
        "SELECT platform, COUNT(*) AS order_count, SUM(pay_amount) AS revenue, AVG(pay_amount) AS aov "
        "FROM orders WHERE status = '已完成' GROUP BY platform ORDER BY revenue DESC"
    )
    expect_df(answer, expected, "各平台已完成订单汇总")


@register("6-2.2", title="单条 SQL 计算各平台退款率", hint="不要在 WHERE 删掉退款订单！用 SUM(CASE WHEN status = '已退款' THEN 1 ELSE 0 END) 算 refunds，再 * 1.0 / COUNT(*) 算 refund_rate，按 platform 升序。")
def check_platform_refund(answer):
    expected = _query(
        "SELECT platform, "
        "COUNT(*) AS all_orders, "
        "SUM(CASE WHEN status = '已退款' THEN 1 ELSE 0 END) AS refunds, "
        "SUM(CASE WHEN status = '已退款' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS refund_rate "
        "FROM orders GROUP BY platform ORDER BY platform ASC"
    )
    expect_df(answer, expected, "各平台退款率")


@register("6-2.3", title="筛选月销售额不低于 16 万元的月份", hint="WHERE status = '已完成'，用 substr(order_time, 1, 7) AS month 分组，HAVING SUM(pay_amount) >= 160000，按 month 升序。")
def check_high_months(answer):
    expected = _query(
        "SELECT substr(order_time, 1, 7) AS month, SUM(pay_amount) AS revenue "
        "FROM orders WHERE status = '已完成' "
        "GROUP BY month HAVING SUM(pay_amount) >= 160000 ORDER BY month ASC"
    )
    expect_df(answer, expected, "月销售额>=16万的月份")


@register("6-2.4", title="高消费客户筛选（HAVING）", hint="WHERE status = '已完成'，按 customer_id 分组，HAVING SUM(pay_amount) >= 1500，ORDER BY total_spend DESC, customer_id ASC。")
def check_high_customers(answer):
    expected = _query(
        "SELECT customer_id, COUNT(*) AS order_count, SUM(pay_amount) AS total_spend "
        "FROM orders WHERE status = '已完成' "
        "GROUP BY customer_id HAVING SUM(pay_amount) >= 1500 "
        "ORDER BY total_spend DESC, customer_id ASC"
    )
    expect_df(answer, expected, "高消费客户表")
