# 6-3 SQL 多表连接、CTE 与窗口函数

请选择 `Python (da-course)` 内核，从 `notebooks/` 打开。本课在 `shop.db` 上练习 `LEFT JOIN`、CTE（`WITH ... AS`）与窗口函数 `ROW_NUMBER()`。

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
## 1. LEFT JOIN 给订单补上商品品类

```python
q("""
SELECT
    p.category,
    COUNT(DISTINCT o.order_id) AS orders,
    ROUND(SUM(o.pay_amount), 2) AS revenue
FROM orders o
LEFT JOIN products p ON o.product_id = p.product_id
WHERE o.status = '已完成'
GROUP BY p.category
ORDER BY revenue DESC
""")
```

+++
## 2. LEFT JOIN 的经典陷阱：ON 条件 vs WHERE 条件

想找“注册了但没有已完成订单的客户”，必须把 `o.status = '已完成'` 写在 `LEFT JOIN ... ON` 里面，再在 `WHERE` 中筛选 `o.order_id IS NULL`。如果把 `o.status = '已完成'` 写进 `WHERE`，就会把没匹配上的 `NULL` 行全滤掉，退化成 `INNER JOIN`。

```python
q("""
SELECT COUNT(*) AS zero_completed_customers
FROM customers c
LEFT JOIN orders o
    ON c.customer_id = o.customer_id AND o.status = '已完成'
WHERE o.order_id IS NULL
""")
```

+++
## 3. CTE（WITH）与窗口函数 ROW_NUMBER()

CTE 把复杂查询拆成清晰的分步积木；窗口函数在不折叠行的前提下完成分组排名。

```python
q("""
WITH prod_rev AS (
    SELECT p.category, p.product_name, SUM(o.pay_amount) AS revenue
    FROM orders o
    LEFT JOIN products p ON o.product_id = p.product_id
    WHERE o.status = '已完成'
    GROUP BY p.category, p.product_name
),
ranked AS (
    SELECT
        category,
        product_name,
        ROUND(revenue, 2) AS revenue,
        ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC) AS rn
    FROM prod_rev
)
SELECT category, product_name, revenue
FROM ranked
WHERE rn = 1
ORDER BY category ASC
""")
```

+++
## 练习 6-3.1 多表连接统计各品类已完成销售额

`orders` 左连接 `products`，仅保留已完成订单，输出 `category, orders, revenue`（不提前 ROUND），按 `revenue` 降序。

```python
### BEGIN SOLUTION
ans_6_3_1 = q("""
SELECT
    p.category,
    COUNT(DISTINCT o.order_id) AS orders,
    SUM(o.pay_amount) AS revenue
FROM orders o
LEFT JOIN products p ON o.product_id = p.product_id
WHERE o.status = '已完成'
GROUP BY p.category
ORDER BY revenue DESC
""")
### STUDENT
ans_6_3_1 = ...
### END SOLUTION
check("6-3.1", ans_6_3_1)
```

+++
## 练习 6-3.2 找出没有已完成订单的注册客户数

用 `customers LEFT JOIN orders`（把 `o.status = '已完成'` 写在 `ON` 中），统计 `o.order_id IS NULL` 的客户数量（整数）。

```python
### BEGIN SOLUTION
ans_6_3_2 = int(q("""
SELECT COUNT(*) AS n
FROM customers c
LEFT JOIN orders o
    ON c.customer_id = o.customer_id AND o.status = '已完成'
WHERE o.order_id IS NULL
""").iat[0, 0])
### STUDENT
ans_6_3_2 = ...
### END SOLUTION
check("6-3.2", ans_6_3_2)
```

+++
## 练习 6-3.3 用 CTE 对齐月度销售与月度目标

先用 CTE 计算每月已完成 `revenue`，再左连接 `monthly_targets`，输出 `month, revenue, target_gmv, achievement`（`revenue * 1.0 / target_gmv`），按 `month` 升序。

```python
### BEGIN SOLUTION
ans_6_3_3 = q("""
WITH monthly AS (
    SELECT substr(order_time, 1, 7) AS month, SUM(pay_amount) AS revenue
    FROM orders
    WHERE status = '已完成'
    GROUP BY month
)
SELECT
    m.month,
    m.revenue,
    t.target_gmv,
    m.revenue * 1.0 / t.target_gmv AS achievement
FROM monthly m
LEFT JOIN monthly_targets t ON m.month = t.month
ORDER BY m.month ASC
""")
### STUDENT
ans_6_3_3 = ...
### END SOLUTION
check("6-3.3", ans_6_3_3)
```

+++
## 练习 6-3.4 用窗口函数找出每个品类的销冠商品

统计每个商品的已完成销售额，用 `ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC)` 选出每个品类第 1 名，输出 `category, product_name, revenue`（不提前 ROUND），按 `category` 升序。

```python
### BEGIN SOLUTION
ans_6_3_4 = q("""
WITH prod_rev AS (
    SELECT p.category, p.product_name, SUM(o.pay_amount) AS revenue
    FROM orders o
    LEFT JOIN products p ON o.product_id = p.product_id
    WHERE o.status = '已完成'
    GROUP BY p.category, p.product_name
),
ranked AS (
    SELECT
        category,
        product_name,
        revenue,
        ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC) AS rn
    FROM prod_rev
)
SELECT category, product_name, revenue
FROM ranked
WHERE rn = 1
ORDER BY category ASC
""")
### STUDENT
ans_6_3_4 = ...
### END SOLUTION
check("6-3.4", ans_6_3_4)
```
