---
summary: 把金额、日期和名称统一为可分析的类型，并为疑似异常保留复核证据。
prereq: 已完成 3-1，理解粒度、缺失值与整行去重
---

## 本课目标与起点

:::goal
- 区分“看起来像数字”和真正的数值类型。
- 清理本模拟文件的金额符号、混合日期和文本别名。
- 用布尔条件标记待核对项，留下隔离表和原因。
- 解释异常规则的业务边界，不把“很大”直接等同于“错误”。
:::

打开 [3-2 练习本](../../notebooks/3-2_clean_types.ipynb)，从第一格运行。每本都独立读取数据，本课不会依赖上一课的内存变量。原文件保持不变，本课将操作去重后的副本。

```python
import pandas as pd
raw = pd.read_csv("../data/shop/orders_dirty.csv")
work = raw.drop_duplicates().copy()
print(work.dtypes)
```

`dtypes` 显示每列的类型。本版 `实付金额` 混有 `￥39.00`、`39.00元` 与 `39.00`，读取后是文本。pandas 3 的文本类型可能显示为 `str`，其他环境可能显示为 `object`；不必背输出单词，重要的是确认这一列能否安全做数值运算。

## 1. 金额：先解释格式，再转数字

字符串是“字符的队伍”。两个文本相加可能是在拼接，不是在算钱；按文本排序，`"100"` 也可能排在 `"20"` 前。清洗过程分为“去掉已知装饰”和“解析为数值”。

```python
money_text = (work["实付金额"].astype("string")
              .str.strip()
              .str.replace("￥", "", regex=False)
              .str.replace("元", "", regex=False))
money = pd.to_numeric(money_text, errors="coerce")
money_failed = work.loc[money.isna() & money_text.notna()].copy()
work["实付金额"] = money
print("非空金额解析失败：", len(money_failed))
```

`regex=False` 表示只替换眼前这个字符，不把它当正则规则。`errors="coerce"` 表示无法解析时产生缺失，而不是让程序在第一处失败就停止。它不是“错误已经修好”：必须检查新产生的缺失并保留原值。原本空白与解析失败也不是同一种问题。

:::df
| 原值 | 去装饰后 | 数值结果 | 后续动作 |
|---|---|---|---|
| `￥39.00` | `39.00` | 39.0 | 可按元统计 |
| `39.00元` | `39.00` | 39.0 | 可按元统计 |
| `待确认`（说明性例子） | `待确认` | 缺失 | 留待核对，不能变成零 |
:::

本文件的金额修复仅涵盖已知符号和单位，不能拿到另一份文件就删除所有非数字字符。例如负号、小数点、千位分隔符和不同币种都有实际含义。人民币元和美元不能清掉符号后直接汇总。

## 2. 日期：统一写法不等于恢复时间

本包日期来自 2025 年，混合了 `2025-06-18 20:30:12`、`2025/6/18 20:30`、`2025年6月18日`。先将中文年月日和斜线统一，再明确告诉 pandas 每行可能有不同格式。

```python
date_text = (work["下单时间"].astype("string").str.strip()
             .str.replace("年", "-", regex=False)
             .str.replace("月", "-", regex=False)
             .str.replace("日", "", regex=False)
             .str.replace("/", "-", regex=False))
parsed_time = pd.to_datetime(date_text, format="mixed", errors="coerce")
date_failed = work.loc[parsed_time.isna()].copy()
work["下单时间"] = parsed_time
work["日期"] = work["下单时间"].dt.normalize()
```

`NaT` 是日期时间中的缺失。`dt` 可以理解为“日期工具箱”；`normalize()` 把时分秒归零，适合按日汇总。不要把归零后的时间解释为顾客真的在午夜下单。

:::warn 信息损失要写在报告里
只剩年月日的记录解析后为 00:00:00，但原始小时、分钟和秒已经丢失；只有时分的记录也没有原秒数。统一格式不能凭空还原这些信息。因此本脏表适合日/月分析，不适合直接研究下单小时。也不能按排序位置推算丢失的分钟。
:::

本包没有 `03/04/2025` 这类日月顺序含糊的来源。遇到跨地区日期，先询问格式约定、时区与业务日边界；`format="mixed"` 不是替你确定这些语义。

## 3. 文本：先去空白，再按已知映射统一

```python
work["城市"] = (work["城市"].astype("string")
                 .str.strip().str.removesuffix("市"))
platform_alias = {
    "taobao": "淘宝", "TB": "淘宝", "微信": "微信小程序",
    "小程序": "微信小程序", "抖音": "抖音小店", "douyin": "抖音小店"
}
work["平台"] = work["平台"].str.strip().replace(platform_alias)
work["订单状态"] = work["订单状态"].str.strip().replace(
    {"完成": "已完成", "退款": "已退款"}
)
print(work["平台"].value_counts(dropna=False))
```

`strip()` 去掉首尾空白，不会改正文。`removesuffix("市")` 只处理结尾，而不是删除名称中所有“市”字。本模拟文件明确把“上海市”和“上海”当作同一个城市，所以规则成立；现实数据需要规范城市字典，不能把所有地名机械截短。映射表也是本案例约定，“微信”在其他数据里可能是营销来源而非支付平台。

