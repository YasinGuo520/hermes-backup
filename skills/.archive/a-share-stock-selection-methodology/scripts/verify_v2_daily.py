#!/usr/bin/env python3
"""v2糅合选股「推荐当日」验证脚本。

读取量化日志 logs/*.json 的 top_k（默认8只），用新浪K线API拉历史日线，
按【推荐日收盘 vs 前一交易日收盘】计算当日涨跌幅 —— 这是 cron 任务里
「累计N天准确率」的口径（NOT T+1，T+1 口径用 backtest_quant_logs.py）。

用法：
    python3 verify_v2_daily.py [日志目录] [--top 8]

输出：每日命中数/平均涨幅 + 累计准确率/总平均涨幅。
"""
import json, os, sys, time, urllib.request

LOG_DIR = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") \
    else os.path.expanduser("~/Desktop/hermes/quant-skill/logs/")
TOP = 8
if "--top" in sys.argv:
    TOP = int(sys.argv[sys.argv.index("--top") + 1])


def get_kline(code):
    prefix = "sh" if code.startswith("6") else "sz"
    url = (f"https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/"
           f"CN_MarketData.getKLineData?symbol={prefix}{code}&scale=240&ma=no&datalen=60")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        raw = resp.read().decode("utf-8")
    return {d["day"]: float(d["close"]) for d in json.loads(raw)}


def prev_trading_day(closes, day):
    days = sorted(closes.keys())
    idx = days.index(day) if day in days else None
    return None if idx is None or idx == 0 else days[idx - 1]


files = sorted(f for f in os.listdir(LOG_DIR) if f.endswith(".json"))
cache, results = {}, {}
for f in files:
    with open(os.path.join(LOG_DIR, f)) as fh:
        log = json.load(fh)
    date = log["date"]
    for item in log.get("top_k", [])[:TOP]:
        code = item["code"]
        if code not in cache:
            try:
                cache[code] = get_kline(code)
                time.sleep(0.15)
            except Exception:
                cache[code] = None
        closes = cache.get(code)
        if not closes:
            continue
        prev = prev_trading_day(closes, date)
        cur = closes.get(date)
        if prev is None or cur is None:
            continue
        chg = (cur - closes[prev]) / closes[prev] * 100
        results.setdefault(date, []).append((code, chg))

total_hits = total_n = 0
all_chgs = []
for date in sorted(results):
    chgs = results[date]
    hits = sum(1 for _, c in chgs if c > 0)
    avg = sum(c for _, c in chgs) / len(chgs)
    total_hits += hits
    total_n += len(chgs)
    all_chgs.extend(c for _, c in chgs)
    print(f"{date}: {hits}/{len(chgs)} 涨 | 平均 {avg:+.2f}%")

if total_n:
    print(f"\n累计: {total_hits}/{total_n} 涨 | 累计准确率 {total_hits/total_n*100:.1f}% | 总平均涨幅 {sum(all_chgs)/len(all_chgs):+.2f}%")
