---
summary: 用15115笔虚构订单完成一份口径明确、检查可复现、结论有边界的年度分析作品。
prereq: 完成阶段0～4；能读取表格、筛选、分组、合并和画图
---

## 你要交付什么，而不只是学什么

:::goal 本项目的可检验目标
- 从原始CSV完整重做2025年度分析，重启内核后仍能运行。
- 明确订单粒度、时间窗口、状态与金额口径，用检查证明连接没有增行或丢单。
- 做出月趋势、平台退款、品类贡献、目标达成四张汇总表，至少三张图。
- 用“发现—证据—限制—待验证建议”写3～5项结论，交一份报告。
- 完成练习本七题；说得清为什么客单价不等于商品均价，复购率分母不等于注册人数。
:::

这是一个虚构线上文创店，销售书籍、文具、帆布包、明信片、徽章、日历和香薰。店铺、客户、商品及经营结果都是程序模拟的。你不是替真实公司证明增长，而是在展示一种可信的分析工作方式。文科训练中的材料辨析、论证结构和表达能力，在这里不是累赘：指标口径相当于概念定义，数据检查相当于核验材料，结论边界相当于避免过度论证。

请在本包 `notebooks/P-1_project_ecommerce.ipynb` 打开练习本，内核选 `Python (da-course)`。网页负责解释思路，练习本负责运行；答案本在 `solutions/`。不要只下载一个Notebook便以为拥有完整项目，它还依赖相邻的 `data/` 和 `dacheck/`。

:::flow 从问题走到交付
1. 写问题与口径：要回答谁的什么决策？
2. 检查数据：每行是什么，缺失与重复意味着什么？
3. 安全取数：保留原始表，验证多表关系。
4. 分析与画图：先有汇总表，再有图，不反过来挑好看的数字。
5. 写结论与限制：区分观察、解释假设与尚未执行的行动。
6. 复现与交付：报告、汇总表、运行路径和检查记录一起交。
:::

## 第一步：把“看一看销售”改成具体问题

如果接到一句“分析全年销售”，不要马上开画饼图。先把问题拆成下面的清单，每个问题都有可计算的输出。问题不必复杂，但必须能被现有数据支持。

:::df 问题与输出对照
| 业务问题 | 指标或表 | 图与报告位置 |
|---|---|---|
| 全年规模怎样？ | 已完成金额、订单数、购买人数、客单价 | 开头的指标卡 |
| 哪些月份突出？ | 月金额、订单数、客单价；可看环比 | 月度折线 |
| 各平台退款是否不同？ | 全年订单数、退款订单数、订单退款率 | 平台柱状图 |
| 哪些品类贡献最多？ | 品类已完成金额及份额 | 降序横向条形图 |
| 目标完成了吗？ | 月实际与月目标、差额、达成率 | 月目标对照表 |
| 有多少购买客户复购？ | 窗口内至少两笔已完成订单的客户占比 | 报告补充指标 |
:::

现有表没有曝光、访问、广告费用、库存、退款原因或上一年订单。因此“哪个渠道转化率最高”“投入多少广告赚回多少”“比2024增长多少”“促销是否带来新增购买”都不在本次能直接回答的问题内。敢于写“暂时不能回答”不是能力差，而是知道证据边界。你仍然可以列补数需求，但不能把需求写成已经完成的分析。

## 第二步：写一页指标口径卡

订单全集 `data/shop/orders.csv` 当前为 **15115行×11列**，覆盖2025年1月1日至12月31日；不是Excel的3000行演示样本。每行一个订单，而且本数据每个订单只有一种商品；`quantity=3` 表示这一订单购买该商品三件，不是三笔订单。多人复购时，同一个 `customer_id` 会出现多次，这是正常交易，不是重复数据。

