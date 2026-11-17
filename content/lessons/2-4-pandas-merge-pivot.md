---
summary: 用编号安全补商品和客户资料，再把明细汇总成品类×平台的透视表。
prereq: 已完成第 2-3 课，能筛已完成订单、分组并说明金额口径
---

:::goal 本课验收目标
- 识别订单、商品、客户的匹配键，不按行位置拼表。
- 用left merge和many_to_one验证多对一关系，检查行数与未匹配。
- 用pivot_table指定sum与fill_value，理解重复组合需要聚合。
- 完成4题，透视合计与合并前已完成金额一致。
:::

打开 [2-4 练习本](../../notebooks/2-4_pandas_merge_pivot.ipynb)，保持原目录，选 `Python (da-course)`。先运行准备格，读年度orders.csv、products.csv、customers.csv。订单15115行，一行一订单一个商品；商品33行，一行一个商品；客户3000行，一行一个模拟客户。并不是“这三张表行数差不多就可以并排粘贴”。

## 1. 先认识关系：一条主表资料被很多订单使用

订单有product_id，但没有商品名称、品类；商品表用同一个product_id记录名称、品类。订单有customer_id，客户表用同一个customer_id记录城市、来源渠道。这个共享编号叫匹配键（key）。书名、姓名或第几行都不能替代稳定编号。

:::df 第一笔订单如何找到商品资料
| 表 | 匹配键 | 已有资料 |
|---|---|---|
| 订单 SG25000001 | product_id=P006 | 数量2，实付24元 |
| 商品主表中的P006 | product_id=P006 | 商品名称诗词胶带，品类文具 |
| 合并后的同一笔订单 | product_id=P006 | 数量2，实付24元，诗词胶带，文具 |
:::

:::cards
:::card many_to_one：多对一
多笔订单可购买同一个商品，商品主表每个product_id只能出现一次；多笔订单也可属于一个客户，客户主表编号只能出现一次。
:::
:::card one_to_one：一对一
两边键都唯一，才是一对一。本课订单对商品不是这个关系，不要因为只有一个商品字段就误判。
:::
:::card many_to_many：多对多
两边同一个键都出现多次，可能配成很多组合，使订单行数和金额膨胀。没有明确业务需要，不接受这种结果。
:::
:::

工作中这个关系也叫“基数”（cardinality）：一个键在两侧允许对应多少条记录。本课只要能够说清“多个订单，对应主表一条资料”，就能理解验证的意义。

## 2. merge分格做：先准备右表，再补字段

```python
completed = orders.loc[orders["status"] == "已完成"].copy()
product_lookup = products[["product_id", "product_name", "category"]]
```

输入年度订单与33行商品主表。先保留13996条已完成订单，再从右表只取键、名称、品类。这里不取商品price，因为订单已带成交时unit_price；两列不能只因名字像就当同一业务口径。少取无关列也能避免同名列被自动加后缀。

```python
enriched = completed.merge(
    product_lookup,
    on="product_id",
    how="left",
    validate="many_to_one",
)
print(completed.shape)
print(enriched.shape)
enriched[["order_id", "product_name", "category", "pay_amount"]].head(3)
```

输入左表completed和右表product_lookup。`on`指定两边共用的键；`how="left"`保留每条左表订单，右边找不到资料就留缺失，而不是删掉订单；`validate="many_to_one"`要求右表每个键唯一。输出规模由 `(13996, 11)` 变 `(13996, 13)`：多两列但不多订单。

实际前三笔：SG25000001诗词胶带/文具/24，SG25000002猫咪图书馆托特包/帆布包/69，SG25000003宋词手账本/文具/90。金额没有因为加资料而改变。行数不变是必要检查，但不是唯一检查，还要看键和未匹配。

`left`与`inner`不同：inner只保留两边能找到的键，若商品表漏了一件，其订单会悄悄丢掉。在当前完整主表里可能结果一样，但不能因此说两种方式永远等价。分析前要明确“是否保留所有订单”的业务要求。

## 3. validate挡住重复主表造成的金额翻倍

```python
bad_lookup = pd.concat([product_lookup, product_lookup.head(1)], ignore_index=True)
try:
    completed.merge(bad_lookup, on="product_id", how="left", validate="many_to_one")
except pd.errors.MergeError:
    print("商品键重复，先检查主表；不要删validate绕过问题。")
```

