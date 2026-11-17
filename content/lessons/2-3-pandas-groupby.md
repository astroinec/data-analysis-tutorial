---
summary: 先保留原始表，再新增计算列，把记录按品类或平台汇总成小表。
prereq: 已完成第 2-2 课，能多条件筛选与排序
---

:::goal 本课可验证目标
- 用copy保留原表，在明确的新表上增加列，不做链式赋值。
- 用整列运算计算两本书价格、订单原价金额。
- 用groupby和agg统计每组行数、金额合计、均值。
- 区分订单数与件数，区分已完成金额与含退款的字段合计。
:::

打开 [2-3 练习本](../../notebooks/2-3_pandas_groupby.ipynb)，选 `Python (da-course)`，先读books和orders两张原始CSV。图书一行一本书；订单一行一订单、一个商品，quantity表示该商品买了几件。所有数据虚构，订单范围是2025年全年15115行，不用Excel前3000行样本代替。

## 1. 新增列：同一公式，作用到整列

上一阶段需要for逐项累加，是为了理解步骤。pandas常用整列运算：每一行的值自动按行标签对齐，不需要你写200次乘法。

```python
books_calc = books.copy()
books_calc["two_book_price"] = books_calc["price"] * 2
books_calc[["title", "price", "two_book_price"]].head(3)
```

输入200行10列books，先copy创建独立的工作表，再为每本书单价乘2，存到新列two_book_price。实际前三行：月光与我88.9→177.8，雨夜的孩子36.9→73.8，故园往事80.5→161.0。books_calc变成11列，books仍有10列，磁盘原始CSV也没被改写。

:::df 从一列到新增计算列
| title | price | two_book_price |
|---|---:|---:|
| 月光与我 | 88.9 | 177.8 |
| 雨夜的孩子 | 36.9 | 73.8 |
| 故园往事 | 80.5 | 161.0 |
:::

`copy()`不是保存文件，也不是为了“让电脑更快”，而是明确原始表与工作表边界。`working = books` 只是给同一个对象多贴一个名字，直接修改时可能一起变。学会先保留原表，日后更容易回头核对处理前后。

## 2. 先定义订单口径，再开始算钱

`pay_amount`是下单时计算的实付字段；数据中还有 `status=已退款`。不能把所有行的pay_amount一加，就叫“全年营收”或“净利润”。本课使用口径：**仅已完成订单的实付金额合计**。它仍未扣平台费、物流、人工等费用，不是净利润。

```python
completed = orders.loc[orders["status"] == "已完成"].copy()
completed["original_amount"] = completed["unit_price"] * completed["quantity"]
completed["discount_amount"] = completed["original_amount"] - completed["pay_amount"]
completed[["order_id", "original_amount", "pay_amount", "discount_amount"]].head(3)
```

输入15115行全年订单，先筛状态，得到13996行已完成订单；新增折扣前金额和优惠金额。前三笔都是无折扣：SG25000001原价24、实付24、优惠0；第二笔69、69、0；第三笔90、90、0。新列是逐行计算，不是把全表单价乘全表数量合计。

```python
print(completed["pay_amount"].sum())
print(orders.loc[orders["status"] == "已退款", "pay_amount"].sum())
```

输入两个不同状态范围，分别合计字段。当前数据结果为1784371.1和144029.9。后一个是1119条退款订单的字段金额，**不能再算作已保留销售金额**。完整项目会更详细写口径，本课先把“数据范围决定数字含义”记住。优惠比例discount=0.1意味着减10%，不是减0.1元，也不是只付10%。

:::compare pandas 3.1.1避免链式赋值
:::bad `orders[orders["status"] == "已完成"]["original_amount"] = ...`
连着筛选和赋值，修改对象不明确。pandas 3启用Copy-on-Write，不要沿用旧教程里“忽略警告即可”的方法。
:::
:::good 先 `completed = orders.loc[...].copy()` 再新增列
工作表名字明确，先筛后改。若确实要修改原工作表的某些格，用一条loc赋值；本课以保留原表为优先。
:::
:::

## 3. groupby：先分堆，再每堆算一个数

:::analogy 给书架按品类分区
把历史书放一堆、小说放一堆，然后每堆数几本、平均多少钱。groupby只是“如何分堆”，sum、mean、size或agg才决定“每堆算什么”。它不等于先把表排序。
:::

```python
category_counts = books.groupby("category")["book_id"].size()
print(category_counts)
```

输入books，按category分组，选book_id列，每组数行。实际得到带品类索引的Series：历史35、哲学20、小说64、心理22、科普22、经济23、诗歌14。加起来200，与原表行数一致。`.size()`数每组记录数；不是“把编号相加”，编号是文字。

```python
category_mean = books.groupby("category")["price"].mean()
print(category_mean.round(2))
```

输入每组price，求均值，再仅为显示保留2位。历史81.21、哲学60.45、小说62.96、心理57.05、科普59.88、经济61.27、诗歌39.94。这里均价只描述这份模拟目录，不证明一个品类“更值得买”。如果算rating均值，默认跳过缺失评分；未评价不是0分，后面清洗课再展开。

## 4. agg：一张结果表装多个指标

```python
book_summary = books.groupby("category", as_index=False).agg(
    book_count=("book_id", "size"),
    mean_price=("price", "mean"),
)
book_summary.round(2)
```

