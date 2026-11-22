# 5-4 假设检验与 A/B 测试

请选择 `Python (da-course)` 内核，从 `notebooks/` 打开。本课使用虚构的“商品详情页新版评价卡片” A/B 测试数据 `data/abtest/ab_experiment.csv`（12000 名用户），练习卡方检验与 Welch t 检验。

```python
import sys
sys.path.insert(0, "..")
from dacheck import check, hint, setup_chinese_font
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
```

读取实验数据并查看各字段。

```python
ab = pd.read_csv("../data/abtest/ab_experiment.csv", encoding="utf-8-sig")
print(ab.shape)
ab.head()
```

+++
## 1. 先看分流与分组转化率

```python
summary = ab.groupby("group", as_index=False).agg(
    users=("user_id", "size"),
    conversions=("converted", "sum"),
    conv_rate=("converted", "mean"),
    avg_load_ms=("page_load_ms", "mean"),
)
summary
```

实验组转化率 10.06% 高于对照组 8.75%（高出 1.31 个百分点），但我们需要检验这是否可能只是随机波动。

+++
## 2. 比例类指标：卡方检验（转化率）

构造 2×2 列联表，调用 `stats.chi2_contingency(ct, correction=False)`（大样本下不使用 Yates 连续性校正，与双样本 z 检验一致）。

```python
ct = pd.crosstab(ab["group"], ab["converted"])
print(ct)
chi2, p_val, dof, _ = stats.chi2_contingency(ct, correction=False)
print(f"chi2 = {chi2:.4f}, p_value = {p_val:.5f}")
```

`p_value ≈ 0.0141 < 0.05`，在 5% 显著性水平下拒绝“两组转化率相同”的零假设。

+++
## 3. 均值类指标：Welch t 检验（护栏指标加载耗时）

新版评价卡片虽然提高了转化，但页面加载耗时是否变慢了？用不假设方差相等的 Welch t 检验 (`equal_var=False`)。

```python
c_ms = ab.loc[ab["group"].eq("control"), "page_load_ms"]
t_ms = ab.loc[ab["group"].eq("treatment"), "page_load_ms"]
t_stat, p_ms = stats.ttest_ind(t_ms, c_ms, equal_var=False)
print(f"对照组均值 {c_ms.mean():.1f}ms，实验组均值 {t_ms.mean():.1f}ms，差值 {t_ms.mean() - c_ms.mean():+.1f}ms")
print(f"t = {t_stat:.2f}, p_value = {p_ms:.3e}")
```

+++
## 练习 5-4.1 A/B 分组转化率汇总

按 `group` 分组（`as_index=False`），计算 `users`（人数）、`conversions`（转化人数）、`conv_rate`（转化率小数），按 `group` 升序排列。

```python
### BEGIN SOLUTION
ab_summary_ans = (
    ab.groupby("group", as_index=False)
    .agg(
        users=("user_id", "size"),
        conversions=("converted", "sum"),
        conv_rate=("converted", "mean"),
    )
    .sort_values("group")
    .reset_index(drop=True)
)
### STUDENT
ab_summary_ans = ...
### END SOLUTION
check("5-4.1", ab_summary_ans)
```

+++
## 练习 5-4.2 总体转化率卡方检验

对 `ab` 的 `group` 与 `converted` 构造列联表，调用 `stats.chi2_contingency(ct, correction=False)`，将 `chi2` 与 `p_value` 存入字典 `chi2_ans`。

```python
### BEGIN SOLUTION
ct_ex = pd.crosstab(ab["group"], ab["converted"])
chi2_val, p_val_ex, _, _ = stats.chi2_contingency(ct_ex, correction=False)
chi2_ans = {"chi2": float(chi2_val), "p_value": float(p_val_ex)}
### STUDENT
chi2_ans = ...
### END SOLUTION
check("5-4.2", chi2_ans)
```

+++
## 练习 5-4.3 护栏指标页面加载耗时 Welch t 检验

用 `stats.ttest_ind(..., equal_var=False)` 比较两组 `page_load_ms`，将 `t_stat` 与 `p_value` 存入字典 `ttest_ans`。

```python
### BEGIN SOLUTION
c_ms_ex = ab.loc[ab["group"].eq("control"), "page_load_ms"]
t_ms_ex = ab.loc[ab["group"].eq("treatment"), "page_load_ms"]
t_val, p_t = stats.ttest_ind(t_ms_ex, c_ms_ex, equal_var=False)
ttest_ans = {"t_stat": float(t_val), "p_value": float(p_t)}
### STUDENT
ttest_ans = ...
### END SOLUTION
check("5-4.3", ttest_ans)
```

+++
## 练习 5-4.4 新客群体转化率提升与显著性检验

仅筛选 `is_new_user == 1` 的新客，计算实验组减对照组的转化率绝对差值 `lift`，以及卡方检验（`correction=False`）的 `p_value`，存入字典 `new_user_ans`。

```python
### BEGIN SOLUTION
sub_new = ab.loc[ab["is_new_user"].eq(1)]
rates_new = sub_new.groupby("group")["converted"].mean()
_, p_new, _, _ = stats.chi2_contingency(pd.crosstab(sub_new["group"], sub_new["converted"]), correction=False)
new_user_ans = {
    "lift": float(rates_new["treatment"] - rates_new["control"]),
    "p_value": float(p_new),
}
### STUDENT
new_user_ans = ...
### END SOLUTION
check("5-4.4", new_user_ans)
```
