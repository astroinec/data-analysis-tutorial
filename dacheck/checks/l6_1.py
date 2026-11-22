"""6-1 SQL 基础：SELECT 查询与筛选。"""
import sqlite3
import pandas as pd

from dacheck.core import DATA_DIR, register, expect_equal, expect_df


def _query(sql: str) -> pd.DataFrame:
    with sqlite3.connect(DATA_DIR / "shop" / "shop.db") as conn:
        return pd.read_sql_query(sql, conn)


@register("6-1.1", title="筛选文具类商品并按价格降序", hint="SELECT product_id, product_name, price FROM products WHERE category = '文具' ORDER BY price DESC")
def check_stationery(answer):
    expected = _query(
        "SELECT product_id, product_name, price FROM products "
        "WHERE category = '文具' ORDER BY price DESC"
    )
    expect_df(answer, expected, "文具商品表")


@register("6-1.2", title="淘宝大额已完成订单前 10 笔", hint="WHERE status = '已完成' AND platform = '淘宝' AND pay_amount >= 300，ORDER BY pay_amount DESC, order_id ASC LIMIT 10。")
def check_taobao_top10(answer):
    expected = _query(
        "SELECT order_id, order_time, pay_amount FROM orders "
        "WHERE status = '已完成' AND platform = '淘宝' AND pay_amount >= 300 "
        "ORDER BY pay_amount DESC, order_id ASC LIMIT 10"
    )
    expect_df(answer, expected, "淘宝大额已完成订单前10笔")


@register("6-1.3", title="未评分的已完成订单数", hint="用 WHERE status = '已完成' AND rating IS NULL，用 COUNT(*) 取整数值（如 df.iat[0, 0]）。")
def check_null_rating(answer):
    expected = int(_query(
        "SELECT COUNT(*) AS n FROM orders WHERE status = '已完成' AND rating IS NULL"
    ).iat[0, 0])
    expect_equal(answer, expected, "未评分已完成订单数")


@register("6-1.4", title="一线与新一线 20~30 岁注册客户数", hint="WHERE city_tier IN ('一线', '新一线') AND age BETWEEN 20 AND 30，统计 COUNT(DISTINCT customer_id)。")
def check_young_tier1(answer):
    expected = int(_query(
        "SELECT COUNT(DISTINCT customer_id) AS n FROM customers "
        "WHERE city_tier IN ('一线', '新一线') AND age BETWEEN 20 AND 30"
    ).iat[0, 0])
    expect_equal(answer, expected, "符合条件的注册客户数")
