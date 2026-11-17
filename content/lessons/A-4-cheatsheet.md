---
summary: 用能直接观察输入与输出的小例子，查Python、pandas和三种图表库的够用写法。
prereq: 至少完成对应课程；速查不能替代第一次学习
---

## 先知道代码在哪运行

本页 `python` 块在Notebook里运行。初始化、读取数据和后面的操作需要按顺序执行；查某一行时别忘了前面的变量从哪里来。终端命令与Python分开，环境问题查[排错向导](lesson:A-1)。

:::goal 使用目标
- 能从一个小输入预测筛选、分组、合并的输出。
- 分清Python列表位置、DataFrame行标签、列名和列位置。
- 按趋势、类别比较、关系与分布选择图表。
- 安全导出到新位置，不改坏原始数据；需要深入时点击原课。
:::

## Python够用速查

| 输入代码 | 结果/含义 | 回到课程 |
|---|---|---|
| `price = 39; quantity = 2; price * quantity` | `78`，变量存值，不是字符串 | [变量](lesson:1-1) |
| `'39' + '2'` | `'392'`，文本拼接不是加法 | [数据类型](lesson:1-1) |
| `int('39') * 2` | `78`，能转换的数字文本才可转整数 | [数据类型](lesson:1-1) |
| `round(10 / 3, 2)` | `3.33`，显示取两位小数；金额最终按业务规则舍入 | [变量](lesson:1-1) |
| `f'{0.074:.2%}'` | `'7.40%'`，得到展示字符串，不再用于数值运算 | [变量](lesson:1-1) |
| `names = ['文具', '书籍']; names[0]` | `'文具'`，Python位置从0开始 | [列表](lesson:1-2) |
| `len(names)` | `2`，元素个数 | [列表](lesson:1-2) |
| `kpi = {'orders': 3}; kpi['orders']` | `3`，字典按键取值 | [字典](lesson:1-2) |
| `39 > 20` | `True`，布尔判断 | [条件](lesson:1-3) |

小函数先定义再调用；参数是输入，`return` 是输出，`print` 只是显示。

```python
def amount(price, quantity):
    return price * quantity

print(amount(39, 2))
```

```output
78
```

`=` 是赋值，`==` 是比较；缩进是代码结构的一部分。循环和函数不是本页新教内容，卡住请回[条件、循环与函数](lesson:1-3)。

## 一个统一的小表

下面所有表格操作都基于这个**独立虚构小样例**，不是项目全集。故意把行索引设为10、20、30，帮你分清行标签和位置。

```python
import sys
sys.path.insert(0, '..')
import pandas as pd
small = pd.DataFrame({
    'order_id': ['A', 'B', 'C'],
    'category': ['文具', '书籍', '文具'],
    'quantity': [2, 1, 3],
    'pay': [78.0, 58.0, 45.0],
    'status': ['已完成', '已退款', '已完成'],
}, index=[10, 20, 30])
small
```

:::df 输入小表
| 索引（不是数据列） | order_id | category | quantity | pay | status |
|---:|---|---|---:|---:|---|
| 10 | A | 文具 | 2 | 78.0 | 已完成 |
| 20 | B | 书籍 | 1 | 58.0 | 已退款 |
| 30 | C | 文具 | 3 | 45.0 | 已完成 |
:::

## 看结构与读文件

| 写法 | 本例输出/含义 |
|---|---|
| `small.shape` | `(3, 5)`，3行5列，不包括左边索引 |
| `small.columns.tolist()` | `['order_id', 'category', 'quantity', 'pay', 'status']` |
| `small.head(2)` | 前两行，不是随机两行 |
| `small.info()` | 类型、非缺失个数等；它直接打印，返回None |
| `small['pay'].dtype` | 浮点类型；若CSV混入￥可能成为object文本 |
| `small.isna().sum()` | 各列缺失数，此例均0 |

```python
# 在notebooks/工作目录读取完整订单
orders = pd.read_csv('../data/shop/orders.csv', encoding='utf-8-sig')
# GBK样本必须写正确编码
sample = pd.read_csv('../data/shop/orders_gbk.csv', encoding='gbk')
# Excel要指定工作表；订单只有前3000行
excel_sample = pd.read_excel('../data/shop/shop_2025.xlsx', sheet_name='订单')
```

不要写 `small = small.info()`，否则会把表格换成None。具体读文件见[认识DataFrame](lesson:2-1)，数据规模与字段见[数据字典](lesson:A-3)。

## 方括号与索引：最容易迷惑的地方

| 代码 | 输出形状/值 | 解释 |
|---|---|---|
| `small['pay']` | Series，索引10/20/30，值78/58/45 | 一层方括号拿一列 |
| `small[['pay']]` | DataFrame，3×1 | 两层方括号保留表格 |
| `small.loc[20, 'pay']` | `58.0` | loc按行标签20、列名pay |
| `small.iloc[1, 3]` | `58.0` | iloc按第2行、第4列的位置 |
| `small.loc[10:20]` | A、B两行 | 标签切片通常包含终点20 |
| `small.iloc[0:2]` | A、B两行 | 位置切片不含终点2 |
| `small.reset_index(drop=True)` | 索引变0/1/2 | drop=True不把旧索引变成数据列 |

