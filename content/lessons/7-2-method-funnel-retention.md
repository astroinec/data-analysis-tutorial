---
summary: 用虚构“墨读 App”数据掌握转化漏斗、次日/7日/30日留存率与同期群分析，避开观察窗口截断陷阱。
prereq: 已完成第 7-1 课，熟练日期差计算与多表合并
---

:::goal 本课可验证目标
- 按唯一用户数构建多步转化漏斗，区分“环节转化率（相对上一步）”与“整体转化率（相对第一步）”。
- 用 `active_date - register_date` 计算 D1、D7、D14、D30 留存率，并避开观察窗口不足的分母陷阱。
- 分渠道对比 7 日留存率，识别“拉新量大但留存低”的低效渠道。
- 按注册月份构造同期群（Cohort）留存表，学会横向看衰减、纵向看趋势。
:::

打开 [7-2 练习本](../../notebooks/7-2_method_funnel_retention.ipynb)，选择 `Python (da-course)` 内核。本课使用虚构的“墨读 App”三张表（`data/app/`：6000 名 2025-07-01 至 2025-09-28 注册用户，活跃观察截至 2025-10-31）。

## 1. 转化漏斗：找到流失最严重的“卡点”

漏斗分析跟踪用户从打开 App 到最终付费的每一步。**务必按唯一 `user_id` 去重**，否则一个用户反复浏览课程 10 次会把 `view_course` 抬得比 `app_open` 还高！

:::df 墨读 App 全量五步漏斗（虚构数据）
| 步骤 | 唯一用户数 | 环节转化率（相对上步） | 整体转化率（相对首步） |
|---|---:|---:|---:|
| 1. `app_open`（打开） | 6000 | 100.00% | 100.00% |
| 2. `view_course`（看课） | 4927 | 82.12% | 82.12% |
| 3. `start_trial`（试听） | 2640 | 53.58% | 44.00% |
| 4. `click_pay`（点付费） | 1081 | **40.95%** | 18.02% |
| 5. `pay_success`（付成功） | 595 | 55.04% | 9.92% |
:::

`start_trial → click_pay` 只有 40.95% 的环节转化率，是五步中流失最大的瓶颈。

## 2. 留存率与“观察窗口截断”陷阱

- **次日留存（D1）**：注册第 0 天的人里，在注册后第 1 天再次活跃的比例。
- **7 日留存（D7）**：注册后恰好第 7 天再次活跃的比例（同理 D14、D30）。
- 本数据集实测全量留存：**D1 = 40.88%，D7 = 17.82%，D14 = 13.68%，D30 = 9.97%**。

:::warn 真实业务里最容易踩的坑：窗口不足却把人算进分母
如果今天是 10 月 31 日，你想算 10 月全部新用户的 30 日留存，10 月 25 日才注册的用户根本还没活到第 30 天！把他们放进分母，会人为把 30 日留存拉低。正确做法：**只把注册日期早于 `截止日 - 30天` 的用户放进 D30 分母**。本教程数据注册截止 9 月 28 日、活跃截止 10 月 31 日，所有 6000 人均满足 30 天完整窗口。
:::

## 3. 同期群（Cohort）分析：横向看衰减，纵向看迭代

把同一时期（同一周或同一月）注册的用户编成一组，称为一个**同期群**。
- **横向看**：同一批用户随天数（D1 → D7 → D30）的自然衰减速度，看曲线何时趋于平缓（留存稳定线）。
- **纵向看**：比较 7 月、8 月、9 月注册的几批用户的 D7 留存，判断产品改版或渠道结构变化是否让新用户留存变好了。

按渠道拆开 D7 留存率，差距一目了然：**朋友推荐 22.47% > 自然搜索 19.52% > 小红书 19.25% >> 信息流广告 12.13%**。信息流广告拉新量不小，但后续留存远低于其他渠道。

