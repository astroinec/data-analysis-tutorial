# 2-4 合并表格与数据透视

从原notebooks目录打开，选择Python (da-course)。模拟文创店订单一行一订单、一个商品；商品与客户为主表。先确认共享编号和多对一关系，再合并。全课金额范围只含已完成订单，不是净利润。

```python
import sys
sys.path.insert(0, "..")
from dacheck import check, hint, setup_chinese_font
import pandas as pd
```

输入2025年度CSV，不用Excel前3000行样本。每份主表键应唯一，订单中可以重复出现同一个商品/客户编号。

```python
orders = pd.read_csv("../data/shop/orders.csv")
products = pd.read_csv("../data/shop/products.csv")
customers = pd.read_csv("../data/shop/customers.csv")
print(orders.shape, products.shape, customers.shape)
```

观察(15115,11)、(33,6)、(3000,7)。行数不同不能按行位置粘贴，要按product_id/customer_id匹配。

+++
## 准备左表和右侧资料

输入全部订单，先筛已完成并copy；右侧仅取键、名称、品类。

```python
completed = orders.loc[orders["status"] == "已完成"].copy()
product_lookup = products[["product_id", "product_name", "category"]]
print(completed.shape)
product_lookup.head(2)
```

左表13996行11列，右表33行3列。很多订单可以买同一商品，右表每个商品只一条，叫many_to_one（多对一基数）。

+++
## left merge：保留每条左订单

输入左已完成订单和右商品资料。on为共享键，left保留左表，validate验证右表唯一。

```python
enriched = completed.merge(
    product_lookup,
    on="product_id",
    how="left",
    validate="many_to_one",
)
print(enriched.shape)
```

结果13996行13列，多2列不多订单。不能因为本次inner也许相同就说两者等价；右表缺资料时inner会删左订单。

+++
### 实际补到了什么

输入合并结果，选择订单编号、商品、品类、实付预览。

```python
enriched[["order_id", "product_name", "category", "pay_amount"]].head(3)
```

实际SG25000001诗词胶带/文具/24，SG25000002猫咪图书馆托特包/帆布包/69，SG25000003宋词手账本/文具/90。按编号匹配，不是按商品表第几行。

+++
## 主表重复会造成一对多膨胀

临时把商品第一条再接一次，故意重复P001。concat这里只拼接行，用于造故障，不是merge替代品。

```python
bad_lookup = pd.concat([product_lookup, product_lookup.head(1)], ignore_index=True)
try:
    completed.merge(bad_lookup, on="product_id", how="left", validate="many_to_one")
except pd.errors.MergeError:
    print("右表商品键重复，先核查主表；不要删除validate绕过。")
```

看到中文提示，未捕获内部长错。如果删validate，P001订单可能配两次、金额重复算。错误的多对多不是“更完整”。

+++
## 完整主表也查未匹配

输入完整右表，indicator新增_merge区分匹配状态。

```python
full_audit = completed.merge(product_lookup, on="product_id", how="left",
    validate="many_to_one", indicator=True)
print(full_audit.loc[full_audit["_merge"] == "left_only"].shape[0])
```

当前未匹配0行；both表示两边找到，left_only只在左侧。验证唯一不代表一定匹配，两个检查各管一种问题。

+++
### 临时移除P006来练未匹配诊断

输入少一件商品的右表，left仍保留全部13996单。

```python
partial_lookup = product_lookup.loc[product_lookup["product_id"] != "P006"]
audit = completed.merge(partial_lookup, on="product_id", how="left",
    validate="many_to_one", indicator=True)
unmatched = audit.loc[audit["_merge"] == "left_only", ["order_id", "product_id", "pay_amount"]]
print(audit.shape[0])
print(unmatched.shape)
unmatched.head(2)
```

输出13996和(352,3)，第一笔SG25000001/P006/24在未匹配中。名称/品类缺失不等于订单金额0，也不要改inner藏掉它。原CSV没有改变。

+++
## 再按客户编号补资料

输入补商品表与客户键、城市、来源。仍多对一，不把来源channel与下单platform混用。

```python
customer_lookup = customers[["customer_id", "city", "channel"]]
with_customers = enriched.merge(customer_lookup, on="customer_id", how="left",
    validate="many_to_one")
print(with_customers.shape)
with_customers[["order_id", "city", "channel", "platform"]].head(3)
```

结果13996行15列。前三笔城市/渠道：兰州/抖音，杭州/小红书，长沙/小红书。第一笔来源抖音却在微信小程序下单，两种字段含义不同。

+++
## pivot_table：行、列、值、聚合四项

