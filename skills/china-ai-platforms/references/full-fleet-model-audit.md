# 全生态模型锁死审计配方（full-fleet model audit）

**触发**：「所有调用模型锁死 flash」「昨天怎么跑的 pro」「导航页里用到模型的查过吗」。核心教训（2026-09-04 实测）：**锁死 ≠ 只改 Hermes config——导航 Hub 链出去的每个服务都可能自带模型配置，必须逐个翻。** 用户会在锁完 Hermes 后追问「导航页里面的查了吗」——主动把全生态扫完再汇报。排查"为什么扣 pro 钱"时，本配方定位**谁在把模型配成什么**；配套 key 轮换见 `references/deepseek-key-rotation.md`。

## Stage 1 — Hermes config 本体（只查 ~/.hermes/config.yaml）

主模型锁了不代表全锁：`delegation.model` 空、auxiliary 一堆段 `provider: auto` 都是漏跑 pro 的路径（auto 跟随主配置，主模型一改就跟着偏）。查漏脚本 + 钉死命令（delegation + 16 个 auxiliary 段逐个 4 键；vision 保留硅基 Qwen3-VL，DeepSeek 无视觉模型）见 china-ai-platforms SKILL.md「模型锁死清单」表。`provider: auto` 或空配置 = 静默漏跑 pro 路径，锁死必须显式钉不能靠继承。

## Stage 2 — 端口 → 代码目录定位（谁在跑、跑在哪）

```bash
ss -tlnp | grep ":$PORT " | grep -oE 'pid=[0-9]+'   # 拿 pid
readlink -f /proc/$PID/cwd                          # 同用户进程可读
docker ps --format '{{.Names}} {{.Ports}}'          # docker 服务（n8n/dify）
# http.server 进程 /proc/PID/cwd 常读不到（跨用户/权限）→ 用页面标题反查身份：
curl -s -m 3 http://127.0.0.1:$PORT/ | grep -oiE '<title>[^<]*' | head -1
```

标题反查实测：8897=`Hermes Agent - Dashboard`（跟主配置走，不用单独查）；8899/8910-8917/8931 全是纯静态展示页；8001=中年人生 API（uvicorn/supervisor）、8002=服小助。

## Stage 3 — 逐服务 grep 模型配置（位置表，2026-09-04 实测）

| 服务类型 | 配置位置 | 实测结论 |
|---|---|---|
| Hermes cron | `~/.hermes/cron/jobs.json` grep `"model":` | 全 flash |
| 16 公司 agents | `company-agents/common/llm.py` 的 `MODEL`；每个 `app.py` 应 `from common import ... llm`（先 `cd company-agents` 再循环 grep，cwd 错会全报 ❌） | 15/16 走公共层；pipeline(8930) 纯流程页无 LLM |
| 研究落地页 | `server.py` 里 `MODEL = "deepseek-v4-flash"` 硬编码行（red-blue/six-persona/market/industry 8920-8923） | 全 flash |
| 服小助 | `app/config.py` `DEEPSEEK_CHAT_MODEL` | flash；⚠️ embedding 调官方 `/v1/embeddings` 404 静默降级 |
| **中年人生** | `/var/www/midlife-test/backend/config.py` `DEEPSEEK_MODEL` | 🔴 曾写 `deepseek-chat`（V3）→ 改 flash + `sudo -n supervisorctl restart midlife-test` |
| 纯静态页 | grep HTML/JS 直连 `chat/completions\|api.deepseek\|api.siliconflow\|openrouter` | 8910-8917 无直连 |
| 工具箱 8900 | 纯导航卡片页 | 无模型 |

全盘兜底扫（排除 venv/node_modules），**误报过滤**：命中 tencentcloud SDK 的 models.py、dify plugin 的 `deepseek-v4-pro.yaml` 是**第三方模型目录清单不是调用配置**——路径含 `site-packages|plugin_daemon/cwd|venv/` 直接排除，别被带偏。

## Stage 4 — docker 内部（n8n / Dify）

**n8n**（单容器 sqlite volume）：`docker inspect n8n --format '{{range .Mounts}}...'` 拿 volume → python sqlite3 读 `workflow_entity`（nodes JSON 里搜 `openAi|deepseek|gpt-|model`）+ `credentials_entity`（type+name）。空 workflow 空 credential = 空壳不产生调用。

**Dify**：插件化供应商，模型在 **plugin 里**（`/app/storage/plugin/langgenius/<pkg>` 的 `models/llm/*.yaml` 是预定义模型清单——deepseek 插件自带 `deepseek-v4-flash.yaml` 与 `deepseek-v4-pro.yaml`，**别只查 provider_models 表，它只存用户自定义模型**）。PG 表：`providers`（provider_name/credential_id/is_valid）+ `provider_credentials`（encrypted_config）。UI 填过 key 且 is_valid=t 即配好；provider_models 空 = 正常（预定义模型不进这表）。

## 结论汇报模板

按「层 | 模型 | 状态」表格输出（主模型/delegation/auxiliary/cron/16agents/研究页/服小助/中年人生/静态页/n8n/Dify），唯一例外 vision 用硅基 Qwen3-VL 需说明原因（DeepSeek 无视觉模型）。
