---
summary: 把CSV与Excel读成表格，检查行列规模，不把样本误当年度全集。
prereq: 已完成阶段1与环境体检，能解释列表、字典和函数调用
---

:::goal 本课验收目标
- 解释 DataFrame 是整张表、Series 是带标签的一列。
- 用 read_csv 和 read_excel 读取正确文件与工作表。
- 用 shape、head、info 检查范围、列名、类型和缺失。
- 区分年度CSV与Excel前3000行样本，完成4题。
:::

打开 [2-1 练习本](../../notebooks/2-1_pandas_intro.ipynb)，保持它在 `notebooks/`，选择 `Python (da-course)`。本教程验证版本为Python 3.12.13、pandas 3.1.1、NumPy 2.5.4；不要因网页上旧例子自行换版本。在Anaconda Prompt中装包，在Notebook里写Python，这两个位置继续分开。

## 1. 把“表”和“一列”分开看

:::analogy 你熟悉的表格，但没有手工单元格操作
DataFrame像一张二维表：行是记录，列是字段。Series像其中一列，还带着行标签。数据分析先问“一行是什么”“每列什么意思”，再决定算什么；不能只看到数字就直接求和。
:::

图书表一行是一部模拟图书，`book_id` 是图书编号，`title` 是书名，`price` 是单本价格，`rating_count` 是评价人数。订单表一行是一笔订单且只有一个商品；`quantity` 可以大于1，不能把订单行数当商品件数。表最左边自动显示的0、1、2是行索引，不是新加的一列业务编号。

:::df books.csv 的前三条：显示列是原始10列中的一部分
| 行索引 | book_id | title | category | year | price |
|---:|---|---|---|---:|---:|
| 0 | B001 | 月光与我 | 历史 | 2016 | 88.9 |
| 1 | B002 | 雨夜的孩子 | 小说 | 1991 | 36.9 |
| 2 | B003 | 故园往事 | 心理 | 2021 | 80.5 |
:::

## 2. 导入工具：import 与别名

```python
import pandas as pd
```

输入是已经安装好的pandas包，操作是导入并起短名 `pd`。没有可见输出是正常的。`pd`只是社区常用别名；它不是价格，也不是文件名。后面的 `pd.read_csv` 表示“使用pandas中的读CSV工具”。若报ModuleNotFoundError，回到[环境体检](lesson:0-5)，检查内核，不要在Notebook乱复制安装命令。

练习本第一格还会导入 `check`、`hint` 等教程检查工具；从原位置打开，才能通过上一级路径找到它们。你可以先直接运行，重点学pandas操作，不需要把所有导入行背下来。

## 3. 读CSV：路径是相对当前位置的

```python
books = pd.read_csv("../data/books.csv")
print(books.shape)
```

输入 `../data/books.csv`：`..` 从notebooks回到教程根，再进入data；斜杠在Windows Python字符串里也能用。操作是读表，交给变量books；输出 `(200, 10)`，意思是200行、10列。括号中的这对数叫元组，本课只需按位置取数。`books.shape[0]` 为200，`books.shape[1]` 为10。

`shape` 是已经记录的信息，所以后面不加括号；`head()` 是要执行的查看动作，所以要加括号。CSV是分隔文本，不等于Excel工作簿。随包普通CSV用UTF-8带BOM存储，pandas默认读取即可，不需要为这些文件乱换编码。

```python
books.head(3)
```

输入整张图书表，操作是预览开头3行，实际返回前三条记录、全部10列；不会删除后197行，也不会改变books本身。截图或页宽可能让列隐藏，要横向查看。`books.head()` 不写数量默认看5行，“只显示5行”不代表文件只有5行。

```python
books.info()
```

输入图书表，操作是显示结构摘要。实际可看到200 entries、10 columns；book_id、title等文字列为字符串类型，year、pages、rating_count为整数，price与rating为小数。rating只有180个非空值，其余20本评分缺失；其他列200个非空。这个输出是说明文字，不是一张新结果表；`info()`通常返回None，别把 `books = books.info()` 写进去。

:::note 评分缺失不等于0分
随包图书评价人数太少时不显示评分。这里先识别缺失，如何处理留到[清洗课](lesson:3-1)。把缺失自动改0会编造低评分，改变平均值。pandas版本不同，文字列类型显示可能不同；本课程用3.1.1，不靠截图里的object字样判断是否安装成功。
:::

## 4. 取一列，理解Series与DataFrame

```python
prices = books["price"]
print(type(prices))
print(prices.head(3))
```

输入整张表，通过列名取price，得到Series。类型输出 `<class 'pandas.Series'>`；前三个带行标签的值是0→88.9、1→36.9、2→80.5。最下方可能还有Name和dtype，这是Series的说明，不是第4条图书记录。

```python
small_table = books[["title", "price"]]
small_table.head(3)
```