:::warn 不是所有“0”都表示第一行
`small.loc[0]` 找的是标签0，本例没有，会报KeyError。`small.iloc[0]` 才是第一行。不要依赖 `small['pay'][0]` 的含混读法，明确写 `.loc` 或 `.iloc`。筛选后索引可能跳号，跳号不代表数据丢失；先看行数与订单ID。
:::

## 筛选、排序、新增列

```python
completed_small = small.loc[small['status'].eq('已完成')].copy()
completed_small[['order_id', 'pay']]
```

```output
   order_id   pay
10        A  78.0
30        C  45.0
```

| 要做什么 | 写法 | 本例结果 |
|---|---|---|
| 两条件都满足 | `small.loc[(small['pay'] > 50) & small['status'].eq('已完成')]` | 仅A |
| 满足一个即可 | `small.loc[(small['pay'] > 70) \| small['category'].eq('书籍')]` | A、B |
| 分类在列表里 | `small.loc[small['category'].isin(['文具'])]` | A、C |
| 按金额降序 | `small.sort_values('pay', ascending=False)` | A、B、C |
| 每件平均实付 | `small.assign(pay_per_item=small['pay']/small['quantity'])` | 新列39、58、15 |
| 修改指定行 | `small.loc[small['order_id'].eq('A'), 'pay'] = 78.0` | 明确给指定行赋值 |

pandas多条件用 `&`、`|`、`~` 并给条件加括号，不用Python标量的and/or。不写 `df[条件]['列']=值` 的链式赋值；明确 `.loc[条件, '列']`。见[筛选](lesson:2-2)、[新增列](lesson:2-3)。

## 分组：先决定统计谁

```python
summary = small.groupby('category', as_index=False).agg(
    revenue=('pay', 'sum'),
    orders=('order_id', 'nunique'),
    quantity=('quantity', 'sum'),
)
summary
```

:::df 输出
| category | revenue | orders | quantity |
|---|---:|---:|---:|
| 书籍 | 58.0 | 1 | 1 |
| 文具 | 123.0 | 2 | 5 |
:::

这是全状态原支付分组，不是已完成净销售额；若统计收入，先筛已完成。`count` 不数缺失，`size` 数行，`nunique` 数不同值；表中一单多行时，不要把行数自动当订单数。`small['pay'].sum()`=181，已完成金额=123，已完成客单价=123/2=61.5，每件平均实付=123/5=24.6。

```python
summary['share'] = summary['revenue'] / summary['revenue'].sum()
# mean是普通平均，不自动按件数/客户数加权
print(completed_small['pay'].mean())
```

```output
61.5
```

只在一行一单、且已完成筛选正确时，这个均值才等于已完成客单价。口径比API更重要；详见[分组统计](lesson:2-3)和[项目](lesson:P-1)。

## 合并与透视

```python
labels = pd.DataFrame({'category': ['文具', '书籍'], 'label': ['办公', '阅读']})
joined = small.merge(labels, on='category', how='left',
                     validate='many_to_one', indicator=True)
assert len(joined) == len(small)
assert joined['order_id'].is_unique
assert joined['_merge'].eq('both').all()
joined[['order_id', 'label']]
```

```output
  order_id label
0        A    办公
1        B    阅读
2        C    办公
```

右表键若重复，关系验证会报错；找不到匹配行不等于0，不静默填金额。`merge`可能重新排列索引，核验的是订单ID与行数。`pivot_table`默认聚合是mean，求收入必须明确sum。

```python
small.pivot_table(index='category', columns='status', values='pay',
                  aggfunc='sum', fill_value=0)
```

结果：文具已完成123、已退款0；书籍已完成0、已退款58。这里缺组合填0符合“小表没有此类订单”规则，不等于所有业务缺失都应填0。详见[合并与透视](lesson:2-4)。

## 缺失、重复、文本、日期

| 需求 | 写法 | 输出/边界 |
|---|---|---|
| 重复主键检查 | `small['order_id'].duplicated().sum()` | 0；客户重复不等于订单重复 |
| 完全重复行去重 | `small.drop_duplicates()` | 本例仍3行；先核实是否重复导出 |
| 查看缺失 | `pd.Series([5, None]).isna().tolist()` | `[False, True]` |
| 文本去空格 | `pd.Series([' 上海 ']).str.strip().iloc[0]` | `'上海'` |
| 去货币符号 | `pd.Series(['￥39元']).str.replace('￥','',regex=False).str.replace('元','',regex=False)` | 文本`'39'`，还不是数字 |
| 安全数字转换 | `pd.to_numeric(pd.Series(['39', '错']), errors='coerce')` | 39与缺失；需报告转换失败，不填0 |
| 标准日期转换 | `pd.to_datetime(pd.Series(['2025-01-02']), errors='raise')` | datetime日期列 |
| 年月提取 | `pd.to_datetime(pd.Series(['2025-01-02'])).dt.strftime('%Y-%m')` | `'2025-01'` |

