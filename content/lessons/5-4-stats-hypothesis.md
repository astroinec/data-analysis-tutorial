---
summary: 用白话理解零假设、p 值、显著性水平与两类错误，并用 scipy 完成转化率卡方检验与耗时 Welch t 检验。
prereq: 已完成第 5-2 与 5-3 课，理解样本波动与置信区间
---

:::goal 本课可验证目标
- 用白话解释零假设 $H_0$、备择假设 $H_1$、p 值与显著性水平 $\alpha = 0.05$。
- 区分比例类指标（用卡方检验/比例 z 检验）与连续均值指标（用 Welch t 检验）。
- 在虚构 A/B 测试数据 `ab_experiment.csv` 上检验主指标转化率与护栏指标加载耗时。
- 区分“统计显著”与“业务显著”，并识别新老客之间的异质性效果。
:::

打开 [5-4 练习本](../../notebooks/5-4_stats_hypothesis.ipynb)，选择 `Python (da-course)` 内核。本课使用虚构的“商品详情页新版评价卡片” A/B 测试数据 `data/abtest/ab_experiment.csv`（12000 名用户，14 天）。

## 1. 假设检验的底层逻辑：像法庭上的“无罪推定”

:::analogy 法庭上的无罪推定
法官先假定嫌疑人“无罪”（**零假设 $H_0$：新旧版本没有真实差异**）。接着收集证据（实验数据）。如果“在无罪前提下，出现这么极端证据的概率”极低（**p 值 < 0.05**），法官才推翻无罪假定，支持**备择假设 $H_1$（两组确实存在差异）**。如果证据不够强（p ≥ 0.05），只能说“证据不足以推翻无罪”，而不能宣称“证明绝对无罪”。
:::

因此，**p 值**的准确白话含义是：**假如新旧版本本来完全没区别，单靠随机运气出现“当前这么大甚至更大差异”的概率。**

:::warn 最容易说错的一句话
千万不要把 `p = 0.014` 解释成“实验组有 98.6% 的概率比对照组好”或“零假设为真的概率是 1.4%”！p 值是在假设 $H_0$ 为真的前提下算出来的条件概率。
:::

## 2. 两类错误：假阳性与假阴性

| 真实情况 \ 检验结论 | 拒绝 $H_0$（认为有效） | 不拒绝 $H_0$（认为没证据） |
|---|---|---|
| 真实无效（$H_0$ 为真） | **一类错误（假阳性，概率 $\alpha$）**：把没用的功能上线了 | 正确决策 |
| 真实有效（$H_1$ 为真） | 正确决策（统计功效 Power = $1-\beta$） | **二类错误（假阴性，概率 $\beta$）**：错过了好功能 |

## 3. 实战检验：比例用卡方，均值用 Welch t

在 `ab_experiment.csv` 中，对照组（`control`）5976 人转化率 **8.75%**，实验组（`treatment`）6024 人转化率 **10.06%**，高出 1.31 个百分点。

```python
ct = pd.crosstab(ab["group"], ab["converted"])
chi2, p_val, _, _ = stats.chi2_contingency(ct, correction=False)
print(f"chi2 = {chi2:.4f}, p_value = {p_val:.5f}")
```

```output
chi2 = 6.0226, p_value = 0.01412
```

- **主指标（转化率，0/1 比例）**：`p = 0.0141 < 0.05`，统计显著！说明总体转化率提升不太可能是随机波动。
- **护栏指标（`page_load_ms`，连续均值）**：用不要求两组方差相等的 Welch t 检验 `stats.ttest_ind(t_ms, c_ms, equal_var=False)`，实测实验组平均慢了 **+43.52 ms**（455.76ms → 499.28ms），`t = 26.17`，`p = 7.68e-147`，极度显著！
- **统计显著 ≠ 必须全量上线**：还要权衡业务收益与性能代价，更要拆开人群看——把新老客拆开后发现，新客转化率大涨 **+2.49 个百分点**（`p = 0.00027`），而老客几乎无变化（−0.19 个百分点，`p = 0.82`）！

