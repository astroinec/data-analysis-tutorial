from dacheck.core import register, expect_df, load


@register("2-3.1", hint="先copy图书全表，只新增two_book_price=price*2，不丢原始列。", title="新增两本书价")
def check_new_book_column(answer):
    expected = load("books.csv").copy()
    expected["two_book_price"] = expected["price"] * 2
    expect_df(answer, expected, "新增两本书价的图书表")


@register("2-3.2", hint="groupby(category, as_index=False)，agg里book_count用size，mean_price用mean，不round。", title="图书品类汇总")
def check_book_summary(answer):
    expected = load("books.csv").groupby("category", as_index=False).agg(
        book_count=("book_id", "size"), mean_price=("price", "mean"),
    )
    expect_df(answer, expected, "图书品类汇总", check_order=False)


@register("2-3.3", hint="先筛已完成并copy，只新增original_amount=unit_price*quantity；不要加别的练习列。", title="已完成订单原价列")
def check_order_column(answer):
    orders = load("shop/orders.csv")
    expected = orders.loc[orders["status"] == "已完成"].copy()
    expected["original_amount"] = expected["unit_price"] * expected["quantity"]
    expect_df(answer, expected, "已完成订单原价表")


@register("2-3.4", hint="先筛已完成再按platform分组；数量用order_id的size，实付sum，每单mean。不round后提交。", title="已完成平台汇总")
def check_platform_summary(answer):
    orders = load("shop/orders.csv")
    done = orders.loc[orders["status"] == "已完成"]
    expected = done.groupby("platform", as_index=False).agg(
        order_count=("order_id", "size"), completed_amount=("pay_amount", "sum"), mean_order=("pay_amount", "mean"),
    )
    expect_df(answer, expected, "已完成订单平台汇总", check_order=False)
