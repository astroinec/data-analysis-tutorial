"""
生成第二批课程（阶段 5–8 与项目 P-2、P-3）用到的模拟数据。

用法（在教程根目录运行）：
    python data/generate_phase2_data.py

说明：
- 使用独立随机种子（SEED = 2026），不修改原有 books.csv 与 data/shop/*.csv。
- 生成三类产物：
  1. data/shop/shop.db          ：由现有 data/shop/*.csv 导出的 SQLite 数据库（供阶段 6 SQL 课使用）
  2. data/app/*.csv             ：虚构“墨读 App”用户注册、漏斗事件与日活留存表（供 7-2、P-2 使用）
  3. data/abtest/ab_experiment.csv：虚构商品详情页新版评价卡片 A/B 测试数据（供 5-4、P-3 使用）
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 2026
DATA = Path(__file__).resolve().parent
SHOP = DATA / "shop"
APP_DIR = DATA / "app"
AB_DIR = DATA / "abtest"
ENC = "utf-8-sig"


def build_shop_sqlite() -> None:
    """将现有文创店 CSV 导入为 SQLite 数据库 data/shop/shop.db。"""
    db_path = SHOP / "shop.db"
    if db_path.exists():
        db_path.unlink()
    tables = {
        "orders": SHOP / "orders.csv",
        "products": SHOP / "products.csv",
        "customers": SHOP / "customers.csv",
        "monthly_targets": SHOP / "monthly_targets.csv",
    }
    with sqlite3.connect(db_path) as conn:
        for name, csv_path in tables.items():
            df = pd.read_csv(csv_path)
            df.to_sql(name, conn, index=False, if_exists="replace")
        conn.execute("CREATE INDEX idx_orders_customer ON orders(customer_id)")
        conn.execute("CREATE INDEX idx_orders_product ON orders(product_id)")
        conn.execute("CREATE INDEX idx_orders_time ON orders(order_time)")
        conn.commit()
    print(f"已生成 SQLite 数据库：{db_path}")


def build_app_data(rng: np.random.Generator) -> None:
    """生成虚构阅读/学习 App（墨读 App）的用户、漏斗事件与日活留存表。"""
    APP_DIR.mkdir(parents=True, exist_ok=True)
    n_users = 6000
    start = pd.Timestamp("2025-07-01")
    end = pd.Timestamp("2025-09-28")  # 13 周，方便按周做同期群
    span_days = (end - start).days + 1

    channels = ["自然搜索", "小红书", "信息流广告", "朋友推荐"]
    ch_p = [0.26, 0.30, 0.28, 0.16]
    devices = ["iOS", "Android"]
    dev_p = [0.46, 0.54]
    tiers = ["一线", "新一线", "二线及以下"]
    tier_p = [0.32, 0.40, 0.28]

    reg_offsets = rng.integers(0, span_days, size=n_users)
    reg_dates = [start + pd.Timedelta(days=int(d)) for d in reg_offsets]
    user_channels = rng.choice(channels, size=n_users, p=ch_p)
    user_devices = rng.choice(devices, size=n_users, p=dev_p)
    user_tiers = rng.choice(tiers, size=n_users, p=tier_p)

    users_df = pd.DataFrame({
        "user_id": [f"U{i + 1:05d}" for i in range(n_users)],
        "register_date": [d.date().isoformat() for d in reg_dates],
        "channel": user_channels,
        "device": user_devices,
        "city_tier": user_tiers,
    })

    # 渠道对转化和留存的差异（故意设计清晰的业务规律）
    ch_funnel_mult = {
        "自然搜索": (0.86, 0.58, 0.44, 0.62),
        "小红书": (0.84, 0.56, 0.40, 0.56),
        "信息流广告": (0.74, 0.38, 0.26, 0.48),  # 获客多但试看->点击付费转化明显偏低
        "朋友推荐": (0.90, 0.64, 0.48, 0.68),
    }
    ch_ret_base = {
        "自然搜索": 0.46,
        "小红书": 0.42,
        "信息流广告": 0.28,
        "朋友推荐": 0.54,
    }

    event_rows: list[tuple[str, str, str]] = []
    active_rows: list[tuple[str, str]] = []
    obs_end = pd.Timestamp("2025-10-31")

    for i in range(n_users):
        uid = users_df.iat[i, 0]
        rdate = reg_dates[i]
        ch = user_channels[i]
        dev = user_devices[i]
        p_view, p_trial, p_click, p_pay = ch_funnel_mult[ch]
        # 故意设计 Android 在 click_pay -> pay_success 略低（例如支付弹窗加载体验差异）
        if dev == "Android":
            p_pay *= 0.82

        t0 = rdate + pd.Timedelta(hours=int(rng.integers(8, 22)), minutes=int(rng.integers(0, 60)))
        event_rows.append((uid, t0.isoformat(sep=" "), "app_open"))
        if rng.random() < p_view:
            t1 = t0 + pd.Timedelta(minutes=int(rng.integers(1, 15)))
            event_rows.append((uid, t1.isoformat(sep=" "), "view_course"))
            if rng.random() < p_trial:
                t2 = t1 + pd.Timedelta(minutes=int(rng.integers(2, 40)))
                event_rows.append((uid, t2.isoformat(sep=" "), "start_trial"))
                if rng.random() < p_click:
                    t3 = t2 + pd.Timedelta(hours=int(rng.integers(1, 72)))
                    event_rows.append((uid, t3.isoformat(sep=" "), "click_pay"))
                    if rng.random() < p_pay:
                        t4 = t3 + pd.Timedelta(minutes=int(rng.integers(1, 20)))
                        event_rows.append((uid, t4.isoformat(sep=" "), "pay_success"))

        # 生成日活记录（第 0 天必然活跃，后续按幂律衰减）
        active_rows.append((uid, rdate.date().isoformat()))
        base = ch_ret_base[ch] * (1.05 if dev == "iOS" else 0.96)
        max_day = min(30, (obs_end - rdate).days)
        for day_n in range(1, max_day + 1):
            prob = base / ((day_n) ** 0.42)
            if rng.random() < prob:
                active_rows.append((uid, (rdate + pd.Timedelta(days=day_n)).date().isoformat()))

    events_df = pd.DataFrame(event_rows, columns=["user_id", "event_time", "event_name"])
    active_df = pd.DataFrame(active_rows, columns=["user_id", "active_date"])

    users_df.to_csv(APP_DIR / "app_users.csv", index=False, encoding=ENC)
    events_df.to_csv(APP_DIR / "app_events.csv", index=False, encoding=ENC)
    active_df.to_csv(APP_DIR / "app_active.csv", index=False, encoding=ENC)
    print(f"已生成 App 数据：users={len(users_df)}, events={len(events_df)}, active={len(active_df)}")


def build_ab_data(rng: np.random.Generator) -> None:
    """生成虚构商品详情页新版评价卡片 A/B 测试数据。"""
    AB_DIR.mkdir(parents=True, exist_ok=True)
    n_users = 12000
    start = pd.Timestamp("2025-10-01")
    days = 14

    groups = rng.choice(["control", "treatment"], size=n_users, p=[0.5, 0.5])
    devices = rng.choice(["iOS", "Android"], size=n_users, p=[0.48, 0.52])
    is_new = rng.choice([1, 0], size=n_users, p=[0.55, 0.45])
    exp_dates = [
        (start + pd.Timedelta(days=int(d))).date().isoformat()
        for d in rng.integers(0, days, size=n_users)
    ]

    clicked = np.zeros(n_users, dtype=int)
    converted = np.zeros(n_users, dtype=int)
    order_amount = np.zeros(n_users, dtype=float)
    page_load_ms = np.zeros(n_users, dtype=int)

    for i in range(n_users):
        is_t = groups[i] == "treatment"
        new_u = is_new[i] == 1
        dev = devices[i]

        # 点击率
        p_click = 0.24 if new_u else 0.30
        if is_t:
            p_click += 0.045 if new_u else 0.008

        # 转化率（新客显著受益于新版评价卡片，老客几乎无变化）
        if new_u:
            p_conv = 0.070 if not is_t else 0.094
        else:
            p_conv = 0.102 if not is_t else 0.104

        c = int(rng.random() < p_click)
        # 转化条件概率：必须先点击详情交互或直接下单，保持逻辑一致
        conv = int(rng.random() < p_conv)
        if conv == 1:
            c = 1
        clicked[i] = c
        converted[i] = conv

        if conv == 1:
            amt = float(np.round(np.clip(rng.lognormal(4.25, 0.42), 18, 420), 2))
            order_amount[i] = amt

        # 护栏指标：页面加载耗时（新版略慢约 45ms，Android 偏慢）
        base_ms = 420 if dev == "iOS" else 490
        if is_t:
            base_ms += 45
        page_load_ms[i] = int(np.clip(rng.normal(base_ms, 85), 180, 1600))

    df = pd.DataFrame({
        "user_id": [f"AB{i + 1:05d}" for i in range(n_users)],
        "group": groups,
        "device": devices,
        "is_new_user": is_new,
        "exposure_date": exp_dates,
        "clicked": clicked,
        "converted": converted,
        "order_amount": order_amount,
        "page_load_ms": page_load_ms,
    })
    df.to_csv(AB_DIR / "ab_experiment.csv", index=False, encoding=ENC)
    print(f"已生成 A/B 测试数据：{len(df)} 行")


def main() -> None:
    rng = np.random.default_rng(SEED)
    build_shop_sqlite()
    build_app_data(rng)
    build_ab_data(rng)


if __name__ == "__main__":
    main()
