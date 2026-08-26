# DeepSeek API 扣费排查与成本控制（2026-08 实测）

用户报「DeepSeek 扣费严重/没怎么用却扣很多/账单出现 pro 费用」时的完整排查链。

## 0. 第一铁律：先确认当前日期！

**会话可能跨多天**（本案例：对话开头显示 8/19，实际执行时已是 8/22 23:41）。查"今天/今晚"的日志前，先 `date "+%Y-%m-%d %H:%M:%S %A"` 确认服务器和 Mac 各自当前时间，否则查错日期全白干。

## 1. 官方定价（deepseek-v4-flash，2026-08 实测）

| 计费项 | 空闲时段 | 高峰时段(9-12/14-18，×2) |
|---|---|---|
| 输入·缓存命中 | ¥0.05/M | ¥0.10/M |
| 输入·缓存未命中 | ¥1.5/M | ¥3.0/M |
| 输出(含thinking) | ¥4.5/M | ¥9.0/M |

- v4-pro 是 flash 的 3 倍价；v4-flash-vision-exp 价格同 flash
- **2026-08-23 起周末全天按低谷价**（官方公告）
- 缓存命中/未命中差 **30 倍**——成本大头几乎总是「未命中缓存的输入」，不是输出、不是 skills 列表

## 2. 成本结构认知（纠正常见误判）

- 每次调用固定「行李」~2.8万 token（灵魂+记忆+工具schema+skills列表），但**90%+ 走缓存命中，实际很便宜**
- 烧钱大头排序：**未命中缓存输入 > 输出/thinking > 固定行李**（Mac 端曾误判 thinking 占 87%，用控制台数据反推发现输出总共才 0.26M，撑不起 87%——别信本地 usage.jsonl 的 reasoningTokens 字段口径）
- cron 任务第一次调用命中率仅 19-26%（前缀不同），同一 cron 第二天起 90%+ 命中
- 跨会话新开 = 新前缀 = 未命中全价；**老会话继续聊 = 缓存命中 = 最便宜**；删老会话不省钱反而逼你开新的
- 上下文压缩（compression.enabled）重写历史会废缓存 → 下轮全价，别让会话无限膨胀

## 3. 快速查账

```bash
# DeepSeek 余额 API（无需登录控制台）
curl -s https://api.deepseek.com/user/balance -H "Authorization: Bearer $DEEPSEEK_API_KEY"
# → {"balance_infos":[{"total_balance":"6.00",...}]}  # 注意：没有按模型明细，只有总额

# 服务器 agent.log 全天模型分布（防 bash 正则转义问题用 python）
python3 - <<'EOF'
import re
from collections import Counter
c = Counter()
with open('/home/ubuntu/.hermes/logs/agent.log') as f:
    for line in f:
        if '2026-08-22' not in line or 'API call' not in line: continue
        m = re.search(r' (\d{2}):\d{2}:\d{2}.*model=(\S+) provider=(\S+)', line)
        if m: c[f"{m.group(2)}/{m.group(3)}"] += 1
print(dict(c))
EOF
```

## 4. pro 扣费排查链（当控制台显示 v4-pro 费用但本机全 flash）

按顺序排查，每步都可能直接锁定：

1. **确认两台机器当天时段日志**：服务器 `agent.log`（`API call` 行带 model/provider）+ Mac `ssh mac@100.80.117.5` 查 `~/.hermes/logs/agent.log`、`gui.log`。**注意 Mac Hermes.app GUI 的调用写 gui.log 而非 agent.log**
2. **全盘搜 pro 引用**：`grep -rln "deepseek-v4-pro"` 排除 venv/node_modules（搜索可能超时，用 background + notify_on_complete）
3. **查旧日志**：pro 可能来自**更早的误切模型**（本案例 8/11 某会话被切到 pro 跑了 19 次、75.9万 token，8/12 才切回）——`grep "model=deepseek-v4-pro" agent.log.1`
4. **Mac 上其他程序**：`ps aux | grep hermes_cli`（serve 进程=GUI后端，写 gui.log）、`~/Library/Application Support/Hermes/Local Storage/leveldb`（strings 搜 model 值）、Hermes.app 二进制 `app.asar`（grep v4-pro）
5. **三方可疑**：key 多端共用（服务器+服小助+落地页+Mac）——服小助看连接数 `ss -tn | grep :8002`，落地页查 nginx access.log 的 /api/analyze
6. 全查完仍无 → 提示用户切控制台 **「API Key」视图**看是哪个 key 在扣（区分 key 泄露 vs 本机使用）

## 5. 锁死只准 v4-flash（用户指令，2026-08-22）

用户要求「以后所有任务只能调 deepseek-v4-flash，禁 pro」时：

- **config.yaml**：`model.default: deepseek-v4-flash` + fallback SiliconFlow `deepseek-ai/DeepSeek-V4-Flash`（config.yaml 被安全策略保护，只能 `hermes config set` 或 python yaml）
- **cron jobs.json**：确认所有 LLM job 的 model 字段；非 LLM job（no_agent）model=None 不影响
- **落地页 server.py（红蓝8920/六分身8921/市场8922/行业8923）**：⚠️ 默认 `os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")` 会悄悄用错模型 → 改成**硬编码** `MODEL = "deepseek-v4-flash"`（不读环境变量），改后**必须重启服务才生效**（keepalive 只查端口活着不重启代码，手动 kill 旧 PID 再起）
- **服小助**：`app/config.py` 的 `DEEPSEEK_CHAT_MODEL` 硬编码 v4-flash
- 锁死铁律写入 memory 备忘

## 6. 常见坑

- `hermes config set fallback_providers '[...]'` 数组存成字符串无效 → 必须 python yaml 写 list
- DeepSeek 真 key 在 `~/.hermes/.env`；`config.yaml` 里 `sk-gaw...` 是 SiliconFlow 的
- DeepSeek 官方 API 高峰(10-11点)503 → fallback SiliconFlow 同款模型
