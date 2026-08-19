# 费用/扣费对账（Cost Billing Audit）

用户问「怎么扣了这么多钱」「token 很厉害」「余额怎么没了」时的完整排查手册。
原则：**先查证再解释**——先拿余额 + 日志数据，再给结论。用户常把「累计多天消耗」或「别的平台扣费」误当成「刚才聊几句烧的」。

## 1. 查余额（两个通道都查，fallback 也可能在烧）

```bash
# DeepSeek（主通道）——key 在 ~/.hermes/.env 的 DEEPSEEK_API_KEY
curl -s https://api.deepseek.com/user/balance -H "Authorization: Bearer $DEEPSEEK_API_KEY"
# → {"is_available": true, "balance_infos": [{"currency":"CNY","total_balance":"0.54","topped_up_balance":"0.54"}]}

# SiliconFlow（fallback 通道）
curl -s https://api.siliconflow.cn/v1/user/info -H "Authorization: Bearer $SILICONFLOW_API_KEY"
# → 看 balance / totalBalance 字段
```

注意：DeepSeek 无消费明细 API，只有余额。明细只能靠本地日志反推（第 2 步）。

## 2. 统计日志 token 消耗（核心证据）

agent.log 每行格式：
```
API call #1: model=deepseek-v4-flash provider=deepseek in=67117 out=1084 total=68201 latency=11.7s cache=20992/67117 (31%)
```

按会话/任务聚合 + 按官方价格估算：

```python
import re, collections
lines = open('/home/ubuntu/.hermes/logs/agent.log', encoding='utf-8', errors='ignore').readlines()
sessions = collections.defaultdict(lambda: {'in':0,'out':0,'cache':0,'calls':0})
for l in lines:
    m = re.search(r'\[([^\]]+)\] agent\.conversation_loop: API call #(\d+): model=\S+ provider=\S+ in=(\d+) out=(\d+) total=\d+ latency=[\d.]+s cache=(\d+)/', l)
    if not m: continue
    sid, inp, out, cache = m.group(1), int(m.group(3)), int(m.group(4)), int(m.group(5))
    sessions[sid]['in'] += inp; sessions[sid]['out'] += out; sessions[sid]['cache'] += cache; sessions[sid]['calls'] += 1
for s, v in sorted(sessions.items(), key=lambda x: -x[1]['in']):
    miss = v['in'] - v['cache']
    cost = miss*1.5/1e6 + v['cache']*0.05/1e6 + v['out']*4.5/1e6   # v4-flash 官方价（空闲时段）
    print(f"{s[:50]:52s} calls={v['calls']:3d} in={v['in']:>9,d} out={v['out']:>7,d} ~¥{cost:.2f}")
```

按天聚合可看消费高峰日（长会话通常在某天集中烧）。

## 3. deepseek-v4-flash 官方价格（2026-08-19 从 api-docs.deepseek.com/zh-cn/quick_start/pricing 直抓）

| 项目 | 空闲时段 | 高峰时段(北京9:00-12:00/14:00-18:00) |
|------|---------|----------------------------------|
| 输入（缓存命中） | ¥0.05/百万 | ¥0.10/百万 |
| 输入（缓存未命中） | ¥1.5/百万 | ¥3.0/百万 |
| 输出 | ¥4.5/百万 | ¥9.0/百万 |

- **高峰=空闲2倍**；高峰时段=北京时间 9-12 / 14-18，其余空闲
- ⚠️ **别用早期估算价（0.02/1/2 或 V3 的 0.5/2/8）**——会把费用低估或高估 50 倍。价格可能变动，对账前先抓官方页：
```bash
curl -sL -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125.0" "https://api-docs.deepseek.com/zh-cn/quick_start/pricing" | python3 -c "import sys,re,html; t=re.sub(r'<[^>]+>',' ',html.unescape(sys.stdin.read())); print(re.sub(r'\s+',' ',t)[:2000])"
```
- **费用大头判断**：未命中缓存 ¥1.5-3/M vs 命中 ¥0.05-0.1/M——**价差30倍**。账单高先看未命中量，不是看总量

## 4. 关键洞察（为什么「感觉没用多少token」却扣费）

