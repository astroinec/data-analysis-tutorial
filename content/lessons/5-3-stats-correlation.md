---
summary: 掌握 Pearson 与 Spearman 相关系数，看懂相关矩阵，并用企鹅数据亲手复现辛普森悖论，牢记“相关不等于因果”。
prereq: 已完成第 5-2 课，能画散点图与按组聚合
---

:::goal 本课可验证目标
- 用 pandas 计算两列数值的 Pearson（线性）与 Spearman（单调）相关系数。
- 生成并解读多变量相关系数矩阵，知道取值范围 `[-1, 1]` 的含义。
- 用 `penguins.csv` 复现辛普森悖论：整体负相关，分物种后全部正相关。
- 识别混杂变量、反向因果与巧合相关，不在报告里把相关性写成因果结论。
:::

打开 [5-3 练习本](../../notebooks/5-3_stats_correlation.ipynb)，选择 `Python (da-course)` 内核。

## 1. 相关系数 r：衡量“是否一起变化”

相关系数 $r$ 落在 $[-1, 1]$ 之间：
- 越接近 `+1`：正相关越强（一个大，另一个也倾向于大）；
- 越接近 `-1`：负相关越强（一个大，另一个倾向于小）；
- 接近 `0`：几乎没有线性/单调关联。

```python
tips = pd.read_csv("../data/public/tips.csv")
print("Pearson :", round(tips["total_bill"].corr(tips["tip"], method="pearson"), 4))
print("Spearman:", round(tips["total_bill"].corr(tips["tip"], method="spearman"), 4))
```

```output
Pearson : 0.6757
Spearman: 0.679
```

:::cards Pearson vs Spearman 怎么选？
:::card Pearson 相关系数
衡量**直线关系**，直接用原始数值计算。对极端离群值敏感；适合分布较对称、关系近似直线的连续变量。
:::
:::card Spearman 秩相关系数
先把数值变成“排名（秩）”，再算相关。衡量**单调关系**（只要一直同步上升即可，不必是直线），抗离群值能力更强。
:::
:::

## 2. 辛普森悖论：不分组看整体，结论可能完全反过来！

在 `penguins.csv` 中，如果我们把三种企鹅混在一起算喙长 `bill_length_mm` 和喙深 `bill_depth_mm` 的相关系数，会得到 **−0.2351**（看起来“嘴越长、嘴越浅”）。但只要按物种 `species` 分开算，三个物种全部变成**显著正相关**！

:::df 企鹅喙长与喙深的相关系数（辛普森悖论实测）
| 分组范围 | Pearson 相关系数 | 方向 |
|---|---:|---|
| 全部企鹅混在一起 | -0.2351 | 负相关 |
| Adelie（阿德利企鹅） | +0.3915 | 正相关 |
| Chinstrap（帽带企鹅） | +0.6535 | 正相关 |
| Gentoo（巴布亚企鹅） | +0.6434 | 正相关 |
:::

为什么会这样？因为 `species`（物种）是一个**混杂变量**：Gentoo 企鹅天生嘴长但嘴较浅，Adelie 企鹅天生嘴短但嘴较深。混在一起画散点图时，物种间的差异把物种内部“嘴越长越深”的真实正相关彻底反转了。

在商业分析里，辛普森悖论每天都在发生：比如“整体转化率下降”，拆开新客和老客一看，其实新客和老客的转化率都涨了，只是转化率较低的新客流量占比突然变大！

## 3. 为什么相关不等于因果？

:::compare 把观察相关误写成因果
:::bad “消费频次和客单价正相关，所以强制用户多买就能提高客单价”
这混淆了关联与因果，既可能是高收入客户（混杂变量）同时买得多且买得贵，也可能是反向因果。
:::
:::good “观察到 A 与 B 呈正相关，可能受客户层级等混杂因素影响，需进一步分层或通过随机实验验证”
先交代相关性、再提出可检验的业务假设，最后用控制变量或 A/B 测试检验因果。
:::
:::

