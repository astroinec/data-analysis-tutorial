---
summary: 掌握 GROUP BY、聚合函数、WHERE 与 HAVING 的执行顺序，以及用 CASE WHEN 在单条 SQL 中计算比率指标。
prereq: 已完成第 6-1 课，会写 SELECT、WHERE 与 ORDER BY
---

:::goal 本课可验证目标
- 用 `GROUP BY` 搭配 `COUNT / SUM / AVG` 汇总各平台、各月与各客户的业务指标。
- 说清 `WHERE`（分组前过滤明细）与 `HAVING`（分组后过滤聚合结果）的区别。
- 用 `SUM(CASE WHEN ... THEN 1 ELSE 0 END)` 在一条 SQL 里同时算出分子与分母（如退款率）。
- 注意 SQLite 整数除法陷阱，用 `* 1.0` 保留小数精度。
:::

打开 [6-2 练习本](../../notebooks/6-2_sql_groupby.ipynb)，选择 `Python (da-course)` 内核。

## 1. SQL 的书写顺序 vs 实际执行顺序

很多初学者把 `HAVING` 和 `WHERE` 写反，是因为没记住数据库引擎的执行顺序：

:::flow 数据库实际执行顺序
1. `FROM`：先找到表
2. `WHERE`：分组前过滤明细行（不能用 SUM/COUNT 等聚合函数）
3. `GROUP BY`：按指定列分堆
4. `HAVING`：分组后过滤聚合结果（可以用 `SUM(pay_amount) >= 160000`）
5. `SELECT`：计算输出列与别名
6. `ORDER BY`：对最终结果排序
7. `LIMIT`：截取前 N 行
:::

## 2. GROUP BY 汇总各平台已完成订单

```sql
SELECT
    platform,
    COUNT(*) AS order_count,
    SUM(pay_amount) AS revenue,
    AVG(pay_amount) AS aov
FROM orders
WHERE status = '已完成'
GROUP BY platform
ORDER BY revenue DESC;
```

:::df 实际查询结果（已完成口径）
| platform | order_count | revenue | aov |
|---|---:|---:|---:|
| 淘宝 | 6442 | 807644.60 | 125.37 |
| 微信小程序 | 4299 | 551636.10 | 128.32 |
| 抖音小店 | 3255 | 425090.40 | 130.60 |
:::

## 3. CASE WHEN 条件聚合：一条 SQL 算退款率

想在一条 SQL 里同时算“总订单数、退款单数、退款率”，**不能在 `WHERE` 里筛掉退款单**，而是用 `CASE WHEN` 给退款行打 1、其余打 0，再 `SUM`：

```sql
SELECT
    platform,
    COUNT(*) AS all_orders,
    SUM(CASE WHEN status = '已退款' THEN 1 ELSE 0 END) AS refunds,
    SUM(CASE WHEN status = '已退款' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS refund_rate
FROM orders
GROUP BY platform
ORDER BY platform ASC;
```

:::warn SQLite 整数除法陷阱
在 SQLite 中，`198 / 4497` 会得到 `0` 而不是 `0.0440`！分子乘以 `1.0`（或用 `CAST(... AS REAL)`）就能转为浮点除法。MySQL 默认返回小数，但养成写 `* 1.0` 的习惯在 SQLite、PostgreSQL、SQL Server 里都能防止截断。
:::

## 4. WHERE vs HAVING：找月销 ≥ 16 万的旺季月份

```sql
SELECT
    substr(order_time, 1, 7) AS month,
    SUM(pay_amount) AS revenue
FROM orders
WHERE status = '已完成'
GROUP BY month
HAVING SUM(pay_amount) >= 160000
ORDER BY month ASC;
```

实测返回 4 个月：`2025-06`（168,320.80 元）、`2025-08`（163,574.30 元）、`2025-11`（229,054.00 元）、`2025-12`（202,855.40 元）。

