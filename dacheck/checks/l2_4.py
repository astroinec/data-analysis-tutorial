from dacheck.core import register, expect_df, load


@register("2-4.1", hint="筛已完成后left merge商品键、名称、品类，validate='many_to_one'；右表别带多余列。", title="安全补商品资料")
def check_product_merge(answer):
    orders = load("shop/orders.csv")
    done = orders.loc[orders["status"] == "已完成"]
    lookup = load("shop/products.csv")[["product_id", "product_name", "category"]]
    expected = done.merge(lookup, on="product_id", how="left", validate="many_to_one")
    expect_df(answer, expected, "已完成订单与商品合并表")


@register("2-4.2", hint="独立先补商品，再按customer_id left补city/channel，两次均many_to_one。", title="再补客户资料")
def check_customer_merge(answer):
    orders = load("shop/orders.csv")
    done = orders.loc[orders["status"] == "已完成"]
    enriched = done.merge(load("shop/products.csv")[["product_id", "product_name", "category"]],
        on="product_id", how="left", validate="many_to_one")
    expected = enriched.merge(load("shop/customers.csv")[["customer_id", "city", "channel"]],
        on="customer_id", how="left", validate="many_to_one")
    expect_df(answer, expected, "补商品和客户资料的订单表")


@register("2-4.3", hint="商品表暂移除P006，left merge加indicator，筛_merge为left_only，只留题目三列。", title="检查未匹配商品")
def check_unmatched(answer):
    orders = load("shop/orders.csv")
    done = orders.loc[orders["status"] == "已完成"]
    products = load("shop/products.csv")
    partial = products.loc[products["product_id"] != "P006", ["product_id", "product_name", "category"]]
    audit = done.merge(partial, on="product_id", how="left", validate="many_to_one", indicator=True)
    expected = audit.loc[audit["_merge"] == "left_only", ["order_id", "product_id", "pay_amount"]]
    expect_df(answer, expected, "未匹配商品资料的已完成订单")


@register("2-4.4", hint="筛已完成、补category；pivot_table(category×platform, pay_amount, aggfunc='sum', fill_value=0)，保留索引。", title="品类平台金额透视")
def check_pivot(answer):
    orders = load("shop/orders.csv")
    done = orders.loc[orders["status"] == "已完成"]
    enriched = done.merge(load("shop/products.csv")[["product_id", "category"]],
        on="product_id", how="left", validate="many_to_one")
    expected = enriched.pivot_table(index="category", columns="platform", values="pay_amount", aggfunc="sum", fill_value=0)
    expect_df(answer, expected, "品类平台已完成金额透视", check_index=True)
