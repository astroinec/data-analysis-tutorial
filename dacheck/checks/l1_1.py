from dacheck.core import register, expect_type, expect_equal, expect_close, load


@register("1-1.1", hint="文字用成对英文引号；第一本书的title字段。", title="保存书名")
def check_title(answer):
    expect_type(answer, str, "书名")
    expect_equal(answer, load("books.csv").iloc[0]["title"], "第一本书名")


@register("1-1.2", hint="单价乘2；不要把数字写进引号或加上元。", title="两本书的金额")
def check_total(answer):
    expect_close(answer, load("books.csv").iloc[0]["price"] * 2, what="两本书金额")


@register("1-1.3", hint="至少2020年写 >= 2020，结果是True/False，不是文字。", title="年份判断")
def check_recent(answer):
    expect_type(answer, bool, "判断结果")
    expect_equal(answer, bool(load("books.csv").iloc[2]["year"] >= 2020), "出版年份判断")


@register("1-1.4", hint="discount是减免比例，用单价 * 数量 * (1 - discount)。", title="折后订单金额")
def check_discount(answer):
    orders = load("shop/orders.csv")
    row = orders.loc[orders["discount"] == 0.1].iloc[0]
    expect_close(answer, row["pay_amount"], what="折后订单金额")
