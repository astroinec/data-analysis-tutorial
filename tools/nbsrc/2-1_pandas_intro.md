# 2-1 认识DataFrame与读取数据

保持文件在notebooks中，选择Python (da-course)。本教程验证Python3.12.13、pandas3.1.1、NumPy2.5.4。这里是Python代码，不是Anaconda Prompt命令。所有商店/图书数据是教学模拟。

```python
import sys
sys.path.insert(0, "..")
from dacheck import check, hint, setup_chinese_font
import pandas as pd
```

输入已安装的pandas工具，import导入，as pd起短名。没有可见输出是正常的。sys.path让原位置的Notebook找到教程检查工具，不要单独移动本文件。

+++
## 读CSV：先检查整表规模

输入相对路径：..回上级教程根目录，再进入data。read_csv读成DataFrame，shape看行列规模。

```python
books = pd.read_csv("../data/books.csv")
print(books.shape)
```

输出(200, 10)，一行一部模拟图书。左边行索引不是book_id字段。

+++
### shape是属性，不加调用括号

输入books的行列元组，0位置取行数，1位置取列数。

```python
print(books.shape[0])
print(books.shape[1])
```

输出200和10；head的显示行数不能替代全集规模。

+++
## head看开头，不删后面的数据

输入整张表，head(3)预览3行、全部10列。

```python
books.head(3)
```

观察前三本月光与我、雨夜的孩子、故园往事。页宽可能要横向看；原表仍200行。

+++
### 默认head显示5行

输入同一表，不给head参数。

```python
books.head()
```

输出前5条；第五本故园的孩子评分缺失，不等于零分。

+++
## info看结构

输入books，info显示列、类型、非空数量，不返回新表。

```python
books.info()
```

观察200 entries、10 columns。rating180个非空、20个缺失；其他列200个非空。pandas3.1.1文字通常显示str，数字列int64/float64。不要books=books.info()，返回None会丢掉变量里的表。

+++
## 一列Series

输入books，用一个列名取price，type看类型。

```python
prices = books["price"]
print(type(prices))
print(prices.head(3))
```

观察Series和0→88.9、1→36.9、2→80.5。Name和dtype是说明，不是额外图书。

+++
## 两列表格DataFrame

输入列名列表，双层方括号选择多列。

```python
small_table = books[["title", "price"]]
print(type(small_table))
small_table.head(3)
```

观察DataFrame，3行2列：月光与我88.9，雨夜的孩子36.9，故园往事80.5。

+++
### 单列仍可保留表格外壳

输入price列名列表，不是一个字符串。

```python
print(type(books[["price"]]))
```

输出DataFrame。books["price"]则输出Series，题目要求的类型不能混用。

+++
## 读Excel：指定工作表

输入工作簿路径与sheet_name="商品"，只读商品表。

```python
products_excel = pd.read_excel("../data/shop/shop_2025.xlsx", sheet_name="商品")
print(products_excel.shape)
products_excel.head(2)
```

输出(33, 6)，前两件故宫红笔记本39元、敦煌飞天书签套装29元。sheet_name是明确的命名参数。

+++
### Excel订单只是前3000行样本

输入工作簿订单工作表与年度订单CSV。读取两个范围不同的数据，不能互当全集。

```python
orders_excel = pd.read_excel("../data/shop/shop_2025.xlsx", sheet_name="订单")
orders = pd.read_csv("../data/shop/orders.csv")
print(orders_excel.shape)
print(orders.shape)
```

输出(3000, 11)和(15115, 11)。Excel只含CSV前3000单，年度分析用CSV。商品33行和客户3000行是完整主表。

+++
## 捕获属性被当函数的示范

输入books，故意错误调用shape()；捕获TypeError不影响运行全部。

```python
try:
    books.shape()
except TypeError:
    print("shape是属性，用books.shape；head是动作，用books.head()。")
```

看到中文提示。此错误与包安装无关，修写法即可。

+++
## 练习2-1.1 图书总行数

从整张books取行数，不用head，不取列数。

```python
### BEGIN SOLUTION
result = books.shape[0]
### STUDENT
result = ...
### END SOLUTION
check("2-1.1", result)
```

输入200行表，输出整数200。

+++
## 练习2-1.2 前三本两列

选title、price，取前3行，结果DataFrame。题目独立读取books，不借上一题result。

```python
### BEGIN SOLUTION
result = books[["title", "price"]].head(3)
### STUDENT
result = ...
### END SOLUTION
check("2-1.2", result)
```

输出3行2列，与预览示意一致。

+++
## 练习2-1.3 Excel商品工作表

明确指定商品工作表，读进result，不要依赖默认第一张订单表。

```python
### BEGIN SOLUTION
result = pd.read_excel("../data/shop/shop_2025.xlsx", sheet_name="商品")
### STUDENT
result = ...
### END SOLUTION
check("2-1.3", result)
```

输出33行6列商品主表，检查动态从工作簿核对。

+++
## 练习2-1.4 年度订单规模

独立从CSV读取全年订单，提交shape这对数，而不是一个行数。

```python
### BEGIN SOLUTION
result = pd.read_csv("../data/shop/orders.csv").shape
### STUDENT
result = ...
### END SOLUTION
check("2-1.4", result)
```

输出元组(15115, 11)，不是Excel样本(3000,11)。

+++
## 验收、错误与求职用途

- 一行图书是一部书；一行订单是一笔单商品订单，quantity可大于1。
- shape核对规模、head核对样貌、info核对类型与缺失。
- Series与DataFrame不同；缺失评分不是零分。
- 四题通过，不覆盖原始CSV。
- FileNotFoundError先查目录是否移动、../层级、文件拼写；ModuleNotFoundError先查内核；工作表不存在查sheet_name。

面试先讲你读到的范围，能指出Excel样本不是年度全集，是数据审慎而不是“代码技巧不足”。下课选行列和排序。
