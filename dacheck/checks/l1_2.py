from dacheck.core import register, expect_type, expect_equal, expect_close, expect, load


@register("1-2.1", hint="用方括号按原顺序放三段书名，不是一个长字符串。", title="书名列表")
def check_titles(answer):
    expect_type(answer, list, "书名清单")
    expect_equal(answer, load("books.csv").head(3)["title"].tolist(), "前三本书名")


@register("1-2.2", hint="first_titles[-1]从右边取最后一项，结果是字符串。", title="最后一本书")
def check_last(answer):
    expect_type(answer, str, "最后一本书名")
    expect_equal(answer, load("books.csv").iloc[2]["title"], "最后一本书名")


@register("1-2.3", hint="字典用花括号，键为title、price、category，价格不要加引号。", title="图书字段字典")
def check_book(answer):
    expect_type(answer, dict, "图书资料")
    expect(set(answer) == {"title", "price", "category"}, "请且仅保留title、price、category三个键。")
    row = load("books.csv").iloc[0]
    expect_type(answer["title"], str, "title")
    expect_type(answer["category"], str, "category")
    expect_equal(answer["title"], row["title"], "title")
    expect_equal(answer["category"], row["category"], "category")
    expect_close(answer["price"], row["price"], what="price")


@register("1-2.4", hint='first_book["price"]按键取价格，再乘2。', title="按字典键计算")
def check_book_amount(answer):
    expect_close(answer, load("books.csv").iloc[0]["price"] * 2, what="两本书金额")
