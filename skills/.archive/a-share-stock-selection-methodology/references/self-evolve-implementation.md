# 糅合量化自进化引擎 v2 — 实现参考

脚本位置：`~/Desktop/hermes/quant-skill/quant_ensemble.py`
模式：`--evolve` （自进化模式）
Cronjob ID: `4b176d3f9c5e`（工作日15:30推送至飞书）
cronjob输出路径：`~/.hermes/cron/output/4b176d3f9c5e/`

## 与 v1 自进化的区别

| 维度 | v1 (quant_self_evolve.py) | v2 (quant_ensemble.py --evolve) |
|:----|:--------------------------|:--------------------------------|
| 数据源 | 新浪实时行情 (收盘价) | baostock 历史K线 (行情记录) |
| 验证方式 | 单日涨跌 (hit=True/False) | 从推荐日到现在的累计收益率 |
| 因子粒度 | 21个因子 (RSI区间/MACD方向/量比等) | 3个信号源 (tech/kronos/flow) |
| 权重更新 | 单个因子权重 (±0.5步长) | Softmax风格信号源权重重分配 |
| 日志格式 | JSON数组 (quant_recommend_log.json) | 每日JSON文件 (logs/YYYY-MM-DD.json) |
| 数据需求 | 最少10条已验证记录 | 每只股票推荐日至今需≥5条行情记录 |

## 架构

```
quant_ensemble.py --evolve --days 5
│
├── 读取历史日志
│   └── logs/ 目录下最近 N 天的 JSON 文件
│       └── 每条记录包含: code, total_score, tech_score, kronos_score, flow_score
│
├── 验证表现 (针对每条推荐)
│   ├── baostock 查从推荐日到今天的行情
│   │   └── bs.query_history_k_data_plus("sh.600XXX", "date,close", date, today, "d", "2")
│   ├── 要求 ≥5 条行情记录（否则跳过）
│   ├── 计算累计收益率: end_close / start_close - 1
│   └── 记录每条: {code, date, return, total_score, tech_score, kronos_score, flow_score}
│
├── 信号源区分度分析
│   ├── 中位数分割: 高分样本 vs 低分样本
│   ├── tech_delta = tech_high_return - tech_low_return
│   ├── kronos_delta = kronos_high_return - kronos_low_return
│   └── flow_delta = flow_high_return - flow_low_return
│
└── 权重调整
    ├── total_delta = |tech_delta| + |kronos_delta| + |flow_delta|
    ├── 约束: tech∈[0.15,0.60], kronos∈[0.10,0.50], flow∈[0.10,0.40]
    ├── 最终归一化使权重之和=1.0
    └── 保存到 weights.json
```

## 验证数据要求

```python
# 关键阈值 — 位于 evolve() 方法第 797 行
if len(rows) >= 5:
    # 才算有效验证数据
    performance.append({...})
```

- **≥5 条行情记录 = 至少 5 个交易日**（约1个自然周）
- 新系统运行不足5天时 **永远无法触发调权**
- **建议初始期（<10交易日）将阈值降到 ≥2**

## 日志文件格式

```json
{
  "date": "2026-07-29",
  "weights": {"tech": 0.45, "kronos": 0.30, "flow": 0.25},
  "top_k": [
    {
      "code": "600031",
      "total": 0.523,
      "tech": 0.495,
      "kronos": 1.0,
      "flow": 0.0,
      "flow_amount": 0.0,
      "disagreement": 0.37,
      "tech_components": {
        "rsi": 0.0, "macd": 0.012, "kdj": 0.0,
        "boll": 0.034, "ma": 0.08, "volume": 0.0,
        "obv": 0.0, "momentum": -0.024, "vol_regime": 0.0
      }
    }
  ],
  "n_scored": 71
}
```

日志存储路径：`~/Desktop/hermes/quant-skill/logs/YYYY-MM-DD.json`

## 已知坑

### baostock API 间歇性不可用
- 表现：`bs.login()` 超时 9+ 秒，返回"网络接收错误"10002007
- 影响：整个 evolve 流程失败，无法获取验证数据
- 修复：重试机制（建议 3 次，间隔 30 秒）；或切换到新浪 K线 API 作为备选

### 验证门槛过高
- 问题：`>=5` 行行情记录要求门槛太高
- 症状：系统运行第 1-4 天时日志文件已存在，但验证永远返回空
- 修复：初始期降到 `>=2`，等积累 ≥10 个交易日后再升回 `>=5`

### Kronos 信号饱和
- 表现：Kronos 对所有股票预测 +1.0，变成无区分度信号
- 影响：分歧度计算和权重调优被干扰
- 检测：检查日志中 `kronos_score` 是否持续接近 +1.0

### 资金流 API 持续不可用
- 表现：flow_score=0.0 持续数天，0.25 权重完全浪费
- 影响：权重分配不公平（空信号占着权重）
- 修复：自动检测 flow API 不可用状态，将 flow 权重暂时分配给 tech/kronos

## 手动触发

```bash
# 带详细日志运行
cd ~/Desktop/hermes/quant-skill
python3 quant_ensemble.py --evolve --days 5 --no-kronos  # 禁用Kronos加速

# 检查当前权重
cat weights.json

# 重置权重（删除weights.json即默认）
rm weights.json
```
