"""
生成本教程用到的全部模拟数据。

用法（在教程根目录运行）：
    python data/generate_data.py

说明：
- 固定随机种子，任何人、任何时候运行，生成的数据都一模一样，方便对照答案。
- 数据完全虚构（店铺、商品、书名、作者都是编的），只用于学习。
- CSV 统一保存为 UTF-8 带 BOM（utf-8-sig），这样用 Excel 双击打开也不会乱码，pandas 读取也没问题。
- orders_gbk.csv 故意保存成 GBK 编码，用来练习“编码报错”。
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

SEED = 2025
DATA = Path(__file__).resolve().parent
SHOP = DATA / "shop"
ENC = "utf-8-sig"


# ============================================================ 1. 图书数据 books.csv
def make_books(rng: np.random.Generator) -> pd.DataFrame:
    head = ["雨夜", "南方", "旧城", "海边", "山中", "远方", "午后", "北国", "长河", "晚风", "月光", "故园",
            "林间", "春日", "灯下", "纸上", "江湖", "孤岛", "人间", "星河", "白鹭", "雪原", "梧桐", "烟火"]
    tail = ["的图书馆", "来信", "往事", "笔记", "漫游记", "简史", "十二讲", "的孩子", "之歌", "札记",
            "的秘密", "手册", "思考录", "小史", "的一年", "日记", "旅人", "密码", "通识课", "与我"]
    surnames = list("王李张刘陈杨黄赵周吴徐孙马朱胡郭林何高罗郑梁谢宋唐")
    given = ["一鸣", "晓", "子涵", "雨桐", "思远", "若溪", "明", "清和", "安", "知夏", "砚", "望舒",
             "嘉言", "书瑶", "牧之", "可", "静", "以宁", "南乔", "听澜"]
    foreign = ["A. 霍尔", "M. 杜邦", "K. 山田", "L. 罗西", "J. 卡特", "E. 诺瓦克", "S. 林德", "H. 穆勒",
               "R. 加西亚", "T. 佐藤", "N. 伊万诺娃", "P. 莫罗"]
    foreign_country = {"A. 霍尔": "英国", "M. 杜邦": "法国", "K. 山田": "日本", "L. 罗西": "意大利",
                       "J. 卡特": "美国", "E. 诺瓦克": "波兰", "S. 林德": "瑞典", "H. 穆勒": "德国",
                       "R. 加西亚": "西班牙", "T. 佐藤": "日本", "N. 伊万诺娃": "俄罗斯", "P. 莫罗": "法国"}
    cats = ["小说", "历史", "哲学", "心理", "经济", "科普", "诗歌"]
    cat_p = [0.30, 0.16, 0.10, 0.12, 0.12, 0.13, 0.07]
    n = 200
    rows = []
    used = set()
    for i in range(n):
        while True:
            title = rng.choice(head) + rng.choice(tail)
            if title not in used:
                used.add(title)
                break
        cat = rng.choice(cats, p=cat_p)
        if rng.random() < 0.35:
            author = rng.choice(foreign)
            country = foreign_country[author]
        else:
            author = rng.choice(surnames) + rng.choice(given)
            country = "中国"
        year = int(rng.integers(1985, 2026))
        pages = int(np.clip(rng.normal({"诗歌": 160, "小说": 330, "历史": 420}.get(cat, 300), 80), 80, 900))
        price = round(pages * rng.uniform(0.12, 0.2) + rng.uniform(5, 20), 1)
        price = float(np.floor(price) + rng.choice([0, 0.5, 0.8, 0.9]))
        popularity = rng.lognormal(6.3, 1.7)
        rating_count = int(np.clip(popularity, 3, 400_000))
        base = {"哲学": 8.2, "历史": 8.0, "诗歌": 8.1}.get(cat, 7.6)
        rating = round(float(np.clip(rng.normal(base, 0.7), 4.5, 9.8)), 1)
        if rating_count < 50:
            rating = np.nan  # 评价人数太少，平台不显示评分
        rows.append([f"B{i + 1:03d}", title, author, country, cat, year, pages, price, rating, rating_count])
    return pd.DataFrame(rows, columns=["book_id", "title", "author", "country", "category", "year",
                                       "pages", "price", "rating", "rating_count"])


# ============================================================ 2. 文创店数据
PRODUCTS = [
    # 名称, 品类, 售价
    ("故宫红笔记本", "文具", 39), ("敦煌飞天书签套装", "文具", 29), ("宋词手账本", "文具", 45),
    ("复古黄铜钢笔", "文具", 69), ("中性笔六支装", "文具", 15), ("诗词胶带", "文具", 12),
    ("古籍风信纸", "文具", 18), ("毛笔练字套装", "文具", 59),
    ("唐诗三百首插图版", "书籍", 58), ("山海经绘本", "书籍", 88), ("诗经今注", "书籍", 42),
    ("人间词话", "书籍", 36), ("中国建筑图鉴", "书籍", 128), ("一本书读懂数据", "书籍", 49),
    ("“读万卷书”帆布包", "帆布包", 59), ("千里江山图帆布包", "帆布包", 79), ("猫咪图书馆托特包", "帆布包", 69),
    ("大容量通勤帆布包", "帆布包", 99),
    ("城市地标明信片", "明信片", 19), ("二十四节气明信片", "明信片", 25), ("名画明信片", "明信片", 22),
    ("手绘猫咪明信片", "明信片", 15),
    ("诗人头像徽章", "徽章", 18), ("“文科生”徽章", "徽章", 15), ("书店系列徽章", "徽章", 22), ("珐琅金属徽章", "徽章", 35),
    ("2026 诗词日历", "日历", 79), ("2026 节气台历", "日历", 59), ("2026 博物馆日历", "日历", 99),
    ("墨香香薰蜡烛", "香薰", 89), ("书页香薰", "香薰", 69), ("雨后青苔扩香", "香薰", 129), ("檀木线香礼盒", "香薰", 159),
]
CITIES = {
    "一线": ["北京", "上海", "广州", "深圳"],
    "新一线": ["杭州", "成都", "南京", "武汉", "西安", "重庆", "苏州", "长沙", "天津", "郑州"],
    "二线及以下": ["厦门", "青岛", "昆明", "合肥", "济南", "福州", "南宁", "哈尔滨", "兰州", "洛阳", "桂林", "绍兴"],
}


def make_products(rng):
    rows = []
    for i, (name, cat, price) in enumerate(PRODUCTS):
        cost = round(price * rng.uniform(0.32, 0.58), 1)
        if cat == "日历":
            launch = pd.Timestamp("2025-09-01") + pd.Timedelta(days=int(rng.integers(0, 30)))
        elif i % 9 == 4:
            launch = pd.Timestamp("2025-03-01") + pd.Timedelta(days=int(rng.integers(0, 150)))
        else:
            launch = pd.Timestamp("2023-06-01") + pd.Timedelta(days=int(rng.integers(0, 500)))
        rows.append([f"P{i + 1:03d}", name, cat, price, cost, launch.date().isoformat()])
    return pd.DataFrame(rows, columns=["product_id", "product_name", "category", "price", "cost", "launch_date"])


def make_customers(rng, n=3000):
    tiers = list(CITIES)
    tier_p = [0.34, 0.42, 0.24]
    channels = ["小红书", "抖音", "微信", "淘宝搜索", "朋友推荐"]
    ch_p = [0.35, 0.25, 0.15, 0.15, 0.10]
    start = pd.Timestamp("2023-06-01")
    end = pd.Timestamp("2025-12-20")
    span = (end - start).days
    # 越往后注册的人越多（店铺在成长）
    u = rng.random(n) ** 0.65
    reg = [start + pd.Timedelta(days=int(x * span)) for x in u]
    rows = []
    for i in range(n):
        tier = rng.choice(tiers, p=tier_p)
        city = rng.choice(CITIES[tier])
        age = int(np.clip(rng.normal(27, 6), 16, 60))
        gender = rng.choice(["女", "男"], p=[0.71, 0.29])
        rows.append([f"C{i + 1:05d}", gender, age, city, tier, reg[i].date().isoformat(),
                     rng.choice(channels, p=ch_p)])
    df = pd.DataFrame(rows, columns=["customer_id", "gender", "age", "city", "city_tier", "register_date", "channel"])
    return df.sort_values("register_date").reset_index(drop=True).assign(
        customer_id=lambda d: [f"C{i + 1:05d}" for i in range(len(d))])


def day_factor(day: pd.Timestamp) -> float:
    f = 1.0 + 0.45 * (day.day_of_year / 365)          # 全年稳步增长
    if day.weekday() >= 5:
        f *= 1.18
    md = (day.month, day.day)
    if pd.Timestamp("2025-01-25") <= day <= pd.Timestamp("2025-02-06"):
        f *= 0.45                                      # 春节物流停运
    if (6, 1) <= md <= (6, 18):
        f *= 1.5
    if md == (6, 18):
        f *= 2.6
    if (11, 1) <= md <= (11, 11):
        f *= 1.7
    if md == (11, 11):
        f *= 3.8
    if md in [(2, 14), (8, 29), (5, 20)]:
        f *= 1.6                                       # 情人节、七夕、520
    if (12, 20) <= md <= (12, 31):
        f *= 1.25
    return f


def category_boost(cat: str, day: pd.Timestamp) -> float:
    m, d = day.month, day.day
    if cat == "文具" and ((m == 9 and d <= 20) or (m == 2 and d >= 15) or (m == 3 and d <= 5)):
        return 2.0                                     # 开学季
    if cat == "日历":
        return {9: 0.6, 10: 1.5, 11: 3.0, 12: 4.0}.get(m, 0.0)
    if cat == "香薰" and (md_between(day, (2, 7), (2, 14)) or md_between(day, (8, 22), (8, 29))):
        return 2.5
    if cat == "香薰" and m in (11, 12, 1):
        return 1.4
    if cat == "帆布包" and m in (4, 5, 6):
        return 1.3
    return 1.0


def md_between(day, a, b):
    return a <= (day.month, day.day) <= b


def make_orders(rng, products, customers):
    days = pd.date_range("2025-01-01", "2025-12-31", freq="D")
    base = 30
    prod = products.copy()
    prod["launch"] = pd.to_datetime(prod["launch_date"])
    popularity = rng.lognormal(0, 0.55, len(prod))
    cust = customers.copy()
    cust["reg"] = pd.to_datetime(cust["register_date"])
    # 每个客户的“回头倾向”：少数忠实客户贡献大量订单（二八定律）
    loyalty = np.clip(rng.pareto(1.6, len(cust)), 0, 12) + 0.2
    hours = np.arange(24)
    hour_w = np.array([2, 1, .5, .3, .2, .2, .4, 1, 2, 3, 4, 4.5, 5, 4.5, 4, 4, 4.5, 5, 5.5, 6.5, 8, 9, 8, 5])
    hour_w = hour_w / hour_w.sum()
    platforms = ["淘宝", "微信小程序", "抖音小店"]
    rows = []
    for day in days:
        n = rng.poisson(base * day_factor(day))
        if n == 0:
            continue
        avail = prod[prod["launch"] <= day]
        w = popularity[avail.index] * np.array([category_boost(c, day) for c in avail["category"]])
        if w.sum() == 0:
            continue
        w = w / w.sum()
        eligible = np.flatnonzero(cust["reg"].values <= day.to_datetime64())
        if len(eligible) == 0:
            continue
        cw = loyalty[eligible]
        # 新注册的客户短期内更可能下单
        recency = (day.to_datetime64() - cust["reg"].values[eligible]) / np.timedelta64(1, "D")
        cw = cw * (1 + 2.5 * np.exp(-recency / 20))
        cw = cw / cw.sum()
        pick_p = rng.choice(avail.index, size=n, p=w)
        pick_c = rng.choice(eligible, size=n, p=cw)
        promo = (md_between(day, (6, 1), (6, 18)) or md_between(day, (11, 1), (11, 11)))
        for pi, ci in zip(pick_p, pick_c):
            p = prod.loc[pi]
            hour = rng.choice(hours, p=hour_w)
            ts = day + pd.Timedelta(hours=int(hour), minutes=int(rng.integers(0, 60)), seconds=int(rng.integers(0, 60)))
            qty = int(rng.choice([1, 1, 1, 1, 2, 2, 3, 4, 5], p=None))
            if p["category"] in ("明信片", "徽章") and rng.random() < 0.3:
                qty += int(rng.integers(1, 4))
            if promo:
                disc = rng.choice([0.0, 0.1, 0.2, 0.3], p=[0.25, 0.3, 0.3, 0.15])
            else:
                disc = rng.choice([0.0, 0.1], p=[0.85, 0.15])
            plat = rng.choice(platforms, p=[0.45, 0.30, 0.25])
            refund_p = {"淘宝": 0.06, "微信小程序": 0.04, "抖音小店": 0.12}[plat]
            status = "已退款" if rng.random() < refund_p else "已完成"
            if status == "已完成" and rng.random() < 0.58:
                rating = int(rng.choice([5, 4, 3, 2, 1], p=[0.58, 0.25, 0.09, 0.05, 0.03]))
            else:
                rating = np.nan
            pay = round(p["price"] * qty * (1 - disc), 2)
            rows.append([ts, cust.at[ci, "customer_id"], p["product_id"], qty, float(p["price"]),
                         float(disc), pay, plat, status, rating])
    df = pd.DataFrame(rows, columns=["order_time", "customer_id", "product_id", "quantity", "unit_price",
                                     "discount", "pay_amount", "platform", "status", "rating"])
    df = df.sort_values("order_time").reset_index(drop=True)
    df.insert(0, "order_id", [f"SG25{i + 1:06d}" for i in range(len(df))])
    df["order_time"] = df["order_time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df["rating"] = df["rating"].astype("Int64")
    return df


def make_targets(orders):
    o = orders[orders["status"] == "已完成"].copy()
    o["month"] = o["order_time"].str[:7]
    real = o.groupby("month")["pay_amount"].sum()
    rng = np.random.default_rng(SEED + 7)
    tgt = (real.mean() * np.linspace(0.85, 1.25, 12) * rng.uniform(0.95, 1.05, 12)).round(-3)
    tgt[10] = round(real.iloc[10] * 0.92, -3)   # 11 月目标定得偏保守
    tgt[1] = round(real.iloc[1] * 1.35, -3)     # 2 月目标没考虑春节，偏高
    return pd.DataFrame({"month": real.index, "target_gmv": tgt.astype(int)})


# ============================================================ 3. 脏数据
def make_dirty(rng, orders, products, customers):
    df = orders.sample(2000, random_state=SEED).sort_values("order_id").reset_index(drop=True)
    df = df.merge(products[["product_id", "product_name", "category"]], on="product_id", how="left")
    df = df.merge(customers[["customer_id", "city"]], on="customer_id", how="left")
    n = len(df)

    # 下单时间：三种格式混在一起
    t = pd.to_datetime(df["order_time"])
    fmt = rng.choice(3, size=n, p=[0.7, 0.2, 0.1])
    df["order_time"] = [
        x.strftime("%Y-%m-%d %H:%M:%S") if f == 0 else
        f"{x.year}/{x.month}/{x.day} {x.hour:02d}:{x.minute:02d}" if f == 1 else
        f"{x.year}年{x.month}月{x.day}日"
        for x, f in zip(t, fmt)
    ]
    # 实付金额：混入货币符号、单位，导致整列变成文本
    pay = df["pay_amount"].map(lambda v: f"{v:.2f}")
    k = rng.random(n)
    pay = np.where(k < 0.12, "￥" + pay, pay)
    pay = np.where((k >= 0.12) & (k < 0.18), pd.Series(pay).str.replace("￥", "", regex=False) + "元", pay)
    df["pay_amount"] = pay
    # 数量：缺失、负数、离谱的大数
    q = df["quantity"].astype("float")
    q[rng.choice(n, 35, replace=False)] = np.nan
    q[rng.choice(n, 6, replace=False)] = -1
    q[rng.choice(n, 3, replace=False)] = 999
    df["quantity"] = q
    # 品类缺失
    c = df["category"].copy()
    c[rng.choice(n, 50, replace=False)] = np.nan
    df["category"] = c
    # 城市写法不统一
    city = df["city"].copy()
    idx = rng.choice(n, 160, replace=False)
    for i in idx:
        v = city[i]
        city[i] = rng.choice([v + "市", " " + v, v + " ", v + "市 "])
    df["city"] = city
    # 平台写法不统一
    plat = df["platform"].copy()
    alias = {"淘宝": ["taobao", "淘宝 ", "TB"], "微信小程序": ["微信", "小程序"], "抖音小店": ["抖音", "douyin"]}
    for i in rng.choice(n, 120, replace=False):
        plat[i] = rng.choice(alias[plat[i]])
    df["platform"] = plat
    # 订单状态写法不统一
    st = df["status"].copy()
    for i in rng.choice(n, 80, replace=False):
        st[i] = {"已完成": "完成", "已退款": "退款"}[st[i]]
    df["status"] = st
    # 评分越界
    r = df["rating"].astype("float")
    r[rng.choice(np.flatnonzero(r.notna()), 5, replace=False)] = 6
    r[rng.choice(np.flatnonzero(r.notna()), 4, replace=False)] = 0
    df["rating"] = r
    # 整行重复（系统重复导出）
    dup = df.sample(60, random_state=SEED + 1)
    df = pd.concat([df, dup]).sort_values("order_id", kind="stable").reset_index(drop=True)

    cols = {"order_id": "订单编号", "order_time": "下单时间", "customer_id": "客户ID", "product_name": "商品名称",
            "category": "品类", "quantity": "数量", "pay_amount": "实付金额", "platform": "平台",
            "city": "城市", "status": "订单状态", "rating": "评分"}
    return df[list(cols)].rename(columns=cols)


# ============================================================ 主程序
def main():
    rng = np.random.default_rng(SEED)
    if not SHOP.exists():
        SHOP.mkdir()

    books = make_books(rng)
    books.to_csv(DATA / "books.csv", index=False, encoding=ENC)

    products = make_products(rng)
    customers = make_customers(rng)
    orders = make_orders(rng, products, customers)
    targets = make_targets(orders)
    dirty = make_dirty(rng, orders, products, customers)

    products.to_csv(SHOP / "products.csv", index=False, encoding=ENC)
    customers.to_csv(SHOP / "customers.csv", index=False, encoding=ENC)
    orders.to_csv(SHOP / "orders.csv", index=False, encoding=ENC)
    targets.to_csv(SHOP / "monthly_targets.csv", index=False, encoding=ENC)
    dirty.to_csv(SHOP / "orders_dirty.csv", index=False, encoding=ENC)
    dirty.head(300).to_csv(SHOP / "orders_gbk.csv", index=False, encoding="gbk")

    with pd.ExcelWriter(SHOP / "shop_2025.xlsx") as xw:
        orders.head(3000).to_excel(xw, sheet_name="订单", index=False)
        products.to_excel(xw, sheet_name="商品", index=False)
        customers.to_excel(xw, sheet_name="客户", index=False)

    print("已生成：")
    for name, df in [("books.csv", books), ("shop/products.csv", products), ("shop/customers.csv", customers),
                     ("shop/orders.csv", orders), ("shop/monthly_targets.csv", targets),
                     ("shop/orders_dirty.csv", dirty), ("shop/orders_gbk.csv", dirty.head(300))]:
        print(f"  data/{name:<26} {len(df):>6} 行 × {df.shape[1]} 列")
    print("  data/shop/shop_2025.xlsx        3 个工作表：订单（前 3000 行）、商品、客户")


if __name__ == "__main__":
    main()
