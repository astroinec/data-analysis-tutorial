# 项目一：线上文创店2025年度销售分析

这是完整复现路线，不是只画几张图。数据是固定随机种子生成的**虚构教学数据**，不代表任何真实店铺业绩。你将交付指标口径、检查记录、三张图和一份有边界的报告。

先完成阶段0～4。选择 `Python (da-course)` 内核，从本包的 `notebooks/` 打开；答案版在 `solutions/`。不要单独搬走本文件，它依赖相邻 `../data` 与 `../dacheck`。从上往下运行；七个练习相互独立，不会让未作答的 `...` 破坏后续示例。金额为元；展示时四舍五入，计算中保留原值。

```python
import sys
sys.path.insert(0, "..")
from dacheck import check, hint, setup_chinese_font
import pandas as pd
```

## 1. 问题与口径先写在纸上

问题：全年规模怎样？哪个月突出？平台退款有何差异？哪些品类贡献最多？目标完成了吗？窗口内有多少客户复购？

一行是一个订单且只有一种商品，`quantity` 是该商品件数。同一客户可有多个订单。全年范围是 `[2025-01-01, 2026-01-01)`，按下单时间归属月份；状态是导出时的最终模拟状态。已退款均视为全额退款，`pay_amount` 仍是退款前原支付金额。

本项目“已完成净销售额”（代码简写 `revenue`）=已完成订单 `pay_amount` 之和，不是财务确认收入、现金到账额或净利润。退款率=退款订单数/全年订单数。客单价=已完成金额/已完成订单数，不是每件商品均价。购买人数只数有已完成订单的不同客户。

## 2. 读取原始数据，先观察再处理

```python
from pathlib import Path

DATA = Path("../data/shop")
orders_raw = pd.read_csv(DATA / "orders.csv", encoding="utf-8-sig")
products = pd.read_csv(DATA / "products.csv", encoding="utf-8-sig")
customers = pd.read_csv(DATA / "customers.csv", encoding="utf-8-sig")
targets = pd.read_csv(DATA / "monthly_targets.csv", encoding="utf-8-sig")
print({"orders": orders_raw.shape, "products": products.shape,
       "customers": customers.shape, "targets": targets.shape})
orders_raw.head()
```

当前包订单全集为15115行；Excel中的订单只有前3000行，不能替代年度全集。原表保留，所有转换在副本完成。

```python
orders = orders_raw.copy()
orders["order_time"] = pd.to_datetime(orders["order_time"], errors="raise")
print(orders["order_time"].min(), orders["order_time"].max())
print(orders["status"].value_counts())
print(orders.isna().sum())
```

## 3. 写出可失败的质量检查

这里 `assert` 检查的是固定完整数据应满足的前提，不是给未作答练习套断言。若失败，停下来查错，不删掉断言继续写结论。评分空值是未评价，不填0；项目金额统计不需要评分，缺失评分不应导致删订单。

```python
import numpy as np

assert orders["order_id"].is_unique
assert orders["order_id"].notna().all()
assert products["product_id"].is_unique
assert customers["customer_id"].is_unique
assert targets["month"].is_unique
required = ["order_time", "customer_id", "product_id", "quantity", "unit_price",
            "discount", "pay_amount", "platform", "status"]
assert orders[required].notna().all().all()
assert set(orders["status"]) == {"已完成", "已退款"}
assert orders["quantity"].gt(0).all()
assert orders["quantity"].mod(1).eq(0).all()
assert orders["unit_price"].gt(0).all()
assert orders["discount"].between(0, 1).all()
assert orders["pay_amount"].ge(0).all()
expected_pay = (orders["unit_price"] * orders["quantity"] * (1 - orders["discount"])).round(2)
assert np.isclose(orders["pay_amount"], expected_pay, atol=0.01, rtol=0).all()
assert orders["rating"].dropna().between(1, 5).all()
assert orders["order_time"].between("2025-01-01", "2026-01-01", inclusive="left").all()
assert targets["target_gmv"].gt(0).all()
print("主键、必要字段、时间、金额、评分范围检查通过")
```

## 4. 多表连接：不能把订单变多，也不能悄悄丢订单

`how='left'` 保留订单；`validate='many_to_one'` 要求右表每个连接键只有一行；`indicator` 检查匹配是否齐全。单看连接后行数相同还不够：也需订单集合与唯一性检查。

