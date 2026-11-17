# 3-1 缺失值与重复值

目标：先确认订单粒度，记录重复和缺失，再依据字段含义处理。数据完全虚构。本文件留在 `notebooks/` 中，选择 `Python (da-course)`，从第一格运行。

```python
import sys
sys.path.insert(0, "..")
from dacheck import check, hint, setup_chinese_font
import pandas as pd
```

## 示范：先看原表，不覆盖原文件

本包脏表一行一个订单、一个商品；在现实多商品明细表中，不可只按订单编号去重。

```python
raw = pd.read_csv("../data/shop/orders_dirty.csv")
print("原表行列：", raw.shape)
print("额外整行重复：", int(raw.duplicated().sum()))
print(raw.isna().sum())
raw.head()
```

```python
duplicate_log = raw.loc[raw.duplicated()].copy()
unique = raw.drop_duplicates().copy()
print("去重后行数：", len(unique))
print("去重后订单编号重复：", int(unique["订单编号"].duplicated().sum()))
print("去重后数量缺失：", int(unique["数量"].isna().sum()))
```

本版依次观察到 2060 原始行、60 额外重复、2000 去重行、35 数量缺失。答案检查从文件动态计算，不要仅背数字。原表缺失与重复可能重叠。

## 练习 1：三项体检

提交字典，键名按下方保留。分别统计原始行数、额外整行重复、去重后数量缺失。

```python
### BEGIN SOLUTION
audit_answer = {
    "原始行数": raw.shape[0],
    "额外整行重复": int(raw.duplicated().sum()),
    "去重后数量缺失": int(raw.drop_duplicates()["数量"].isna().sum())
}
### STUDENT
audit_answer = ...
### END SOLUTION
check("3-1.1", audit_answer)
```

需要提示可运行 `hint("3-1.1")`。所有练习相互独立，后面的示范不使用练习答案。

## 练习 2：去重后的副本

提交保留所有原始列、保留第一次、保持行顺序的去重表。不要 `dropna()`，也不要修改 `raw`。

```python
### BEGIN SOLUTION
dedup_answer = raw.drop_duplicates().copy()
### STUDENT
dedup_answer = ...
### END SOLUTION
check("3-1.2", dedup_answer)
```

## 示范：品类缺失优先查可信主表

本包原订单 `order_id` 唯一，可关联到商品 ID，再到商品品类。不能假定商品名称永远唯一；本例用订单 ID 和商品 ID。没有可信来源时标记未知并核对，不随意填最常见品类。

```python
orders = pd.read_csv("../data/shop/orders.csv")
products = pd.read_csv("../data/shop/products.csv")
print("原订单ID唯一：", orders["order_id"].is_unique)
master = orders[["order_id", "product_id"]].merge(
    products[["product_id", "category"]],
    on="product_id", how="left", validate="many_to_one"
)
category_lookup = master.set_index("order_id")["category"]
clean = unique.copy()
missing_category = unique["品类"].isna()
clean["品类"] = unique["品类"].fillna(
    unique["订单编号"].map(category_lookup)
).fillna("未知")
repair_log = clean.loc[missing_category, ["订单编号", "品类"]].copy()
repair_log["原品类"] = unique.loc[missing_category, "品类"]
repair_log["处理原因"] = "原订单商品ID关联可信模拟主表"
print("原品类缺失：", int(missing_category.sum()))
print("修复后未知：", int(clean["品类"].eq("未知").sum()))
repair_log.head()
```

## 练习 3：提交补回后的品类列

从 `unique` 独立生成一列 Series，原有品类不改，缺失品类用主表映射，仍缺失则标记“未知”。

```python
### BEGIN SOLUTION
category_answer = unique["品类"].fillna(
    unique["订单编号"].map(category_lookup)
).fillna("未知")
### STUDENT
category_answer = ...
### END SOLUTION
check("3-1.3", category_answer)
```

## 示范：未评分不是评分为零

数量缺失留在待核对表；评分缺失不删除订单金额。下方均值暂时还含越界评分，只用于练习缺失行为，下一课才做五分制质量检查。

```python
quantity_review = unique.loc[unique["数量"].isna()].copy()
ratings = unique["评分"]
print("已有评分数（暂含越界）：", int(ratings.notna().sum()))
print("已有评分均值（暂含越界）：", ratings.mean())
print("已有评分覆盖率：", ratings.notna().mean())
print("待核对数量行数：", len(quantity_review))
```

## 练习 4：评分的数量与均值

提交两个键的字典，针对 `unique` 的原始评分。不要填 0；不要在这题提前过滤越界，因为本题检验缺失的处理，结果不可当成最终满意度。

```python
### BEGIN SOLUTION
rating_answer = {
    "已有评分数": int(unique["评分"].notna().sum()),
    "已有评分均值": unique["评分"].mean()
}
### STUDENT
rating_answer = ...
### END SOLUTION
check("3-1.4", rating_answer)
```

## 小测与验收

一笔已完成订单未评分，计算实付金额时是否应该删掉它？先口头回答。

<details><summary>参考答案</summary>不应只因为评分缺失删除它。金额、销量、评分分别检查所需字段；未评价与低评价不同。</details>

验收：能区分整行重复和键重复；保存原表、重复日志、修复日志；能说明缺失字段处理依据。`KeyError` 时先看 `raw.columns.tolist()`，确认读取的是中文脏表。本模拟练习展示清洗方法，不虚构企业营收提升。
