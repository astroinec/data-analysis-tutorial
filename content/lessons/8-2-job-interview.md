---
summary: 系统拆解数据分析面试四大高频题型（SQL 笔试、指标异动排查、A/B 测试判断、项目深挖），并在练习本完成 4 道模拟面试真题。
prereq: 已完成阶段 5～7 与第 8-1 课
---

:::goal 本课可验证目标
- 掌握数据分析面试四大模块的标准答题框架：SQL、指标异动、A/B 测试与项目复盘。
- 在练习本中独立写出两道高频面试 SQL（渠道注册→下单转化率、月度累计窗口函数）。
- 用结构化思路完成漏斗瓶颈定位与 A/B 新老客异质性拆解。
- 准备 3 个高质量的面试反问问题，展现业务思考深度。
:::

打开 [8-2 练习本](../../notebooks/8-2_job_interview.ipynb)，选择 `Python (da-course)` 内核。建议给自己计时 **25 分钟**，模拟真实机考独立完成 4 道实战题，再运行 `check(...)` 验收。

## 1. 面试四大高频模块与标准答题框架

:::tabs
:::tab 模块一：SQL 笔试（占笔试 60% 以上）
高频套路只有五类，全部在阶段 6 练过：
1. **条件聚合**：用 `CASE WHEN` 一条 SQL 算转化率/退款率（记得 `* 1.0`）。
2. **LEFT JOIN 防丢主表**：统计“注册了但未下单”或“各渠道转化率”时，右表状态过滤写在 `ON`，不要写在 `WHERE`。
3. **分组 Top N**：CTE + `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)`。
4. **累计/移动汇总**：`SUM(revenue) OVER (ORDER BY month)`。
5. **留存/连续登录**：自连接或 `LAG/LEAD` 窗口函数算日期差。
:::
:::tab 模块二：指标异动排查题
经典问法：“昨天 DAU 跌了 15%，怎么查？”“某月 GMV 降了，怎么分析？”

**四步结构化答题模板**：
1. **先排假警报**：确认口径是否变更、埋点/数据链路是否延迟或丢数、是否碰上节假日或天气等周期因素。
2. **公式拆解**：如 `GMV = 流量 × 转化率 × 客单价` 或 `DAU = 新用户 + 留存老用户 + 回流用户`，定位是哪一项在掉。
3. **维度下钻**：按渠道、iOS/Android、新老客、城市层级、核心品类逐层切分，把问题缩小到具体人群或页面。
4. **内外因归因与验证**：内部查版本发布、活动结束、支付故障；外部查竞品大促、舆情；给出“先验证什么数据，再采取什么动作”。
:::
:::tab 模块三：A/B 测试与统计题
高频追问：
- **“p 值小于 0.05 就一定全量上线吗？”** → 不一定！还要看 SRM 分流是否均衡、提升幅度是否具备业务价值（统计显著 ≠ 业务显著）、护栏指标（加载耗时、退款率）是否恶化、以及新老客/端内外是否存在异质性。
- **“实验组和对照组样本量明显偏离 50/50 怎么办？”** → 触发 SRM 警报，立即停止下结论，优先排查分流逻辑、埋点上报丢失或客户端兼容 Bug。
- **“整体转化率降了，但新客和老客都在涨，可能吗？”** → 可能，这就是**辛普森悖论**，检查新老客流量权重是否大幅变化。
:::
:::tab 模块四：项目深挖与反问环节
面试官常针对简历项目连环追问：
- “你这个指标的分母为什么选它，不选另一个？”
- “如果老板不同意你的建议，你怎么说服他？”
- “如果重做一次这个项目，你觉得哪里还能改进？”

**高质量反问（选 1～2 个）**：
- “团队目前日常工作中，取数、看板维护和专题分析的大致时间占比是怎样的？”
- “如果我有幸加入，前 3 个月最希望能帮团队解决哪类具体的业务分析问题？”
:::
:::

## 2. 面试口述避坑指南

:::compare 回答业务案例题时的正误对比
:::bad 想到哪说到哪、没有结构
“我觉得可能是最近天气不好，或者竞争对手搞活动了，也可能是我们商品太贵了，还可以看看是不是小红书流量少了……”
:::
:::good 先给框架、再逐层收窄
“我会分三步排查：第一步先核对数据链路和口径，排除统计误差；第二步把销售额拆成购买人数、人均单数和客单价，先锁定是流量问题还是客单问题；第三步按渠道、设备和品类下钻，找出具体拖累项后再结合内外因提出验证方案。”
:::
:::

