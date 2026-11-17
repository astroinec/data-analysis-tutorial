# 1-1 变量与数据类型

从本文件原位置打开，选择 **Python (da-course)**。Python写在代码格，Shift+Enter运行。数据全部是教学模拟；本课验证Python 3.12.13、pandas 3.1.1。先读说明、预测输出，再运行。每题result独立，未答格运行会提示“还没作答”。

```python
import sys
sys.path.insert(0, "..")
from dacheck import check, hint, setup_chinese_font
import pandas as pd
```

## 准备少量真实随包值

输入是图书CSV与2025年度订单CSV。下面是准备代码，读文件写法将在2-1详细讲，不要求现在背下来。取前三本和第一笔减10%的订单，仅供核对后面数字。

```python
books = pd.read_csv("../data/books.csv")
orders = pd.read_csv("../data/shop/orders.csv")
books[["title", "year", "price"]].head(3)
```

观察前三本：月光与我/2016/88.9，雨夜的孩子/1991/36.9，故园往事/2021/80.5。head只显示，未改原表。

```python
promo_order = orders.loc[orders["discount"] == 0.1].head(1)
promo_order[["order_id", "unit_price", "quantity", "discount", "pay_amount"]]
```

观察SG25000039：22元、5件、减免比例0.1、实付99元。不要把0.1当一折。准备代码不用后面练习的result。

+++
## 一个名字，对应一个值

输入第一本书的书名与价格、购买数量。赋值不输出；print才显示。预测金额再运行。

```python
title = "月光与我"
price = 88.9
quantity = 2
print(title)
print(price * quantity)
```

实际书名为月光与我，金额177.8。`=`把右边结果交给左边名字，不是比较。

+++
### 重新赋值

输入数量2，先算旧数量加1再保存。预测结果应为3。

```python
quantity = 2
quantity = quantity + 1
print(quantity)
```

赋值改变内存里的名字，没有写回CSV。

+++
## 看类型，不只看数字长相

输入四个值，type查看类别。第二项是数字，第三项有引号是文字。

```python
print(type(2))
print(type(88.9))
print(type("88.9"))
print(type(True))
```

观察int、float、str、bool。True/False首字母大写，不加引号。

+++
### 同一个加号，两种含义

输入两段文字，先拼接；再输入数字做乘法。预测输出不同。

```python
print("88.9" + "2")
print(88.9 * 2)
```

观察88.92是字符串拼接，177.8才是两本金额。

+++
## 优惠比例和金额

输入核验过的订单单价22、5件、减免0.1。先算原价，再乘保留比例。

```python
unit_price = 22.0
quantity = 5
discount = 0.1
original_amount = unit_price * quantity
print(original_amount)
```

原价110.0。下一格输入这个原价与优惠比例，支付90%。

```python
pay_amount = original_amount * (1 - discount)
print(pay_amount)
print(discount * 100)
```

实付99.0，优惠百分数数值10.0。报告写10%，代码计算用0.1，`%`在Python里不是百分比写法。

+++
## 比较产生布尔值

输入第三本年份2021，比较至少2020与恰好2020。

```python
year = 2021
print(year >= 2020)
print(year == 2020)
```

观察True和False。一个等号赋值，两个等号比较。

+++
## 捕获示范错误：字符串不能直接加数字

输入文字价格与整数，故意触发TypeError。try/except只是为了不让示范打断运行全部，不需要现在背这段。

```python
try:
    print("88.9" + 2)
except TypeError:
    print("价格写成了文字；金额运算请使用数字88.9。")
```

应看到中文提示，后面的练习仍能运行。

+++
## 练习1-1.1 保存第一本书名

把月光与我写成字符串。只替换...，不要改check编号。准备表books可以用来观察，不依赖其他练习。

```python
### BEGIN SOLUTION
result = "月光与我"
### STUDENT
result = ...
### END SOLUTION
check("1-1.1", result)
```

参考输出观察：字符串“月光与我”；检查通过说明类型与文字正确。

+++
## 练习1-1.2 两本金额

第一本单价88.9，买2本。用乘法表达公式，不要写“177.8元”字符串。

```python
### BEGIN SOLUTION
result = 88.9 * 2
### STUDENT
result = ...
### END SOLUTION
check("1-1.2", result)
```

输入单价、本数，结果177.8。浮点尾数不影响合理精度的检查。

+++
## 练习1-1.3 年份判断

第三本2021出版，把至少2020的判断赋给result，要求bool。

```python
### BEGIN SOLUTION
result = 2021 >= 2020
### STUDENT
result = ...
### END SOLUTION
check("1-1.3", result)
```

输入年份与边界，结果True，不是带引号的"True"。

+++
## 练习1-1.4 订单折后金额

独立使用22元、5件、减免0.1，计算实付。不要引用上一题result。

```python
### BEGIN SOLUTION
result = 22.0 * 5 * (1 - 0.1)
### STUDENT
result = ...
### END SOLUTION
check("1-1.4", result)
```

实际99.0，与随包订单SG25000039字段一致。

+++
## 验收与排错

- 能解释数字88.9与文字"88.9"区别。
- 能解释discount是减免比例、0.1是九折支付。
- 四题通过；未答时只有中文“还没作答”，没有NameError。
- NameError先查名字并运行前格；SyntaxError先查成对引号与英文半角标点。
- 代码改了要重新运行，旧输出不会自动更新。重启内核后从头运行。

求职用途：用模拟数据解释单价、数量、比例和金额核对，不虚构真实企业业绩。下一课把多个书名放进列表。
