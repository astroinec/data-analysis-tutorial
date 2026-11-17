# 2-3 新增列与分组统计

选择Python (da-course)，原位置打开。本课先copy保留原表，再算整列，再分组。订单只用2025全年CSV；**已完成订单实付金额不是净利润**，退款不能当已保留销售。

```python
import sys
sys.path.insert(0, "..")
from dacheck import check, hint, setup_chinese_font
import pandas as pd
```

输入两张原始CSV，读取后检查规模。练习彼此独立，只读这些准备变量。

```python
books = pd.read_csv("../data/books.csv")
orders = pd.read_csv("../data/shop/orders.csv")
print(books.shape)
print(orders.shape)
```

输出(200,10)、(15115,11)。订单一行一订单一个商品，quantity是件数而非订单数。

+++
## copy与整列乘法

输入原始books，copy出工作表，给每行price乘2，新增two_book_price。

```python
books_calc = books.copy()
books_calc["two_book_price"] = books_calc["price"] * 2
books_calc[["title", "price", "two_book_price"]].head(3)
```

实际月光与我177.8、雨夜的孩子73.8、故园往事161.0。整列计算不用逐行for。

+++
### 处理前后规模

输入原始与工作表，分别看shape。

```python
print(books.shape)
print(books_calc.shape)
```

输出(200,10)和(200,11)。copy保护原表；没有写回磁盘。working=books不是独立副本，不能当copy替代。

+++
## 先筛已完成再新增订单原价

输入年度订单，状态明确过滤，copy后新增original_amount。

```python
completed = orders.loc[orders["status"] == "已完成"].copy()
completed["original_amount"] = completed["unit_price"] * completed["quantity"]
completed[["order_id", "original_amount", "pay_amount"]].head(3)
```

13996条已完成。前三笔原价与实付都是24、69、90。不能连写orders[mask][新列]=...，pandas3使用Copy-on-Write，不靠忽略警告修链式赋值。

+++
### 新增优惠金额

输入已完成原价与实付列，逐行相减。

```python
completed["discount_amount"] = completed["original_amount"] - completed["pay_amount"]
completed.loc[completed["discount"] == 0.1,
    ["order_id", "original_amount", "pay_amount", "discount_amount"]].head(1)
```

SG25000039原价110、实付99、优惠11。discount=0.1是减10%，保留90%。

+++
### 两种状态金额不能混叫营收

输入已完成与退款两种范围，分别合计字段。

```python
print(completed["pay_amount"].sum())
print(orders.loc[orders["status"] == "已退款", "pay_amount"].sum())
```

输出1784371.1与144029.9。退款1119单的字段金额不能再视为已保留销售。已完成金额也未扣成本、平台费、物流、人工，不叫净利润。

+++
## groupby分堆，size数每组行

输入books，按category分组，对book_id数行。

```python
category_counts = books.groupby("category")["book_id"].size()
print(category_counts)
```

输出历史35、哲学20、小说64、心理22、科普22、经济23、诗歌14，合计200。groupby本身只是分组，size才执行统计。

+++
### 各品类均价

输入每组price，mean求均值，round只用于显示。

```python
category_mean = books.groupby("category")["price"].mean()
print(category_mean.round(2))
```

实际历史81.21、哲学60.45、小说62.96、心理57.05、科普59.88、经济61.27、诗歌39.94。不是读者喜好的证据。

+++
## agg同时给多个指标命名

输入books，category保留普通列；新列book_count对book_id size，新列mean_price对price mean。

```python
book_summary = books.groupby("category", as_index=False).agg(
    book_count=("book_id", "size"),
    mean_price=("price", "mean"),
)
book_summary.round(2)
```

输出7行3列DataFrame。括号内两项为来源字段、统计动作，不是参数函数。原始精度保留，展示可round。

+++
## 平台已完成订单指标

输入已完成明细，按platform分堆，算行数、实付合计、每单均值。

```python
platform_summary = completed.groupby("platform", as_index=False).agg(
    order_count=("order_id", "size"),
    completed_amount=("pay_amount", "sum"),
    mean_order=("pay_amount", "mean"),
)
platform_summary.round(2)
```

实际微信4299单/551636.10/128.32，抖音3255单/425090.40/130.60，淘宝6442单/807644.60/125.37。数量与金额可对回总表。

+++
### size与count：评分缺失会影响count

输入同一已完成范围，比较行数与评分非空数。只做观察，不让你把缺失评分改零。

```python
print(completed.shape[0])
print(completed["rating"].count())
```

第一项13996，第二项8146，因为5850笔已完成订单未评分。count数非空，size数行；quantity.sum是件数。每单平均实付也不是每客户平均消费。

+++
## 练习2-3.1 复制并新增两本书价

从books复制，只新增two_book_price=price*2，保留全部原列。

```python
### BEGIN SOLUTION
result = books.copy()
result["two_book_price"] = result["price"] * 2
### STUDENT
result = ...
### END SOLUTION
check("2-3.1", result)
```

输入200行10列，结果200行11列。不要引用示范books_calc或前题result。

+++
## 练习2-3.2 图书品类汇总

category为普通列，book_count用book_id size，mean_price用price mean。提交未round的结果。

```python
### BEGIN SOLUTION
result = books.groupby("category", as_index=False).agg(
    book_count=("book_id", "size"),
    mean_price=("price", "mean"),
)
### STUDENT
result = ...
### END SOLUTION
check("2-3.2", result)
```

输出7行3列，数量合计200，不要求你按均价排名。

+++
## 练习2-3.3 已完成订单原价列

独立筛orders已完成并copy，只新增original_amount，不加discount_amount。

```python
### BEGIN SOLUTION
result = orders.loc[orders["status"] == "已完成"].copy()
result["original_amount"] = result["unit_price"] * result["quantity"]
### STUDENT
result = ...
### END SOLUTION
check("2-3.3", result)
```

输出13996行12列。状态、原字段、计算结果都要对。

+++
## 练习2-3.4 平台汇总

独立从orders筛已完成，按platform算order_count(size)、completed_amount(sum)、mean_order(mean)。不要用含示范额外列的result。

```python
### BEGIN SOLUTION
work = orders.loc[orders["status"] == "已完成"].copy()
result = work.groupby("platform", as_index=False).agg(
    order_count=("order_id", "size"),
    completed_amount=("pay_amount", "sum"),
    mean_order=("pay_amount", "mean"),
)
### STUDENT
result = ...
### END SOLUTION
check("2-3.4", result)
```

输出3行4列，金额1784371.10。提交原精度，round只是给人看。

+++
## 验收与排错

- 四题通过，能解释copy、整列运算、分组与聚合。
- size数记录，count数非空，quantity.sum数件数。
- 分组键缺列查as_index=False；只显示分组对象要再执行agg/size/mean。
- 不用链式赋值，不通过关闭警告绕过问题。
- 已完成实付口径明确；没有把退款纳入已保留销售，没有称为净利润。

求职表达：保留原表→明确状态→新增列→按平台汇总→核对数量金额。模拟数据不能伪称真实业绩。下课补商品/客户资料并透视。
