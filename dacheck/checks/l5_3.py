"""5-3 相关性与因果。"""
import pandas as pd

from dacheck.core import register, load, expect, expect_type, expect_close, expect_df


@register("5-3.1", title="账单与小费的 Pearson 与 Spearman 相关", hint="对 tips['total_bill'].corr(tips['tip'], method='pearson' / 'spearman') 分别计算。")
def check_tips_corr(answer):
    expect_type(answer, dict)
    tips = load("public/tips.csv")
    expected = {
        "pearson": tips["total_bill"].corr(tips["tip"], method="pearson"),
        "spearman": tips["total_bill"].corr(tips["tip"], method="spearman"),
    }
    expect(set(answer) == set(expected), "字典需要且只需要 pearson、spearman 两个键。")
    for k, v in expected.items():
        expect_close(answer[k], v, what=k)


@register("5-3.2", title="数值列相关系数矩阵", hint="选取 tips[['total_bill', 'tip', 'size']] 后调用 .corr()。")
def check_tips_corr_matrix(answer):
    tips = load("public/tips.csv")
    expected = tips[["total_bill", "tip", "size"]].corr()
    expect_df(answer, expected, "相关系数矩阵", check_index=True)


@register("5-3.3", title="企鹅喙长与喙深的整体相关系数", hint="先去掉 bill_length_mm 和 bill_depth_mm 的缺失行，再计算两列 Pearson 相关系数。")
def check_penguin_overall_corr(answer):
    p = load("public/penguins.csv").dropna(subset=["bill_length_mm", "bill_depth_mm"])
    expected = p["bill_length_mm"].corr(p["bill_depth_mm"])
    expect_close(answer, expected, what="整体相关系数")


@register("5-3.4", title="分物种验证辛普森悖论", hint="去缺失后按 species 分组，计算每组 bill_length_mm 与 bill_depth_mm 的 Pearson 相关系数，输出 species、corr 两列并按 species 升序。")
def check_penguin_group_corr(answer):
    p = load("public/penguins.csv").dropna(subset=["bill_length_mm", "bill_depth_mm"])
    rows = []
    for sp, g in p.groupby("species"):
        rows.append({"species": sp, "corr": g["bill_length_mm"].corr(g["bill_depth_mm"])})
    expected = pd.DataFrame(rows).sort_values("species").reset_index(drop=True)
    expect_df(answer, expected, "分物种相关系数表")