输入商品主表加一条重复资料，右边P001出现两次。`pd.concat`在这里只是把两份表的行接在一起，`ignore_index=True`重新编行标签；它不是按商品键匹配。合并验证触发MergeError，捕获后显示中文。没有validate时，同一商品的订单可能复制两遍，金额被重复累计。

本段只用于展示故障，不要求你把concat当新重点。看懂“主表重复→一条订单匹配两次→合计膨胀”即可。遇到报错先定位重复编号，核对来源，不能随便删一条记录让代码变绿。

## 4. 未匹配也要看：indicator让问题显形

完整数据的商品键都能匹配。为了练排查，临时从商品清单移除P006，原始CSV不改写。

```python
partial_lookup = product_lookup.loc[product_lookup["product_id"] != "P006"]
audit = completed.merge(
    partial_lookup,
    on="product_id",
    how="left",
    validate="many_to_one",
    indicator=True,
)
unmatched = audit.loc[audit["_merge"] == "left_only", ["order_id", "product_id", "pay_amount"]]
print(unmatched.shape)
unmatched.head(2)
```

输入少了P006的右表和全部已完成订单。indicator新增 `_merge` 列，`both`表示两边找到，`left_only`表示只在左边有。实际未匹配352行3列；第一笔SG25000001/P006/24就在其中。left合并仍保留13996条订单，未匹配的名称、品类缺失，不能说“未匹配金额为0”。

这里用缺失的匹配信息诊断，不是给订单贴“坏数据”标签。实际业务可能是主表漏导、编号空格、类型不同或商品下架。先查根因，不拿inner把问题藏起来。对完整主表同样可加indicator，当前应为0条left_only。

## 5. 再按客户键补城市与来源

```python
customer_lookup = customers[["customer_id", "city", "channel"]]
with_customers = enriched.merge(
    customer_lookup,
    on="customer_id",
    how="left",
    validate="many_to_one",
)
with_customers[["order_id", "city", "channel"]].head(3)
```

输入已补商品的订单与3000行客户主表，按customer_id多对一补两列。仍是13996行，现在15列。实际前三笔城市/渠道是兰州/抖音、杭州/小红书、长沙/小红书。注意客户channel是客户来源，订单platform是下单平台，两列不是一回事：来源于抖音的客户可以在微信小程序下单。

:::warn 合并后的成本也不是净利润
若以后补cost，每件成本需要乘quantity；即便实付减商品成本，也只近似商品毛利，还没扣平台、物流、人工。当前课不做“净利润”计算。不要为了讲merge而给一个未过滤退款的总金额贴上营收标签。
:::

## 6. 数据透视：品类作行，平台作列，金额填格子

```python
category_platform = enriched.pivot_table(
    index="category",
    columns="platform",
    values="pay_amount",
    aggfunc="sum",
    fill_value=0,
)
category_platform
```

输入13996条已完成且已补品类的订单。index决定结果行，columns决定结果列，values决定统计哪个数字，aggfunc决定同一组合多条订单如何合成一个值。这里用sum，因此不是平均金额；默认aggfunc通常为mean，不能省略后仍称合计。

:::df 当前透视结果：已完成订单实付金额，单位元
| category | 微信小程序 | 抖音小店 | 淘宝 |
|---|---:|---:|---:|
| 书籍 | 90498.4 | 66129.0 | 143841.3 |
| 帆布包 | 96457.2 | 74698.5 | 128765.2 |
| 徽章 | 39641.3 | 29604.7 | 59983.4 |
| 文具 | 76173.9 | 60917.3 | 113933.8 |
| 日历 | 51624.5 | 35767.4 | 74305.7 |
| 明信片 | 33384.4 | 23575.5 | 50766.0 |
| 香薰 | 163856.4 | 134398.0 | 236049.2 |
:::

输出7行3列，category在索引，不是普通数值列；platform是列轴名称，不是多出来的一条记录。`fill_value=0`只把透视中没有记录的组合填0，便于读表；它不会修好未匹配商品资料，也不应该拿来把缺失评分变0。当前全年每个品类平台组合都有记录，所以这份表没有需要补0的格子。

```python
print(category_platform.sum().sum())
print(completed["pay_amount"].sum())
```

输入透视与合并前明细，第一个sum按列汇总、第二个再合计各列。两者都约为1784371.10，浮点尾数可能略有差异。只看合计一致仍不保证分类绝对正确，但若合计变大，应查键重复；若变小，应查未匹配品类或筛选范围。透视默认可能不展示缺失分组键，所以必须先做未匹配审计。