:::cards 四个容易混淆的概念
:::card 一笔订单与一件商品
订单数用唯一 `order_id`，件数用 `quantity` 求和。客单价是金额/订单数；每件平均实付价格才是金额/件数。本数据恰好一单一种商品，但一单仍可多件。
:::
:::card 已退款与退款金额
已退款订单视为全额退款。其 `pay_amount` 仍记录原支付，不会变成0；把全部行直接相加会把已退的钱算进去。没有退款时间，不能做财务月度现金流。
:::
:::card 购买客户与注册客户
客户表有3000名注册客户；2025有已完成订单的购买客户是2427人。退款客户不自动算购买客户，注册更不等于购买。
:::
:::card 估算毛利与净利润
商品成本是静态每件成本。已完成金额减数量乘成本，得到商品毛利估算；平台费、运费、广告、人工、税费均不在表内，绝非净利润。
:::
:::

正式口径如下。报告中可以使用容易读懂的中文，代码里用短变量名，但要在第一次出现时解释。

| 指标 | 本项目定义 | 常见误算 |
|---|---|---|
| 时间窗口 | 下单时间≥2025-01-01且<2026-01-01 | 只拿Excel前3000行当全年 |
| 已完成净销售额 `revenue` | `status=='已完成'` 的 `pay_amount` 之和 | 所有状态直接求和 |
| 全状态原支付GMV | 已完成+已退款的原支付之和 | 只写GMV不写状态口径 |
| 已完成订单数 | 已完成订单的唯一 `order_id` 数 | 件数求和当订单数 |
| 购买人数 | 已完成订单的 `customer_id.nunique()` | 客户表总行数 |
| 客单价 AOV | 已完成金额/已完成订单数 | 单价列的平均值 |
| 订单退款率 | 已退款订单数/全年全部订单数 | 退款额/金额，或仅在已完成表统计 |
| 窗口复购率 | 2025至少2笔已完成订单的客户/2025购买客户 | 除以3000注册客户或称终身忠诚 |
| 目标达成率 | 已完成金额/同期间 `target_gmv` | 不按月份对齐，或先平均月百分比 |

:::warn 名称必须有边界
“已完成净销售额”只是本练习按最终订单状态扣除全额退款的业务统计名，不是财务确认收入，也不是到账资金或净利润。若使用“GMV”，必须写明是全状态原支付GMV还是已完成口径。目标表字段虽然叫 `target_gmv`，本项目约定它与已完成金额比较；目标本身由模拟生成器构造，不是独立真实预算。
:::

## 第三步：读表并保留原样

先在Notebook运行下面的初始化。不要在终端粘贴Python，也不要把路径改成网页下载地址。运行目录按课程约定为 `notebooks/` 或 `solutions/`，因此数据路径以 `../data` 开头。路径出错先回到[文件与路径](lesson:0-2)，不要随意给系统加管理员权限。

```python
import sys
sys.path.insert(0, "..")
from dacheck import check, hint, setup_chinese_font
import pandas as pd
from pathlib import Path

DATA = Path("../data/shop")
orders_raw = pd.read_csv(DATA / "orders.csv", encoding="utf-8-sig")
products = pd.read_csv(DATA / "products.csv", encoding="utf-8-sig")
customers = pd.read_csv(DATA / "customers.csv", encoding="utf-8-sig")
targets = pd.read_csv(DATA / "monthly_targets.csv", encoding="utf-8-sig")
orders = orders_raw.copy()
orders["order_time"] = pd.to_datetime(orders["order_time"], errors="raise")
print(orders.shape, products.shape, customers.shape, targets.shape)
```

```output
(15115, 11) (33, 6) (3000, 7) (12, 2)
```

`copy()` 的作用是留下未经修改的原始材料。不要直接用脏数据教学样本替代完整订单：`orders_dirty.csv` 是2000笔抽样订单加60行人为重复，并混入文本金额、别名、缺失与异常；它服务[清洗课](lesson:3-1)，不是全年全集。会清洗和用错样本是两回事，干净的2060行也不可能自动恢复15115行完整订单。