评分缺失不是0分；日期或金额转换失败不是合法0值。混合中文日期和时间格式要先明确规则，不靠盲目试格式。详见[缺失与重复](lesson:3-1)、[类型与异常](lesson:3-2)。

## 按问题挑图，不按库挑图

:::cards 图表选择
:::card 趋势
横轴有时间顺序，用折线；月份先排序，单位写元/万元。没有上一年数据不写同比。
:::
:::card 类别比较
少量类别用柱状，长中文标签用横向条形。柱轴从0起，降序可更清楚。
:::
:::card 两变量关系
散点呈现关系与离群点，不能自动证明因果。加颜色要说明分组，避免用颜色掩盖小样本。
:::
:::card 分布
直方图看数值分布；箱线图看中位数与四分位。箱线图中的离群标记不是业务异常的自动判定。
:::
:::

### matplotlib：控制标题与坐标

```python
import matplotlib.pyplot as plt
from dacheck import setup_chinese_font
setup_chinese_font()
fig, ax = plt.subplots(figsize=(6, 3))
ax.bar(summary['category'], summary['revenue'])
ax.set(title='小样例全状态原支付（虚构）', xlabel='品类', ylabel='金额（元）')
fig.tight_layout()
plt.show()
```

输出是两根柱：书籍58、文具123。字体助手提示未找到字体时查[图表课](lesson:4-1)与[报错表](lesson:A-2)，不忽略缺字警告。`plt.show()` 显示图，`fig.savefig()` 才保存；不要混淆显示与导出。

### seaborn：明确是否在自动聚合

```python
import seaborn as sns
fig, ax = plt.subplots(figsize=(6, 3))
sns.scatterplot(data=small, x='quantity', y='pay', hue='category', ax=ax)
ax.set(title='件数与原支付的小样例（虚构）', xlabel='件数', ylabel='金额（元）')
fig.tight_layout()
plt.show()
```

输出3个点。`sns.barplot` 默认求均值并可能显示不确定性区间，不是收入求和；已有汇总表直接用matplotlib柱图更直白。复杂统计图见[seaborn课](lesson:4-2)，不把区间当标准差或因果证据。

### Plotly：交互与离线导出

```python
import plotly.express as px
fig_interactive = px.bar(summary, x='category', y='revenue',
                         title='虚构小表全状态原支付',
                         labels={'category': '品类', 'revenue': '金额（元）'})
fig_interactive.show(renderer='notebook')
```

导出使用 `include_plotlyjs=True` 把脚本内嵌，离线可用但文件较大；不要选CDN假装离线完整。导出示例见下面，详细交互见[Plotly课](lesson:4-3)。

## 安全导出：不污染data/

```python
from pathlib import Path
import tempfile
with tempfile.TemporaryDirectory(prefix='da-cheatsheet-') as tmp:
    out = Path(tmp)
    summary.to_csv(out / 'summary.csv', index=False, encoding='utf-8-sig')
    summary.to_excel(out / 'summary.xlsx', index=False)
    fig.savefig(out / 'example.png', dpi=150, bbox_inches='tight')
    fig_interactive.write_html(out / 'example.html', include_plotlyjs=True)
    print(pd.read_csv(out / 'summary.csv').shape)
```

```output
(2, 5)
```

临时目录退出后删除，正式交付时请换成自己新建且不在 `data/` 内的目录。`index=False` 避免把左边行索引额外保存成 `Unnamed: 0` 列。此代码依赖上方示例的summary和fig变量，不是可以脱离上下文执行的一行魔法。

## SQL与下一批内容

SQL、统计检验、留存、同期群、A/B测试在下一批路线，本工具箱不把它们列成已完成技能或提供未经本课程验证的成套练习。当前作品重点是Python、pandas、清洗、图表和完整项目。

:::try 三项小练习
1. 小表第一行pay应写 `loc[0]` 还是 `iloc[0]`？
2. 小表已完成客单价与每件均价各是多少？
3. 已汇总品类收入交给seaborn柱图时，为什么要注意默认聚合？
:::fold 参考答案
1. `small.iloc[0]['pay']` 或 `small.loc[10, 'pay']`；标签0不存在。
2. 123/2=61.5元/单；123/5=24.6元/件。
3. `barplot` 默认估计均值，不自动求收入总和；确认输入粒度与参数，或直接用matplotlib绘汇总。
:::
:::

:::checklist 速查验收
- [ ] 能分清列、索引、位置和一层/两层方括号。
- [ ] 知道多条件加括号、使用&/|而非and/or。
- [ ] 合并验证关系，按主键检查不增不丢。
- [ ] 先定义筛选口径再求和，缺失不机械填0。
- [ ] 图表标清单位、模拟来源，导出不覆盖原始数据。
:::
