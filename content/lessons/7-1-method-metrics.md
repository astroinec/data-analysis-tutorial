---
summary: 学会用北极星指标、乘法公式拆解和维度下钻定位业务异动，告别“只报总数、说不清原因”。
prereq: 已完成阶段 2～6，能熟练分组聚合与多表连接
---

:::goal 本课可验证目标
- 用 OSM（目标—策略—度量）思路把模糊业务目标翻译成可监控的指标树。
- 掌握电商核心乘法拆解：`销售额 = 购买人数 × 人均订单数 × 客单价`，并用代码验证恒等式。
- 通过 2025-11 到 2025-12 的实例，识别“客单价上涨但总销售额下降”的真实驱动因素。
- 用维度下钻（按城市层级、按品类拆解件数与件单价）把宏观变化落到具体业务动作。
:::

打开 [7-1 练习本](../../notebooks/7-1_method_metrics.ipynb)，选择 `Python (da-course)` 内核。

## 1. 从“会算指标”到“会拆问题”

新手接到“12 月销售额比 11 月跌了 11.4%，查查怎么回事”时，常常随机画五六张图却讲不出重点。资深分析师会按**乘法公式拆解 + 维度下钻**两把手术刀层层定位：

:::flow 电商销售额拆解树
1. **北极星/顶层指标**：已完成净销售额（Revenue）
2. **第一层乘法拆解**：`购买人数（Buyers） × 人均订单数（Orders/Buyer） × 客单价（AOV）`
3. **第二层乘法拆解**：`客单价 = 平均每单件数（连带率） × 每件平均实付（件单价）`
4. **横向维度下钻**：按平台、城市层级、商品品类、新老客拆开对比
:::

## 2. 实战拆解：为什么 12 月客单价涨了，总销售额反而跌了？

用 2025-11 与 2025-12 的模拟文创店数据直接验算：

:::df 2025-11 vs 2025-12 三因子拆解实测
| 月份 | 购买人数 | 人均订单数 | 客单价（元） | 已完成净销售额（元） |
|---|---:|---:|---:|---:|
| 2025-11 | 977 | 1.76 | 133.17 | 229,054.00 |
| 2025-12 | 881 | 1.58 | 145.83 | 202,855.40 |
| 环比变化 | **−9.83%** | **−10.30%** | **+9.51%** | **−11.44%** |
:::

一眼看清真相：
- 12 月每单其实卖得更贵了（客单价上涨 9.51%），不是“价格崩了”；
- 真正拖累销售额的是**购买人数减少 9.83%** 以及 **人均下单频次减少 10.30%**。
- 业务上，下一步排查就应该立刻聚焦“12 月拉新流量/触达是否减少”和“大促后复购频次是否透支”，而不是盲目去改商品定价！

## 3. 客单价再拆解与口径五要素

任何业务指标落地前，必须对齐**口径五要素**：
1. **统计对象**：所有注册用户，还是有已完成订单的购买用户？
2. **时间归属**：按下单时间、支付时间还是发货时间？
3. **状态范围**：是否排除已退款/测试单？
4. **计算公式**：分子、分母分别是什么（如件单价是 `总金额 / 总件数`，不是每单均价再平均）？
5. **去重粒度**：按订单号去重，还是按客户 ID 去重？

:::quiz 指标异动排查第一步
老板发来消息：“昨天 GMV 突然掉了 20%，赶紧查一下！”你最合理的排查顺序是？
- [ ] 立刻去问运营昨天是不是文案写得不好
- [x] 先核对数据采集与口径有无异常，再把 GMV 拆解为“流量 × 转化率 × 客单价”或“人数 × 频次 × 客单价”，最后按渠道/品类下钻定位
- [ ] 直接把昨天和去年同月平均对比
---
排查异动永远先排“数据/口径假警报”，再做结构化公式拆解与维度下钻，避免靠直觉猜原因。
:::

## 4. 四道独立练习