## 第四步：检查数据，不机械地删行

检查从“业务前提”出发：订单主键是否唯一、关键字段有无缺失、日期是否都在2025年、状态是否只有两类、数量是否正整数、折扣是否0～1、金额是否符合公式、商品与客户是否能关联。评分缺失意味着未评价，不是差评；项目不使用评分计算销售，所以不能因为评分空就删订单。当前订单评分缺失6969行，误删会大幅改变销售统计。

```python
import numpy as np
assert orders["order_id"].is_unique
assert products["product_id"].is_unique
assert customers["customer_id"].is_unique
assert targets["month"].is_unique
assert orders[["order_id", "order_time", "product_id", "customer_id",
               "quantity", "pay_amount", "status"]].notna().all().all()
assert set(orders["status"]) == {"已完成", "已退款"}
assert orders["quantity"].gt(0).all()
assert orders["quantity"].mod(1).eq(0).all()
assert orders["discount"].between(0, 1).all()
assert orders["order_time"].between("2025-01-01", "2026-01-01", inclusive="left").all()
expected_pay = (orders["unit_price"] * orders["quantity"] * (1 - orders["discount"])).round(2)
assert np.isclose(orders["pay_amount"], expected_pay, atol=0.01, rtol=0).all()
```

这里断言是对固定数据前提的验证。断言失败时，先看具体数据与读取方法；不要删掉失败的断言假装通过。Notebook还检查必要字段、评分范围、成本、上架时间和注册时间。质量检查不是“把所有缺失值消灭”，而是确认现有信息是否足以回答问题，并记录哪些字段不能支持进一步分析。

:::try 练习一：这个删行决定合理吗？
有人写 `orders.dropna()` 后说“现在数据很干净”。你应指出什么？
:::fold 参考答案
默认按所有列删空值，会删掉未评价订单。评分不影响交易是否存在，删除它们会改变总体。应单独报告评分缺失，不在本项目据此删除订单。关键字段若缺失则停下来核实，不自动填0。
:::
:::

## 第五步：多表关联一定要验证

订单表中 `product_id` 指向商品表，`customer_id` 指向客户表。一个商品或客户可以对应很多订单，所以是“订单多、右表一”。左连接保留订单，`many_to_one` 限制右表键唯一，匹配标记让你看到找不到的商品。即使行数相同，也要检查订单集合与唯一性：一个订单丢了，另一个重复了，行数仍可能一样。

```python
joined = orders.merge(products, on="product_id", how="left",
                      validate="many_to_one", indicator="product_match")
assert joined["product_match"].eq("both").all()
joined = joined.merge(customers, on="customer_id", how="left",
                      validate="many_to_one", indicator="customer_match")
assert joined["customer_match"].eq("both").all()
assert len(joined) == len(orders)
assert joined["order_id"].is_unique
assert set(joined["order_id"]) == set(orders["order_id"])
joined = joined.drop(columns=["product_match", "customer_match"])
completed = joined.loc[joined["status"].eq("已完成")].copy()
completed["month"] = completed["order_time"].dt.strftime("%Y-%m")
```

如果商品表某个商品重复两行，普通连接会把对应订单复制；金额求和看起来上升，实际是连接制造了增长。若用内连接，缺少匹配的订单会被悄悄删掉。所以“成功运行”和“统计正确”并不等价。回到[合并表格](lesson:2-4)查看小样例，再在练习本完成 **P-1.7**，交订单号、商品名称、品类、城市四列。检查函数会核对完整订单是否保留，但代码中的关系验证仍需要你自己写。

## 第六步：做全年指标，再相互对账

```python
revenue = completed["pay_amount"].sum()
refunds = orders.loc[orders["status"].eq("已退款")]
print(f"已完成净销售额：{revenue:,.2f}元")
print(f"购买人数：{completed['customer_id'].nunique()}人")
print(f"客单价：{revenue / len(completed):.2f}元/单")
print(f"订单退款率：{len(refunds) / len(orders):.2%}")
```

