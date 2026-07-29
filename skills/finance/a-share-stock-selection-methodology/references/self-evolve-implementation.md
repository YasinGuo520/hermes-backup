# 量化选股自进化引擎 — 实现参考

脚本位置：`~/Desktop/hermes/quant_self_evolve.py`
cronjob ID: `061d01b7b2cd`（工作日15:30推送至微信）

## 前置依赖

- `daily_stock_brief.py` 必须至少运行过一次（生成 `quant_recommend_log.json`）
- 推荐记录日志路径：`~/Desktop/hermes/quant_recommend_log.json`
- 因子权重文件路径：`~/Desktop/hermes/quant_weights.json`

## 架构

```
quant_self_evolve.py
├── 复盘核心 (review_recommendations)
│   ├── 读取日志中未复盘的记录（actual_chg is None）
│   ├── 调用新浪实时行情API获取今日收盘价
│   ├── 标记hit=True/False（涨=hit）
│   ├── 更新日志文件
│   └── 计算总体/分区/T+1准确率
├── 进化核心 (evolve_weights)
│   ├── 检查数据量（<10条不调权）
│   ├── 按评分区间对比准确率
│   ├── 按T+1分区对比准确率
│   ├── 根据准确率差异调整因子权重
│   └── 保存权重到 quant_weights.json
└── 报告输出
    ├── 今日复盘表（6只推荐股的涨跌）
    ├── 历史累计准确率
    ├── 评分区间准确率分析
    ├── T+1评分有效性分析
    └── 因子调整记录
```

## 推荐记录格式

```json
{
  "date": "2026-07-09",
  "code": "603019",
  "name": "中科曙光",
  "sector": "AI算力",
  "score": 53,
  "base": 39,
  "t1_score": 14,
  "price": 98.15,
  "rsi": 61.8,
  "vr": 1.39,
  "up_days": 1,
  "predict_chg": 1.56,
  "actual_chg": null,   // 收盘后填充
  "hit": null            // 收盘后填充
}
```

## 因子权重格式

```json
{
  "rsi_45_65": {"weight": 8, "desc": "RSI 45-65强势区间", "type": "base"},
  "macd_zero_up": {"weight": 10, "desc": "MACD零轴上强势", "type": "base"},
  "up3d": {"weight": 10, "desc": "连续3天上涨", "type": "t1"},
  "rsi_safe_40_60": {"weight": 10, "desc": "RSI 40-60安全区", "type": "t1"},
  "rsi_overbought": {"weight": -5, "desc": "RSI>70超买(扣分)", "type": "t1"},
  ...
}
```

共21个因子，`type: base` 是基础评分因子，`type: t1` 是T+1持续性评分因子。

## 使用方式

```bash
# 完整复盘+调权（15:30自动运行）
python3 ~/Desktop/hermes/quant_self_evolve.py

# 只看报告，不调权
python3 ~/Desktop/hermes/quant_self_evolve.py --report-only

# 重置因子权重为默认值
python3 ~/Desktop/hermes/quant_self_evolve.py --reset-weights
```

## 已知限制

- 最少需要10条已完成复盘的数据才触发调权（大约2个交易日）
- 调权规则当前偏保守（阈值设定较高），避免早期数据噪音导致过度拟合
- 不自动引入新因子或删除因子（只是调权重），需手动更新DEFAULT_WEIGHTS
- hit判定只是简单的"收盘涨了就算赢"，未区分涨幅大小
- 未考虑大盘系统风险（如果全市场跌，选股再准也跌）