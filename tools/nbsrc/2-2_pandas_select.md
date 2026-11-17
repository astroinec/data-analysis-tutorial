# 2-2 选取、筛选与排序

从原notebooks目录打开，选择Python (da-course)。目标：在200本模拟书中找预算小说书单，再找最高价5本。先明确行条件、列清单、排序方向。

```python
import sys
sys.path.insert(0, "..")
from dacheck import check, hint, setup_chinese_font
import pandas as pd
```

输入CSV读成原始books，所有练习独立从它选择，不使用上一题result。

```python
books = pd.read_csv("../data/books.csv")
print(books.shape)
```

输出(200, 10)，一行一部模拟书。

+++
## 一列和多列

输入整表，分别用单个列名与列名列表取数据。

```python
prices = books["price"]
book_list = books[["book_id", "title", "price"]]
print(prices.head(3))
book_list.head(3)
```

输出price Series前三项88.9、36.9、80.5，以及对应三行三列表。外层选择、内层列表。

+++
## loc[行,列]，按标签取

输入books，选0到2标签，取title、price。

```python
books.loc[0:2, ["title", "price"]]
```

实际3行2列。loc标签切片包含终点2，**不同于Python列表0:2只取0、1**。刚读表标签恰好连续；筛选后标签不等于当前位置，预览前三行用head(3)。

+++
## 先看条件的布尔清单

输入200个价格，逐行判断是否≤50。

```python
cheap_mask = books["price"] <= 50
print(cheap_mask.head(3))
```

输出False、True、False。mask只是判断清单，不是书单。

+++
### 把清单交给loc

输入原表和布尔清单，保留True的行、取3列。

```python
cheap_books = books.loc[cheap_mask, ["book_id", "title", "price"]]
cheap_books.head(3)
```

实际B002雨夜的孩子36.9、B010梧桐手册35.8、B012春日的孩子40.5。还未排序，原记录顺序保留。

+++
## 多条件：括号和&

输入品类与价格，分别比较再逐行并且。条件都满足才保留。

```python
novel_mask = (books["category"] == "小说") & (books["price"] <= 50)
novels = books.loc[novel_mask, ["book_id", "title", "price"]]
print(novels.shape)
novels.head(3)
```

输出(17, 3)；前三条B002雨夜的孩子36.9、B010梧桐手册35.8、B018北国密码49.5。

+++
### 或条件：|

输入小说与诗歌两个品类，满足任一即可。

```python
two_categories = (books["category"] == "小说") | (books["category"] == "诗歌")
print(books.loc[two_categories].shape[0])
```

输出78，即64小说加14诗歌。不需要按每本书写for和if。

+++
### 捕获and用于整列的错误

输入两个Series，故意用and。它需要单个真假，不能直接处理整列，所以捕获ValueError。

```python
try:
    wrong_mask = (books["price"] <= 50) and (books["category"] == "小说")
except ValueError:
    print("整列条件用&，每个比较单独加括号；单值判断和整列判断不同。")
```

中文提示后继续运行，不忽略自己的筛选错误。

+++
## 价格升序，编号打破并列

输入17本预算小说，按价格升序，同价按编号升序。

```python
ranked_novels = novels.sort_values(["price", "book_id"], ascending=[True, True])
ranked_novels.head(3)
```

输出B010梧桐手册35.8、B002雨夜的孩子36.9、B063旧城漫游记40.5。sort_values返回新表，不修改novels。

+++
## 全表最高价：先排序再取5本

输入原始books，price降序False、book_id升序True，选三列再取5条。

```python
top_books = books.sort_values(["price", "book_id"], ascending=[False, True])
top_books[["book_id", "title", "price"]].head(5)
```

实际B152山中来信112.8、B135人间的图书馆108.9、B117长河的秘密108.0、B011春日手册107.5、B073雪原之歌107.5。107.5并列用编号确定顺序。原索引未重新编号不是错误。

+++
## 练习2-2.1 取整表price Series

要求Series，一层方括号，不只前三项。

```python
### BEGIN SOLUTION
result = books["price"]
### STUDENT
result = ...
### END SOLUTION
check("2-2.1", result)
```

输出200项price，标签与原表一致。

+++
## 练习2-2.2 loc选标签0到2

只保留title、price列，loc标签终点2包含。

```python
### BEGIN SOLUTION
result = books.loc[0:2, ["title", "price"]]
### STUDENT
result = ...
### END SOLUTION
check("2-2.2", result)
```

输出前三本3行2列，不依赖上一题。

+++
## 练习2-2.3 小说预算书单

price≤50且category为小说，只保留book_id、title、price；按price升序、并列book_id升序。提交全部17条，不head截断。

```python
### BEGIN SOLUTION
mask = (books["price"] <= 50) & (books["category"] == "小说")
result = books.loc[mask, ["book_id", "title", "price"]]
result = result.sort_values(["price", "book_id"], ascending=[True, True])
### STUDENT
result = ...
### END SOLUTION
check("2-2.3", result)
```

输入200本，筛选并排序得到17行3列，最便宜35.8。

+++
## 练习2-2.4 最高价5本

独立从books按price降序、book_id升序，选book_id、title、price，取前5本。

```python
### BEGIN SOLUTION
result = books.sort_values(["price", "book_id"], ascending=[False, True])
result = result[["book_id", "title", "price"]].head(5)
### STUDENT
result = ...
### END SOLUTION
check("2-2.4", result)
```

结果5行3列，与上文最高价清单一致。

+++
## 验收与排错

- 四题通过，能解释价格≤50和品类条件要同时满足。
- KeyError查列名Price/price与空格；多列用内层列表。
- truth value ambiguous查是否用了and/or，逐行用&/|且每个比较带括号。
- 顺序不对查ascending与次级编号键。
- loc标签切片包含终点，不能照搬列表切片规则。

求职用途：预算书单、状态订单、TOP榜单。价格排行不是质量排行或销量排行，结论不能越过指标。下课计算新列与分组。
