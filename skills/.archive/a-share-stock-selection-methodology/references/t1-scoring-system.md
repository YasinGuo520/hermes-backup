# T+1趋势持续性评分系统 — 实现参考

> 2026-07-09 新增（v3模型）
> 关联脚本：`~/Desktop/hermes/daily_stock_brief.py`

## 问题背景

A股T+1交易规则下，买入后最早次日才能卖出。原模型只评估"明天会不会涨"，忽略了趋势持续性。导致：
- 追高涨停股 → 次日低开被套
- RSI>70的过热股 → 次日回调
- MACD单日金叉 → 一日游假突破

## 评分结构

```
综合评分 = 基础分(0~60) + T+1持续性分(-10~40)
满分100, 实际分布 -10~70
```

## T+1持续性分 代码实现

```python
def calc_t1_score(daily, price, rsi_v, macd_v, ma5_v, ma20_v):
    """
    daily: K线数组 [{close, volume}, ...]
    返回: (t1_score, t1_reasons)
    """
    t1 = 0
    reasons = []
    c = [k["close"] for k in daily]
    v = [k["volume"] for k in daily]

    # B1: 近3天趋势连续性 (0~10分)
    up_days = 0
    for i in range(min(3, len(daily)-1)):
        if daily[-1-i]["close"] >= daily[-2-i]["close"]:
            up_days += 1
        else:
            break
    if up_days == 3: t1 += 10; reasons.append("连续3天上涨")
    elif up_days == 2: t1 += 7; reasons.append("连续2天上涨")
    elif up_days == 1: t1 += 3
    else: t1 -= 2

    # B2: RSI安全区 (0~10分)
    if rsi_v and 40 <= rsi_v <= 60:
        t1 += 10; reasons.append(f"RSI{rsi_v:.0f}安全区")
    elif rsi_v and 30 <= rsi_v < 40:
        t1 += 7; reasons.append(f"RSI{rsi_v:.0f}超卖反弹区")
    elif rsi_v and 60 < rsi_v <= 70:
        t1 += 4; reasons.append(f"RSI{rsi_v:.0f}偏强需留意")
    elif rsi_v and rsi_v > 70:
        t1 -= 5; reasons.append(f"⚠️ RSI{rsi_v:.0f}超买！T+1风险大")
    elif rsi_v and rsi_v < 30:
        t1 += 5; reasons.append(f"RSI{rsi_v:.0f}极限超卖")

    # B3: MACD柱趋势持续性 (0~8分)
    hist_vals = []
    for i in range(min(5, len(daily))):
        m = macd_f(c[:len(c)-i])[-1] if i > 0 else macd_v
        if m and m["hist"] is not None:
            hist_vals.append(m["hist"])
    if len(hist_vals) >= 3:
        if hist_vals[0] > hist_vals[1] > hist_vals[2]:
            t1 += 8; reasons.append("MACD柱持续扩大")
        elif hist_vals[0] > hist_vals[1] > 0:
            t1 += 5; reasons.append("MACD柱企稳")
        elif hist_vals[0] < hist_vals[1] < hist_vals[2]:
            t1 -= 3; reasons.append("MACD柱持续萎缩")
        else:
            t1 += 2

    # B4: 距均线空间 (0~7分)
    if ma5_v and ma20_v:
        gap5 = (ma5_v - price) / price * 100
        gap20 = (ma20_v - price) / price * 100
        if gap5 > 3 and gap20 > 5:
            t1 += 7; reasons.append(f"距MA5还有{gap5:.0f}%空间")
        elif gap5 > 1:
            t1 += 4; reasons.append(f"距MA5还有{gap5:.0f}%空间")
        elif gap5 < -3:
            t1 -= 3

    # B5: 单日涨幅不过热 (0~5分)
    if len(daily) >= 2:
        last_chg = (c[-1] - c[-2]) / c[-2] * 100
        if 0 < last_chg < 5:
            t1 += 5; reasons.append(f"温和上涨{last_chg:.1f}%")
        elif -2 < last_chg <= 0:
            t1 += 3
        elif last_chg > 7:
            t1 -= 5; reasons.append(f"⚠️ 涨幅{last_chg:.1f}%过大")
        elif last_chg < -5:
            t1 -= 3

    return max(-10, min(40, t1)), reasons
```

## 实盘验证（2026-07-09测试结果）

| 股票 | 旧评分 | 新评分 | T+1结论 | 次日真实表现 |
|:----|:-----:|:-----:|:--------|:------------|
| 中科曙光 | 34 | 53/100 | ⚠️ 需观察 | +0.87% 横盘微涨 |
| 浪潮信息 | 27 | 38/100 | ⚠️ 涨停过热 | +10% 封死涨停 |
| 招商银行 | 未上榜 | 44/100 | ✅ 最安全 | -0.37% 平稳 |
| 有研硅 | 27 | — | 未入前3 | +17% 暴涨 |

## 局限性

- 无法预测大盘系统性风险（上证跌超1%时任何荐股都可能失效）
- T+1分高≠涨得多，只是"明天能安全离场"
- 极端行情（涨停/跌停）下所有技术指标失效
