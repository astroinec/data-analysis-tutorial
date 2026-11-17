# 1-2 列表与字典

保持文件在notebooks目录，选择Python (da-course)，逐格Shift+Enter。列表回答第几项，字典回答哪个字段。全部数据虚构，本课只取随包前三本，不依赖上一课内核。

```python
import sys
sys.path.insert(0, "..")
from dacheck import check, hint, setup_chinese_font
import pandas as pd
```

## 准备：这段读文件在2-1详细讲

输入200行图书CSV，准备原始三项列表与第一本字段字典。它们专供独立练习，不会读取上一题result。

```python
books = pd.read_csv("../data/books.csv")
first_titles = books.head(3)["title"].tolist()
first_book = books.iloc[0][["title", "price", "category"]].to_dict()
print(first_titles)
print(first_book)
```

观察前三本书名月光与我、雨夜的孩子、故园往事；字典价格88.9、品类历史。tolist/to_dict只是准备，当前重点是容器本身。

+++
## 创建列表

输入三段书名，方括号放多项、逗号隔开。len数项数。

```python
titles = ["月光与我", "雨夜的孩子", "故园往事"]
print(titles)
print(len(titles))
```

输出三项列表和3。输出用单引号也正确，开头结尾成对即可。

+++
## 索引从0开始

输入列表，分别取位置0、1和最后一个。先预测三个书名。

```python
print(titles[0])
print(titles[1])
print(titles[-1])
```

输出月光与我、雨夜的孩子、故园往事。取出的是单个字符串，不是一个列表。

+++
## 切片取一段

输入titles；0:2包含0、1但不含2；省略起点从头开始，省略终点到末尾。

```python
print(titles[0:2])
print(titles[:2])
print(titles[1:])
```

前两行输出同样的前两本列表，最后输出后两本列表。列表切片规则以后不能直接套loc标签切片。

+++
### 一个值与一项列表不同

输入同一列表，比较索引与切片的结果类型。

```python
print(titles[0])
print(titles[0:1])
print(type(titles[0]))
print(type(titles[0:1]))
```

观察月光与我是str，['月光与我']是list。是否有外层容器很重要。

+++
## 追加：直接改这个列表

输入两项新列表，append加到末尾。初始化与追加同格，每次运行从头创建，避免重复追加。

```python
reading_list = ["月光与我", "雨夜的孩子"]
reading_list.append("故园往事")
print(reading_list)
```

输出三项。不写reading_list=reading_list.append(...)，append返回None，不是新列表。

+++
## 捕获越界示范

三项正向索引只能0、1、2，取3会出错。此处捕获IndexError，运行全部不中断。

```python
try:
    print(titles[3])
except IndexError:
    print("只有3项，可用正向索引0、1、2；最后一项可用-1。")
```

看到中文提示；你自己的练习越界时先数项数、查位置，不靠重装环境修索引。

+++
## 创建字典：键对应字段

输入一本书三项资料，花括号创建dict，冒号隔开键和值。价格是数字。

```python
book = {"title": "月光与我", "price": 88.9, "category": "历史"}
print(book["title"])
print(book["price"])
```

输出月光与我和88.9。book[0]不是“第一个字段”，除非真的有数字0这个键。

+++
### 取数字字段，再计算

输入刚创建字典，取price乘2。

```python
print(book["price"] * 2)
```

输出177.8，与1-1金额一致，不需要变量price恰好在内核存在。

+++
### 替换字段值，不写回文件

输入教学字典，把price替换90。原CSV仍88.9，练习使用未改的first_book。

```python
book["price"] = 90.0
print(book["price"])
print(first_book["price"])
```

分别输出90.0和88.9：修改对象不同。不要把同一份工作变量与原始数据混淆。

+++
### 捕获键拼错

输入Price大写键，实际只存在price小写。故意示范错误被捕获。

```python
try:
    print(book["Price"])
except KeyError:
    print("没有Price这个键，请核对小写price。")
```

看到中文提示。缺字段不等于值为0；不要随便补0掩盖KeyError。

+++
## 练习1-2.1 创建前三本列表

按原文件顺序创建result：月光与我、雨夜的孩子、故园往事，要求list。

```python
### BEGIN SOLUTION
result = ["月光与我", "雨夜的孩子", "故园往事"]
### STUDENT
result = ...
### END SOLUTION
check("1-2.1", result)
```

实际三项列表，检查核对类型、内容与顺序。

+++
## 练习1-2.2 取最后一本

从准备好的first_titles取最后一个，结果应是字符串。独立于第一题。

```python
### BEGIN SOLUTION
result = first_titles[-1]
### STUDENT
result = ...
### END SOLUTION
check("1-2.2", result)
```

输入三项列表，输出最后书名故园往事。

+++
## 练习1-2.3 创建一本书字典

只保留title、price、category三个键，第一本值分别为月光与我、88.9、历史。

```python
### BEGIN SOLUTION
result = {"title": "月光与我", "price": 88.9, "category": "历史"}
### STUDENT
result = ...
### END SOLUTION
check("1-2.3", result)
```

输入三项字段，形成三键dict；重复price键不会存两本书。

+++
## 练习1-2.4 按键算两本金额

从未被修改的first_book取price，买2本。不要用示范中已变90的book，也不读上一题result。

```python
### BEGIN SOLUTION
result = first_book["price"] * 2
### STUDENT
result = ...
### END SOLUTION
check("1-2.4", result)
```

取原价88.9乘2，金额177.8。

+++
## 验收

- 说清列表的0、1、2位置，最后一项是-1。
- 说清切片结果还是列表，取单项得到元素。
- 说清字典键和值，书价字段是数字。
- 四题通过；越界示范与键错误示范都有中文提示。
- IndexError查位置；KeyError查键；SyntaxError查方括号/花括号及英文逗号、冒号。

求职迁移：书目清单用多项顺序，单条资料用命名字段。下课用if和for让同一套规则处理每条记录。
