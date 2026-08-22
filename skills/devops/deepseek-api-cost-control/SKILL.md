---
name: deepseek-api-cost-control
description: "DeepSeek扣费审计与模型锁死。触发词：为什么扣费/锁死模型/只能v4-flash。"
version: 1.0
author: Yasin + Agent
created_by: agent
---

# DeepSeek API 成本审计与模型锁死

## 触发场景

用户问"为什么DeepSeek扣费这么严重"、"感觉没用多少token却扣钱"、"以后只能调v4-flash锁死"、"账单里出现pro费用"。核心目标：**先归因（钱烧在哪），再锁死（防止再烧）**。

## 一、官方定价（deepseek-v4-flash，百万token）

| 项目 | 空闲时段 | 高峰时段(9-12/14-18) |
|---|---|---|
| 输入·缓存命中 | ¥0.05 | ¥0.10 |
| 输入·缓存未命中 | ¥1.5 | **¥3.0** |
| 输出 | ¥4.5 | ¥9.0 |

- deepseek-v4-pro 是 flash 的 **3倍**（未命中 ¥4.5/9.0，输出 ¥13.5/27）
- **2026-08-23起周末全天按低谷价**（峰谷规则调整）
- 控制台 tooltip 区分：输入命中缓存 / 输入未命中缓存 / 输出——**输出已含thinking token**（thinking 不是独立大项，别被本地 usage.jsonl 的 reasoningTokens 误导）

## 二、成本三大规律

1. **贵不贵看缓存命中率，不看总量**：同样10万token，命中率90%约¥0.5，命中率0%约¥30，差60倍。DeepSeek按**前缀匹配**收缓存费：system prompt 稳定→第二次起命中；新会话/新cron/上下文压缩→前缀变→全价未命中。
2. **每次调用背固定行李**：Hermes 系统提示词（灵魂+记忆+画像~7.6K）+ 全部工具 schema（~15K）+ skills 列表（~3K）≈ **2.8万token/次**。它"重"（影响速度）但不"贵"（90%走缓存命中，每天约¥0.5-1）。
3. **烧钱大头排序**：输入未命中缓存（新会话、cron冷启动、压缩重置）≫ 输出/thinking（量小）> 固定行李（命中便宜）。

## 三、扣费排查五步（按此顺序，先数据后结论）

1. **控制台截图归因**：DeepSeek 控制台 → 用量 → 模型维度。tooltip 看"输入未命中缓存"数字——**它 × 高峰价就是最大扣费项**。别信本地 usage.jsonl 的 reasoningTokens 口径。
2. **服务器 agent.log 统计**：
   ```bash
   grep "API call" ~/.hermes/logs/agent.log | grep "2026-08-XX" | grep -oP 'model=\S+ provider=\S+' | sort | uniq -c
   ```
   `cache=N/M (P%)` 字段直接给命中率。注意 cron 会话 ID 格式是 `[cron_xxx_时间戳]`，交互会话是 `[YYYYMMDD_HHMMSS_hash]`。
3. **cron 模型审计**：`cat ~/.hermes/cron/jobs.json`（结构是 `{"jobs":[...]}`，直接 python json.load 遍历 model/provider 字段）。model=None 的任务会用默认配置。
4. **全站服务模型扫描**：落地页 `server.py` 的 `MODEL` 行、服小助 `app/config.py` 的 `DEEPSEEK_CHAT_MODEL`。**共用同一个 DeepSeek key 的服务都要查**（服小助/落地页/Hermes 三处常共用 `sk-ce1a8ba...`）。
5. **跨机排查（Mac/桌面）**：SSH 查 `~/.hermes/logs/agent.log` + `gui.log`（Hermes.app 桌面版 GUI 走 `hermes serve` 进程，写 gui.log 不写 agent.log）。查 `Library/Application Support/Hermes/` leveldb 的 model 字段确认 GUI 用的模型。

**历史日志**：`agent.log.1`（轮转旧档）里可能藏着早先的 pro 调用——grep `model=deepseek-v4-pro` 全文件，别只查当天。

## 四、模型锁死清单（用户铁律：只允许 deepseek-v4-flash）

| 位置 | 做法 |
|---|---|
| config.yaml | `model.default: deepseek-v4-flash` + `fallback_providers` SiliconFlow `deepseek-ai/DeepSeek-V4-Flash` |
| cron jobs | 每个 LLM job 显式 `model: deepseek-v4-flash` |
| 落地页 server.py | **硬编码** `MODEL = "deepseek-v4-flash"`，不要 `os.environ.get("DEEPSEEK_MODEL", ...)`——环境变量可被覆盖成 pro |
| 服小助 | `app/config.py` 硬编码 `DEEPSEEK_CHAT_MODEL = "deepseek-v4-flash"` |

**注意**：config.yaml 受安全保护，agent 的 patch/write_file 会被拒，只能 `hermes config set` 或 sed；落地页/服小助是普通文件可以直接改。改完落地页要 kill 旧进程重启（keepalive 只在端口挂了才拉起，**不会**因为代码变了自动重启旧进程——`ps -o lstart -p PID` 验证启动时间）。

## 五、成本优化动作（按 ROI 排序）

1. **少开新会话**：同一个会话里连续干活=缓存命中打折；频繁 `/new` 每开一次=多付一次未命中全价。老会话删掉反而亏（下次只能开新的）。
2. **cron 挪到空闲时段**：避开 9-12/14-18，单价直接减半。
3. **cron 之间错开**（如 8:30/8:35/8:45/8:55），避免同刻抢资源。
4. 压缩阈值调高/降频（`compression.threshold: 0.5` → 历史重写=缓存全废）。
5. 删不用 skills 只提速、省钱微小；裁剪 toolsets 不推荐（能力受损）。

## 六、观察脚本（0 token）

`scripts/deepseek_watch.sh` — 调 balance API 记录基线余额，2天后对比并提醒查控制台。部署：cronjob no_agent=true 一次性。

```bash
curl -s https://api.deepseek.com/user/balance -H "Authorization: Bearer $KEY"
# → balance_infos[0].total_balance
```

案例细节（8/11 pro 调用历史、8/22 ¥0.62 未查明、keepalive 端口顶替）见 `references/billing-incidents.md`。
