---
summary: 从200本书中选字段、按条件留记录、按价格排顺序，逐步核对结果。
prereq: 已完成第 2-1 课，能读取CSV、区分Series与DataFrame
---

:::goal 本课目标
- 用列名列表和loc分别表达“要哪些列”“要哪些行”。
- 看懂布尔筛选的True/False，多条件用括号和 `&`、`|`。
- 用sort_values升降序排序，为并列值加一个稳定的次级排序键。
- 完成4题，核对行数与前几条，不只追求没有报错。
:::

打开 [2-2 练习本](../../notebooks/2-2_pandas_select.ipynb)，从原位置运行准备格，读取 `../data/books.csv`。图书数据有200行10列，一行一部虚构图书。目标问题是：“找出价格不超过50元的小说，先看便宜的；另找出全表最贵5本。”筛选是选哪些记录，排序是改变展示顺序，两件事不能混为一谈。

## 1. 先选列：把结果变成可读的清单

```python
books = pd.read_csv("../data/books.csv")
prices = books["price"]
book_list = books[["book_id", "title", "price"]]
print(prices.head(3))
book_list.head(3)
```

输入全年图书目录。单个列名取出price Series，前三个值88.9、36.9、80.5；列名列表选出三列DataFrame，前三条为B001月光与我88.9、B002雨夜的孩子36.9、B003故园往事80.5。这里只隐藏其他字段，不是从原始CSV永久删除字段。

外层方括号表示从books取内容，内层列表告诉它多个字段。把 `books["title", "price"]` 写成一个方括号逗号隔开，通常会触发KeyError：它不是正确的多列清单。先修语法，再确认是不是选到了题目要求的列。

## 2. loc：把“行条件、列清单”并排写

```python
books.loc[0:2, ["title", "price"]]
```

输入books，`loc[行, 列]` 的逗号左边选行，右边选列。刚读CSV时行标签是0、1、2……，`0:2` 在loc中包含终点标签2，所以实际结果3行2列。这个规则和 [Python列表切片](lesson:1-2) 的右边不包含不同：**loc按标签取，标签切片包含终点**。不要只凭“都长得像冒号”就当规则一样。

筛选后标签可能不再连续，0、1、2也不等于当前前三行的位置。想预览当前前三条，最直接用 `head(3)`。本课的loc更常用于条件，不要求你靠行标签记住某本书的身份；业务编号是book_id。

## 3. 条件先生成一列判断，再交给loc

```python
cheap_mask = books["price"] <= 50
print(cheap_mask.head(3))
```

输入price列，每个值与50比较，输出前三个判断：索引0为False、1为True、2为False。这是一条布尔Series，可称为“是否保留的清单”或mask。这里不写if，因为判断的不是单本书，而是200本的整列。

```python
cheap_books = books.loc[cheap_mask, ["book_id", "title", "price"]]
cheap_books.head(3)
```

输入原表和判断清单，loc只保留True对应的行，并取三列。实际开头是B002雨夜的孩子36.9、B010梧桐手册35.8、B012春日的孩子40.5；顺序仍按原文件，不会自动从便宜到贵。你可以比较结果的price列有没有超过50，主动验证题意。

:::widget table-lab 小样本筛选演示（不执行Python）
{"mode":"filter"}
:::

上面的交互只用网页固定的小样本演示筛选，**不会读取books.csv，也不执行Python**。你在页面点对不代表Notebook已经做对，实际200本结果仍需运行代码和检查函数。

## 4. 两个条件：每个比较都用括号

```python
novel_mask = (books["category"] == "小说") & (books["price"] <= 50)
novels = books.loc[novel_mask, ["book_id", "title", "price"]]
print(novels.shape)
novels.head(3)
```

输入品类与价格两列，两个条件都为真才保留。实际结果 `(17, 3)`；原文件顺序的前三条为B002雨夜的孩子36.9、B010梧桐手册35.8、B018北国密码49.5。单靠价格便宜不能满足“小说”条件，单靠品类为小说也不能满足预算。

`&` 表示逐行“并且”，`|` 表示逐行“或者”，`~` 放在一条布尔清单前表示取反。多个比较要分别包在括号中；Python运算优先级不会自动按中文题意理解。这里不是单个True/False，不能直接用阶段1单值判断常用的 `and` 或 `or`。

```python
two_categories = (books["category"] == "小说") | (books["category"] == "诗歌")
print(books.loc[two_categories].shape[0])
```

输入两种品类，保留至少满足一个条件的书，实际有78行：64部小说加14部诗歌。同一图书在数据中只有一个品类，没有重复加两次。若要排除小说可用 `~(books["category"] == "小说")`；本课先掌握两条件括号，不追求把所有需求塞在一行。