:::try 7-1.1 月度销售额三因子拆解
计算 2025 年 12 个月的 `month, buyers, orders_per_buyer, aov, revenue`，按 `month` 升序。
:::fold 参考答案
```python
m_ex = completed.groupby("month", as_index=False).agg(
    revenue=("pay_amount", "sum"), orders=("order_id", "nunique"), buyers=("customer_id", "nunique"))
m_ex["orders_per_buyer"] = m_ex["orders"] / m_ex["buyers"]
m_ex["aov"] = m_ex["revenue"] / m_ex["orders"]
ans_7_1_1 = m_ex[["month", "buyers", "orders_per_buyer", "aov", "revenue"]].sort_values("month").reset_index(drop=True)
```
:::
:::

:::try 7-1.2 11 月到 12 月四项指标环比变化率
计算 `(12月 - 11月) / 11月`，填入 4 键字典：`revenue_mom, buyers_mom, opb_mom, aov_mom`。
:::fold 参考答案
实算：`revenue_mom ≈ -0.1144`, `buyers_mom ≈ -0.0983`, `opb_mom ≈ -0.1030`, `aov_mom ≈ +0.0951`。
:::
:::

:::try 7-1.3 按城市层级下钻拆解
已完成订单左连接 `customers[["customer_id", "city_tier"]]`，按 `city_tier` 统计 `buyers, orders, revenue, aov`，按 `revenue` 降序。
:::fold 参考答案
```python
wc = completed.merge(customers[["customer_id", "city_tier"]], on="customer_id", how="left", validate="many_to_one")
ans_7_1_3 = wc.groupby("city_tier", as_index=False).agg(
    buyers=("customer_id", "nunique"), orders=("order_id", "nunique"), revenue=("pay_amount", "sum"))
ans_7_1_3["aov"] = ans_7_1_3["revenue"] / ans_7_1_3["orders"]
ans_7_1_3 = ans_7_1_3.sort_values("revenue", ascending=False).reset_index(drop=True)
```
:::
:::

:::try 7-1.4 品类平均件数与件单价
已完成订单左连接 `products[["product_id", "category"]]`，按 `category` 计算 `avg_qty = sum(quantity)/nunique(order_id)` 与 `price_per_item = sum(pay_amount)/sum(quantity)`，按 `category` 升序。
:::fold 参考答案
```python
wp = completed.merge(products[["product_id", "category"]], on="product_id", how="left", validate="many_to_one")
g_cat = wp.groupby("category", as_index=False).agg(
    orders=("order_id", "nunique"), total_qty=("quantity", "sum"), revenue=("pay_amount", "sum"))
g_cat["avg_qty"] = g_cat["total_qty"] / g_cat["orders"]
g_cat["price_per_item"] = g_cat["revenue"] / g_cat["total_qty"]
ans_7_1_4 = g_cat[["category", "avg_qty", "price_per_item"]].sort_values("category").reset_index(drop=True)
```
:::
:::

## 常见问题与求职用途

| 问题 | 纠正路径 |
|---|---|
| 用“每个月客单价简单平均”算全年客单价 | 错！必须用“全年总金额 / 全年总订单数”加权计算 |
| 三个因子变化率直接相加等于总变化率 | 乘法公式近似满足，但大波动时存在交叉项，精确验算请直接用乘积 |
| 下钻维度太多看花眼 | 每次优先下钻“体量最大”或“变化幅度最大”的前 2～3 个维度 |

:::job 面试加分表达
“被问到‘某核心指标突然下降怎么办’时，我会给出结构化框架：先排数据口径故障 → 再按乘法公式拆解定位驱动因子 → 接着按渠道/设备/人群/品类下钻 → 最后结合内外因提出可验证假设。”
:::

:::checklist 本课验收
- [ ] 我能写出销售额的三因子乘法公式并用代码验算。
- [ ] 我能解释为什么 12 月客单价上升而总销售额下降。
- [ ] 我能说出定义任何业务指标的口径五要素。
- [ ] 练习本 7-1.1 ～ 7-1.4 四题全部通过检查。
:::

下一课：[漏斗、留存与同期群](lesson:7-2)。