输入已完成且补品类的明细。category作行标签，platform作列，pay_amount是格内统计字段，sum明确合计多笔订单。

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

输出7行3列透视。书籍微信90498.4/抖音66129.0/淘宝143841.3；香薰163856.4/134398.0/236049.2。所有格为已完成实付合计（元）。category是索引，platform是列轴名，不是新记录。

fill_value=0只填没有订单组合的透视空格，当前全年7×3都有订单，不需要补0。它不会修未匹配品类，也不能用来把评分缺失变0。默认aggfunc常是mean，所以本题sum不能省。

+++
### 核对总金额

输入透视结果与合并前明细，透视先按列加、再把各列加起来。

```python
print(category_platform.sum().sum())
print(completed["pay_amount"].sum())
```

两者约1784371.10，浮点尾数可能不同。合计变大查主表键重复，变小查未匹配品类被透视遗漏或过滤范围不同。合计一致是检查之一，不代表全部分类必然正确。

+++
## pivot不能自动聚合重复组合

输入多笔同品类/平台明细，pivot无法把多个值放一格，故意捕获ValueError。

```python
try:
    enriched.pivot(index="category", columns="platform", values="pay_amount")
except ValueError:
    print("同一品类与平台有多笔订单；pivot_table指定sum进行汇总。")
```

重复组合是正常多笔业务，不等于整行重复数据。pivot_table汇总，不是删除重复订单。

+++
## 练习2-4.1 补商品资料

独立筛已完成订单，left merge商品product_id、product_name、category，validate=many_to_one。保留全部订单列，不要带商品price/cost。

```python
### BEGIN SOLUTION
work = orders.loc[orders["status"] == "已完成"].copy()
result = work.merge(products[["product_id", "product_name", "category"]],
    on="product_id", how="left", validate="many_to_one")
### STUDENT
result = ...
### END SOLUTION
check("2-4.1", result)
```

结果13996行13列，金额未改变。

+++
## 练习2-4.2 独立补商品再补客户

不要依赖上一题result。先按商品键补名称品类，再按客户键补city/channel，两次left、多对一。

```python
### BEGIN SOLUTION
work = orders.loc[orders["status"] == "已完成"].copy()
work = work.merge(products[["product_id", "product_name", "category"]],
    on="product_id", how="left", validate="many_to_one")
result = work.merge(customers[["customer_id", "city", "channel"]],
    on="customer_id", how="left", validate="many_to_one")
### STUDENT
result = ...
### END SOLUTION
check("2-4.2", result)
```

结果13996行15列，来源渠道和下单平台分别保留。

+++
## 练习2-4.3 找未匹配商品订单

独立从商品主表暂移除P006；left merge加indicator；只取left_only的order_id、product_id、pay_amount，保持订单原顺序。

```python
### BEGIN SOLUTION
work = orders.loc[orders["status"] == "已完成"].copy()
partial = products.loc[products["product_id"] != "P006", ["product_id", "product_name", "category"]]
audit = work.merge(partial, on="product_id", how="left",
    validate="many_to_one", indicator=True)
result = audit.loc[audit["_merge"] == "left_only", ["order_id", "product_id", "pay_amount"]]
### STUDENT
result = ...
### END SOLUTION
check("2-4.3", result)
```

结果352行3列。未匹配金额依然是原订单值，不填0。

+++
## 练习2-4.4 品类平台透视

独立筛已完成、补category，透视category×platform、pay_amount sum、fill_value=0。保留category索引，不reset_index。

```python
### BEGIN SOLUTION
work = orders.loc[orders["status"] == "已完成"].copy()
work = work.merge(products[["product_id", "category"]],
    on="product_id", how="left", validate="many_to_one")
result = work.pivot_table(index="category", columns="platform",
    values="pay_amount", aggfunc="sum", fill_value=0)
### STUDENT
result = ...
### END SOLUTION
check("2-4.4", result)
```

结果7行3列，合计1784371.10，严格按已完成口径。

+++
## 验收、排错与面试

- 四题通过；原始CSV未写回。
- 能解释订单对商品/客户多对一；left保留左表，inner可能删除未匹配。
- MergeError查右表键重复，不删validate；KeyError查文件与字段；_x/_y查同名非键来源。
- 指标金额没有重复累计，未匹配有主动审计。
- pivot_table明确sum，不把重复组合与重复整行混淆，fill_value不替代清洗。

面试讲安全合并的输入、键、基数、保留范围、未匹配和金额核对；数据均是模拟，不声称真实企业结果，也不把实付减成本直接叫净利润。下一阶段处理缺失与整行重复。
