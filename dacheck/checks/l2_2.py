import pandas as pd

from dacheck.core import register, expect_type, expect_series, expect_df, load


@register("2-2.1", hint='一层方括号books["price"]返回Series，不是双层方括号。', title="选取price列")
def check_prices(answer):
    expect_type(answer, pd.Series, "price结果")
    expect_series(answer, load("books.csv")["price"], "整表price列")


@register("2-2.2", hint="loc[0:2,列清单]按标签包含终点2，输出三行两列。", title="loc选行列")
def check_loc(answer):
    expect_df(answer, load("books.csv").loc[0:2, ["title", "price"]], "loc选出的前三行", check_columns_order=True)


@register("2-2.3", hint="两个条件分别加括号并用&，sort_values按price、book_id升序，别head截断。", title="小说预算书单")
def check_novels(answer):
    books = load("books.csv")
    mask = (books["category"] == "小说") & (books["price"] <= 50)
    expected = books.loc[mask, ["book_id", "title", "price"]].sort_values(["price", "book_id"], ascending=[True, True])
    expect_df(answer, expected, "小说预算书单")


@register("2-2.4", hint="price降序False，book_id升序True，然后head(5)，只保留要求的三列。", title="最高价五本")
def check_top(answer):
    expected = load("books.csv").sort_values(["price", "book_id"], ascending=[False, True])
    expected = expected[["book_id", "title", "price"]].head(5)
    expect_df(answer, expected, "最高价五本")
