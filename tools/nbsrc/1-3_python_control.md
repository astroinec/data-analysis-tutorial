# 1-3 条件、循环与函数

选择Python (da-course)，从原位置打开，逐格预测输出后运行。模拟图书的“至少2020年出版归新书”是练习规则，不是行业标准。本课不依赖上一课变量。

```python
import sys
sys.path.insert(0, "..")
from dacheck import check, hint, setup_chinese_font
import pandas as pd
```

## 准备独立练习输入

输入随包books.csv。读取与转换只是准备，2-1解释读表；这里观察前三本价格和书名。

```python
books = pd.read_csv("../data/books.csv")
first_prices = books.head(3)["price"].tolist()
first_books = books.head(3)[["title", "price"]].to_dict("records")
print(first_prices)
print(first_books)
```

价格88.9、36.9、80.5。first_books是三项列表，每项是一部书的字典。后题只读这些准备变量。

+++
## if/else：一条条件，两条路

输入2021，判断至少2020。冒号后缩进四格；else与if对齐。

```python
year = 2021
if year >= 2020:
    label = "新书"
else:
    label = "较早出版"
print(label)
```

实际输出新书。print在外层，不论走哪条分支都执行。

+++
### 换输入，走另一条路

输入2016，同一规则，预测较早出版。

```python
year = 2016
if year >= 2020:
    label = "新书"
else:
    label = "较早出版"
print(label)
```

观察输出较早出版。不需要先把label赋成某个猜测的值，因为两条分支都会给它结果。

+++
## elif：前面不满足，继续问

输入88.9，先问低于50，再问不超过80，剩下归高于80。50和80都在中档。

```python
price = 88.9
if price < 50:
    price_label = "低于50元"
elif price <= 80:
    price_label = "50至80元"
else:
    price_label = "高于80元"
print(price_label)
```

输出高于80元。满足一档就停止选择，不会输出所有档。

+++
## for逐项读取

输入三项书名列表，每轮一个title。观察循环执行三次。

```python
titles = ["月光与我", "雨夜的孩子", "故园往事"]
for title in titles:
    print(title)
```

实际三行书名按原顺序输出。titles是整个列表，title是本轮一个值。

+++
## 循环累计，初始化在外面

输入前三本价格，合计先为0，每轮加本次值。

```python
total = 0
for price in first_prices:
    total = total + price
    print("本轮累计：", total)
```

逐次观察88.9、125.8、206.3。这个print刻意在循环里帮助追踪。

+++
### 完成后输出一次

输入相同价格，初始化同格避免重复运行污染。print移到循环外。

```python
total = 0
for price in first_prices:
    total = total + price
print(total)
```

只输出最终206.3。若每轮把total设0，会只剩最后一本80.5。

+++
## 循环内条件筛选

输入first_books三本字典，空结果列表初始化一次。仅价格≤50时追加书名。

```python
cheap_titles = []
for book in first_books:
    if book["price"] <= 50:
        cheap_titles.append(book["title"])
print(cheap_titles)
```

输出['雨夜的孩子']。两层缩进分别属于循环和条件，输出仍是list。

+++
## 函数定义：预留三个参数

输入公式结构，没有具体订单。def给工具起名，return把结果交回，不直接显示。

```python
def discounted_total(unit_price, quantity, discount):
    amount = unit_price * quantity * (1 - discount)
    return amount
```

定义格运行没有输出正常。必须先定义才能在下格调用。

+++
### 调用：换输入，公式不变

输入第一笔订单12元、2件、无优惠，以及另一笔22元、5件、减10%。

```python
first_amount = discounted_total(12.0, 2, 0.0)
promo_amount = discounted_total(22.0, 5, 0.1)
print(first_amount)
print(promo_amount)
```

实际24.0、99.0。参数顺序对应单价、数量、减免比例；return的值才能保存继续使用。

+++
### 捕获参数没给齐的示范

故意只传一个参数，捕获TypeError不中断。

```python
try:
    discounted_total(22.0)
except TypeError:
    print("需要单价、数量、减免比例三个输入。")
```

应显示中文。你写函数若只print没有return，调用结果会是None；检查要求数值时会给中文指导。

+++
## 练习1-3.1 按年份分类

第三本2021年，用if/else产生新书或较早出版。至少2020归新书。result是字符串。

```python
### BEGIN SOLUTION
if 2021 >= 2020:
    result = "新书"
else:
    result = "较早出版"
### STUDENT
result = ...
### END SOLUTION
check("1-3.1", result)
```

输入2021，走第一支，结果新书。

+++
## 练习1-3.2 for求价格总和

独立使用first_prices；result在循环前设0，不借前题值。

```python
### BEGIN SOLUTION
result = 0
for price in first_prices:
    result = result + price
### STUDENT
result = ...
### END SOLUTION
check("1-3.2", result)
```

输入三个价格，结果206.3。

+++
## 练习1-3.3 循环筛选

first_books里价格≤50的书名保存到result列表，按原顺序。

```python
### BEGIN SOLUTION
result = []
for book in first_books:
    if book["price"] <= 50:
        result.append(book["title"])
### STUDENT
result = ...
### END SOLUTION
check("1-3.3", result)
```

输入三本资料，只有第二本满足，结果['雨夜的孩子']。

+++
## 练习1-3.4 写可复用函数

重新定义discounted_total(unit_price, quantity, discount)，返回折后金额。把函数本身交给result：result=discounted_total，**这里不加括号**。检查会用当前数据的多笔订单调用，不只测99。

```python
### BEGIN SOLUTION
def discounted_total(unit_price, quantity, discount):
    return unit_price * quantity * (1 - discount)
result = discounted_total
### STUDENT
result = ...
### END SOLUTION
check("1-3.4", result)
```

检查多个输入：例如12×2无折扣24、22×5减10%为99。不能固定return99或只print金额。

+++
## 验收与排错

- if和else对齐，冒号下四格缩进；别把=赋值当==比较。
- total初始化在循环前，筛选结果列表也初始化在循环前。
- 定义与调用不同，return与print不同。
- 四题全部通过。未答result=...不被后续示范拿去运算。
- IndentationError查缩进，NameError先运行准备/定义格，TypeError查参数与返回类型。

求职迁移：规则分类书单、核对模拟折扣订单。下一阶段整列表格交给pandas，不用手工为200行写长循环。
