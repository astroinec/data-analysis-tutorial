"""6-3 SQL 多表连接、CTE 与窗口函数。"""
import sqlite3
import pandas as pd

from dacheck.core import DATA_DIR, register, expect_equal, expect_df


def _query(sql: str) -> pd.DataFrame:
    with sqlite3.connect(DATA_DIR / "shop" / "shop.db") as conn:
        return pd.read_sql_query(sql, conn)


@register("6-3.1", title="多表连接统计各品类已完成销售额", hint="orders o LEFT JOIN products p ON o.product_id = p.product_id，WHERE o.status = '已完成'，按 p.category 分组，按 revenue 降序。")
def check_category_join(answer):
    expected = _query(
        "SELECT p.category, COUNT(DISTINCT o.order_id) AS orders, SUM(o.pay_amount) AS revenue "
        "FROM orders o LEFT JOIN products p ON o.product_id = p.product_id "
        "WHERE o.status = '已完成' GROUP BY p.category ORDER BY revenue DESC"
    )
    expect_df(answer, expected, "品类已完成销售额")


@register("6-3.2", title="找出没有已完成订单的注册客户数", hint="customers c LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status = '已完成'，再 WHERE o.order_id IS NULL。")
def check_zero_order_customers(answer):
    expected = int(_query(
        "SELECT COUNT(*) AS n FROM customers c "
        "LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status = '已完成' "
        "WHERE o.order_id IS NULL"
    ).iat[0, 0])
    expect_equal(answer, expected, "无已完成订单的注册客户数")


@register("6-3.3", title="用 CTE 对齐月度销售与月度目标", hint="WITH monthly AS (...) 先算每月已完成 revenue，再 LEFT JOIN monthly_targets t ON m.month = t.month，计算 achievement = revenue * 1.0 / target_gmv，按 month 升序。")
def check_cte_targets(answer):
    expected = _query(
        "WITH monthly AS ("
        "  SELECT substr(order_time, 1, 7) AS month, SUM(pay_amount) AS revenue "
        "  FROM orders WHERE status = '已完成' GROUP BY month"
        ") "
        "SELECT m.month, m.revenue, t.target_gmv, m.revenue * 1.0 / t.target_gmv AS achievement "
        "FROM monthly m LEFT JOIN monthly_targets t ON m.month = t.month ORDER BY m.month ASC"
    )
    expect_df(answer, expected, "月度目标达成表")


@register("6-3.4", title="窗口函数找每个品类的销冠商品", hint="先按 category、product_name 汇总已完成销售额，再用 ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC) AS rn 取 rn = 1，按 category 升序。")
def check_top_product_per_category(answer):
    expected = _query(
        "WITH prod_rev AS ("
        "  SELECT p.category, p.product_name, SUM(o.pay_amount) AS revenue "
        "  FROM orders o LEFT JOIN products p ON o.product_id = p.product_id "
        "  WHERE o.status = '已完成' GROUP BY p.category, p.product_name"
        "), ranked AS ("
        "  SELECT category, product_name, revenue, "
        "         ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC) AS rn "
        "  FROM prod_rev"
        ") "
        "SELECT category, product_name, revenue FROM ranked WHERE rn = 1 ORDER BY category ASC"
    )
    expect_df(answer, expected, "各品类销冠商品")