:::df 实算基准，不是虚构企业的真实业绩
| 指标 | 当前随包数据结果 |
|---|---:|
| 全年订单 | 15115笔 |
| 已完成订单 | 13996笔 |
| 已退款订单 | 1119笔 |
| 全状态原支付GMV | 1928401.00元 |
| 已完成净销售额 | 1784371.10元 |
| 已退款原支付 | 144029.90元 |
| 购买人数 | 2427人 |
| 客单价 | 127.49元/单 |
| 订单退款率 | 7.40% |
:::

第一条对账：13996+1119=15115。第二条：1784371.10+144029.90=1928401.00。第三条：后面所有月份金额与所有品类金额分别求和，都应等于已完成金额。对账不能证明所有业务定义正确，但能发现漏筛选、重复连接和误用样本等常见错误。练习 **P-1.1** 交六键字典，退款率交小数0.074032…而不是字符串“7.40%”；展示格式与计算值分开。

## 第七步：月度趋势，先表后图

```python
monthly = completed.groupby("month", as_index=False).agg(
    revenue=("pay_amount", "sum"), orders=("order_id", "nunique"))
monthly["aov"] = monthly["revenue"] / monthly["orders"]
monthly["mom"] = monthly["revenue"].pct_change()
```

`month` 使用有序的 `2025-01` 字符串而不是“1月、10月、2月”混排。环比是与上个月相比，第一月没有上个月，结果为缺失；不要填成0再解释“1月零增长”。没有2024数据，所以本项目不能计算同比。练习 **P-1.2** 只交 `month, revenue, orders` 三列，按月份升序。

```python
import matplotlib.pyplot as plt
setup_chinese_font()
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(monthly["month"], monthly["revenue"] / 10000, marker="o")
ax.set(title="2025月度已完成净销售额（模拟数据）", xlabel="下单月份", ylabel="金额（万元）")
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()
plt.show()
```

图应告诉读者时间、口径与单位。11月229054元最高，2月95747.40元最低，12月202855.40元次高。但“11月高”只是观察，不自动推出“促销有效”。模拟生成器预设了增长、季节、活动和商品上架规则，图形出现规律正是生成规则的结果；不是你发现了真实世界的因果效应。

:::compare 让一句结论变可靠
:::bad
双十一活动让公司销售提升，证明应该加倍投放。
:::
:::good
模拟订单中11月已完成金额为229054元、全年月度最高。生成器设置了季节波动，且缺少流量、费用与对照组，因此不能证明活动增量。真实场景需补活动记录和可比对照后验证投放建议。
:::
:::

## 第八步：平台退款，要用没有筛掉退款的表

```python
platform_stats = orders.assign(is_refund=orders["status"].eq("已退款")).groupby(
    "platform", as_index=False).agg(all_orders=("order_id", "nunique"), refunds=("is_refund", "sum"))
platform_stats["refund_rate"] = platform_stats["refunds"] / platform_stats["all_orders"]
```

| 平台 | 全年订单 | 退款订单 | 订单退款率 |
|---|---:|---:|---:|
| 微信小程序 | 4497 | 198 | 4.40% |
| 抖音小店 | 3732 | 477 | 12.78% |
| 淘宝 | 6886 | 444 | 6.45% |

完成 **P-1.3**，按平台名升序交四列。图表使用柱状图，纵轴为百分比且从0开始。本例差异受到模拟器中平台退款概率设定的影响，不能宣传某个真实平台“质量差”。在真实工作中还需比较品类、促销、用户群及退款原因，必要时用更进一步的方法；本课只做描述统计，不声称完成显著性检验。

