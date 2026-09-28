# 量化糅合系统健康度诊断与修复 (quant_ensemble.py)

来源：2026-08-04 会话。用户反馈"量化模型不太行"，实际诊断为三个因子坏了两个。

## 诊断触发
用户说"模型不太行 / 推荐不准"时，**先拉数据验证，不要直接重写**。三步走：

### 第1步：检查日志信号分布
路径 `~/Desktop/hermes/quant-skill/logs/*.json`（每天一个 JSON，top_k 含各因子分数）。

- **Kronos 全 1.0 或全 0.0 交替出现** = 信号饱和/失效，无区分度（权重 30% 变摆设）
- **flow 连续多天全是 0.00** = 资金流接口空响应（东方财富 push2 在腾讯云等服务器环境不稳定，技能早有警告）
- **同一批股票反复被推**（如 600406/600031 各 5 次）= 因子失效后只剩 MA 在选票，全是"均线多头蓝筹"

用脚本批量检查：`python3 -c` 读 logs 目录全部 JSON，统计每天 kronos 值集合、flow 范围、推荐股票出现次数。

### 第2步：拉实际行情验证命中率
用新浪 K 线 API（`money.finance.sina.com.cn/.../getKLineData?symbol=shXXXXXX&scale=240&ma=no&datalen=60`）拉推荐日之后 1/2/3 交易日涨跌：

- 命中率 ~50% = 抛硬币，模型失效
- 必须对比同期上证指数（symbol=sh000001），判断是否跑赢大盘（震荡市 50% 命中 + 0 收益 = 白搭）

### 第3步：定位根因
读 `quant_ensemble.py` 对应逻辑。本次根因链：Kronos strength 放大系数 10 过大 → 信号饱和全 ±1.0 → z-score 前无区分度 → 总分被拉平 → 只剩 tech 的 MA 因子在排序。

## 本次修复（2026-08-04，已上线）

1. **Kronos 饱和**：`strength = min(abs(pc/start_p-1)*10, 1.0)` 放大系数 **10→2.5**；并在 run() 里对 kronos_signal 做 z-score 归一化 `tanh(z*2)*0.5`（与 tech 同款），防止饱和拉平
2. **资金流降级**：run() 里计算 `flow_coverage = len(money_flow)/len(codes)`，覆盖率 <60% 时 flow 权重按线性衰减降权，空出权重按原比例（tech:kronos=0.45:0.30）分给 tech/kronos；日志记录实际使用的权重 + flow_coverage
3. **分歧度**：>0.3 标"观望"、>0.5 直接排除（原来只显示不排除）；日志 top_k 增加 `advice` 字段（推荐/观望）

改前必备份：`cp quant_ensemble.py quant_ensemble.py.bak_$(date +%Y%m%d_%H%M%S)`

## 回测验证方法（关键坑）

对比"**日志真实旧推荐**" vs "**修复后新推荐**"的实际 1/3 日表现：

- ⚠️ **不能用修复后的信号重算旧推荐**——那样"旧"也混入了新逻辑，对比失真。必须直接读日志里记录的原 top_k
- 修复后重跑当日脚本验证输出合理性（Kronos 应有区分度区间而非全同值）
- 样本小（25 条）时结果仅供参考，**不夸大提升幅度**——如实告诉用户"提升有但不大"

## 模型天花板（对用户诚实）

- 该模型本质是"均线多头蓝筹"选股器，选不出妖股，不是打板模型
- 50-60% 命中率、跑赢大盘 2-3 个点是正常水平，不承诺超额收益
- 修完跑一周真实数据再决定是否动因子权重

## 常用命令

```bash
# 手动跑
cd ~/Desktop/hermes/quant-skill && python3 quant_ensemble.py --top 10
# 回测行情源（新浪K线，无 Referer 要求）
curl -s "https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sh000001&scale=240&ma=no&datalen=30"
# cron：8:45 早报(ea324446676f) + 15:30 自进化(4b176d3f9c5e) + 8:50 看板同步(084374e236cc)
```