:::tip 不认识的值应该冒出来
用 `value_counts(dropna=False)` 检查统一后的所有取值。`replace()` 会保留未匹配值，便于发现新的别名；不要把未知平台默认归到淘宝。对文本先清空白，再映射，也能正确处理本文件的“淘宝 ”。
:::

## 4. 异常：统计上的少见，不是业务上的无效

999 件可能是录入错，也可能是团购；一个高金额订单可能只是购买昂贵商品。箱线图上的点也不自动是错误。本课采用**明确标注的练习业务假设**：数量应在 1～20 且为整数，评分应在五分制 1～5。超范围先进入复核流程，规则不是对现实订单的实证判断。

```python
quantity = pd.to_numeric(work["数量"], errors="coerce")
quantity_issue = (quantity.isna() | ~quantity.between(1, 20)
                  | quantity.mod(1).ne(0))
rating = pd.to_numeric(work["评分"], errors="coerce")
rating_issue = rating.notna() & ~rating.between(1, 5)
review = work.loc[quantity_issue | rating_issue].copy()
review["数量待核对"] = quantity_issue.loc[review.index]
review["评分越界"] = rating_issue.loc[review.index]
print("数量问题：", quantity_issue.sum())
print("已有评分越界：", rating_issue.sum())
```

括号包住每个条件，用 `|` 表示“或者”；pandas 的列条件不使用 Python 的 `or`。数量缺失需要复核，而评分缺失仍是“没有观察”，所以 `rating_issue` 必须先限定 `notna()`。

如果某张销量图临时只使用符合假设的订单，图下注明排除了什么、排除了多少行，并保留 `review`。做评分分析时，可以另建 `valid_rating = rating.where(rating.between(1, 5))`，保留原评分与越界标记。不要把越界评分改成边界值，更不要因为评分问题删掉整笔金额。

## 5. 四个练习

:::try 练习 1：金额转数值
从去重后的原始金额列生成数值列，并统计非空输入的解析失败数。
:::fold 提示与答案
按上文先移除 `￥` 与 `元`，再 `pd.to_numeric(..., errors="coerce")`。本包这些格式可解析，但仍必须运行失败检查。不要直接 `astype(float)` 处理 `￥39.00`。
:::
:::

:::try 练习 2：统一日期
解析混合日期并计算共有多少个不同月份。说明为什么不据此报告“最热门下单小时”。
:::fold 参考答案
统一分隔符后用 `pd.to_datetime(..., format="mixed", errors="coerce")`，再用 `.dt.to_period("M").nunique()`。中文日期已丢掉小时，解析出的 00:00 不是真实观察。
:::
:::

:::try 练习 3：统一标签
独立创建仅含“城市、平台、订单状态”的新表，统一空白、后缀和已知别名。
:::fold 参考答案
先选择三列并 `.copy()`，再分别执行上文规则。完成后查看取值集合，预期本包平台只有淘宝、微信小程序、抖音小店；不要把未匹配值偷偷删除。
:::
:::

:::try 练习 4：隔离数量问题
从去重后的原始记录中选出数量缺失、不在 1～20 或非整数的行，保留所有原列。另用一句话解释隔离不代表判定无效。
:::fold 参考答案
`q = pd.to_numeric(unique["数量"], errors="coerce")`，随后 `unique.loc[q.isna() | ~q.between(1, 20) | q.mod(1).ne(0)].copy()`。这是本案例规则下的待复核集合；需要业务依据才能修复或排除。
:::
:::

:::quiz
`errors="coerce"` 成功运行后，最重要的下一步是？
- [ ] 认为所有数据已经正确
- [x] 检查解析失败的位置并保留原值
- [ ] 把新缺失全部填 0
---
不抛异常只说明程序继续运行，不代表源数据问题消失。
:::

## 6. 排错与验收

| 症状 | 纠正路径 |
|---|---|
| `ValueError: could not convert ...` | 先清理已知符号，再使用数值解析并记录失败 |
| `.dt` 提示只适用于日期 | 检查 `pd.to_datetime` 的结果是否赋回，确认列类型 |
| `truth value ... ambiguous` | 列条件用带括号的 `&`、`|`，不用 `and`、`or` |
| 修改列出现链式赋值问题 | 在副本上直接赋列，用 `.loc`，不写连续索引赋值 |

:::job
可在作品中放一张“问题—规则—影响行数—处理动作”的质量表。面试时说明规则来自本模拟案例，金额、销量、评分分别使用不同有效字段范围。这体现可复核的分析习惯，不是用删除数据把结果变好看。
:::

:::checklist 本课验收
- [ ] 金额变成数值，解析失败表仍保留。
- [ ] 混合日期可按月统计，报告明确时间精度限制。
- [ ] 已知文本别名统一，未知值有核对入口。
- [ ] 数量与评分按字段分别标记，缺失评分不判为越界。
- [ ] 能指出 1～20 只是本课假设，不自动套用到其他行业。
:::
