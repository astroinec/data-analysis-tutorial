# 6-2 SQL 分组聚合

请选择 `Python (da-course)` 内核，从 `notebooks/` 打开。本课练习 `GROUP BY`、`COUNT / SUM / AVG`、`HAVING` 以及面试最常见的 `CASE WHEN` 条件聚合。

```python
import sys
sys.path.insert(0, "..")
from dacheck import check, hint, setup_chinese_font
import sqlite3
import pandas as pd

conn = sqlite3.connect("../data/shop/shop.db")

def q(sql):
    return pd.read_sql_query(sql, conn)
```

+++
## 1. GROUP BY 与常用聚合函数

`COUNT(*)` 数所有行，`COUNT(rating)` 只数非空评分，`COUNT(DISTINCT customer_id)` 数去重购买人数。

```python
q("""
SELECT
    platform,
    COUNT(*) AS order_count,
    COUNT(rating) AS rated_orders,
    COUNT(DISTINCT customer_id) AS buyers,
    ROUND(SUM(pay_amount), 2) AS revenue
FROM orders
WHERE status = '已完成'
GROUP BY platform
ORDER BY revenue DESC
""")
```

+++
## 2. CASE WHEN 条件聚合：一条 SQL 算退款率

SQLite 中两个整数相除会截断为整数（如 `198 / 4497 = 0`），乘以 `1.0` 可转为浮点除法。

```python
q("""
SELECT
    platform,
    COUNT(*) AS all_orders,
    SUM(CASE WHEN status = '已退款' THEN 1 ELSE 0 END) AS refunds,
    ROUND(SUM(CASE WHEN status = '已退款' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS refund_pct
FROM orders
GROUP BY platform
ORDER BY platform ASC
""")
```

+++
## 3. WHERE 与 HAVING 的区别

`WHERE` 在分组**前**过滤明细行（例如只保留 `status = '已完成'`）；`HAVING` 在分组**后**过滤聚合结果（例如只保留月销售额 `>= 160000` 的月份）。

```python
q("""
SELECT
    substr(order_time, 1, 7) AS month,
    COUNT(*) AS orders,
    ROUND(SUM(pay_amount), 2) AS revenue
FROM orders
WHERE status = '已完成'
GROUP BY month
HAVING SUM(pay_amount) >= 160000
ORDER BY month ASC
""")
```

+++
## 练习 6-2.1 各平台已完成订单汇总

筛选 `status = '已完成'`，按 `platform` 分组，输出 `platform, order_count, revenue, aov`（不提前 ROUND），按 `revenue` 降序。

```python
### BEGIN SOLUTION
ans_6_2_1 = q("""
SELECT
    platform,
    COUNT(*) AS order_count,
    SUM(pay_amount) AS revenue,
    AVG(pay_amount) AS aov
FROM orders
WHERE status = '已完成'
GROUP BY platform
ORDER BY revenue DESC
""")
### STUDENT
ans_6_2_1 = ...
### END SOLUTION
check("6-2.1", ans_6_2_1)
```

+++
## 练习 6-2.2 单条 SQL 计算各平台退款率

使用全部订单（不要用 `WHERE` 过滤掉退款），输出 `platform, all_orders, refunds, refund_rate`（0~1 小数，记得 `* 1.0`），按 `platform` 升序。

```python
### BEGIN SOLUTION
ans_6_2_2 = q("""
SELECT
    platform,
    COUNT(*) AS all_orders,
    SUM(CASE WHEN status = '已退款' THEN 1 ELSE 0 END) AS refunds,
    SUM(CASE WHEN status = '已退款' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS refund_rate
FROM orders
GROUP BY platform
ORDER BY platform ASC
""")
### STUDENT
ans_6_2_2 = ...
### END SOLUTION
check("6-2.2", ans_6_2_2)
```

+++
## 练习 6-2.3 用 HAVING 筛选月销售额不低于 16 万元的月份

仅统计已完成订单，提取 `substr(order_time, 1, 7) AS month`，输出 `month, revenue`，筛选 `SUM(pay_amount) >= 160000`，按 `month` 升序。

```python
### BEGIN SOLUTION
ans_6_2_3 = q("""
SELECT
    substr(order_time, 1, 7) AS month,
    SUM(pay_amount) AS revenue
FROM orders
WHERE status = '已完成'
GROUP BY month
HAVING SUM(pay_amount) >= 160000
ORDER BY month ASC
""")
### STUDENT
ans_6_2_3 = ...
### END SOLUTION
check("6-2.3", ans_6_2_3)
```

+++
## 练习 6-2.4 找出累计消费不低于 1500 元的高消费客户

仅统计已完成订单，按 `customer_id` 分组，输出 `customer_id, order_count, total_spend`，筛选 `HAVING SUM(pay_amount) >= 1500`，按 `total_spend` 降序、`customer_id` 升序。

```python
### BEGIN SOLUTION
ans_6_2_4 = q("""
SELECT
    customer_id,
    COUNT(*) AS order_count,
    SUM(pay_amount) AS total_spend
FROM orders
WHERE status = '已完成'
GROUP BY customer_id
HAVING SUM(pay_amount) >= 1500
ORDER BY total_spend DESC, customer_id ASC
""")
### STUDENT
ans_6_2_4 = ...
### END SOLUTION
check("6-2.4", ans_6_2_4)
```