:::compare 常见多条件错误
:::bad `books["price"] <= 50 and books["category"] == "小说"`
Series包含很多判断，Python无法把整列当成一个真假值，会提示truth value is ambiguous。
:::
:::good `(books["price"] <= 50) & (books["category"] == "小说")`
每条比较有括号，再逐行合并。结果仍需用loc选择，判断清单本身不是书单。
:::
:::

## 5. 排序：告诉程序按哪列、朝哪个方向

```python
ranked_novels = novels.sort_values(["price", "book_id"], ascending=[True, True])
ranked_novels.head(3)
```

输入17本符合条件的小说，操作先按price升序；同价时按book_id升序。`ascending=True` 是从小到大，False是从大到小。实际前三本：B010梧桐手册35.8、B002雨夜的孩子36.9、B063旧城漫游记40.5。sort_values返回排好序的新表，默认不改变novels。

```python
top_books = books.sort_values(["price", "book_id"], ascending=[False, True])
top_books[["book_id", "title", "price"]].head(5)
```

输入全表，操作价格从高到低，并列按编号从小到大，再取5行3列。

:::df 实际最贵5本：单价排行，不是销量或质量排行
| book_id | title | price |
|---|---|---:|
| B152 | 山中来信 | 112.8 |
| B135 | 人间的图书馆 | 108.9 |
| B117 | 长河的秘密 | 108.0 |
| B011 | 春日手册 | 107.5 |
| B073 | 雪原之歌 | 107.5 |
:::

两本107.5元并列，明确次级键才有可复现顺序。最左边索引仍可能是151、134等原标签；这不是排序坏了，也不代表漏掉第0行。不要把“按索引排序”当“按价格排序”，`sort_values`关注数据列。

:::widget table-lab 小样本排序演示（不执行Python）
{"mode":"sort"}
:::

这仍是内置小样本界面，只模拟排序，不执行你的Python。回到Notebook核对真实200行数据的结果。

:::quiz
查“价格≤50的小说”，为什么用 `&`？
- [ ] 任一条件满足就够了
- [x] 同一行的品类与价格两个条件都必须满足
- [ ] &会让价格自动升序
---
筛选决定留哪些行，排序决定这些行如何排列；两步各司其职。
:::

## 6. 四道独立练习

每题使用准备好的books，不借用前题结果。自动检查会核对类型、列、内容和题目要求的顺序。

:::try 2-2.1 单列Series
取整表price列赋给result，要求是Series而不是单列表格。
:::
:::fold 答案与观察
```python
result = books["price"]
```
输入整表，输出200项Series，行标签与原表一致。
:::

:::try 2-2.2 loc选行列
用loc选标签0到2，列只保留title、price，赋给result。
:::
:::fold 答案与观察
```python
result = books.loc[0:2, ["title", "price"]]
```
输入原表，标签切片包含2，输出3行2列。
:::

:::try 2-2.3 小说预算书单
价格≤50且品类为小说，保留book_id、title、price；按价格升序、并列编号升序。不只取前三条。
:::
:::fold 答案与观察
```python
mask = (books["price"] <= 50) & (books["category"] == "小说")
result = books.loc[mask, ["book_id", "title", "price"]]
result = result.sort_values(["price", "book_id"], ascending=[True, True])
```
输入200本，保留17本，输出17行3列，前三条见上文。
:::

:::try 2-2.4 最高价5本
全表按price降序、并列book_id升序，取前5条，只保留book_id、title、price。
:::
:::fold 答案与观察
```python
result = books.sort_values(["price", "book_id"], ascending=[False, True])
result = result[["book_id", "title", "price"]].head(5)
```
输入全表，排序后预览，输出5行3列，与实际排行一致。
:::

## 报错和验收

| 现象 | 纠正动作 |
|---|---|
| KeyError: Price | 核对列名，price全小写，不要加空格 |
| truth value is ambiguous | 整列条件用&或\|，每个比较单独加括号 |
| 筛完还是200行 | 是否只创建mask却忘记放入loc |
| 内容对、顺序不对 | 检查ascending方向和并列次级键 |
| loc取0:2得到3行 | 这是标签切片规则，不是报错 |

:::job 求职场景
编辑筛选预算书单、运营筛选特定状态订单、助理整理TOP榜单，都可以用同一结构：先说行条件，再说字段，再说排序。只根据书价不能推断读者偏好或书的品质；报告结论必须匹配指标。
:::

:::checklist 本课验收
- [ ] 我能用loc表达“行条件、列清单”。
- [ ] 我知道loc标签切片包含终点。
- [ ] 我能解释&与\|的条件区别。
- [ ] 我能稳定处理两条相同价格的记录。
- [ ] 四题通过，筛选与排序没有覆盖原始CSV。
:::

下一课：[新增列与分组统计](lesson:2-3)。