```python
joined = orders.merge(products, on="product_id", how="left",
                      validate="many_to_one", indicator="product_match")
assert joined["product_match"].eq("both").all()
joined = joined.merge(customers, on="customer_id", how="left",
                      validate="many_to_one", indicator="customer_match")
assert joined["customer_match"].eq("both").all()
assert len(joined) == len(orders)
assert joined["order_id"].is_unique
assert set(joined["order_id"]) == set(orders["order_id"])
assert joined["category"].notna().all()
assert joined["cost"].ge(0).all()
assert joined["order_time"].ge(pd.to_datetime(joined["launch_date"])).all()
assert joined["order_time"].ge(pd.to_datetime(joined["register_date"])).all()
joined = joined.drop(columns=["product_match", "customer_match"])
print("连接前后行数：", len(orders), len(joined))
```

练习 P-1.7：从原始 `orders` 开始自行左连接，只交指定四列。它不依赖其他练习。用 `hint('P-1.7')` 获取提示。

```python
### BEGIN SOLUTION
join_answer = orders.merge(products[["product_id", "product_name", "category"]],
                           on="product_id", how="left", validate="many_to_one")
join_answer = join_answer.merge(customers[["customer_id", "city"]],
                                on="customer_id", how="left", validate="many_to_one")
join_answer = join_answer[["order_id", "product_name", "category", "city"]]
### STUDENT
join_answer = ...
### END SOLUTION
check("P-1.7", join_answer)
```

## 5. 全年仪表盘：别把退款算成收入

示例基准数据不使用任何被挖空的练习变量。

```python
completed = joined.loc[joined["status"].eq("已完成")].copy()
completed["month"] = completed["order_time"].dt.strftime("%Y-%m")
revenue = completed["pay_amount"].sum()
refunded = orders.loc[orders["status"].eq("已退款")]
print(f"已完成净销售额：{revenue:,.2f}元")
print(f"全状态原支付GMV：{orders['pay_amount'].sum():,.2f}元")
print(f"已退款原支付：{refunded['pay_amount'].sum():,.2f}元")
print(f"已完成订单：{len(completed):,}笔；购买人数：{completed['customer_id'].nunique():,}人")
print(f"客单价：{revenue / len(completed):.2f}元/单")
print(f"订单退款率：{len(refunded) / len(orders):.2%}")
```

练习 P-1.1：交字典，键恰好为 `all_orders, completed_orders, revenue, buyers, aov, refund_rate`；退款率用0～1小数，金额不用提前取整。

```python
### BEGIN SOLUTION
kpi_answer = {
    "all_orders": len(orders),
    "completed_orders": len(completed),
    "revenue": completed["pay_amount"].sum(),
    "buyers": completed["customer_id"].nunique(),
    "aov": completed["pay_amount"].sum() / len(completed),
    "refund_rate": orders["status"].eq("已退款").mean(),
}
### STUDENT
kpi_answer = ...
### END SOLUTION
check("P-1.1", kpi_answer)
```

## 6. 月趋势：先看数，再画图

练习 P-1.2：交12行表 `month, revenue, orders`，月份升序。`orders` 是已完成唯一订单数。

```python
### BEGIN SOLUTION
monthly_answer = completed.groupby("month", as_index=False).agg(
    revenue=("pay_amount", "sum"), orders=("order_id", "nunique"))
### STUDENT
monthly_answer = ...
### END SOLUTION
check("P-1.2", monthly_answer)
```

以下是独立示例，即便上一题未作答也可运行。环比没有上一个月时为缺失；不要把一月缺失填0并说“没有增长”。

```python
monthly = completed.groupby("month", as_index=False).agg(
    revenue=("pay_amount", "sum"), orders=("order_id", "nunique"))
monthly["aov"] = monthly["revenue"] / monthly["orders"]
monthly["mom"] = monthly["revenue"].pct_change()
monthly
```

```python
import matplotlib.pyplot as plt
setup_chinese_font()
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(monthly["month"], monthly["revenue"] / 10000, marker="o")
ax.set(title="虚构文创店2025月度已完成净销售额", xlabel="下单月份", ylabel="金额（万元）")
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()
plt.show()
```

