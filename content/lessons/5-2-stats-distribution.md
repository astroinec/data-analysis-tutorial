---
summary: 理解总体与样本、中心极限定理、标准误与 95% 置信区间，识别非随机抽样带来的截断偏差。
prereq: 已完成第 5-1 课，会计算均值、标准差与分位数
---

:::goal 本课可验证目标
- 区分“总体参数”与“样本统计量”，理解为什么每次抽样得到的均值都会轻微波动。
- 用固定随机种子模拟中心极限定理，观察右偏总体的样本均值如何趋近钟形分布。
- 计算样本标准误 `SE = std / sqrt(n)` 与大样本 95% 置信区间。
- 对比全年全集与前 3000 行样本的均价差，说清什么是抽样偏差。
:::

打开 [5-2 练习本](../../notebooks/5-2_stats_distribution.ipynb)，选择 `Python (da-course)` 内核。

## 1. 总体与样本：为什么我们只能“估计”？

真实业务里，我们很少能拿到“全部潜在用户”的数据，通常只能拿到一段时期或一部分人的**样本**。

- **总体（Population）**：你想研究的所有对象（例如 2025 全年 13996 笔已完成订单）。
- **样本（Sample）**：从总体中抽出来的一部分（例如随机抽出的 50 笔订单）。
- **抽样波动**：即便完全随机抽样，第一批 50 单的均价可能是 119 元，第二批可能是 136 元。样本均值围绕总体均值上下波动，这种波动的幅度就是**标准误（Standard Error, SE）**。

## 2. 中心极限定理（CLT）：不需要背公式，跑一次就看懂

:::analogy 抛硬币与“样本均值”
单次抛硬币只有 0 或 1，完全不像钟形曲线；但如果每次抛 50 次算正面比例，把这件事重复做 500 轮，这 500 个比例画成直方图就会变成漂亮的对称钟形。
:::

订单实付金额本身是明显右偏的，但只要每次随机抽取 `n = 50` 笔求均值并重复 500 次，这 500 个样本均值会集中在总体均值 127.49 元附近，呈近似正态分布：

```python
rng = np.random.default_rng(2026)
vals = completed["pay_amount"].to_numpy()
means = np.array([rng.choice(vals, size=50, replace=True).mean() for _ in range(500)])
print(f"500次均值的均值={means.mean():.2f}, 均值的标准差={means.std(ddof=1):.2f}")
print(f"理论标准误 std/sqrt(50) = {completed['pay_amount'].std() / np.sqrt(50):.2f}")
```

```output
500次均值的均值=128.00, 均值的标准差=18.50
理论标准误 std/sqrt(50) = 18.68
```

实测的 18.50 元与理论公式 `SE = std / sqrt(n) = 18.68` 非常接近！这就是为什么后续做 A/B 测试时，即使原始订单金额不服从正态分布，只要样本量足够大，依然可以用基于正态/t 分布的检验方法。

## 3. 标准误与 95% 置信区间

标准误衡量“样本均值的精确度”：

$$SE = \frac{s}{\sqrt{n}}, \qquad \text{95\% CI} \approx \bar{x} \pm 1.96 \times SE$$

注意区分两个容易混淆的概念：

:::compare 标准差（SD） vs 标准误（SE）
:::bad 把标准差当成均值误差，或把置信区间说成“95% 的订单都在这个区间内”
全量订单标准差高达 132.10 元，单笔订单跨度很大；而均值的 95% 置信区间只有 `[125.30, 129.68]` 元，显然不可能装下 95% 的单笔订单！
:::
:::good SD 描述个体差异，SE 与 95% CI 描述“均值估计的稳定区间”
样本量 n 扩大到 4 倍，标准误减半，均值估计的置信区间就窄一半；但单笔订单本身的离散度（SD）不会因为多抽样就变小。
:::
:::

## 4. 抽样偏差：样本量再大，抽偏了也没用

`shop_2025.xlsx` 里的订单表只截取了按时间排在最前面的 3000 行（主要是年初月份）。看看它和全年的均价差：

:::df 全集 vs 前 3000 行时间截断样本
| 范围 | 已完成均价（元） | 说明 |
|---|---:|---|
| 2025 全年全集 | 127.49 | 覆盖全年季节与大促 |
| 前 3000 行截断 | 120.00 | 仅覆盖年初，缺少下半年高单价新品与旺季 |
| 绝对偏差 | 7.49 | 即使样本量有 3000 行，非随机截断依然导致明显偏差 |
:::

