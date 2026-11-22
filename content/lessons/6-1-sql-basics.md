---
summary: 零安装用 Python 内置 SQLite 上手 SQL，掌握 SELECT、WHERE、IN、BETWEEN、IS NULL、ORDER BY 与 LIMIT。
prereq: 已完成阶段 2，熟悉表格的列、筛选与排序概念
---

:::goal 本课可验证目标
- 理解数据库表与 CSV 的关系，会用 `sqlite3` + `pd.read_sql_query` 在本地运行 SQL。
- 用 `SELECT / FROM / WHERE / ORDER BY / LIMIT` 精准取数，不随意 `SELECT *`。
- 正确使用 `AND / OR / IN / BETWEEN / IS NULL / COUNT(DISTINCT ...)` 组合条件。
- 看懂 SQL 语句与 pandas 筛选排序的一一对应关系。
:::

打开 [6-1 练习本](../../notebooks/6-1_sql_basics.ipynb)，选择 `Python (da-course)` 内核。本课连接的数据库 `data/shop/shop.db` 已随包生成，里面装的就是文创店四张模拟表（`orders`、`products`、`customers`、`monthly_targets`），无需另外装 MySQL 或配置服务器。

## 1. 为什么会 pandas 还要学 SQL？

在公司里，数据通常不会以几兆的 CSV 直接躺在你桌面，而是存在百万、亿级行的数据库或数据仓库里。**SQL（结构化查询语言）**负责把你要的那一小块数据从数据库“取出来”，再交给 Python 或 BI 工具做深度分析与画图。几乎所有数据分析岗位的笔试和一面，第一题都是 SQL。

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect("../data/shop/shop.db")
def q(sql):
    return pd.read_sql_query(sql, conn)

q("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name")
```

## 2. SELECT、WHERE、ORDER BY 与 LIMIT

:::df SQL 与 pandas 对照表
| 想做什么 | SQL 写法 | pandas 写法 |
|---|---|---|
| 选指定列 | `SELECT product_id, price FROM products` | `products[["product_id", "price"]]` |
| 条件筛选 | `WHERE category = '文具' AND price >= 30` | `products.loc[(...) & (...)]` |
| 枚举筛选 | `WHERE city_tier IN ('一线', '新一线')` | `customers["city_tier"].isin([...])` |
| 区间筛选 | `WHERE age BETWEEN 20 AND 30` | `customers["age"].between(20, 30)` |
| 缺失判断 | `WHERE rating IS NULL` | `orders["rating"].isna()` |
| 排序与前 N 行 | `ORDER BY pay_amount DESC LIMIT 10` | `.sort_values("pay_amount", ascending=False).head(10)` |
:::

```sql
SELECT product_id, product_name, category, price
FROM products
WHERE category = '书籍'
ORDER BY price DESC
LIMIT 5;
```

:::warn SQL 的三个高频新手坑
1. **字符串用单引号** `'已完成'`，不要漏写引号，也不要把等号写成 Python 的 `==`（SQL 相等比较是单个 `=`）。
2. **判断空值用 `IS NULL`**，千万不要写 `rating = NULL`（在 SQL 里任何值与 NULL 做 `=` 比较结果都不是 True，会返回 0 行）。
3. **线上慎用 `SELECT *`**：大表可能有上百列，显式写出需要的列名既省带宽，也防止表结构变动导致脚本出错。
:::

## 3. 去重计数：COUNT(*) vs COUNT(DISTINCT col)

```sql
SELECT COUNT(*) AS total_rows,
       COUNT(rating) AS rated_rows,
       COUNT(DISTINCT customer_id) AS unique_buyers
FROM orders
WHERE status = '已完成';
```

在 13996 条已完成订单中，`COUNT(*)` 为 13996，`COUNT(rating)` 为 8146（自动跳过 5850 条 `NULL` 评分），`COUNT(DISTINCT customer_id)` 为 2427 位购买客户。

:::quiz SQL 空值筛选
想查 `orders` 表中“已完成但尚未评分”的订单数，下面哪条 `WHERE` 条件是正确的？
- [ ] `WHERE status == '已完成' AND rating == NULL`
- [ ] `WHERE status = '已完成' AND rating = NULL`
- [x] `WHERE status = '已完成' AND rating IS NULL`
---
SQL 相等判断用单等号 `=`，空值判断必须用 `IS NULL`。
:::

## 4. 四道独立练习

:::try 6-1.1 筛选文具类商品并按价格降序
查询 `products` 中 `category = '文具'` 的 `product_id, product_name, price`，按 `price` 降序。
:::fold 参考答案
```sql
SELECT product_id, product_name, price
FROM products
WHERE category = '文具'
ORDER BY price DESC
```
共返回 8 个文具商品。
:::
:::

:::try 6-1.2 淘宝大额已完成订单前 10 笔
查询 `orders` 中 `status = '已完成'`、`platform = '淘宝'`、`pay_amount >= 300` 的 `order_id, order_time, pay_amount`，按 `pay_amount DESC, order_id ASC`，取前 10 行。
:::fold 参考答案
```sql
SELECT order_id, order_time, pay_amount
FROM orders
WHERE status = '已完成' AND platform = '淘宝' AND pay_amount >= 300
ORDER BY pay_amount DESC, order_id ASC
LIMIT 10
```
:::
:::

:::try 6-1.3 统计未评分的已完成订单数
返回 `status = '已完成'` 且 `rating IS NULL` 的订单整数数量。
:::fold 参考答案
```python
ans_6_1_3 = int(q("SELECT COUNT(*) AS n FROM orders WHERE status = '已完成' AND rating IS NULL").iat[0, 0])
```
实算：5850 笔。
:::
:::

:::try 6-1.4 一线与新一线 20～30 岁注册客户数
查询 `customers` 中 `city_tier IN ('一线', '新一线')` 且 `age BETWEEN 20 AND 30` 的 `COUNT(DISTINCT customer_id)`（整数）。
:::fold 参考答案
```python
ans_6_1_4 = int(q("""
SELECT COUNT(DISTINCT customer_id) AS n FROM customers
WHERE city_tier IN ('一线', '新一线') AND age BETWEEN 20 AND 30
""").iat[0, 0])
```
实算：1430 人。
:::
:::

## 常见问题与求职用途

| 问题 | 纠正路径 |
|---|---|
| `OperationalError: no such column` | 检查列名拼写，或先查 `PRAGMA table_info(orders)` 核对表结构 |
| `AND` 和 `OR` 混用时结果偏多 | `AND` 优先级高于 `OR`，只要混用就一定给 `OR` 加括号 |
| `BETWEEN 20 AND 30` 是否包含边界？ | 在 SQL 中 `BETWEEN` 两端都包含（即 `>= 20 AND <= 30`） |

:::job 面试加分表达
“写查询前先确认主键与时间字段，按需只选必要列，并把状态过滤和空值处理明确写进 WHERE，避免把未评分或退款记录误算进核心指标。”
:::

:::checklist 本课验收
- [ ] 我能用 `sqlite3` + `pd.read_sql_query` 执行本地 SQL 查询。
- [ ] 我知道 SQL 用单等号 `=`、单引号字符串和 `IS NULL`。
- [ ] 我能区分 `COUNT(*)`、`COUNT(col)` 和 `COUNT(DISTINCT col)`。
- [ ] 练习本 6-1.1 ～ 6-1.4 四题全部通过检查。
:::

下一课：[SQL 分组聚合](lesson:6-2)。
