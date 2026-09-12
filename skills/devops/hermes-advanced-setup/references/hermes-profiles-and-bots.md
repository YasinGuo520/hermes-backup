# Hermes 分身知识库：Profiles × Bot Mode × peers

> 来源：官方文档 `/user-guide/profiles`、`/user-guide/bot-mode`、`/user-guide/features/kanban`、
> `/user-guide/features/delegation`（2026-09-12 从 llms-full.txt 抓取整理）。
> 抓取方式见 SKILL.md「查 Hermes 文档的正确姿势」。

## 一、Profile

> A profile is a separate Hermes home directory. Each profile gets its own directory containing its own
> `config.yaml`, `.env`, `SOUL.md`, memories, sessions, skills, cron jobs, and state database.

- 建完**自动成为一条命令**：`hermes profile create coder` → 就有 `coder chat` / `coder setup` / `coder gateway start`
- 显式指定：`hermes -p coder chat`、`hermes --profile=coder doctor`、`hermes chat -p coder -q "hi"`
- sticky 默认：`hermes profile use coder`（像 `kubectl config use-context`）
- 其它子命令：`list / use / create / delete / describe / show / alias / rename / export / import / install / update / info`
  （`export/import/install` = 把整个 agent 打包分发给别人，配 `hermes profile info` 看版本清单）

### 克隆语义（容易误判）
| 参数 | 复制什么 | 不复制什么 |
|------|---------|-----------|
| `--clone` | 当前 profile 的 config.yaml + .env + SOUL.md + skills | 会话、记忆 |
| `--clone-from <p>` | 指定源 profile 的 config/skills/SOUL | 同上 |
| `--clone-all` | **全部**（config、key、人格、记忆、技能、插件） | 会话历史、state.db、backups/、checkpoints/**、cron**（会双跑） |

- OAuth（Claude Pro/Max、Codex、xAI）用**一次性 refresh token**：克隆不复制那些行，仍读根 `~/.hermes/auth.json`，
  任何 profile 刷新都会写回根 → 所有 profile 保持登录。要给某 profile 独立登录：`hermes -p <name> auth add <provider>`。
- Honcho 记忆开启时，克隆会自动为新 profile 建独立 AI peer（同一用户工作区）。

### 隔离边界（别混）
- **profile** = 自己的状态目录；**workspace** = 终端起始目录（`terminal.cwd`）；**sandbox** = 文件系统限制。
- **profile 不做沙箱**：local 后端下 agent 仍有你账号的文件系统权限。
- ⚠️ 两个进程同一个 profile = 记忆互写污染，必须一 profile 一进程。

## 二、Bot Mode

> Bot Mode turns your Hermes profiles into a roster of named **Bots**. Each Bot has its own role, model,
> memory, skills, and avatar; Bots run recurring routines, deliberate together in group chats, and message
> each other directly.

- **位置**：桌面 App 左栏 **Bots** 页签（Sessions 旁边），**默认开启、无需安装**；Routines 磁贴贴在会话旁
- **一个 Bot = 一个 profile**：`~/.hermes/profiles/<name>/`，一切操作 CLI 也可见（`hermes -p <bot> chat`、`hermes cron list`）
- **新建**：New Agent → Name / Title / Description（秒建，Bot 用第一条消息自我介结）；Advanced 里可
  clone 现有 profile / Fresh / Create empty、**model & provider pin**（不同 Bot 跑不同模型）、自定义 SOUL.md、
  逐项勾技能/工具集/MCP、共享 key 池
- **Create on**：注册了多个连接（Settings→Connections）时，可选 profile 建在哪台机；远程建的 clone 源只能是目标机的 `default`
- **Bot Chat** 是「永远会话」：`/new` 被改写成 `/compact`，保证关系不 fork；同一 profile 的普通会话仍有完整 `/new` 自由
- **组织**：分组（sections，自己建、拖动归档、藏在 profile 元数据里，跟桌面端走）；右键可 Hide（只影响显示）
- **头像**：blob 脸（由名字决定，可 Randomize / Lock）、几何脸（7型×10色，干活时抬头）、上传图、AI 生成、petdex 像素宠物
- **Routines** = cron，命名 `[bot:<name>] <routine>`，在 `hermes cron list` 与核心 Cron 页都看得到，运行结果落在该 Bot 会话里
- **群聊**：一房 2–6 Bot；你的消息触发**最多 3 轮**成员发言（@提到的必回，无人@则都可能回，每 Bot 自行决定回或 pass）；
  每成员有自己的 `Group: <name>` 持久会话；上限 10 条/次发送；同机房的房间由网关侧 durable driver 调度，
  **关掉桌面端也继续跑**；跨机房的房间每成员在自己机器上跑
- **Bot 互发**：`message_agent(target="researcher", message="…")`（fire-and-forget：先 ack，回复以后台完成通知回来）；
  人类侧用 `@名字` 触发（Bot 自己组织措辞，不是转发你的原话）；工具**只在 canonical Bot Chat 里存在**；
  由 `agent.bot_mode_protocol`（默认 on）把协议注入 Bot Chat
- **跨机**：`hermes peer add <name> --url <api server> --key <API_SERVER_KEY>`（key 存 `~/.hermes/.env` 的
  `HERMES_PEER_<NAME>_KEY`，名字/URL 存 config 的 `bot_peers`）；`hermes peer dm <peer>[/<profile>] < file`、
  `peer run --idempotency-key` + `peer status/stop`；注册后 Bot Chat 的协议自动带上 peer 名单
- ⚠️ **NAT 单向**：跨网关是 gateway→gateway 直连，桌面端只是观众；内网机可拨出到公网 VPS，反向无入站路由（除非 Tailscale/VPN）

## 三、多 profile 协作（Kanban）

- Kanban worker 就是完整 Hermes 进程，每 worker 一个会话；dispatcher 跑在 gateway 进程内，60s tick
- worker 至少每小时 heartbeat，否则被 reclaim；资源参考：单 worker 200–500MB RAM
- **编排器按 profile 的 `description` 路由任务** → 建分身的 `--description` 要写清「它擅长什么」
- 并发三层闸：`kanban.max_in_progress` / `max_in_progress_per_profile` / `max_spawn`
- 2核/3.6G 轻量机：已占 ~1.8G，建议同跑 2–3 个 worker

## 四、选型速查（回答用户「要不要做成分身」）

| 活的性质 | 归属 | 常驻成本 |
|---------|------|---------|
| 有明确算法/规则（违禁词、库存红黄橙、打分、差评识别） | 自建服务 / 纯规则 | 0 token |
| 要理解、要生成、要点按钮才跑（洞察、文案、回复建议） | 自建服务 + 手动触发 LLM | 每次 1–3 分钱 |
| 要长期记忆 + 要自己判断 + 要主动沟通（财务顾问、内容主编、总机） | **Profile / Bot** | 跑才烧，另有 context 成本 |

铁律：**代笔类分身放在便宜常开的机器上**（服务器），门脸/语音/需要本机权限的放本地机（Mac）。