常见的三种伪因果陷阱：
1. **混杂变量（Confounder）**：夏天冰淇淋销量和溺水人数高度正相关，背后的共同原因是气温升高。
2. **反向因果（Reverse Causality）**：医院越多的城市生病记录越多，不是医院让人变病，而是人口多/需求大才建更多医院。
3. **巧合相关**：把足够多毫无关系的时间序列两两配对，总能碰巧撞出高相关。

:::quiz 识别辛普森悖论
某 App 本月 iOS 和 Android 两个端的留存率都比上月上升了 1 个百分点，但全站总留存率反而下降了 0.5 个百分点。最可能的原因是？
- [ ] 代码一定算错了，部分上升整体不可能下降
- [x] 本月留存率本身较低的那个端新增流量占比大幅上升，拉低了加权整体（辛普森悖论）
- [ ] 这说明 iOS 和 Android 之间存在负相关
---
当各子群体的权重（流量占比）发生明显变化时，加权平均完全可能与所有子群体的变化方向相反。
:::

## 4. 四道独立练习

:::try 5-3.1 账单与小费的两种相关系数
计算 `tips` 中 `total_bill` 与 `tip` 的 `pearson` 和 `spearman` 相关系数，存入 2 键字典。
:::fold 参考答案
```python
tips_corr = {
    "pearson": tips["total_bill"].corr(tips["tip"], method="pearson"),
    "spearman": tips["total_bill"].corr(tips["tip"], method="spearman"),
}
```
:::
:::

:::try 5-3.2 生成三列相关系数矩阵
计算 `tips[["total_bill", "tip", "size"]].corr()`（3×3 DataFrame）。
:::fold 参考答案
```python
corr_matrix = tips[["total_bill", "tip", "size"]].corr()
```
:::
:::

:::try 5-3.3 企鹅喙长与喙深的整体相关系数
先 `dropna(subset=["bill_length_mm", "bill_depth_mm"])`，再计算两列 Pearson 相关系数。
:::fold 参考答案
```python
p_sub = penguins.dropna(subset=["bill_length_mm", "bill_depth_mm"])
overall_r = p_sub["bill_length_mm"].corr(p_sub["bill_depth_mm"])
```
实算：-0.2351。
:::
:::

:::try 5-3.4 分物种计算相关系数
按 `species` 分组计算 `bill_length_mm` 与 `bill_depth_mm` 的 Pearson 相关系数，输出 `species, corr` 两列，按 `species` 升序。
:::fold 参考答案
```python
p_sub2 = penguins.dropna(subset=["bill_length_mm", "bill_depth_mm"])
group_r = pd.DataFrame([
    {"species": sp, "corr": g["bill_length_mm"].corr(g["bill_depth_mm"])}
    for sp, g in p_sub2.groupby("species")
]).sort_values("species").reset_index(drop=True)
```
:::
:::

## 常见问题与求职用途

| 问题 | 纠正路径 |
|---|---|
| 对含文本列整表调用 `df.corr()` 报错 | 先用 `df[["列1", "列2"]]` 选出数值列，或传 `numeric_only=True` |
| 看到 `r = 0` 就断定两变量无关 | Pearson 只测线性关系，U 型等非线性关系也可能算出接近 0，务必画散点图 |
| 在报告里写“相关系数 0.68 证明 A 导致 B” | 改为“观察到中等正相关，因果关系需通过对照实验验证” |

:::job 面试加分表达
“面试被问到‘整体指标跌了但各渠道都在涨’时，直接点出辛普森悖论——先查各渠道流量结构（权重）是否变化，再看单渠道质量，这是数据分析师非常核心的拆解敏感度。”
:::

:::checklist 本课验收
- [ ] 我能区分 Pearson 与 Spearman 相关系数的适用场景。
- [ ] 我能画散点图并用企鹅数据解释辛普森悖论。
- [ ] 我能说出混杂变量、反向因果、巧合相关三种伪因果陷阱。
- [ ] 练习本 5-3.1 ～ 5-3.4 四题全部通过检查。
:::

下一课：[假设检验与 A/B 测试](lesson:5-4)。
