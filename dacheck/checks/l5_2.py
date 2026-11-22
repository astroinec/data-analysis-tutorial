"""5-2 分布与抽样。"""
import numpy as np
import pandas as pd

from dacheck.core import register, load, expect, expect_type, expect_close


def _completed_pay():
    orders = load("shop/orders.csv")
    return orders.loc[orders["status"].eq("已完成"), "pay_amount"].copy()


@register("5-2.1", title="企鹅体重的均值、标准差与标准误", hint="去掉 body_mass_g 缺失后，标准误 se = std / np.sqrt(len(s))。")
def check_penguin_se(answer):
    expect_type(answer, dict)
    s = load("public/penguins.csv")["body_mass_g"].dropna()
    expected = {
        "mean": s.mean(),
        "std": s.std(),
        "se": s.std() / np.sqrt(len(s)),
    }
    expect(set(answer) == set(expected), "字典需要且只需要 mean、std、se 三个键。")
    for k, v in expected.items():
        expect_close(answer[k], v, what=k)


@register("5-2.2", title="抽样分布模拟（中心极限定理）", hint="用 np.random.default_rng(2026)，循环 500 次每次 rng.choice(values, size=50, replace=True).mean()，求 500 个均值的均值和样本标准差(ddof=1)。")
def check_clt_sim(answer):
    expect_type(answer, dict)
    values = _completed_pay().to_numpy()
    rng = np.random.default_rng(2026)
    means = np.array([rng.choice(values, size=50, replace=True).mean() for _ in range(500)])
    expected = {
        "mean_of_means": float(means.mean()),
        "std_of_means": float(means.std(ddof=1)),
    }
    expect(set(answer) == set(expected), "字典需要且只需要 mean_of_means、std_of_means 两个键。")
    for k, v in expected.items():
        expect_close(answer[k], v, tol=1e-4, what=k)


@register("5-2.3", title="已完成订单均价的 95% 置信区间", hint="se = std / sqrt(n)，ci_low = mean - 1.96 * se，ci_high = mean + 1.96 * se。")
def check_ci95(answer):
    expect_type(answer, dict)
    s = _completed_pay()
    mean = s.mean()
    se = s.std() / np.sqrt(len(s))
    expected = {
        "ci_low": mean - 1.96 * se,
        "ci_high": mean + 1.96 * se,
    }
    expect(set(answer) == set(expected), "字典需要且只需要 ci_low、ci_high 两个键。")
    for k, v in expected.items():
        expect_close(answer[k], v, tol=1e-4, what=k)


@register("5-2.4", title="截断样本与全集均价偏差", hint="分别计算全年已完成订单均价，以及 orders.iloc[:3000] 中已完成订单均价，取两者绝对差值 abs(...)。")
def check_truncation_bias(answer):
    orders = load("shop/orders.csv")
    full_mean = orders.loc[orders["status"].eq("已完成"), "pay_amount"].mean()
    head_done = orders.iloc[:3000]
    head_mean = head_done.loc[head_done["status"].eq("已完成"), "pay_amount"].mean()
    expect_close(answer, abs(full_mean - head_mean), tol=1e-4, what="均价绝对差值")
