# 3-2 类型、日期、文本与异常复核

本课从原始脏表独立开始。不自动删除缺失，不根据“大”判定无效；规则仅针对本模拟文件。练习本保持原位置，内核选 `Python (da-course)`。

```python
import sys
sys.path.insert(0, "..")
from dacheck import check, hint, setup_chinese_font
import pandas as pd
```

```python
raw = pd.read_csv("../data/shop/orders_dirty.csv")
unique = raw.drop_duplicates().copy()
work = unique.copy()
print(work.dtypes)
```

## 示范：金额文本解析

本文件已知装饰为 `￥` 与 `元`。`errors="coerce"` 将解析失败变成缺失，必须检查；它不证明原值已经修好，也不应把失败填成 0。

```python
money_text = (unique["实付金额"].astype("string").str.strip()
              .str.replace("￥", "", regex=False)
              .str.replace("元", "", regex=False))
parsed_money = pd.to_numeric(money_text, errors="coerce")
money_failed = unique.loc[parsed_money.isna() & money_text.notna()].copy()
work["实付金额"] = parsed_money
print("非空输入解析失败：", len(money_failed))
print(work["实付金额"].head())
```

## 练习 1：金额数值列

从 `unique` 独立生成金额 Series。不覆盖原表，不修改符号之外的数字。

```python
### BEGIN SOLUTION
money_answer = pd.to_numeric(
    unique["实付金额"].astype("string").str.strip()
    .str.replace("￥", "", regex=False).str.replace("元", "", regex=False),
    errors="coerce"
)
### STUDENT
money_answer = ...
### END SOLUTION
check("3-2.1", money_answer)
```

## 示范：2025 年混合日期

先把 `2025年6月18日` 与 `2025/6/18 20:30` 的分隔符统一，再用 `format="mixed"`。只有日期的记录没有原小时和分钟，解析后的午夜不是实际下单时间。只有时分的记录也不能恢复原秒数，所以不据脏表做小时偏好分析。

```python
date_text = (unique["下单时间"].astype("string").str.strip()
             .str.replace("年", "-", regex=False)
             .str.replace("月", "-", regex=False)
             .str.replace("日", "", regex=False)
             .str.replace("/", "-", regex=False))
parsed_time = pd.to_datetime(date_text, format="mixed", errors="coerce")
date_failed = unique.loc[parsed_time.isna()].copy()
work["下单时间"] = parsed_time
print("日期解析失败：", len(date_failed))
print("覆盖月份数：", parsed_time.dt.to_period("M").nunique())
print("原文仅年月日记录：", int(unique["下单时间"].str.contains("年", na=False).sum()))
```

## 练习 2：日期列

独立生成解析后的日期 Series，保留原行索引。不要把日期缺失改成今天，也不要声称恢复了分钟。

```python
### BEGIN SOLUTION
dates_answer = pd.to_datetime(
    unique["下单时间"].astype("string").str.strip()
    .str.replace("年", "-", regex=False).str.replace("月", "-", regex=False)
    .str.replace("日", "", regex=False).str.replace("/", "-", regex=False),
    format="mixed", errors="coerce"
)
### STUDENT
dates_answer = ...
### END SOLUTION
check("3-2.2", dates_answer)
```

## 示范：文本别名

去“市”后缀和平台映射仅是本模拟规则，不是通用城市清洗或平台识别器。未知值要保留检查。

```python
platform_alias = {
    "taobao": "淘宝", "TB": "淘宝", "微信": "微信小程序",
    "小程序": "微信小程序", "抖音": "抖音小店", "douyin": "抖音小店"
}
work["城市"] = unique["城市"].astype("string").str.strip().str.removesuffix("市")
work["平台"] = unique["平台"].str.strip().replace(platform_alias)
work["订单状态"] = unique["订单状态"].str.strip().replace({"完成": "已完成", "退款": "已退款"})
print(work["平台"].value_counts(dropna=False))
print(work["订单状态"].value_counts(dropna=False))
```

## 练习 3：统一后的三个标签列

提交仅有“城市、平台、订单状态”三列的新表，保持行顺序。

```python
### BEGIN SOLUTION
labels_answer = unique[["城市", "平台", "订单状态"]].copy()
labels_answer["城市"] = labels_answer["城市"].astype("string").str.strip().str.removesuffix("市")
labels_answer["平台"] = labels_answer["平台"].str.strip().replace(platform_alias)
labels_answer["订单状态"] = labels_answer["订单状态"].str.strip().replace({"完成": "已完成", "退款": "已退款"})
### STUDENT
labels_answer = ...
### END SOLUTION
check("3-2.3", labels_answer)
```

## 示范：字段分别标记，保留原值

练习假设数量为 1～20 的整数。缺失、不在范围、非整数均待核对；这是隔离，不是证明业务无效。评分五分制，缺失评分不算越界。

```python
quantity = pd.to_numeric(unique["数量"], errors="coerce")
quantity_issue = quantity.isna() | ~quantity.between(1, 20) | quantity.mod(1).ne(0)
rating = pd.to_numeric(unique["评分"], errors="coerce")
rating_issue = rating.notna() & ~rating.between(1, 5)
review = unique.loc[quantity_issue | rating_issue].copy()
review["数量待核对"] = quantity_issue.loc[review.index]
review["评分越界"] = rating_issue.loc[review.index]
valid_rating = rating.where(rating.between(1, 5))
print("数量待核对：", int(quantity_issue.sum()))
print("已有评分越界：", int(rating_issue.sum()))
print("有效评分数与均值：", int(valid_rating.notna().sum()), valid_rating.mean())
review.head()
```

若临时只分析符合数量假设的行，必须说明规则、排除数量和结果限制。评分越界不应自动删除订单金额。不要写 pandas 列条件 `and` / `or`，使用带括号的 `&` / `|`。

## 练习 4：仅数量问题的原始记录

从 `unique` 独立选出数量缺失、不在 1～20 或非整数的记录，保留全部原列，不加入评分条件。

```python
### BEGIN SOLUTION
q_for_answer = pd.to_numeric(unique["数量"], errors="coerce")
quantity_review_answer = unique.loc[
    q_for_answer.isna() | ~q_for_answer.between(1, 20) | q_for_answer.mod(1).ne(0)
].copy()
### STUDENT
quantity_review_answer = ...
### END SOLUTION
check("3-2.4", quantity_review_answer)
```

## 小测与验收

一个 999 件的订单应立即删除吗？

<details><summary>参考答案</summary>先标记并复核。999 与本课假设不符，但真实场景可能存在团购，需核对来源和业务依据。</details>

验收：金额真正是数值、日期解析失败有记录；不还原丢失分钟；文本映射有案例边界；异常和缺失按字段分别处理。求职作品应说明规则依据与处理日志，不把“删掉多少行”本身当作能力成果。
