"""缺失与重复：按随包数据动态核对。"""
from dacheck.core import register, expect_type, expect_equal, expect_close, expect_df, expect_series, load


@register("3-1.1", hint="shape[0] 数行；duplicated().sum() 数额外重复；先整行去重再统计数量缺失。", title="清洗前体检")
def check_audit(answer):
    expect_type(answer, dict)
    raw = load("shop/orders_dirty.csv")
    expected = {"原始行数": len(raw), "额外整行重复": int(raw.duplicated().sum()),
                "去重后数量缺失": int(raw.drop_duplicates()["数量"].isna().sum())}
    expect_equal(set(answer), set(expected), "字典键名")
    for key, value in expected.items():
        expect_equal(answer[key], value, key)


@register("3-1.2", hint="不指定 subset 的 drop_duplicates() 按整行比较，随后 copy()。不要 dropna。", title="整行去重副本")
def check_dedup(answer):
    expect_df(answer, load("shop/orders_dirty.csv").drop_duplicates(), "去重表")


@register("3-1.3", hint="用订单ID映射到商品主表的品类，只填缺失，无法恢复才填未知。", title="可靠来源补品类")
def check_category(answer):
    unique = load("shop/orders_dirty.csv").drop_duplicates()
    master = load("shop/orders.csv")[["order_id", "product_id"]].merge(
        load("shop/products.csv")[["product_id", "category"]],
        on="product_id", how="left", validate="many_to_one")
    lookup = master.set_index("order_id")["category"]
    expected = unique["品类"].fillna(unique["订单编号"].map(lookup)).fillna("未知")
    expect_series(answer, expected, "补回后的品类")


@register("3-1.4", hint="notna().sum() 数已有评分；mean() 跳过缺失。本题暂不处理越界，不能当最终满意度。", title="评分观察分母")
def check_rating(answer):
    expect_type(answer, dict)
    expect_equal(set(answer), {"已有评分数", "已有评分均值"}, "字典键名")
    ratings = load("shop/orders_dirty.csv").drop_duplicates()["评分"]
    expect_equal(answer["已有评分数"], int(ratings.notna().sum()), "已有评分数")
    expect_close(answer["已有评分均值"], ratings.mean(), what="已有评分均值")