:::quiz 关于置信区间的正确理解
某实验测得用户客单价均值的 95% 置信区间为 `[125.30, 129.68]` 元，下面哪句话最准确？
- [ ] 有 95% 的订单金额落在 125.30 到 129.68 元之间
- [x] 这是对总体均值的区间估计：如果重复抽样建区间，约 95% 的区间会覆盖真实总体均值
- [ ] 只要样本量够大，哪怕只抽年初 3000 单也能消除季节偏差
---
95% 置信区间衡量的是均值估计的抽样不确定性，不是个体分布区间，也不能修复非随机抽样偏差。
:::

## 5. 四道独立练习

:::try 5-2.1 企鹅体重的均值、标准差与标准误
对 `penguins["body_mass_g"].dropna()` 计算 `mean`、`std`、`se = std / sqrt(n)`。
:::fold 参考答案
```python
mass = penguins["body_mass_g"].dropna()
penguin_se = {"mean": mass.mean(), "std": mass.std(), "se": mass.std() / np.sqrt(len(mass))}
```
实算：n=342，mean=4201.75g，std=801.95g，se=43.36g。
:::
:::

:::try 5-2.2 用固定种子模拟抽样分布
用 `np.random.default_rng(2026)` 从已完成订单 `pay_amount` 有放回抽取 500 次 `size=50` 的样本均值，返回 `mean_of_means` 和 `std_of_means`（`ddof=1`）。
:::fold 参考答案
```python
vals_ex = orders.loc[orders["status"].eq("已完成"), "pay_amount"].to_numpy()
rng_ex = np.random.default_rng(2026)
means_ex = np.array([rng_ex.choice(vals_ex, size=50, replace=True).mean() for _ in range(500)])
clt_answer = {"mean_of_means": float(means_ex.mean()), "std_of_means": float(means_ex.std(ddof=1))}
```
:::
:::

:::try 5-2.3 已完成订单均价的 95% 置信区间
计算 `ci_low = mean - 1.96 * se` 与 `ci_high = mean + 1.96 * se`。
:::fold 参考答案
```python
s_ci = orders.loc[orders["status"].eq("已完成"), "pay_amount"]
se_ci = s_ci.std() / np.sqrt(len(s_ci))
ci_answer = {"ci_low": float(s_ci.mean() - 1.96 * se_ci), "ci_high": float(s_ci.mean() + 1.96 * se_ci)}
```
:::
:::

:::try 5-2.4 计算截断样本与全集的均价绝对偏差
比较全年已完成均价与 `orders.iloc[:3000]` 已完成均价的绝对差值 `abs(...)`。
:::fold 参考答案
```python
full_mean = orders.loc[orders["status"].eq("已完成"), "pay_amount"].mean()
head_done = orders.iloc[:3000]
head_mean = head_done.loc[head_done["status"].eq("已完成"), "pay_amount"].mean()
bias_diff = float(abs(full_mean - head_mean))
```
:::
:::

## 常见问题与求职用途

| 问题 | 纠正路径 |
|---|---|
| 每次运行模拟结果不一样 | 固定随机种子 `np.random.default_rng(2026)`，保证结果可复现 |
| 忘记去掉企鹅体重缺失值就取 `len()` | 先 `.dropna()` 再算 `len()`，否则分母偏大、标准误算小 |
| 混淆 `ddof=0` 与 `ddof=1` | numpy 默认 `ddof=0`，pandas 默认 `ddof=1`；算样本标准差请显式写 `ddof=1` |

:::job 面试加分表达
“拿到一份抽样数据时，我会先检查抽样方式是否存在时间截断或渠道幸存者偏差，再通过标准误和 95% 置信区间判断波动范围，不把小样本偶然波动当成趋势。”
:::

:::checklist 本课验收
- [ ] 我能解释中心极限定理在右偏业务数据上的意义。
- [ ] 我能区分标准差（个体离散）和标准误（均值波动）。
- [ ] 我知道非随机截断不能靠增大样本量自动修正。
- [ ] 练习本 5-2.1 ～ 5-2.4 四题全部通过检查。
:::

下一课：[相关性与因果](lesson:5-3)。
