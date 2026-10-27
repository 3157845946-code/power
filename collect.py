#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓取剩余电量，追加到 data/YYYY-MM-DD.json"""
import json, os, re, sys, time, urllib.request, datetime

URL = "http://www.wap.cnyiot.com/nat/pay.aspx?mid=18501681136"
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

def fetch_power():
    req = urllib.request.Request(URL, headers={
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 MicroMessenger/8.0.20"
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        html = r.read().decode("utf-8", errors="ignore")
    m = re.search(r"剩余电量:</span>\s*<label[^>]*>([0-9.]+)", html)
    if m:
        return float(m.group(1))
    return None

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")
    fpath = os.path.join(DATA_DIR, f"{date_str}.json")

    power = fetch_power()
    if power is None:
        print("未抓到剩余电量")
        sys.exit(1)

    # 读已有数据
    records = []
    if os.path.exists(fpath):
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                records = json.load(f)
        except: records = []

    # 同一分钟去重（覆盖该分钟旧值）
    records = [r for r in records if r["t"] != time_str]
    records.append({"t": time_str, "v": power})
    records.sort(key=lambda x: x["t"])

    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    # 更新日期索引
    index_path = os.path.join(DATA_DIR, "index.json")
    dates = []
    if os.path.exists(index_path):
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                dates = json.load(f)
        except: dates = []
    if date_str not in dates:
        dates.append(date_str)
        dates.sort()
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(dates, f, ensure_ascii=False, indent=2)

    print(f"[{now}] 记录: {power} kWh, 今日共 {len(records)} 条")

if __name__ == "__main__":
    main()
