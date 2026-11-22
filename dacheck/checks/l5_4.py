"""5-4 假设检验与 A/B 测试。"""
import pandas as pd
from scipy import stats

from dacheck.core import register, load, expect, expect_type, expect_close, expect_df


def _ab():
    return load("abtest/ab_experiment.csv")


@register("5-4.1", title="A/B 分组转化率汇总", hint="按 group 分组（as_index=False），计算 users（size）、conversions（converted 求和）、conv_rate（converted 均值），按 group 升序。")
def check_ab_summary(answer):
    ab = _ab()
    expected = (
        ab.groupby("group", as_index=False)
        .agg(
            users=("user_id", "size"),
            conversions=("converted", "sum"),
            conv_rate=("converted", "mean"),
        )
        .sort_values("group")
        .reset_index(drop=True)
    )
    expect_df(answer, expected, "A/B 分组转化率汇总")


@register("5-4.2", title="转化率差异卡方检验", hint="用 pd.crosstab(ab['group'], ab['converted']) 构造列联表，传入 stats.chi2_contingency(ct, correction=False)。")
def check_ab_chi2(answer):
    expect_type(answer, dict)
    ab = _ab()
    ct = pd.crosstab(ab["group"], ab["converted"])
    chi2, p, _, _ = stats.chi2_contingency(ct, correction=False)
    expected = {"chi2": float(chi2), "p_value": float(p)}
    expect(set(answer) == set(expected), "字典需要且只需要 chi2、p_value 两个键。")
    for k, v in expected.items():
        expect_close(answer[k], v, tol=1e-5, what=k)


@register("5-4.3", title="护栏指标页面加载耗时 Welch t 检验", hint="分别取出 control 和 treatment 的 page_load_ms，调用 stats.ttest_ind(t_ms, c_ms, equal_var=False) 或顺序相反均可（本检查核对 |t_stat| 与 p_value）。")
def check_ab_ttest(answer):
    expect_type(answer, dict)
    ab = _ab()
    c_ms = ab.loc[ab["group"].eq("control"), "page_load_ms"]
    t_ms = ab.loc[ab["group"].eq("treatment"), "page_load_ms"]
    t_stat, p = stats.ttest_ind(t_ms, c_ms, equal_var=False)
    expect(set(answer) == {"t_stat", "p_value"}, "字典需要且只需要 t_stat、p_value 两个键。")
    expect_close(abs(answer["t_stat"]), abs(float(t_stat)), tol=1e-4, what="|t_stat|")
    expect_close(answer["p_value"], float(p), tol=1e-5, what="p_value")


@register("5-4.4", title="新客转化率提升与卡方 p 值", hint="先筛 is_new_user == 1，计算 treatment 转化率减去 control 转化率作为 lift，再做 chi2_contingency(..., correction=False)。")
def check_ab_new_user(answer):
    expect_type(answer, dict)
    sub = _ab().loc[lambda d: d["is_new_user"].eq(1)]
    rates = sub.groupby("group")["converted"].mean()
    lift = float(rates["treatment"] - rates["control"])
    ct = pd.crosstab(sub["group"], sub["converted"])
    _, p, _, _ = stats.chi2_contingency(ct, correction=False)
    expected = {"lift": lift, "p_value": float(p)}
    expect(set(answer) == set(expected), "字典需要且只需要 lift、p_value 两个键。")
    for k, v in expected.items():
        expect_close(answer[k], v, tol=1e-5, what=k)