读图：11月22.91万元为峰值，2月9.57万元为低点。不能据此证明促销产生了增量：生成器本身设置了增长与季节波动，数据没有对照组、流量、投放费用，更没有2024年订单用于同比。

## 7. 平台退款：分母必须回到全集

练习 P-1.3：交 `platform, all_orders, refunds, refund_rate`，按平台名升序。若先用 `completed` 再统计，只会制造退款率0。

```python
### BEGIN SOLUTION
platform_answer = orders.assign(is_refund=orders["status"].eq("已退款")).groupby(
    "platform", as_index=False).agg(all_orders=("order_id", "nunique"), refunds=("is_refund", "sum"))
platform_answer["refund_rate"] = platform_answer["refunds"] / platform_answer["all_orders"]
### STUDENT
platform_answer = ...
### END SOLUTION
check("P-1.3", platform_answer)
```

```python
platform_stats = orders.assign(is_refund=orders["status"].eq("已退款")).groupby(
    "platform", as_index=False).agg(all_orders=("order_id", "nunique"), refunds=("is_refund", "sum"))
platform_stats["refund_rate"] = platform_stats["refunds"] / platform_stats["all_orders"]
print(platform_stats.to_string(index=False))
fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(platform_stats["platform"], platform_stats["refund_rate"] * 100)
ax.set(title="2025平台订单退款率（模拟数据）", xlabel="平台", ylabel="退款订单/该平台全年订单（%）")
fig.tight_layout()
plt.show()
```

抖音小店477/3732=12.78%，微信小程序198/4497=4.40%，淘宝444/6886=6.45%。这只是描述；平台退款概率在生成器中被事先设定，不能当作真实平台优劣评价。建议是“若在真实业务看到类似差异，先补退款原因和品类构成再验证”，不是“立即停止某平台”。

## 8. 品类贡献与静态成本估算

练习 P-1.4：交 `category, revenue, share`，按收入降序；份额是小数，所有品类之和应为1。

```python
### BEGIN SOLUTION
category_answer = completed.groupby("category", as_index=False).agg(revenue=("pay_amount", "sum"))
category_answer["share"] = category_answer["revenue"] / category_answer["revenue"].sum()
category_answer = category_answer.sort_values("revenue", ascending=False).reset_index(drop=True)
### STUDENT
category_answer = ...
### END SOLUTION
check("P-1.4", category_answer)
```

```python
category_stats = completed.groupby("category", as_index=False).agg(revenue=("pay_amount", "sum"))
category_stats["share"] = category_stats["revenue"] / category_stats["revenue"].sum()
category_stats = category_stats.sort_values("revenue", ascending=False).reset_index(drop=True)
print(category_stats.to_string(index=False))
fig, ax = plt.subplots(figsize=(8, 4))
ax.barh(category_stats["category"], category_stats["revenue"] / 10000)
ax.invert_yaxis()
ax.set(title="2025品类已完成净销售额贡献（模拟数据）", xlabel="金额（万元）", ylabel="品类")
fig.tight_layout()
plt.show()
```

```python
completed["estimated_goods_cost"] = completed["quantity"] * completed["cost"]
completed["estimated_gross_profit"] = completed["pay_amount"] - completed["estimated_goods_cost"]
estimated_cost = completed["estimated_goods_cost"].sum()
estimated_profit = completed["estimated_gross_profit"].sum()
print(f"静态商品成本估算：{estimated_cost:,.2f}元")
print(f"商品毛利估算：{estimated_profit:,.2f}元；估算毛利率：{estimated_profit / revenue:.2%}")
```

`cost` 是商品表中的静态每件成本，乘实际件数，不乘折扣。估算未计平台费、运费、广告费、人工、税费，也没有历史成本变化、退款处理成本；不能称“净利润”，不能用于财务披露。

## 9. 目标对齐：按月份，不按表格行位置

`target_gmv` 名字虽含GMV，本项目规定与已完成净销售额比较。模拟目标是生成器从销售数据构造的练习目标，不是独立真实经营预算。

```python
expected_months = [f"2025-{m:02d}" for m in range(1, 13)]
assert sorted(targets["month"].tolist()) == expected_months
assert monthly["month"].tolist() == expected_months
performance = monthly[["month", "revenue"]].merge(
    targets, on="month", how="left", validate="one_to_one", indicator=True)
assert performance["_merge"].eq("both").all()
assert len(performance) == 12
performance = performance.drop(columns="_merge")
performance["achievement"] = performance["revenue"] / performance["target_gmv"]
performance["gap"] = performance["revenue"] - performance["target_gmv"]
performance
```

