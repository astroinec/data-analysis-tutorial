---
summary: 掌握 LEFT JOIN 与 INNER JOIN、避免 ON/WHERE 混用陷阱，并用 CTE（WITH）与窗口函数 ROW_NUMBER() 解决分组 Top N 问题。
prereq: 已完成第 6-2 课，会写 GROUP BY 与 HAVING
---

:::goal 本课可验证目标
- 用 `LEFT JOIN` 把 `orders` 与 `products`、`monthly_targets` 等多张表正确关联。
- 说清 `LEFT JOIN` 中把右表过滤条件写在 `ON` 与写在 `WHERE` 的本质区别。
- 用 CTE（`WITH ... AS (...)`）把多步分析拆成可读、易调试的模块。
- 用窗口函数 `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)` 解决面试必考的“每组 Top N”问题。
:::

打开 [6-3 练习本](../../notebooks/6-3_sql_join.ipynb)，选择 `Python (da-course)` 内核。

## 1. LEFT JOIN vs INNER JOIN：优先保留主表不丢单

给订单补商品品类时，用 `orders o LEFT JOIN products p ON o.product_id = p.product_id`，并始终给表起短别名（`o`、`p`、`c`），避免同名列冲突。

## 2. 面试最爱考的陷阱：LEFT JOIN 时条件放 ON 还是 WHERE？

假设产品经理问：“注册了 3000 个客户，有多少人**从来没有已完成订单**？”

:::compare 找“0 笔已完成订单的客户”
:::bad 把 `o.status = '已完成'` 写在 `WHERE` 里
```sql
SELECT COUNT(*)
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.status = '已完成' AND o.order_id IS NULL;
```
结果永远是 **0**！因为没下过单的客户连接后 `o.status` 是 `NULL`，`NULL = '已完成'` 不成立，直接被 `WHERE` 过滤掉了，等价于把 `LEFT JOIN` 强行变成了 `INNER JOIN`。
:::
:::good 把右表筛选写在 `ON` 里，再在 `WHERE` 找 `IS NULL`
```sql
SELECT COUNT(*) AS n
FROM customers c
LEFT JOIN orders o
    ON c.customer_id = o.customer_id AND o.status = '已完成'
WHERE o.order_id IS NULL;
```
先只连接“已完成订单”，连接不上的客户右表全为 `NULL`，再用 `WHERE o.order_id IS NULL` 精准找出 **573** 位未成交客户（核对：3000 − 2427 = 573！）。
:::
:::

## 3. CTE（WITH）：告别层层嵌套的“洋葱子查询”

当需要先算月销售额、再和月目标表对齐求达成率时，用 `WITH` 定义一个清晰的临时结果集（CTE）：

```sql
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
ORDER BY m.month ASC;
```

## 4. 窗口函数入门：每组取 Top 1（销冠商品）

`GROUP BY` 会把多行折叠成一行；**窗口函数**（`OVER (...)`）则保留每一行，同时按 `PARTITION BY`（分组）和 `ORDER BY`（排序）给每行打上排名号或累计值。

```sql
WITH prod_rev AS (
    SELECT p.category, p.product_name, SUM(o.pay_amount) AS revenue
    FROM orders o
    LEFT JOIN products p ON o.product_id = p.product_id
    WHERE o.status = '已完成'
    GROUP BY p.category, p.product_name
),
ranked AS (
    SELECT category, product_name, revenue,
           ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC) AS rn
    FROM prod_rev
)
SELECT category, product_name, revenue
FROM ranked
WHERE rn = 1
ORDER BY category ASC;
```

:::quiz 窗口函数与 GROUP BY 的区别
为什么求“每个品类销售额最高的商品名称”时，通常用 CTE + `ROW_NUMBER()` 而不是直接 `SELECT category, product_name, MAX(revenue) ... GROUP BY category`？
- [ ] `MAX()` 不能用在小数上
- [x] 直接 `GROUP BY category` 无法可靠保证 `product_name` 与最大销售额一一对应，用窗口函数排序取 `rn = 1` 既标准又可扩展到 Top 3
- [ ] SQL 不支持同时使用 `GROUP BY` 和 `MAX`
---
窗口函数取每组 Top N 是标准 SQL 写法，在 SQLite、MySQL 8+、PostgreSQL、Hive、Spark SQL 中完全通用。
:::

