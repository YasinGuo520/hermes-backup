#!/usr/bin/env python3
"""
backtest_quant_logs.py — 量化推荐多日回测验证 + 因子健康度检查

读取 quant_ensemble.py 的日志目录（默认 ~/Desktop/hermes/quant-skill/logs/*.json），
用新浪财经K线API拉历史行情，计算每个推荐日之后 1/2/3 个交易日的实际涨跌，
输出命中率(>0%算赢)与平均收益，并拉上证指数(sh000001)对比判断是否跑赢大盘。
同时检查 Kronos / 资金流 因子是否失效（全1.0/全0.0/全0 = 因子退化）。

用法:
  python3 backtest_quant_logs.py                  # 默认日志目录, Top-5, 看3日
  python3 backtest_quant_logs.py --top 8          # 每期前8只
  python3 backtest_quant_logs.py --window 5       # 看推荐后5个交易日
  python3 backtest_quant_logs.py /path/to/logs    # 自定义日志目录

仅依赖标准库。数据源: 新浪财经K线API（纯JSON，无需Referer头）。

⚠️ 注意: 上证指数必须用 fetch_kline_by_symbol('sh000001') 拉取，
不能走代码映射 fetch_kline('000001')——那会映射到 sz000001 平安银行。
"""
import argparse, glob, json, os, statistics, sys, time, urllib.request

SINA_KLINE = ("https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/"
              "CN_MarketData.getKLineData?symbol={sym}&scale=240&ma=no&datalen={n}")


def fetch_kline_by_symbol(symbol, datalen=60, retries=2):
    url = SINA_KLINE.format(sym=symbol, n=datalen)
    for _ in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode('utf-8'))
            return {x['day'][:10]: float(x['close']) for x in data}
        except Exception:
            time.sleep(0.5)
    return None


def fetch_kline(code, datalen=60, cache=None):
    """按纯数字代码拉K线（6开头→sh，其他→sz），带进程内缓存。"""
    if cache is not None and code in cache:
        return cache[code]
    symbol = ('sh' if code.startswith('6') else 'sz') + code
    kline = fetch_kline_by_symbol(symbol, datalen)
    if cache is not None:
        cache[code] = kline
    time.sleep(0.15)
    return kline


def forward_returns(day_str, kline, window):
    """返回 (基准价, 后续window个交易日收盘价列表)。
    推荐日当天无K线（盘中推荐/未收盘）时，用其之前最近交易日作基准日。"""
    days = sorted(kline.keys())
    idx = -1
    for i, d in enumerate(days):
        if d > day_str:
            break
        idx = i
    if idx < 0:
        return None, []
    base = kline[days[idx]]
    fwd = [kline[days[i]] for i in range(idx + 1, min(idx + 1 + window, len(days)))]
    return base, fwd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('logs_dir', nargs='?',
                    default=os.path.expanduser('~/Desktop/hermes/quant-skill/logs'))
    ap.add_argument('--top', type=int, default=5)
    ap.add_argument('--window', type=int, default=3)
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(args.logs_dir, '*.json')))
    if not files:
        print(f"❌ 日志目录无JSON文件: {args.logs_dir}")
        sys.exit(1)

    recs = []          # {date, code, rank}
    factor_health = [] # {date, kronos_set, flow_min, flow_max}
    for f in files:
        try:
            d = json.load(open(f))
        except Exception as e:
            print(f"⚠️ 跳过 {f}: {e}")
            continue
        tk = d.get('top_k', [])
        for rank, x in enumerate(tk[:args.top], 1):
            recs.append({'date': d['date'], 'code': x['code'], 'rank': rank})
        ks = [x.get('kronos', 0) for x in tk]
        fs = [x.get('flow', 0) for x in tk]
        factor_health.append({
            'date': d['date'],
            'kronos_set': sorted(set(round(k, 2) for k in ks)),
            'flow_min': min(fs) if fs else 0.0,
            'flow_max': max(fs) if fs else 0.0,
        })

    # ── 拉K线 ──
    all_codes = sorted({r['code'] for r in recs})
    print(f"📅 {len(files)} 天日志 | {len(recs)} 条推荐 | {len(all_codes)} 只股票\n拉取K线...")
    cache = {}
    klines = {c: fetch_kline(c, 60, cache) for c in all_codes}
    ok = sum(1 for v in klines.values() if v)
    print(f"✅ K线有效 {ok}/{len(all_codes)}\n")

    # 上证指数（必须显式 sh000001，见文件头警告）
    sse = fetch_kline_by_symbol('sh000001', 60)
    sse_chg = {}
    if sse:
        sse_days = sorted(sse.keys())
        sse_chg = {d: (sse[d] - sse[sse_days[i - 1]]) / sse[sse_days[i - 1]] * 100
                   for i, d in enumerate(sse_days) if i > 0}

    # ── 回测 ──
    rows = []
    for r in recs:
        kline = klines.get(r['code'])
        if not kline:
            continue
        base, fwd = forward_returns(r['date'], kline, args.window)
        if base is None or not fwd:
            continue
        rets = [(x / base - 1) * 100 for x in fwd]
        rows.append({**r, 'rets': rets})

    print(f"{'推荐日':<12}{'代码':<8}{'排名':<5}"
          + "".join(f"{i+1}日后%".rjust(9) for i in range(args.window)))
    for r in sorted(rows, key=lambda x: (x['date'], x['rank'])):
        cells = "".join(f"{v:+.2f}".rjust(9) for v in r['rets'])
        print(f"{r['date']:<12}{r['code']:<8}{r['rank']:<5}{cells}")

    print()
    for i in range(args.window):
        vals = [r['rets'][i] for r in rows if i < len(r['rets'])]
        if not vals:
            continue
        hit = sum(1 for v in vals if v > 0)
        print(f"{i+1}日后  命中率 {hit}/{len(vals)} ({hit/len(vals)*100:.0f}%)  "
              f"平均 {statistics.mean(vals):+.2f}%")

    # ── 大盘对比 ──
    if sse_chg:
        print("\n同期上证指数:")
        for r in sorted(rows, key=lambda x: x['date']):
            if r['date'] in sse_chg:
                print(f"  {r['date']}: {sse_chg[r['date']]:+.2f}%")

    # ── 因子健康度 ──
    print("\n因子健康度（🚩 = 因子失效）:")
    for h in factor_health:
        kflag = "🚩 全1.0/全0.0 = Kronos饱和" if len(h['kronos_set']) <= 1 else ""
        fflag = "🚩 flow全0 = 东财接口空响应" if h['flow_max'] <= 0.01 else ""
        print(f"  {h['date']}: kronos取值{h['kronos_set']}  "
              f"flow[{h['flow_min']:.2f}~{h['flow_max']:.2f}] {kflag} {fflag}")

    print("\n判定参考: 命中率>65%且跑赢大盘=健康; ~50%=抛硬币; "
          "连续推同一批代码=只剩MA在排序")
    print("修复方向: Kronos放大系数10→2.5; flow全0时权重自动重分配; "
          "disagreement>0.3标观望/>0.5排除")


if __name__ == '__main__':
    main()
