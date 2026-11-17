"""
下载本教程用到的公开数据集，保存到 data/public/ 文件夹。

用法（在教程根目录运行）：
    python data/download_public_data.py

教程压缩包里已经附带了这些文件，正常情况下不需要运行本脚本。
只有当 data/public/ 里的文件丢了，或者你想重新下载时才需要。

如果网络连不上 GitHub，脚本会自动尝试国内镜像；都失败的话，
请按提示手动下载，放到 data/public/ 文件夹即可。
"""
from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

PUBLIC = Path(__file__).resolve().parent / "public"

# 文件名: (说明, [下载地址, 备用地址...])
DATASETS = {
    "tips.csv": ("餐厅小费数据：244 笔账单的金额、小费、性别、是否吸烟、星期、时段、人数", [
        "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/tips.csv",
        "https://cdn.jsdelivr.net/gh/mwaskom/seaborn-data@master/tips.csv",
    ]),
    "titanic.csv": ("泰坦尼克号乘客数据：891 名乘客的舱位、性别、年龄、票价、是否生还", [
        "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv",
        "https://cdn.jsdelivr.net/gh/mwaskom/seaborn-data@master/titanic.csv",
    ]),
    "penguins.csv": ("帕尔默企鹅数据：344 只企鹅的种类、岛屿、嘴长、嘴厚、鳍长、体重", [
        "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv",
        "https://cdn.jsdelivr.net/gh/mwaskom/seaborn-data@master/penguins.csv",
    ]),
}


def download(url: str, dest: Path) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = r.read()
        if len(data) < 500:
            return False
        dest.write_bytes(data)
        return True
    except Exception as e:  # noqa: BLE001
        print(f"    失败：{type(e).__name__} {e}")
        return False


def save_gapminder() -> bool:
    """gapminder 数据随 plotly 一起安装，不需要联网。"""
    try:
        import plotly.express as px
    except ImportError:
        print("    没有安装 plotly，跳过。可以运行 pip install plotly 后再试。")
        return False
    df = px.data.gapminder()
    df.to_csv(PUBLIC / "gapminder.csv", index=False, encoding="utf-8-sig")
    return True


def main() -> int:
    if not PUBLIC.exists():
        PUBLIC.mkdir(parents=True)
    failed = []
    for name, (desc, urls) in DATASETS.items():
        dest = PUBLIC / name
        print(f"[{name}] {desc}")
        if dest.exists() and "--force" not in sys.argv:
            print("    已存在，跳过（加 --force 参数可强制重新下载）")
            continue
        for url in urls:
            print(f"    下载：{url}")
            if download(url, dest):
                print("    完成")
                break
        else:
            failed.append((name, urls[0]))

    print("[gapminder.csv] 全球发展数据：142 个国家 1952-2007 年的人均 GDP、预期寿命、人口")
    if save_gapminder():
        print("    完成（来自 plotly 自带数据）")
    else:
        failed.append(("gapminder.csv", "pip install plotly 后重新运行本脚本"))

    if failed:
        print("\n以下文件没有下载成功，请手动下载后放进 data/public/ 文件夹：")
        for name, url in failed:
            print(f"  {name}: {url}")
        return 1
    print(f"\n全部完成，文件在：{PUBLIC}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
