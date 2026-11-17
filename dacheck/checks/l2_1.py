from dacheck.core import register, expect_equal, expect_df, expect_type, load


@register("2-1.1", hint="shape[0]是行数；head只预览，不是全集。", title="图书总行数")
def check_rows(answer):
    expect_equal(answer, load("books.csv").shape[0], "图书总行数")


@register("2-1.2", hint='books[["title", "price"]].head(3)先选列，再看前三行。', title="前三本两列")
def check_preview(answer):
    expect_df(answer, load("books.csv")[["title", "price"]].head(3), "前三本书名与价格", check_columns_order=True)


@register("2-1.3", hint='read_excel中明确sheet_name="商品"，不是默认第一张订单表。', title="读取Excel商品表")
def check_excel(answer):
    expect_df(answer, load("shop/shop_2025.xlsx", sheet_name="商品"), "Excel商品主表")


@register("2-1.4", hint="从shop/orders.csv取shape；Excel订单只有前3000行，不能当全年。", title="年度订单规模")
def check_order_shape(answer):
    expect_type(answer, tuple, "行列规模")
    expect_equal(answer, load("shop/orders.csv").shape, "年度订单行列规模")