输入同一200本图书，按品类分堆，两个命名聚合同时计算。`book_count=("book_id", "size")`读作“新列叫book_count，对book_id按组数行”；`mean_price`对price求均值。这里括号内的两项是一个元组参数，不是函数定义。

`as_index=False`让category保留为普通列，结果是7行3列DataFrame，适合后续导出或画图。不写时分组键通常成为索引，结果内容也许正确但形态不同。要明确题目要表格还是Series，不要只看输出长得像表就提交。

:::widget table-lab 小样本分组演示（不执行Python）
{"mode":"groupby"}
:::

网页只模拟固定小样本分组，不执行Python、不读取全年订单。你可以先体会分堆后表变短，再回Notebook验证真实随包模拟数据。

## 5. 工作里的分组：按平台统计已完成订单

```python
platform_summary = completed.groupby("platform", as_index=False).agg(
    order_count=("order_id", "size"),
    completed_amount=("pay_amount", "sum"),
    mean_order=("pay_amount", "mean"),
)
platform_summary.round(2)
```

输入已筛好的13996条已完成订单，按平台分组，算订单数、已完成实付合计、每单平均实付。输出3行4列：

:::df 当前CSV的实际结果：金额单位元
| platform | order_count | completed_amount | mean_order |
|---|---:|---:|---:|
| 微信小程序 | 4299 | 551636.10 | 128.32 |
| 抖音小店 | 3255 | 425090.40 | 130.60 |
| 淘宝 | 6442 | 807644.60 | 125.37 |
:::

订单数合计13996，金额合计1784371.10，可以与筛选后的总数核对。不要用 `quantity.sum()`代替订单数：一笔买5件仍是1单。`.count()`只数某列非空值，`.size()`数行；若用rating.count数订单，会遗漏未评分订单。每单平均金额也不是“每位客户平均消费”，客户可下多单，分母不同。

:::quiz
统计已完成订单数量，为什么用order_id的size而不是rating的count？
- [ ] 评分值太大
- [x] rating有缺失，count会少算未评分订单；size数记录行
- [ ] size会自动过滤退款
---
状态需要事先显式筛选，size本身不会替你判断退款口径。
:::

## 6. 四道独立练习

各题都从books或orders原始变量重新生成工作表，后题不会依赖前题的未作答变量。

:::try 2-3.1 新增两本书价
复制books，新列two_book_price等于price乘2；保留全部原始列，结果放result。
:::
:::fold 答案与观察
```python
result = books.copy()
result["two_book_price"] = result["price"] * 2
```
输入200行10列，新增计算列后200行11列，原始books不变。
:::

:::try 2-3.2 图书品类汇总
输出普通列category、book_count、mean_price。按category分组，数量用book_id的size、均价用price的mean。不要先四舍五入原价。
:::
:::fold 答案与观察
```python
result = books.groupby("category", as_index=False).agg(
    book_count=("book_id", "size"),
    mean_price=("price", "mean"),
)
```
输入图书全表，分堆求两项指标，输出7行3列，数量合计200。
:::

:::try 2-3.3 订单原价列
筛已完成订单并copy，只新增original_amount=unit_price乘quantity，保留全部原订单字段。
:::
:::fold 答案与观察
```python
result = orders.loc[orders["status"] == "已完成"].copy()
result["original_amount"] = result["unit_price"] * result["quantity"]
```
输入15115单，保留13996单，新增后12列。不要额外加本题没要求的discount_amount。
:::

:::try 2-3.4 平台汇总
独立从orders筛已完成，然后按平台产生order_count、completed_amount、mean_order，指标定义与上文一致。提交未round的结果。
:::
:::fold 答案与观察
```python
work = orders.loc[orders["status"] == "已完成"].copy()
result = work.groupby("platform", as_index=False).agg(
    order_count=("order_id", "size"),
    completed_amount=("pay_amount", "sum"),
    mean_order=("pay_amount", "mean"),
)
```
输入年度订单，先定状态范围再分组，输出3行4列，金额合计1784371.10。
:::

## 常见问题和求职用途

| 问题 | 纠正路径 |
|---|---|
| KeyError: 新列不存在 | 先运行创建工作表与新增列格，核对拼写 |
| 输出只有分组对象 | groupby之后还需要size/mean/agg等统计动作 |
| 数量比预期少 | 是否count了缺失评分；状态过滤是否一致 |
| 检查说少了category列 | 用as_index=False让分组键成为普通列 |
| 金额被叫作净利润 | 写清筛选口径，并列出没有扣除的费用 |

:::job 面试可以讲的一套步骤
“保留原始表→明确已完成状态→新增原价列→按平台汇总→核对订单数与金额合计”。这套说法比“我熟练掌握groupby”更有说服力。案例是模拟文创店，不应声称做出了真实销售增长，也不因为淘宝金额最高就推断平台更有效，平台订单基数不同。
:::

:::checklist 验收
- [ ] 我能解释copy保护的是哪一份表。
- [ ] 我知道整列运算不需要逐行for。
- [ ] 我能读懂命名聚合中的新列名、来源列、统计动作。
- [ ] 我能区分订单数、件数、评分人数和每单均值。
- [ ] 四题通过，报告金额口径明确排除退款。
:::

下一课：[给订单补商品资料并做数据透视](lesson:2-4)。