练习 P-1.5：交 `month, revenue, target_gmv, achievement`，月份升序，不包含 `gap` 列。

```python
### BEGIN SOLUTION
target_answer = completed.groupby("month", as_index=False).agg(revenue=("pay_amount", "sum"))
target_answer = target_answer.merge(targets, on="month", how="left", validate="one_to_one")
target_answer["achievement"] = target_answer["revenue"] / target_answer["target_gmv"]
### STUDENT
target_answer = ...
### END SOLUTION
check("P-1.5", target_answer)
```

```python
print(f"全年目标：{targets['target_gmv'].sum():,.2f}元")
print(f"全年达成率：{revenue / targets['target_gmv'].sum():.2%}")
print("达标月份：", performance.loc[performance["achievement"].ge(1), "month"].tolist())
```

全年达成率必须用全年收入/全年目标，不能简单平均12个月百分比；月份目标不同，相当于需要按目标金额加权。

## 10. 窗口复购，不等于终身忠诚度

练习 P-1.6：交一个0～1小数。2025年至少2笔已完成订单的客户/2025有已完成购买的客户。不是1881/3000，不包含仅退款客户，也不是“新增客户留存率”。

```python
### BEGIN SOLUTION
purchase_counts_answer = completed.groupby("customer_id")["order_id"].nunique()
repeat_answer = purchase_counts_answer.ge(2).mean()
### STUDENT
repeat_answer = ...
### END SOLUTION
check("P-1.6", repeat_answer)
```

```python
purchase_counts = completed.groupby("customer_id")["order_id"].nunique()
print(f"购买客户：{len(purchase_counts)}；窗口复购客户：{purchase_counts.ge(2).sum()}")
print(f"窗口复购率：{purchase_counts.ge(2).mean():.2%}")
```

年底首次购买者观察期短，不能与年初客户直接比较“忠诚”。留存、同期群和更复杂方法在后续批次，不在此冒充已经实现。

## 11. 安全导出与报告

以下只演示生成文件，不覆盖原始数据。临时目录退出后会删除，正式保存时请用自己新建的输出目录，确认路径不在 `data/` 下。

```python
import tempfile
with tempfile.TemporaryDirectory(prefix="da-project-") as tmp:
    export_dir = Path(tmp)
    monthly.to_csv(export_dir / "monthly_summary.csv", index=False, encoding="utf-8-sig")
    with pd.ExcelWriter(export_dir / "analysis_tables.xlsx") as writer:
        monthly.to_excel(writer, sheet_name="月趋势", index=False)
        platform_stats.to_excel(writer, sheet_name="平台退款", index=False)
        category_stats.to_excel(writer, sheet_name="品类贡献", index=False)
        performance.to_excel(writer, sheet_name="目标达成", index=False)
    print("演示生成：", [p.name for p in export_dir.iterdir()])
    print("回读校验：", pd.read_csv(export_dir / "monthly_summary.csv").shape)
```

报告模板在 `../report/analysis-report-template.md`，实算参考报告在 `../report/project-reference-report.md`。报告至少交代：问题、数据来源及模拟声明、时间与口径、质量检查、复现路径、3～5项有数字的发现、限制、行动建议及待补数据。不要只贴代码截图。

### 参考结论写法

- 发现：11月已完成净销售额229054元，全年月度最高；2月95747.40元最低。证据为月度分组表。
- 边界：模拟器设定季节波动，没有流量、上年数据和对照组，不能认定促销因果或同比增长。
- 建议：真实店铺可先补日级流量、费用和库存，比较活动前后与可比对照，再验证备货策略；本作业尚未执行该建议。

### 最终自验

1. 七题都通过，重启内核后“运行全部”仍能复现。
2. 月份和品类收入之和均等于1784371.10，退款原支付与已完成金额之和等于全状态原支付。
3. 连接后仍15115笔唯一订单；已完成13996笔，购买2427人。
4. 每张图标明模拟数据、单位、时间和口径；没有截断柱状图制造差距。
5. 简历写“独立完成模拟文创店年度分析作品，处理15115笔订单、验证多表连接并交付报告”，不写“为某公司提升收入20%”。