## 5. 四道独立练习

:::try 6-3.1 多表连接统计各品类已完成销售额
`orders LEFT JOIN products`，仅保留已完成订单，输出 `category, orders, revenue`（不提前 ROUND），按 `revenue` 降序。
:::fold 参考答案
```sql
SELECT p.category, COUNT(DISTINCT o.order_id) AS orders, SUM(o.pay_amount) AS revenue
FROM orders o LEFT JOIN products p ON o.product_id = p.product_id
WHERE o.status = '已完成' GROUP BY p.category ORDER BY revenue DESC
```
:::
:::

:::try 6-3.2 找出没有已完成订单的注册客户数
用 `customers LEFT JOIN orders`（`o.status = '已完成'` 放在 `ON` 中），返回无已完成订单的客户数（整数）。
:::fold 参考答案
```python
ans_6_3_2 = int(q("""
SELECT COUNT(*) AS n FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status = '已完成'
WHERE o.order_id IS NULL
""").iat[0, 0])
```
实算：573 人。
:::
:::

:::try 6-3.3 用 CTE 对齐月度销售与月度目标
输出 `month, revenue, target_gmv, achievement`，按 `month` 升序。
:::fold 参考答案
```sql
WITH monthly AS (
    SELECT substr(order_time, 1, 7) AS month, SUM(pay_amount) AS revenue
    FROM orders WHERE status = '已完成' GROUP BY month
)
SELECT m.month, m.revenue, t.target_gmv, m.revenue * 1.0 / t.target_gmv AS achievement
FROM monthly m LEFT JOIN monthly_targets t ON m.month = t.month ORDER BY m.month ASC
```
:::
:::

:::try 6-3.4 用窗口函数找出每个品类的销冠商品
用 `ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC)` 选出每个品类第 1 名，输出 `category, product_name, revenue`，按 `category` 升序。
:::fold 参考答案
```sql
WITH prod_rev AS (
    SELECT p.category, p.product_name, SUM(o.pay_amount) AS revenue
    FROM orders o LEFT JOIN products p ON o.product_id = p.product_id
    WHERE o.status = '已完成' GROUP BY p.category, p.product_name
),
ranked AS (
    SELECT category, product_name, revenue,
           ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC) AS rn
    FROM prod_rev
)
SELECT category, product_name, revenue FROM ranked WHERE rn = 1 ORDER BY category ASC
```
:::
:::

## 常见问题与求职用途

| 问题 | 纠正路径 |
|---|---|
| `ambiguous column name: product_id` | 多表有同名列时必须加表别名前缀，如 `o.product_id` |
| `WHERE rn = 1` 直接写在含窗口函数的同一层报错 | 窗口函数在 `WHERE` 之后执行，必须先包一层 CTE 或子查询再在外部 `WHERE rn = 1` |
| 多表连接后总金额莫名变大 | 检查右表连接键是否唯一；多对多连接会造成行膨胀 |

:::job 面试加分表达
“写复杂取数需求时，我习惯用 CTE 分层拆解：第一层做口径过滤与连接，第二层做聚合，第三层用窗口函数做排名或累计占比，既方便同事 review，也方便逐层对账行数。”
:::

:::checklist 本课验收
- [ ] 我能解释 `LEFT JOIN` 中右表条件放在 `ON` 和 `WHERE` 的区别。
- [ ] 我会用 `WITH`（CTE）组织多步骤 SQL。
- [ ] 我会用 `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)` 求每组 Top N。
- [ ] 练习本 6-3.1 ～ 6-3.4 四题全部通过检查。
:::

下一课：[进入阶段 7：指标体系与拆解思路](lesson:7-1)。
