"""本模拟文件的类型、日期、别名与待核对数量。"""
import pandas as pd
from dacheck.core import register, expect, expect_df, expect_series, load


@register("3-2.1", hint="去首尾空白，按字面移除￥与元，再 pd.to_numeric(errors='coerce')。", title="金额数值解析")
def check_money(answer):
    expect(isinstance(answer, pd.Series), "请提交金额 Series，而不是合计数字。")
    expect(pd.api.types.is_numeric_dtype(answer.dtype), "金额必须转为数值类型，不能只把符号去掉。")
    raw = load("shop/orders_dirty.csv").drop_duplicates()["实付金额"]
    expected = pd.to_numeric(raw.astype("string").str.strip()
                             .str.replace("￥", "", regex=False)
                             .str.replace("元", "", regex=False), errors="coerce")
    expect_series(answer, expected, "金额列")


@register("3-2.2", hint="先把年月日与斜线统一，再 format='mixed' 解析；不能恢复缺失的时分秒。", title="混合日期解析")
def check_dates(answer):
    expect(isinstance(answer, pd.Series), "请提交日期 Series。")
    expect(pd.api.types.is_datetime64_any_dtype(answer.dtype), "结果必须为日期时间类型，不能只是统一后的文本。")
    text = load("shop/orders_dirty.csv").drop_duplicates()["下单时间"].astype("string").str.strip()
    text = (text.str.replace("年", "-", regex=False).str.replace("月", "-", regex=False)
            .str.replace("日", "", regex=False).str.replace("/", "-", regex=False))
    expect_series(answer, pd.to_datetime(text, format="mixed", errors="coerce"), "日期列")


@register("3-2.3", hint="只交三列；城市先 strip 再 removesuffix，平台与状态按已知别名 replace。", title="已知文本别名")
def check_labels(answer):
    expected = load("shop/orders_dirty.csv").drop_duplicates()[["城市", "平台", "订单状态"]].copy()
    expected["城市"] = expected["城市"].astype("string").str.strip().str.removesuffix("市")
    expected["平台"] = expected["平台"].str.strip().replace({
        "taobao": "淘宝", "TB": "淘宝", "微信": "微信小程序", "小程序": "微信小程序",
        "抖音": "抖音小店", "douyin": "抖音小店"})
    expected["订单状态"] = expected["订单状态"].str.strip().replace({"完成": "已完成", "退款": "已退款"})
    expect_df(answer, expected, "标签统一表")


@register("3-2.4", hint="数量缺失、非1～20、非整数用 | 合并，选 unique 原始行，不加入评分条件。", title="数量待核对原记录")
def check_quantity_review(answer):
    unique = load("shop/orders_dirty.csv").drop_duplicates()
    q = pd.to_numeric(unique["数量"], errors="coerce")
    expected = unique.loc[q.isna() | ~q.between(1, 20) | q.mod(1).ne(0)]
    expect_df(answer, expected, "数量待核对表")
