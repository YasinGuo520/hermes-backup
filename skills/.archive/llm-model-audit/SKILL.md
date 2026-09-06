---
name: llm-model-audit
description: "模型跑错/扣费异常/全锁flash时，以出站日志为铁证审计所有LLM调用方。"
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [llm, audit, cost, deepseek, model-lock, docker, n8n, dify]
    related_skills: [china-ai-platforms, server-service-deployment, hermes-advanced-setup]
---

# LLM 调用审计与扣费排查

## When to Use

用户说「所有调用模型锁死 flash」「昨天怎么跑的 pro」「为什么最近扣 pro 的钱」「导航页/XX服务里用到模型的查过吗」「谁在调 X 模型」——任何需要确认/强制「每个 LLM 调用方用哪个模型哪个渠道」的任务；也适用怀疑 key 泄漏、切换模型供应商后验证无残留。

Yasin 环境（2026-09 实测）：铁律=全链路只允许 deepseek-v4-flash via DeepSeek 官方（禁 v4-pro/chat/reasoner），但**每次切换/锁死都必须重新审计全生态**——锁 Hermes config 不等于锁了导航 Hub 链出去的每个服务。

## 核心原则

1. **以实际出站调用为唯一铁证**，不凭配置印象下结论。Hermes 每次 LLM 调用都在 agent.log 留 `OpenAI client created ... provider=... base_url=... model=...` 行——这是「谁真的调了什么」的第一证据源。逐条统计 model 分布，零 pro 就是零 pro。
2. 用户要**先证据后结论**：报告里给表（端|时段|调用数|flash|pro），区分「有日志支撑的结论」与「推断」（如本机全 clean → 控制台却扣 pro → 明说推断=key 泄漏，给用户自查动作）。
3. 用户说「不用查昨天情况」= 只关心未来锁死：先钉死配置面，别翻历史。

## Stage 1 — Hermes config 本体

主模型锁了不代表全锁：`delegation.model` 空、auxiliary 一堆段 `provider: auto` 都是漏跑路径（auto 跟随主配置，主模型一改就跟着偏）。钉死命令 + 验证：

```bash
# 查漏：打印每段 model/provider
python3 -c "
import yaml
cfg = yaml.safe_load(open('/home/ubuntu/.hermes/config.yaml'))
for k,v in cfg.get('auxiliary',{}).items():
    if isinstance(v,dict): print(k, v.get('model'), v.get('provider'))
print('delegation:', cfg.get('delegation',{}).get('model'))
"
hermes config set delegation.model deepseek-v4-flash
hermes config set delegation.provider deepseek
hermes config set delegation.base_url https://api.deepseek.com/v1
hermes config set delegation.api_key '${DEEPSEEK_API_KEY}'
# auxiliary 全段 4 键逐个钉（skills_hub approval review mcp title_generation
# memory_query_rewrite tts_audio_tags triage_specifier kanban_decomposer
# profile_describer goal_judge curator monitor background_review
# moa_reference moa_aggregator）；vision 保留硅基 Qwen3-VL（DeepSeek 无视觉）
```

⚠️ bash 里 `UID` 是 readonly 变量，做 UUID 变量别用 UID 名。

## Stage 2 — 端口 → 代码目录定位

```bash
ss -tlnp | grep ":PORT " | grep -oE 'pid=[0-9]+'   # 拿 pid（非 root 看不了他用户进程）
readlink -f /proc/PID/cwd                          # 同用户进程可读
docker ps --format '{{.Names}} {{.Ports}}'         # docker 服务（n8n/dify）
# http.server /proc/PID/cwd 常读不到 → curl 页面标题反查身份：
curl -s -m 3 http://127.0.0.1:PORT/ | grep -oiE '<title>[^<]*' | head -1
```

## Stage 3+4 — 逐服务 grep + docker 平台

配置位置实测表见 `references/audit-locations-2026-09.md`；n8n/Dify 内部表结构与操作配方见 `references/docker-platform-internals.md`。

## Stage 5 — 实际出站调用证据（扣费排查必做）

```bash
# 服务器 Hermes 出站模型分布（按日志轮转文件逐个查 .log/.log.1/.log.2）
grep -hoE "model=deepseek-[a-z0-9-]+" ~/.hermes/logs/agent.log* | sort | uniq -c
# 时间线：某日起每次调用
awk '/^2026-09-0[56]/ && /OpenAI client created/ {print}' ~/.hermes/logs/agent.log \
  | grep -oE "model=[^ ]+" | sort | uniq -c
# cron request dump 的实际请求体（dump 顶层键 request.body.model 才是真值）
python3 -c "
import json; d=json.load(open('PATH/request_dump_cron_*.json'))
print(d['request']['body']['model'])"
# cron jobs.json 钉模型情况
python3 -c "
import json; jobs=json.load(open('/home/ubuntu/.hermes/cron/jobs.json'))
for j in jobs if isinstance(jobs,list) else jobs.get('jobs',[]):
    print(j.get('id','?')[:12], j.get('name','?'), j.get('model','未钉'), j.get('provider','未钉'))"
```

## Stage 6 — 噪音过滤（防误报带偏）

- `agent.message_sanitization` 日志会把**记忆文本**整个打进 WARNING——内含「v4-pro」字样≠真调用。只看 `OpenAI client created ... model=` 行。
- 全盘 grep 模型名会命中第三方库：`tencentcloud/*/models.py`、`dify plugin cwd/langgenius/*/models/llm/deepseek-v4-pro.yaml`（插件模型目录清单不是调用配置）、`site-packages|venv|node_modules`——路径含这些直接排除。
- `request_dump_*.json` 含 pro 字样也可能是错误体/正文噪音，以 `body.model` 字段为准。

## Stage 7 — 扣费来源排查（本机全 clean 时）

DeepSeek 官方：**无 usage 明细 API**（user/usage 等端点全 404），只有 `GET /user/balance`（查余额）。控制台用量图是唯一明细源。

排查流向：服务器 agent.log → Mac（SSH `mac@100.80.117.5`）agent.log + config + cron → 全盘 grep key 使用点（服务器 `~/Desktop/hermes`、Mac `~/Desktop ~/Library/Application\ Support ~/.config`）→ 若全 clean → **key 泄漏嫌疑**：key 曾明文贴聊天/硬编码在 server.py → 建议重置 key + 全端换新（Hermes .env/config、服小助 ai_cs_package/.env、落地页 server.py、Dify/n8n、Mac .env）。

读图细节用 vision_analyze 精确读日期刻度和每日数值——控制台图常是 30 天窗（如 8/8-9/6），峰值日期≠昨天，别被总览误导。

## Pitfalls

- `company-agents` 循环 grep 前必须 `cd` 进目录，cwd 错会全报 ❌ 误判。
- ss 拿不到 pid 时换 `ps aux` + 按 cmdline 匹配；docker 容器进程在宿主机 ps 可见。
- Dify console API 登录需 RSA 加密密码（`Invalid encrypted data`）且无 RSA env → 别走 API 登录死磕，恢复原 hash 让用户 UI 操作（见 references/docker-platform-internals.md）。
- 改用户密码前先备份原 hash 到文件，配完立刻恢复并验证。
