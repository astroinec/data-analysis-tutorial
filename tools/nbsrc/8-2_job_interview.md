# 8-2 面试高频题：SQL、业务排查与实验演练

请选择 `Python (da-course)` 内核，从 `notebooks/` 打开。本练习本把数据分析校招/转行面试中最常考的四类实战题浓缩成 4 道限时演练：2 道 SQL（渠道转化 + 累计窗口）、1 道漏斗定位、1 道 A/B 分层判断。

```python
import sys
sys.path.insert(0, "..")
from dacheck import check, hint, setup_chinese_font
import sqlite3
import pandas as pd

conn = sqlite3.connect("../data/shop/shop.db")
def q(sql):
    return pd.read_sql_query(sql, conn)

app_users = pd.read_csv("../data/app/app_users.csv", encoding="utf-8-sig")
app_events = pd.read_csv("../data/app/app_events.csv", encoding="utf-8-sig")
ab = pd.read_csv("../data/abtest/ab_experiment.csv", encoding="utf-8-sig")
print("四类面试数据集加载完成")
```

+++
## 面试题 8-2.1（SQL）：各获客渠道注册到下单转化率

用 SQL 在 `shop.db` 中计算每个 `channel` 的注册人数 `registered`、有已完成订单的转化人数 `buyers` 以及转化率 `conv_rate = buyers * 1.0 / registered`，按 `conv_rate` 降序排列。

提示：把 `o.status = '已完成'` 放在 `LEFT JOIN ... ON` 中，避免丢掉未下单客户。

```python
### BEGIN SOLUTION
ans_8_2_1 = q("""
SELECT
    c.channel,
    COUNT(DISTINCT c.customer_id) AS registered,
    COUNT(DISTINCT o.customer_id) AS buyers,
    COUNT(DISTINCT o.customer_id) * 1.0 / COUNT(DISTINCT c.customer_id) AS conv_rate
FROM customers c
LEFT JOIN orders o
    ON c.customer_id = o.customer_id AND o.status = '已完成'
GROUP BY c.channel
ORDER BY conv_rate DESC
""")
### STUDENT
ans_8_2_1 = ...
### END SOLUTION
check("8-2.1", ans_8_2_1)
```

+++
## 面试题 8-2.2（SQL 窗口函数）：月度销售额与年内累计销售额

用 SQL 的 CTE + 窗口函数 `SUM(revenue) OVER (ORDER BY month)` 计算 2025 年各月已完成净销售额 `revenue` 与累计销售额 `cum_revenue`，输出 `month, revenue, cum_revenue`，按 `month` 升序。

```python
### BEGIN SOLUTION
ans_8_2_2 = q("""
WITH m AS (
    SELECT substr(order_time, 1, 7) AS month, SUM(pay_amount) AS revenue
    FROM orders
    WHERE status = '已完成'
    GROUP BY month
)
SELECT
    month,
    revenue,
    SUM(revenue) OVER (ORDER BY month) AS cum_revenue
FROM m
ORDER BY month ASC
""")
### STUDENT
ans_8_2_2 = ...
### END SOLUTION
check("8-2.2", ans_8_2_2)
```

+++
## 面试题 8-2.3（业务排查）：定位试看到点击付费转化最低的渠道

结合 `app_events` 与 `app_users`，按 `channel` 计算 `start_trial -> click_pay` 的唯一用户转化率，找出最低的渠道名称 `lowest_channel` 和对应转化率 `lowest_rate`，存入字典 `ans_8_2_3`。

```python
### BEGIN SOLUTION
eu = app_events.merge(app_users[["user_id", "channel"]], on="user_id", how="left")
ch_rates = {}
for ch, g in eu.groupby("channel"):
    t = g.loc[g["event_name"].eq("start_trial"), "user_id"].nunique()
    c = g.loc[g["event_name"].eq("click_pay"), "user_id"].nunique()
    ch_rates[ch] = c / t
worst_ch = min(ch_rates, key=ch_rates.get)
ans_8_2_3 = {"lowest_channel": worst_ch, "lowest_rate": float(ch_rates[worst_ch])}
### STUDENT
ans_8_2_3 = ...
### END SOLUTION
check("8-2.3", ans_8_2_3)
```

+++
## 面试题 8-2.4（A/B 实验）：拆解新老客的转化率绝对提升

在 `ab` 中分别计算新客（`is_new_user == 1`）与老客（`is_new_user == 0`）的实验组减对照组转化率差值（小数），填入字典 `ans_8_2_4`（键：`new_lift, old_lift`）。

```python
### BEGIN SOLUTION
piv = ab.groupby(["is_new_user", "group"])["converted"].mean().unstack()
ans_8_2_4 = {
    "new_lift": float(piv.loc[1, "treatment"] - piv.loc[1, "control"]),
    "old_lift": float(piv.loc[0, "treatment"] - piv.loc[0, "control"]),
}
### STUDENT
ans_8_2_4 = ...
### END SOLUTION
check("8-2.4", ans_8_2_4)
```