:::quiz 分母理解检查
只保留已完成订单后再统计退款率，会出现什么问题？
- [ ] 因为表更干净，所以更准确
- [x] 退款行已经删掉，分子会被人为变成0
- [ ] pandas会自动帮你找回退款订单
---
收入统计与退款统计需要不同的筛选口径。可以保留全年全集，再分别构造各分析表。
:::

## 第九步：品类贡献与成本边界

```python
category_stats = completed.groupby("category", as_index=False).agg(revenue=("pay_amount", "sum"))
category_stats["share"] = category_stats["revenue"] / category_stats["revenue"].sum()
category_stats = category_stats.sort_values("revenue", ascending=False)
completed["estimated_goods_cost"] = completed["quantity"] * completed["cost"]
completed["estimated_gross_profit"] = completed["pay_amount"] - completed["estimated_goods_cost"]
```

完成 **P-1.4**，交 `category, revenue, share`，按金额降序。香薰534303.60元、份额29.94%，书籍300468.70元、16.84%，帆布包299920.90元、16.81%。这三类合计约63.59%，可以作为复核贡献结构的起点，而不是仅凭收入就把其他品类淘汰。收入份额受价格、销量和时间共同影响，日历9月起上架，全年金额不能直接解释成需求弱。

横向条形图适合长中文标签；收入降序后将纵轴反转，最大项放在顶部。份额加起来因四舍五入可能不是恰好100%，但未舍入计算之和应为1。成本估算总计849059.30元，商品毛利估算935311.80元，估算毛利率52.42%。成本不按折扣打折，售价折扣影响收入；成本表只是静态估计。没有运费、退货损耗与平台费等支出，不能说店铺“净赚93.53万元”。

## 第十步：月目标按键对齐

```python
expected_months = [f"2025-{m:02d}" for m in range(1, 13)]
assert sorted(targets["month"]) == expected_months
assert monthly["month"].tolist() == expected_months
performance = monthly[["month", "revenue"]].merge(
    targets, on="month", how="left", validate="one_to_one", indicator=True)
assert performance["_merge"].eq("both").all()
performance = performance.drop(columns="_merge")
performance["achievement"] = performance["revenue"] / performance["target_gmv"]
performance["gap"] = performance["revenue"] - performance["target_gmv"]
```

不按表格第几行直接相除，因为排序和缺月会让行位置不同。两个表都转成同样的年月字符串，通过 `month` 连接，验证唯一性、12个月齐全和无未匹配。完成 **P-1.5**，只交月份、实际金额、目标金额与达成率四列。

全年目标1896000元，全年实际1784371.10元，全年达成率94.11%，差额为-111628.90元。达标月份是5、6、11、12月，共4个月。全年达成率是总实际/总目标，不是12个月达成率的简单平均。模拟目标与实际数据存在生成关系，因此不能拿“达标4个月”评价真实管理者水平；它只是练习口径、对齐和加权汇总的材料。

## 第十一步：窗口复购率，说出观察偏差

```python
purchase_counts = completed.groupby("customer_id")["order_id"].nunique()
repeat_buyers = purchase_counts.ge(2).sum()
repeat_rate = repeat_buyers / len(purchase_counts)
```

1881/2427=77.50%。完成 **P-1.6**，交0～1小数。这个比率仅表示2025观察窗口内购买客户中至少两笔已完成订单的比例，不是终身复购率，不是所有3000注册客户的转化率，更不是每月留存率。年末才首次下单的人可复购的时间更短，不能仅凭一次年度汇总就说他们“不忠诚”。同期群与留存课程属于下一批，先记下这种比较风险，别编造本课没有做出的分析。

## 第十二步：写报告，保留别人重做的路径

报告模板在 `report/analysis-report-template.md`，当前实算参考报告在 `report/project-reference-report.md`。Markdown可以用文本编辑器阅读；网页是学习入口，报告是交付材料，不需要强行转换成Word。若自己美化报告或让GPT/Kimi调整外观，请保留表头、数据来源、模拟声明、图注、口径和限制；好看的排版不能替代核验。

