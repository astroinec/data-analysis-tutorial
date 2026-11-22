"""P-3 项目三：A/B 测试分析。"""
import pandas as pd
from scipy import stats

from dacheck.core import register, load, expect, expect_type, expect_close, expect_df


def _ab():
    return load("abtest/ab_experiment.csv")


@register("P-3.1", title="SRM 样本比例失衡检验", hint="统计 control_n、treatment_n，再用 stats.chisquare([control_n, treatment_n]) 得到 srm_chi2 和 srm_p。")
def check_p3_srm(answer):
    expect_type(answer, dict)
    ab = _ab()
    c_n = int((ab["group"] == "control").sum())
    t_n = int((ab["group"] == "treatment").sum())
    chi2, p = stats.chisquare([c_n, t_n])
    expected = {"control_n": c_n, "treatment_n": t_n, "srm_chi2": float(chi2), "srm_p": float(p)}
    expect(set(answer) == set(expected), "字典需要且只需要 control_n、treatment_n、srm_chi2、srm_p 四个键。")
    for k, v in expected.items():
        expect_close(answer[k], v, tol=1e-5, what=k)


@register("P-3.2", title="总体核心与护栏指标对比表", hint="按 group 分组（as_index=False），计算 users、click_rate、conv_rate、avg_load_ms、arpu（order_amount 均值），按 group 升序。")
def check_p3_overview(answer):
    ab = _ab()
    expected = (
        ab.groupby("group", as_index=False)
        .agg(
            users=("user_id", "size"),
            click_rate=("clicked", "mean"),
            conv_rate=("converted", "mean"),
            avg_load_ms=("page_load_ms", "mean"),
            arpu=("order_amount", "mean"),
        )
        .sort_values("group")
        .reset_index(drop=True)
    )
    expect_df(answer, expected, "总体指标对比表")


@register("P-3.3", title="主指标转化率显著性检验", hint="计算 control_rate、treatment_rate、lift = treatment_rate - control_rate，并用 chi2_contingency(ct, correction=False) 求 p_value。")
def check_p3_conv_test(answer):
    expect_type(answer, dict)
    ab = _ab()
    r = ab.groupby("group")["converted"].mean()
    _, p, _, _ = stats.chi2_contingency(pd.crosstab(ab["group"], ab["converted"]), correction=False)
    expected = {
        "control_rate": float(r["control"]),
        "treatment_rate": float(r["treatment"]),
        "lift": float(r["treatment"] - r["control"]),
        "p_value": float(p),
    }
    expect(set(answer) == set(expected), "字典需要且只需要 control_rate、treatment_rate、lift、p_value 四个键。")
    for k, v in expected.items():
        expect_close(answer[k], v, tol=1e-5, what=k)


@register("P-3.4", title="护栏指标页面加载耗时检验", hint="计算 control_ms、treatment_ms、diff_ms = treatment_ms - control_ms，并用 stats.ttest_ind(t_ms, c_ms, equal_var=False) 求 p_value。")
def check_p3_guardrail(answer):
    expect_type(answer, dict)
    ab = _ab()
    c_ms = ab.loc[ab["group"].eq("control"), "page_load_ms"]
    t_ms = ab.loc[ab["group"].eq("treatment"), "page_load_ms"]
    _, p = stats.ttest_ind(t_ms, c_ms, equal_var=False)
    expected = {
        "control_ms": float(c_ms.mean()),
        "treatment_ms": float(t_ms.mean()),
        "diff_ms": float(t_ms.mean() - c_ms.mean()),
        "p_value": float(p),
    }
    expect(set(answer) == set(expected), "字典需要且只需要 control_ms、treatment_ms、diff_ms、p_value 四个键。")
    for k, v in expected.items():
        expect_close(answer[k], v, tol=1e-5, what=k)


@register("P-3.5", title="新老客分层转化率与 p 值汇总", hint="按 is_new_user (0 和 1) 分别计算 control_rate、treatment_rate、lift 和卡方检验 p_value，按 is_new_user 升序。")
def check_p3_segment(answer):
    ab = _ab()
    rows = []
    for nu, sub in ab.groupby("is_new_user"):
        r = sub.groupby("group")["converted"].mean()
        _, p, _, _ = stats.chi2_contingency(pd.crosstab(sub["group"], sub["converted"]), correction=False)
        rows.append({
            "is_new_user": int(nu),
            "control_rate": float(r["control"]),
            "treatment_rate": float(r["treatment"]),
            "lift": float(r["treatment"] - r["control"]),
            "p_value": float(p),
        })
    expected = pd.DataFrame(rows).sort_values("is_new_user").reset_index(drop=True)
    expect_df(answer, expected, "新老客分层检验表", tol=1e-5)


@register("P-3.6", title="已转化用户客单价对比与 Welch t 检验", hint="先筛 converted == 1，再比较两组 order_amount 均值与 Welch t 检验 p_value。")
def check_p3_aov(answer):
    expect_type(answer, dict)
    conv = _ab().loc[lambda d: d["converted"].eq(1)]
    c_a = conv.loc[conv["group"].eq("control"), "order_amount"]
    t_a = conv.loc[conv["group"].eq("treatment"), "order_amount"]
    _, p = stats.ttest_ind(t_a, c_a, equal_var=False)
    expected = {
        "control_aov": float(c_a.mean()),
        "treatment_aov": float(t_a.mean()),
        "diff_aov": float(t_a.mean() - c_a.mean()),
        "p_value": float(p),
    }
    expect(set(answer) == set(expected), "字典需要且只需要 control_aov、treatment_aov、diff_aov、p_value 四个键。")
    for k, v in expected.items():
        expect_close(answer[k], v, tol=1e-5, what=k)