:::quiz 漏斗去重原则
统计某 App 从“打开首页”到“点击购买”的转化漏斗时，如果直接用事件行数（`COUNT(*)`）而不是唯一用户数（`nunique(user_id)`），可能出现什么荒谬结果？
- [ ] 转化率永远等于 0
- [x] 若少数用户反复点击按钮多次，下一步事件数可能大于上一步，算出超过 100% 的转化率
- [ ] pandas 会直接报错拒绝计算
---
人头漏斗必须按用户 ID 去重，确保每个用户在每个步骤最多计数一次。
:::

## 4. 四道独立练习

:::try 7-2.1 App 五步转化漏斗表
按 `["app_open", "view_course", "start_trial", "click_pay", "pay_success"]` 顺序计算 `step, users, step_rate, overall_rate`。
:::fold 参考答案
```python
steps_ex = ["app_open", "view_course", "start_trial", "click_pay", "pay_success"]
cnt_ex = [events.loc[events["event_name"].eq(st), "user_id"].nunique() for st in steps_ex]
ans_7_2_1 = pd.DataFrame([
    {"step": st, "users": u, "step_rate": 1.0 if i == 0 else u / cnt_ex[i - 1], "overall_rate": u / cnt_ex[0]}
    for i, (st, u) in enumerate(zip(steps_ex, cnt_ex))
])
```
:::
:::

:::try 7-2.2 全量用户 D1/D7/D14/D30 留存率
计算 `day_diff = (active_date - register_date).dt.days`，返回 `d1, d7, d14, d30` 四键字典。
:::fold 参考答案
实算：d1=0.4088, d7=0.1782, d14=0.1368, d30=0.0997。
:::
:::

:::try 7-2.3 各渠道 7 日留存率对比
按 `channel` 统计 `users, d7_retained, d7_rate`，按 `d7_rate` 降序排列。
:::fold 参考答案
```python
base_ch = users.groupby("channel", as_index=False).agg(users=("user_id", "nunique"))
d7_ch = au_ch.loc[au_ch["day_diff"].eq(7)].groupby("channel", as_index=False).agg(d7_retained=("user_id", "nunique"))
ans_7_2_3 = base_ch.merge(d7_ch, on="channel", how="left")
ans_7_2_3["d7_retained"] = ans_7_2_3["d7_retained"].fillna(0).astype(int)
ans_7_2_3["d7_rate"] = ans_7_2_3["d7_retained"] / ans_7_2_3["users"]
ans_7_2_3 = ans_7_2_3.sort_values("d7_rate", ascending=False).reset_index(drop=True)
```
:::
:::

:::try 7-2.4 按注册月份制作同期群留存表
按 `register_month`（`2025-07`～`2025-09`）输出 `register_month, users, d1, d7, d30`，按 `register_month` 升序。
:::fold 参考答案
详见 `solutions/7-2_method_funnel_retention.ipynb` 最后一题。
:::
:::

## 常见问题与求职用途

| 问题 | 纠正路径 |
|---|---|
| `active_date - register_date` 报错 TypeError | 先用 `parse_dates` 或 `pd.to_datetime` 把文本转成日期类型，再取 `.dt.days` |
| 用 `count()` 而不是 `nunique()` 算某天留存 | 若同一用户一天产生多条活跃日志，`count()` 会重复计数导致留存虚高 |
| 忽略渠道/设备差异只看全量漏斗 | 全量漏斗找“哪一步掉了”，分维度漏斗找“是谁掉了” |

:::job 面试加分表达
“做留存和同期群分析时，我会第一时间检查注册日期与数据截止日之间是否满足完整观察窗口，避免右截断偏差；同时结合渠道与设备交叉下钻，把‘留存下降’定位到具体获客渠道或客户端体验问题。”
:::

:::checklist 本课验收
- [ ] 我能区分环节转化率与整体转化率，并按唯一用户去重。
- [ ] 我会用日期差计算 D1/D7/D14/D30 留存率，并知道如何避免观察窗口截断。
- [ ] 练习本 7-2.1 ～ 7-2.4 四题全部通过检查。
:::

下一课：[RFM 用户分层](lesson:7-3)，也可以在学完后直接挑战[项目二：App 转化漏斗与用户留存](lesson:P-2)。
