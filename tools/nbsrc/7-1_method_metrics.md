# 7-1 指标体系与拆解思路

请选择 `Python (da-course)` 内核，从 `notebooks/` 打开。本课练习用乘法公式拆解销售额：`已完成净销售额 = 购买人数 × 人均订单数 × 客单价`，并用维度下钻定位变化来源。

```python
import sys
sys.path.insert(0, "..")
from dacheck import check, hint, setup_chinese_font
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
```

读取三张原始表并筛出已完成订单。

```python
orders = pd.read_csv("../data/shop/orders.csv", parse_dates=["order_time"], encoding="utf-8-sig")
products = pd.read_csv("../data/shop/products.csv", encoding="utf-8-sig")
customers = pd.read_csv("../data/shop/customers.csv", encoding="utf-8-sig")
completed = orders.loc[orders["status"].eq("已完成")].copy()
completed["month"] = completed["order_time"].dt.strftime("%Y-%m")
print("已完成订单：", len(completed))
```

+++
## 1. 乘法拆解：为什么 12 月客单价涨了，总销售额反而跌了？

```python
monthly = completed.groupby("month", as_index=False).agg(
    revenue=("pay_amount", "sum"),
    orders=("order_id", "nunique"),
    buyers=("customer_id", "nunique"),
)
monthly["orders_per_buyer"] = monthly["orders"] / monthly["buyers"]
monthly["aov"] = monthly["revenue"] / monthly["orders"]
# 验算乘法恒等式
assert np.allclose(monthly["buyers"] * monthly["orders_per_buyer"] * monthly["aov"], monthly["revenue"])
monthly.loc[monthly["month"].isin(["2025-11", "2025-12"])].round(2)
```

11 月到 12 月，客单价从 133.17 元升至 145.83 元（+9.51%），但购买人数从 977 降到 881（-9.83%），人均订单数也从 1.76 降到 1.58（-10.30%），导致总销售额下降 11.44%。如果不拆解，很容易误以为“卖得便宜了”。

+++
## 2. 维度下钻：按城市层级看客单价与规模

```python
with_cust = completed.merge(customers[["customer_id", "city_tier"]], on="customer_id", how="left", validate="many_to_one")
tier_df = with_cust.groupby("city_tier", as_index=False).agg(
    buyers=("customer_id", "nunique"),
    orders=("order_id", "nunique"),
    revenue=("pay_amount", "sum"),
)
tier_df["aov"] = tier_df["revenue"] / tier_df["orders"]
tier_df.sort_values("revenue", ascending=False).round(2)
```

+++
## 练习 7-1.1 月度销售额三因子拆解

计算 2025 年 12 个月的 `month, buyers, orders_per_buyer, aov, revenue`（按 `month` 升序，保留原始精度）。

```python
### BEGIN SOLUTION
m_ex = completed.groupby("month", as_index=False).agg(
    revenue=("pay_amount", "sum"),
    orders=("order_id", "nunique"),
    buyers=("customer_id", "nunique"),
)
m_ex["orders_per_buyer"] = m_ex["orders"] / m_ex["buyers"]
m_ex["aov"] = m_ex["revenue"] / m_ex["orders"]
ans_7_1_1 = m_ex[["month", "buyers", "orders_per_buyer", "aov", "revenue"]].sort_values("month").reset_index(drop=True)
### STUDENT
ans_7_1_1 = ...
### END SOLUTION
check("7-1.1", ans_7_1_1)
```

+++
## 练习 7-1.2 计算 11 月到 12 月四项指标的环比变化率

计算 `(12月 - 11月) / 11月`（小数），填入字典 `ans_7_1_2`（键：`revenue_mom, buyers_mom, opb_mom, aov_mom`）。

```python
### BEGIN SOLUTION
m_idx = completed.groupby("month").agg(
    revenue=("pay_amount", "sum"),
    orders=("order_id", "nunique"),
    buyers=("customer_id", "nunique"),
)
m_idx["opb"] = m_idx["orders"] / m_idx["buyers"]
m_idx["aov"] = m_idx["revenue"] / m_idx["orders"]
nov, dec = m_idx.loc["2025-11"], m_idx.loc["2025-12"]
ans_7_1_2 = {
    "revenue_mom": float((dec["revenue"] - nov["revenue"]) / nov["revenue"]),
    "buyers_mom": float((dec["buyers"] - nov["buyers"]) / nov["buyers"]),
    "opb_mom": float((dec["opb"] - nov["opb"]) / nov["opb"]),
    "aov_mom": float((dec["aov"] - nov["aov"]) / nov["aov"]),
}
### STUDENT
ans_7_1_2 = ...
### END SOLUTION
check("7-1.2", ans_7_1_2)
```

+++
## 练习 7-1.3 按城市层级下钻拆解

已完成订单左连接 `customers[["customer_id", "city_tier"]]`，按 `city_tier` 统计 `buyers, orders, revenue, aov`，按 `revenue` 降序。

```python
### BEGIN SOLUTION
wc = completed.merge(customers[["customer_id", "city_tier"]], on="customer_id", how="left", validate="many_to_one")
ans_7_1_3 = wc.groupby("city_tier", as_index=False).agg(
    buyers=("customer_id", "nunique"),
    orders=("order_id", "nunique"),
    revenue=("pay_amount", "sum"),
)
ans_7_1_3["aov"] = ans_7_1_3["revenue"] / ans_7_1_3["orders"]
ans_7_1_3 = ans_7_1_3.sort_values("revenue", ascending=False).reset_index(drop=True)
### STUDENT
ans_7_1_3 = ...
### END SOLUTION
check("7-1.3", ans_7_1_3)
```

+++
## 练习 7-1.4 客单价再拆解：品类平均件数与件单价

已完成订单左连接 `products[["product_id", "category"]]`，按 `category` 计算 `avg_qty = sum(quantity) / nunique(order_id)` 和 `price_per_item = sum(pay_amount) / sum(quantity)`，输出 `category, avg_qty, price_per_item`，按 `category` 升序。

```python
### BEGIN SOLUTION
wp = completed.merge(products[["product_id", "category"]], on="product_id", how="left", validate="many_to_one")
g_cat = wp.groupby("category", as_index=False).agg(
    orders=("order_id", "nunique"),
    total_qty=("quantity", "sum"),
    revenue=("pay_amount", "sum"),
)
g_cat["avg_qty"] = g_cat["total_qty"] / g_cat["orders"]
g_cat["price_per_item"] = g_cat["revenue"] / g_cat["total_qty"]
ans_7_1_4 = g_cat[["category", "avg_qty", "price_per_item"]].sort_values("category").reset_index(drop=True)
### STUDENT
ans_7_1_4 = ...
### END SOLUTION
check("7-1.4", ans_7_1_4)
```