:::quiz WHERE 与 HAVING 分工
想筛选“已完成订单累计消费不低于 1500 元的客户”，哪句 SQL 写法正确？
- [ ] `WHERE status = '已完成' AND SUM(pay_amount) >= 1500 GROUP BY customer_id`
- [x] `WHERE status = '已完成' GROUP BY customer_id HAVING SUM(pay_amount) >= 1500`
- [ ] `GROUP BY customer_id WHERE status = '已完成' HAVING SUM(pay_amount) >= 1500`
---
状态过滤作用于单行明细，放在 `WHERE`；累计金额过滤作用于分组聚合之后，必须放在 `HAVING`。
:::

## 5. 四道独立练习

:::try 6-2.1 各平台已完成订单汇总
输出 `platform, order_count, revenue, aov`（不提前 ROUND），按 `revenue` 降序。
:::fold 参考答案
```sql
SELECT platform, COUNT(*) AS order_count, SUM(pay_amount) AS revenue, AVG(pay_amount) AS aov
FROM orders WHERE status = '已完成' GROUP BY platform ORDER BY revenue DESC
```
:::
:::

:::try 6-2.2 单条 SQL 计算各平台退款率
输出 `platform, all_orders, refunds, refund_rate`（0～1 小数），按 `platform` 升序。
:::fold 参考答案
```sql
SELECT platform, COUNT(*) AS all_orders,
       SUM(CASE WHEN status = '已退款' THEN 1 ELSE 0 END) AS refunds,
       SUM(CASE WHEN status = '已退款' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS refund_rate
FROM orders GROUP BY platform ORDER BY platform ASC
```
:::
:::

:::try 6-2.3 筛选月销售额不低于 16 万元的月份
用 `substr(order_time, 1, 7) AS month` 分组，仅含已完成订单，用 `HAVING` 筛选 `>= 160000`，按 `month` 升序。
:::fold 参考答案
```sql
SELECT substr(order_time, 1, 7) AS month, SUM(pay_amount) AS revenue
FROM orders WHERE status = '已完成'
GROUP BY month HAVING SUM(pay_amount) >= 160000 ORDER BY month ASC
```
:::
:::

:::try 6-2.4 高消费客户筛选
仅含已完成订单，按 `customer_id` 分组输出 `customer_id, order_count, total_spend`，`HAVING SUM(pay_amount) >= 1500`，按 `total_spend DESC, customer_id ASC`。
:::fold 参考答案
```sql
SELECT customer_id, COUNT(*) AS order_count, SUM(pay_amount) AS total_spend
FROM orders WHERE status = '已完成'
GROUP BY customer_id HAVING SUM(pay_amount) >= 1500
ORDER BY total_spend DESC, customer_id ASC
```
共筛选出 279 位高消费客户。
:::
:::

## 常见问题与求职用途

| 问题 | 纠正路径 |
|---|---|
| `SELECT` 中写了没在 `GROUP BY` 里的普通列 | 严格模式下会报错；非聚合列必须出现在 `GROUP BY` 中 |
| 退款率全算出 0 | 检查是否漏了 `* 1.0` 导致整数除法，或是否在 `WHERE` 中误删了退款单 |
| `HAVING` 里用别名报错 | 部分数据库不允许 `HAVING` 引用 `SELECT` 别名，直接写完整聚合表达式 `HAVING SUM(pay_amount) >= 1500` 最通用 |

:::job 面试加分表达
“`CASE WHEN` 条件聚合是面试里最高频的 SQL 技巧之一：用它可以在一次全表扫描里同时产出转化率、退款率、分平台分列汇总，避免写多次子查询。”
:::

:::checklist 本课验收
- [ ] 我能准确说出 `WHERE` 和 `HAVING` 的执行时机差异。
- [ ] 我会用 `CASE WHEN` 在单条 SQL 中计算比率类指标，并记得 `* 1.0`。
- [ ] 练习本 6-2.1 ～ 6-2.4 四题全部通过检查。
:::

下一课：[多表连接与子查询](lesson:6-3)。
