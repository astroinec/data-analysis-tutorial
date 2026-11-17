"""历史统计数据图形练习，检查有效范围及成对坐标。"""
import numpy as np
from dacheck.core import register, expect, expect_equal, expect_series, load


@register("4-2.1", hint="dropna 的 subset 仅需喙长、体重、物种，不因 sex 缺失而排除。", title="散点入图范围")
def check_plot_rows(answer):
    expected = load("public/penguins.csv").dropna(subset=["bill_length_mm", "body_mass_g", "species"])
    expect_equal(answer, len(expected), "有效入图数")


@register("4-2.2", hint="按 day 分组取 total_bill 的 median，再 reindex 四个营业日。", title="营业日账单中位数")
def check_median(answer):
    expected = load("public/tips.csv").groupby("day")["total_bill"].median().reindex(["Thur", "Fri", "Sat", "Sun"])
    expect_series(answer, expected, "账单中位数")


@register("4-2.3", hint="提交未设 hue 的 Axes，散点的 x/y 来自同一行，标签包含毫米与克。", title="企鹅散点成对测量")
def check_scatter(answer):
    from matplotlib.axes import Axes
    from matplotlib.collections import PathCollection
    expect(isinstance(answer, Axes), "请提交 matplotlib 的 Axes 绘图区。")
    collections = [c for c in answer.collections if isinstance(c, PathCollection)]
    expect_equal(len(collections), 1, "散点组数（本题不设hue）")
    expected = load("public/penguins.csv").dropna(subset=["bill_length_mm", "body_mass_g", "species"])
    actual_points = np.asarray(collections[0].get_offsets(), dtype=float)
    expected_points = expected[["bill_length_mm", "body_mass_g"]].to_numpy(dtype=float)
    expect_equal(actual_points.shape, expected_points.shape, "散点坐标形状")
    expect(np.allclose(actual_points, expected_points), "点坐标不对：x为喙长、y为体重，必须来自同一行并使用指定入图范围。")
    expect_equal(answer.get_title(), "企鹅测量关系", "标题")
    expect_equal(answer.get_xlabel(), "喙长（毫米）", "横轴标签")
    expect_equal(answer.get_ylabel(), "体重（克）", "纵轴标签")


@register("4-2.4", hint="观察性散点无法排除物种等影响，不是随机干预证据。", title="相关与因果边界")
def check_causal(answer):
    expect_equal(answer, "相关不等于因果", "结论提醒")