:::quiz 关于 p 值与统计显著的判断
某 A/B 测试样本量极大（每组 500 万人），测得点击率提升 0.02 个百分点，`p = 0.001`。你该如何给产品经理建议？
- [ ] 因为 p < 0.01 非常显著，说明收益巨大，应立即全量上线
- [x] 这是“统计显著但业务未必显著”：差异大概率不是随机波动，但 0.02pp 的提升需结合研发成本和护栏指标综合权衡
- [ ] p = 0.001 说明 99.9% 的用户都更喜欢新版
---
超大样本下极微小的差异也能达到极小的 p 值，决策必须同时看效应量（提升幅度）与业务成本。
:::

## 4. 四道独立练习

:::try 5-4.1 A/B 分组转化率汇总
按 `group` 分组（`as_index=False`）统计 `users`、`conversions`、`conv_rate`，按 `group` 升序。
:::fold 参考答案
```python
ab_summary_ans = (
    ab.groupby("group", as_index=False)
    .agg(users=("user_id", "size"), conversions=("converted", "sum"), conv_rate=("converted", "mean"))
    .sort_values("group").reset_index(drop=True)
)
```
:::
:::

:::try 5-4.2 总体转化率卡方检验
用 `pd.crosstab(ab["group"], ab["converted"])` 和 `stats.chi2_contingency(ct, correction=False)` 计算 `chi2` 和 `p_value`。
:::fold 参考答案
```python
ct_ex = pd.crosstab(ab["group"], ab["converted"])
chi2_val, p_val_ex, _, _ = stats.chi2_contingency(ct_ex, correction=False)
chi2_ans = {"chi2": float(chi2_val), "p_value": float(p_val_ex)}
```
:::
:::

:::try 5-4.3 护栏指标页面加载耗时 Welch t 检验
用 `stats.ttest_ind(..., equal_var=False)` 检验两组 `page_load_ms`，返回 `t_stat` 与 `p_value`。
:::fold 参考答案
```python
c_ms_ex = ab.loc[ab["group"].eq("control"), "page_load_ms"]
t_ms_ex = ab.loc[ab["group"].eq("treatment"), "page_load_ms"]
t_val, p_t = stats.ttest_ind(t_ms_ex, c_ms_ex, equal_var=False)
ttest_ans = {"t_stat": float(t_val), "p_value": float(p_t)}
```
:::
:::

:::try 5-4.4 新客群体转化率提升与卡方 p 值
筛选 `is_new_user == 1`，计算 `lift = treatment - control` 以及卡方检验（`correction=False`）`p_value`。
:::fold 参考答案
```python
sub_new = ab.loc[ab["is_new_user"].eq(1)]
rates_new = sub_new.groupby("group")["converted"].mean()
_, p_new, _, _ = stats.chi2_contingency(pd.crosstab(sub_new["group"], sub_new["converted"]), correction=False)
new_user_ans = {"lift": float(rates_new["treatment"] - rates_new["control"]), "p_value": float(p_new)}
```
实算：lift = +2.49pp，p = 0.000275。
:::
:::

## 常见问题与求职用途

| 问题 | 纠正路径 |
|---|---|
| 每天偷看 p 值，一低于 0.05 就提前停实验 | 偷看会大幅推高假阳性率，应提前约定实验周期（如 14 天覆盖完整周周期） |
| 对转化率直接用 `ttest_ind` 还是 `chi2_contingency`？ | 比例类指标优先用卡方检验或双样本比例 z 检验；连续均值用 `ttest_ind(..., equal_var=False)` |
| 只看主指标不看护栏指标 | 性能变慢、退款率飙升等负向副作用必须纳入护栏监控 |

:::job 面试加分表达
“做 A/B 测试复盘时，我会按‘SRM 分流校验 → 主指标显著性与置信区间 → 护栏指标 → 分人群异质性 → 业务决策’五步展开，并清楚区分统计显著与业务显著。”
:::

:::checklist 本课验收
- [ ] 我能用白话准确解释 p 值，不把它说成“新版更好的概率”。
- [ ] 我会用 `scipy.stats.chi2_contingency` 与 `ttest_ind(..., equal_var=False)` 做检验。
- [ ] 我能解释为什么护栏指标和分人群拆解同样重要。
- [ ] 练习本 5-4.1 ～ 5-4.4 四题全部通过检查。
:::

下一课：[进入阶段 6：SQL SELECT 查询与筛选](lesson:6-1)，也可以在学完后直接挑战[项目三：A/B 测试分析](lesson:P-3)。
