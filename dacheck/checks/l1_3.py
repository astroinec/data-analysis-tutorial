from dacheck.core import register, expect_type, expect_equal, expect_close, expect, fail, load


@register("1-3.1", hint="用if/else；年份>=2020返回新书，否则较早出版。", title="按年份分类")
def check_label(answer):
    expect_type(answer, str, "分类标签")
    year = load("books.csv").iloc[2]["year"]
    expected = "新书" if year >= 2020 else "较早出版"
    expect_equal(answer, expected, "分类标签")


@register("1-3.2", hint="result先设0，每次循环增加本次price；初始化不放循环内。", title="循环累加价格")
def check_price_sum(answer):
    expect_close(answer, load("books.csv").head(3)["price"].sum(), what="前三本书价格合计")


@register("1-3.3", hint="空列表放循环前，满足price<=50才append该书title。", title="循环筛选书名")
def check_cheap_titles(answer):
    expect_type(answer, list, "筛选书名结果")
    first = load("books.csv").head(3)
    expect_equal(answer, first.loc[first["price"] <= 50, "title"].tolist(), "不超过50元的前三本候选书名")


@register("1-3.4", hint="定义三个参数，用return返回折后金额；result=函数名，不加调用括号。", title="可复用折后金额函数")
def check_function(answer):
    expect(callable(answer), "请提交函数本身：result = discounted_total，而不是某一次调用得到的金额。")
    for row in load("shop/orders.csv").head(40).to_dict("records"):
        try:
            actual = answer(float(row["unit_price"]), int(row["quantity"]), float(row["discount"]))
        except Exception:
            fail("函数调用失败，请确认接收unit_price、quantity、discount三个参数，且数字可以运算。")
        expect_close(actual, row["pay_amount"], what=f"订单{row['order_id']}的函数返回金额（注意return而不是print）")