报告结构建议为：一句话问题→数据与范围→方法与口径→质量检查→结果表与图→3～5项发现→限制→建议和待补数据→复现说明。每项发现至少有一个实算数字和证据位置，建议要写成可检验步骤。例如先按“退款原因×品类×平台”补表，再决定是否优化商品介绍，而不是直接承诺“退款率会下降5%”。未执行的建议用“建议、待验证”，不写成“已实现”。

导出时别覆盖原始文件。Notebook用 `tempfile.TemporaryDirectory()` 演示CSV和Excel汇总表的生成及回读；目录关闭后会删除。正式作品请另建输出目录，确认不在 `data/` 下，使用新的文件名。静态图可保存PNG，交互图若采用Plotly应把脚本内嵌，不能依赖CDN；具体方法见[交互图课](lesson:4-3)。

:::try 最后四个独立口头练习
1. 金额对账正确就一定能证明促销有效吗？
2. 将 `pay_amount.mean()` 直接当客单价是否总正确？
3. 目标表漏掉一个月时该继续报告年度达成率吗？
4. 把本项目写进简历，什么表达真实且有价值？
:::fold 参考答案
1. 不能。对账验证统计一致性，因果还需研究设计和额外数据。
2. 先筛已完成且一行一单时等价；全状态直接平均会含退款，真实多商品订单表还可能按行而非按单加权。本项目明确使用金额/唯一订单数。
3. 应停下来核实缺月和预算口径，不能静默删月或填0再算。
4. “独立完成模拟文创店年度分析作品，处理15115笔订单，验证多表关系，制作月趋势及平台退款分析并交付可复现报告。”不冒称服务真实公司或创造真实增长。
:::
:::

## 常见错误与纠正路线

| 症状 | 首先检查 | 纠正路径 |
|---|---|---|
| 金额接近1928401而非1784371.10 | 是否筛已完成 | 对照口径卡，保留两个指标但名称区分 |
| 年度只有3000笔 | 是否读取Excel样本 | 换为完整 `orders.csv` |
| 合并后金额增加 | 商品/客户键是否重复 | 使用关系验证与匹配检查 |
| 平台退款率全为0 | 是否在completed表统计 | 回到全年orders构造退款标记 |
| 复购率得到62.70%左右 | 是否除以3000 | 分母改为有已完成购买的2427人 |
| 月目标对应不上 | month类型与月份齐全性 | 统一YYYY-MM，按键合并 |
| 中文显示方框 | 字体未找到 | 调用字体助手并看提示，查[报错表](lesson:A-2) |
| `...`参与计算报错 | 后续代码依赖空白答案 | 按原练习本运行；独立示例不使用答案变量 |

:::job 求职中的价值
作品的说服力来自“我为什么这样定义、怎样避免误算、哪些事尚不能下结论”，而不只是会调用库。面试时可挑一个错误口径讲清：例如连接重复制造虚假收入，或复购分母误用注册客户。承认模拟来源，展示可复现文件与质量记录，是专业而诚实的表达。
:::

:::checklist 项目验收
- [ ] 能解释每行是一单一种商品，区分笔数与件数。
- [ ] 完整订单15115笔，连接后仍15115个唯一订单且全部匹配。
- [ ] 已完成13996笔，购买2427人，已完成净销售额1784371.10元。
- [ ] 月份和品类金额分别能对账到全年金额。
- [ ] 七题都通过，学生版未作答运行全部也不会因答案变量崩溃。
- [ ] 目标按month对齐，全年达成率用总实际/总目标。
- [ ] 图有模拟声明、时间、口径、单位，报告至少三项发现。
- [ ] 报告写清静态成本、无上年/流量/因果证据等限制。
- [ ] 建议尚未执行，简历不虚构真实业绩，原始数据未覆盖。
:::