- **Hermes 每次 API 调用带固定行李 5-6万 tokens/次**（system prompt + 工具定义 + 技能列表 + 记忆）。用户「感觉没聊多少」，但每次调用都在付这 5-6 万输入——这是「扣费严重但好像没用多少token」的核心解释
- 会话内缓存命中率通常 90-100%（命中 ¥0.05/M 极便宜）
- **cron 任务首次调用缓存命中率只有 19-26%**（新会话前缀不同→缓存失效→按未命中 ¥1.5-3/M 全价收）。cron 多 = 未命中量大头
- 单次 cron 任务：¥0.03-0.2；日常对话一轮：~¥0.2-1
- 一天全自动（5-6 个 cron + 聊天）：¥2-10（取决于 cron 数量、缓存命中率、是否踩高峰）
- **⚠️ 多服务共享同一个 DeepSeek key**：Hermes + 服小助(ai_cs_package/.env) + 红蓝/六分身落地页(server.py 硬编码) 全用 sk-ce1a8ba...。控制台总量 >> agent.log 统计时，差额来自其他服务或**用户 Mac 上的另一个 Hermes 实例**（多实例用户）。区分方法：agent.log 里 `[cron_xxx]` 前缀=cron、`[yyyyMMdd_...]`=交互会话；对不上账先问用户 Mac 端是否也配了 cron

## 4.5 会话经济学（2026-08-19 实测：老会话=缓存钱包）

- **老会话不花钱**（躺在磁盘上零成本），而且是**最便宜的会话**——同会话继续聊前缀稳定，缓存命中率90%+，单价便宜30倍
- **❌ 千万别建议「删老会话省钱」**——删了下次只能开新会话=全新前缀=又付一次未命中全价（¥3/M）
- **❌ 别建议「聊完就 /new」**——新会话=未命中全价起步。日常问答钉在同一个会话里最省
- **唯一该开新会话的时机**：上下文快满/即将触发压缩时（`compression.threshold: 0.5`）——压缩会重写历史→缓存全废→下轮全价，还多花一次 auxiliary 压缩调用费。会话明显变慢或 agent 提醒「上下文快满了」再开
- 开新会话后先聊几句无关的（预热缓存前缀），后续调用命中率更高
- **给用户的说法**：会话是你的缓存钱包，留着继续用=打折，删了=全价重来

## 4.6 ⚠️ 别信「thinking token 占大头」的结论（易错点）

- Mac 端 Hermes 曾给出「今天费用 87% 是 thinking」的分析——**用控制台数据直接证伪**：当日输出 token 总共才 0.26M，**就算全部是 thinking**，按最高输出价 ¥9/M 算也只有 ¥2.3，撑不起 87%
- 本地 usage.jsonl 的 `reasoningTokens` 字段统计口径与 DeepSeek 实际计费对不上，**不能作为账单依据**
- **费用大头判断铁律：先看「输入·未命中缓存」的量**（¥1.5-3/M vs 命中 ¥0.05-0.1/M，价差30倍）。当日 8.56M 未命中 ≈ ¥25.7（高峰价）≈ 账单的 80%。真凶是**未命中缓存的输入**，不是 thinking、不是 skills 列表、不是固定行李
- 未命中率高的原因：新会话多、上下文压缩触发（重写历史）、system prompt 不稳定（记忆/技能每次变动→前缀变）

## 5. 对账结论模板

用户说「扣了10块」时的标准核查路径：
1. 查余额 → 确认充值余额还剩多少
2. 日志统计 → 最近 N 天全部消耗合计
3. 对照：
   - 日志合计 ≈ 余额减少 → 「是累计消耗，不是一次扣的」
   - 日志合计 << 扣费额 → 「扣费来自别处」：**另一个 Hermes 实例（Mac）、服小助、落地页**、GPT 订阅、机场、苹果内购、硅基流动
4. 给省钱建议（**修正版**）：**日常钉在同一会话，别频繁 /new，绝不删老会话**；cron 挪到空闲时段（价格减半）；Mac 与服务器 cron 去重（双份 cron=双份输入token）；会话快满时才开新的

## 6. 本次实测案例（2026-08-19 账单排查）

- 用户发 DeepSeek 控制台截图：月累计 ¥126.45、当日 24.7M tokens（命中15.9M + 未命中8.56M + 输出0.26M）
- 服务器 agent.log 实测当日：104 calls、input 5.2M、cache 命中率 89% ≈ ¥2-3
- 差额 ~19M tokens ≈ ¥12-27 → **来自 Mac 上的 Hermes**（用户确认「主要的是Mac上的Hermes跑的」）——多实例用户对账必须算 Mac
- 单次调用 in=54727/62126 证实「固定行李5-6万」；cron 首调用 cache=19-26%（记忆瘦身 04:00 那次）
- 结论：当日总账单 ¥15-30 里服务器只占 ~10%；大头是 Mac 实例 + cron 未命中
- 省钱动作：Mac 端 cron 去重、cron 挪空闲时段、长会话 /new