输入books与两个列名，得到只含书名和价格的DataFrame；前3行是月光与我88.9、雨夜的孩子36.9、故园往事80.5。两层方括号中，内层是上一阶段学过的列名列表，外层是“从books选择”。选一列但仍要表格，可写 `books[["price"]]`；`books["price"]` 则是一列Series。不要为了看起来像表而随意改变结果类型。

:::compare 属性和动作
:::bad `books.shape()`
shape不是函数，括号会引发TypeError。不要看到报错就重新安装pandas。
:::
:::good `books.shape` 与 `books.head()`
前者读取行列规模，后者调用预览动作。先检查代码标点与接口用法。
:::
:::

## 5. Excel：工作簿里先指定哪一张表

```python
products_excel = pd.read_excel("../data/shop/shop_2025.xlsx", sheet_name="商品")
print(products_excel.shape)
products_excel.head(2)
```

输入文创店工作簿和工作表名“商品”，操作是只读商品表。输出规模 `(33, 6)`；前两件是P001故宫红笔记本（39元、成本20.6）与P002敦煌飞天书签套装（29元、成本14.7）。`sheet_name` 叫命名参数：明确告诉函数要哪张工作表，而不是靠默认第一张猜。

```python
orders_excel = pd.read_excel("../data/shop/shop_2025.xlsx", sheet_name="订单")
orders_csv = pd.read_csv("../data/shop/orders.csv")
print(orders_excel.shape)
print(orders_csv.shape)
```

输入同一业务的两份不同范围文件，操作为读取和规模核对，实际输出 `(3000, 11)` 和 `(15115, 11)`。**Excel订单表只保存CSV前3000行，不是2025年度全集**。商品33行、客户3000行在Excel中是完整主表，但订单不是。做年度订单分析必须用 `orders.csv`，不能拿Excel结果乘一个比例假装还原全年。

:::warn 不写sheet_name可能悄悄读错
默认读第一个工作表，本工作簿恰好是订单，但以后文件顺序可能变。没有报错也要核对shape与列名。若提示找不到工作表，核对“商品”“订单”“客户”是否完全一致，不能写成“商品表”。
:::

:::quiz
`books.head()`显示5行，能得出哪个结论？
- [ ] 文件只有5本书
- [ ] books被永久删到只剩5行
- [x] 默认预览5行，应另用shape核对全集规模
---
显示范围、文件范围、变量是否被修改是三个不同问题。
:::

## 6. 四道独立练习

顶部准备格已独立读好books与orders。读文件练习仍请按题目写，别直接输入表格截图。每题检查结果类型与数据，后题不引用前题result。

:::try 2-1.1 图书行数
把图书总行数赋给result，不是列数，也不是head的长度。
:::
:::fold 答案与输出
```python
result = books.shape[0]
```
输入整张表，取行数，实际是整数200。
:::

:::try 2-1.2 前三本的两列
选title与price两列，再取前3行，结果必须是DataFrame。
:::
:::fold 答案与输出
```python
result = books[["title", "price"]].head(3)
```
输入200行表，选两列并预览，输出3行2列，值与本页示意一致。
:::

:::try 2-1.3 读Excel商品表
从shop_2025.xlsx指定“商品”工作表读入result，不要读默认的订单表。
:::
:::fold 答案与输出
```python
result = pd.read_excel("../data/shop/shop_2025.xlsx", sheet_name="商品")
```
输入工作簿路径与表名，输出33行6列商品主表。
:::

:::try 2-1.4 核对年度订单规模
从orders.csv读取全年订单，把shape这对行列数赋给result。
:::
:::fold 答案与输出
```python
result = pd.read_csv("../data/shop/orders.csv").shape
```
输入年度CSV，读取后查看规模，结果 `(15115, 11)`。不能用Excel样本的3000行作答。
:::

## 读取失败时怎么做

| 最后一行报错 | 先做什么 |
|---|---|
| FileNotFoundError | 确认Notebook没移走，文件名和层级正确；不是安装pandas问题 |
| ModuleNotFoundError | 确认选Python (da-course)，回环境体检 |
| UnicodeDecodeError | 核对文件说明；本课普通CSV无需GBK，故意的orders_gbk另有清洗练习 |
| Worksheet named ... not found | 核对sheet_name，工作表名不是文件名 |
| Missing optional dependency openpyxl | 激活课程环境按requirements安装，不装到base |

:::job 面试里先展示“我读对了什么”
取数任务最重要的第一步是说明范围：图书200行、商品33行、客户3000行、2025全年订单15115行。能指出Excel只是订单样本，是审慎的数据意识。对模拟数据应写“教学模拟数据”，不伪称拿到了真实客户明细。
:::

:::checklist 验收
- [ ] 我能解释一行图书和一行订单各代表什么。
- [ ] 我能区分Series和单列DataFrame。
- [ ] 我会用shape/head/info分别核对规模、样貌、类型。
- [ ] 我知道评分缺失不等于0，Excel订单不等于全年。
- [ ] 四题通过，数据仍保留原始文件未覆盖。
:::

下一课：[选取、筛选与排序](lesson:2-2)。