```python
try:
    enriched.pivot(index="category", columns="platform", values="pay_amount")
except ValueError:
    print("同一品类与平台有多笔订单，用pivot_table明确聚合方式。")
```

输入有重复品类平台组合的明细，pivot不能把多笔数值塞进同一格，触发ValueError。pivot_table的sum是**按业务组合汇总多笔订单**，不是删除重复订单。整行重复的清洗留到下一阶段，不能混用概念。

:::quiz
left merge时找不到商品资料，正确做法是什么？
- [ ] 订单会自动消失，所以无需查
- [x] 保留订单并检查left_only，补查主表或编号问题
- [ ] 给金额填0，把它当没有销售
---
未匹配说明资料没对上，不说明订单不存在或金额为0。
:::

## 7. 四道独立练习

每题从orders、products、customers原始表独立处理；参考答案展开后逐格对照，不依赖上一题result。

:::try 2-4.1 商品资料合并
筛已完成订单，left合并商品的product_id、product_name、category，验证many_to_one，保留全部订单字段。
:::
:::fold 答案与输出
```python
work = orders.loc[orders["status"] == "已完成"].copy()
result = work.merge(products[["product_id", "product_name", "category"]],
    on="product_id", how="left", validate="many_to_one")
```
输入两表，输出13996行13列，订单数不变。
:::

:::try 2-4.2 再补客户资料
独立完成上一题要求的商品合并，再left合并客户的customer_id、city、channel，两次均验证many_to_one。
:::
:::fold 答案与输出
```python
work = orders.loc[orders["status"] == "已完成"].copy()
work = work.merge(products[["product_id", "product_name", "category"]],
    on="product_id", how="left", validate="many_to_one")
result = work.merge(customers[["customer_id", "city", "channel"]],
    on="customer_id", how="left", validate="many_to_one")
```
输入三表，输出13996行15列，城市与来源不等于下单平台。
:::

:::try 2-4.3 找出缺失商品资料的订单
临时从商品主表移除P006，按已完成订单left merge并加indicator。只返回left_only的order_id、product_id、pay_amount三列，保持原订单顺序。
:::
:::fold 答案与输出
```python
work = orders.loc[orders["status"] == "已完成"].copy()
partial = products.loc[products["product_id"] != "P006", ["product_id", "product_name", "category"]]
audit = work.merge(partial, on="product_id", how="left",
    validate="many_to_one", indicator=True)
result = audit.loc[audit["_merge"] == "left_only", ["order_id", "product_id", "pay_amount"]]
```
输入缺项主表，保留未匹配订单，输出352行3列。不是把全部订单都删掉。
:::

:::try 2-4.4 品类平台透视
从原表筛已完成订单并补品类，按category×platform汇总pay_amount，明确sum、fill_value=0。提交带category索引的透视表，不转成长表。
:::
:::fold 答案与输出
```python
work = orders.loc[orders["status"] == "已完成"].copy()
work = work.merge(products[["product_id", "category"]],
    on="product_id", how="left", validate="many_to_one")
result = work.pivot_table(index="category", columns="platform",
    values="pay_amount", aggfunc="sum", fill_value=0)
```
输入已完成明细，输出7行3列透视，总金额1784371.10。
:::

## 排错与求职表达

| 报错或异常 | 先检查 |
|---|---|
| MergeError | 右侧主表键是否重复，many_to_one是否符合业务 |
| KeyError: product_id | 两表是否都有指定键，是否误读了Excel工作表 |
| 名称出现_x、_y | 左右有同名非键列；先明确各字段来源，少取无关列 |
| 合并后行数增加 | 键基数是否错，不能删除validate继续汇总 |
| 透视金额减少 | 未匹配的品类是否被遗漏，状态范围是否一致 |
| pivot重复组合报错 | 多笔订单需要pivot_table并指定aggfunc |

:::job 面试要说“安全合并”，不只说会merge
你可以展示：确认一行粒度→选择共享编号→明确left保留范围→验证主表键唯一→查未匹配→核对行数金额→做透视。说明数据全为模拟，结果用于练习。这个过程体现数据质量意识，比拼出一张大表更有价值。
:::

:::checklist 验收
- [ ] 我能解释订单对商品、订单对客户为何是多对一。
- [ ] 我知道left与inner何时会丢不同记录。
- [ ] 我能用validate和indicator发现两类不同问题。
- [ ] 我能解释pivot_table的行、列、值、聚合四个参数。
- [ ] 四题通过，透视合计与已完成明细一致。
:::

下一阶段：[缺失值与重复值](lesson:3-1)。