:::quiz 面试 SQL 陷阱快问快答
面试官让你写 SQL 计算“各获客渠道的注册到下单转化率（已完成下单人数 / 注册人数）”，`customers` 左连接 `orders` 时，`o.status = '已完成'` 应该写在哪里？
- [ ] 写在 `WHERE` 里，这样性能更快
- [x] 写在 `LEFT JOIN ... ON` 里，这样未下单的注册客户仍会保留在分母中
- [ ] 不用写，直接 `COUNT(o.order_id) / COUNT(c.customer_id)`
---
写在 `WHERE` 会把右表为 `NULL` 的未下单客户过滤掉，导致算出来的转化率变成虚假的 100%！同时分子分母都必须用 `COUNT(DISTINCT customer_id)` 去重。
:::

## 3. 练习本四道模拟面试真题

:::try 8-2.1 面试 SQL 1：各获客渠道注册到下单转化率
在 `shop.db` 中输出 `channel, registered, buyers, conv_rate`，按 `conv_rate` 降序。
:::fold 参考答案
```sql
SELECT c.channel,
       COUNT(DISTINCT c.customer_id) AS registered,
       COUNT(DISTINCT o.customer_id) AS buyers,
       COUNT(DISTINCT o.customer_id) * 1.0 / COUNT(DISTINCT c.customer_id) AS conv_rate
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status = '已完成'
GROUP BY c.channel
ORDER BY conv_rate DESC
```
:::
:::

:::try 8-2.2 面试 SQL 2：月度销售额与年内累计销售额
用 CTE + 窗口函数 `SUM(revenue) OVER (ORDER BY month)` 输出 `month, revenue, cum_revenue`，按 `month` 升序。
:::fold 参考答案
```sql
WITH m AS (
    SELECT substr(order_time, 1, 7) AS month, SUM(pay_amount) AS revenue
    FROM orders WHERE status = '已完成' GROUP BY month
)
SELECT month, revenue, SUM(revenue) OVER (ORDER BY month) AS cum_revenue
FROM m ORDER BY month ASC
```
:::
:::

:::try 8-2.3 面试业务题：定位试看到点击付费转化最低的渠道
结合 `app_events` 与 `app_users`，找出 `start_trial → click_pay` 转化率最低的 `lowest_channel` 和 `lowest_rate`。
:::fold 参考答案
实算：`lowest_channel = "信息流广告"`，`lowest_rate ≈ 26.35%`。
:::
:::

:::try 8-2.4 面试实验题：拆解新老客的转化率绝对提升
在 `ab_experiment.csv` 中计算新客（`is_new_user == 1`）与老客（`0`）的 `treatment - control` 转化率差值，返回 `new_lift` 与 `old_lift`。
:::fold 参考答案
实算：`new_lift ≈ +0.0249`（+2.49pp），`old_lift ≈ -0.0019`（-0.19pp）。
:::
:::

## 常见问题与心态提醒

| 问题 | 纠正路径 |
|---|---|
| 笔试遇到没见过的业务场景大脑空白 | 别背具体行业的答案，永远套用“口径核验 → 公式拆解 → 维度下钻 → 假设验证”通用骨架 |
| 被问到不会的高级算法/工具 | 坦诚说目前未在项目中深入使用，但能关联已有基础说明学习路径，绝不现场硬编 |
| SQL 写完直接交卷不检查 | 交卷前默查三点：`DISTINCT` 没漏？`LEFT JOIN` 条件放 `ON` 了？整数除法乘 `1.0` 了？ |

:::checklist 面试冲刺验收
- [ ] 我能流畅口述指标异动四步排查框架与 A/B 测试五步复盘框架。
- [ ] 我能在 25 分钟内独立跑通练习本 8-2.1 ～ 8-2.4 四道模拟真题。
- [ ] 我已针对自己作品集里的每个项目准备了“口径、局限、改进方向”三个追问回答。
- [ ] 我准备好了 2～3 个与目标岗位业务相关的反问问题。
:::

接下来，如果你还没完成另外两个实战项目，可以继续挑战：[项目二：App 转化漏斗与用户留存](lesson:P-2) 与 [项目三：A/B 测试分析](lesson:P-3)。
