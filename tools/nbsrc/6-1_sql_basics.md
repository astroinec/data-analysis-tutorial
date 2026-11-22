# 6-1 SQL 基础：SELECT 查询与筛选

请选择 `Python (da-course)` 内核，从 `notebooks/` 打开。本课使用 Python 自带的 `sqlite3` 直接连接随包数据库 `../data/shop/shop.db`（包含 `orders`、`products`、`customers`、`monthly_targets` 四张表），无需额外安装数据库软件。

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

先看看数据库里有哪些表。

```python
q("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name")
```

+++
## 1. SELECT、WHERE 与 ORDER BY

尽量显式写出需要的列名，不要动辄 `SELECT *`。筛选用 `WHERE`，排序用 `ORDER BY`，限制行数用 `LIMIT`。

```python
q("""
SELECT product_id, product_name, category, price
FROM products
WHERE category = '书籍'
ORDER BY price DESC
LIMIT 5
""")
```

+++
## 2. 多条件、IN、BETWEEN 与 IS NULL

SQL 中判断缺失值必须用 `IS NULL` 或 `IS NOT NULL`，不能写 `= NULL`。

```python
q("""
SELECT order_id, order_time, platform, pay_amount, rating
FROM orders
WHERE status = '已完成'
  AND platform IN ('淘宝', '微信小程序')
  AND pay_amount BETWEEN 200 AND 260
  AND rating IS NULL
ORDER BY pay_amount DESC
LIMIT 5
""")
```

+++
## 练习 6-1.1 筛选文具类商品并按价格降序

用 SQL 查询 `products` 表中 `category = '文具'` 的 `product_id, product_name, price`，按 `price` 降序排列。

```python
### BEGIN SOLUTION
sql_6_1_1 = """
SELECT product_id, product_name, price
FROM products
WHERE category = '文具'
ORDER BY price DESC
"""
ans_6_1_1 = q(sql_6_1_1)
### STUDENT
ans_6_1_1 = ...
### END SOLUTION
check("6-1.1", ans_6_1_1)
```

+++
## 练习 6-1.2 淘宝大额已完成订单前 10 笔

用 SQL 查询 `orders` 表中 `status = '已完成'`、`platform = '淘宝'` 且 `pay_amount >= 300` 的前 10 笔订单（列：`order_id, order_time, pay_amount`），按 `pay_amount` 降序、`order_id` 升序排列。

```python
### BEGIN SOLUTION
sql_6_1_2 = """
SELECT order_id, order_time, pay_amount
FROM orders
WHERE status = '已完成'
  AND platform = '淘宝'
  AND pay_amount >= 300
ORDER BY pay_amount DESC, order_id ASC
LIMIT 10
"""
ans_6_1_2 = q(sql_6_1_2)
### STUDENT
ans_6_1_2 = ...
### END SOLUTION
check("6-1.2", ans_6_1_2)
```

+++
## 练习 6-1.3 统计未评分的已完成订单数

用 SQL 查询 `orders` 表中 `status = '已完成'` 且 `rating IS NULL` 的订单数，取出整数结果交给 `ans_6_1_3`。

```python
### BEGIN SOLUTION
ans_6_1_3 = int(q("""
SELECT COUNT(*) AS n
FROM orders
WHERE status = '已完成' AND rating IS NULL
""").iat[0, 0])
### STUDENT
ans_6_1_3 = ...
### END SOLUTION
check("6-1.3", ans_6_1_3)
```

+++
## 练习 6-1.4 筛选一线与新一线 20~30 岁注册客户数

用 SQL 查询 `customers` 表中 `city_tier IN ('一线', '新一线')` 且 `age BETWEEN 20 AND 30` 的唯一 `customer_id` 数量（整数）。

```python
### BEGIN SOLUTION
ans_6_1_4 = int(q("""
SELECT COUNT(DISTINCT customer_id) AS n
FROM customers
WHERE city_tier IN ('一线', '新一线')
  AND age BETWEEN 20 AND 30
""").iat[0, 0])
### STUDENT
ans_6_1_4 = ...
### END SOLUTION
check("6-1.4", ans_6_1_4)
```
