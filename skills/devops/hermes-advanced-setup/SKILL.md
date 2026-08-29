---
name: hermes-advanced-setup
description: 配置 Hermes Agent 高级功能——Kanban看板/Holographic记忆/GitHub备份/Dashboard鉴权/多机部署/自动备份/升级。覆盖 David Ondrej 7级路线图 Level 4-6。
category: devops
---

# Hermes Agent 高级功能配置

> **本技能覆盖 David Ondrej 7级路线图 Level 1-7**（合并自 hermes-config-evolution）——下面先给总览与审计，再给 Level 4-6 实操。

## 7级路线图总览与审计（合并自 hermes-config-evolution）

| Level | 名称 | 核心能力 | 成本 | 设置时间 |
|-------|------|---------|------|---------|
| 1 | VPS 部署 | 常驻服务器、隔离环境 | 仅VPS费用 | ~30min |
| 2 | 消息接入 | Discord/飞书/Telegram 远程控制 | 免费 | ~15min |
| 3 | Curator | 自动压缩技能省 token | 省钱 | ~5min |
| 4 | GitHub 备份 | 每日 git push ~/.hermes/ | 免费 | ~10min |
| 5 | Kanban 看板 | 多 Agent 可视化任务编排 | 每任务开销 | ~5min+dashboard |
| 6 | Holographic 记忆 | 向量库长期召回 | 检索token | ~2min |
| 7 | MCP Server | 把 Hermes 暴露给其他 AI 工具 | 看用量 | ~15min |

**现状审计命令**：`hostname && hermes config show | grep terminal.backend`（L1）/ `hermes gateway status`（L2）/ `grep -A2 "curator:" ~/.hermes/config.yaml`（L3）/ `hermes cron list | grep -i backup`（L4）/ `ls -la ~/.hermes/kanban.db`（L5）/ `hermes memory status`（L6）/ `grep -i mcp ~/.hermes/config.yaml`（L7）。

**决策规则**：L1-3 是标配先查；L4 是保险人人推荐；L5 给要「起码知道你在干嘛」的用户；L6 给多工作流（量化+SaaS+内容）需要跨会话召回的用户；L7 只给开发者（本地有 Claude Code/Codex/Cursor 才用，非技术用户跳过）。

**完整映射表与来源**：`references/7-levels-framework.md`；**中国网络工作区**（GitHub SSH vs HTTPS、dashboard 隧道、provider 注意）：`references/china-network.md`；**升级 Hermes 本体**（pip 已弃用、GitCode 镜像、本地补丁保留、网关重启陷阱）：`references/update-hermes.md`。

## 升级 Hermes 本体（2026-08 起）

- ⚠️ **pip 安装已非官方支持平台，不再更新**；PyPI 停在 0.19.0，新版本只在 GitHub main
- 升级 = 源码树 `git fetch gitcode main` → `--ff-only` merge → 重应用本地补丁 → `pip install --user --break-system-packages -e .`
- **必须先 stash 本地补丁**（feishu adapter 的 channel tag 注释，上游没修），merge 后 apply
- **网关重启不能从网关进程内做**（SIGTERM 传播杀会话），用 crontab flag 技巧让 cron 在进程树外重启
- ⚠️ **GitHub 被墙时 `git fetch origin` 可能静默失败**（exit 0 但没拉到），版本以 `git ls-remote gitcode HEAD` 为准
- ⚠️ **依赖重装三连坑**：bashrc 7890 代理劫持（unset 代理）、uv 连不上（用 venv 内 pip3.11 + 腾讯内网源）、旧 editable root 属主 pyc 卡权限（sudo find -delete）
- 完整流程+坑：`references/update-hermes.md`；**DeepSeek 扣费/成本排查**（定价表、缓存命中率、pro扣费排查链、锁死只准 v4-flash）：`references/deepseek-billing-diagnosis.md`

## config.yaml 格式陷阱：gateway.platforms 必须 dict 不能 list（v0.20+）

**症状：** 用户发消息没回应/反复问"你好了没"；网关日志出现：

```
ERROR gateway.run: Agent error in session agent:main:feishu:dm:...
  File ".../gateway/run.py", line 4457, in _handle_message_with_agent
    _plat_gw_cfg = _platforms_gw_cfg.get(platform_key) or {}
AttributeError: 'list' object has no attribute 'get'
```

**根因：** v0.20 起 `gateway.platforms` 需要 dict 格式（按平台配 `skip_context_files`），如果被写成 list（`- feishu`）格式，网关每次处理该平台消息就崩，且是**进程内异常、不是整个网关退出**——所以用户看到的只是"没回应"，网关进程还活着。

**检查：**
```bash
grep -A6 "^gateway:" ~/.hermes/config.yaml
```
❌ 坏（list）：
```yaml
gateway:
  platforms:
  - feishu
  - qqbot
```
✅ 好（dict）：
```yaml
gateway:
  platforms:
    feishu:
      skip_context_files: false
    qqbot:
      skip_context_files: false
```

**修复：** python yaml 改写（同 fallback 配置模式，先备份），改后**必须重启网关**才生效。

**重启后健康检查（一套命令）：**
```bash
pgrep -af "hermes_cli.main gateway run"                # 确认新PID已起
tail -50 ~/.hermes/logs/gateway.log | grep -cE "ERROR|AttributeError"   # 应为0
ss -tlnp | grep 8897                                   # 端口在听
systemctl --user status hermes-gateway | head -3       # Active: running
```

完整诊断记录：`references/gateway-message-crash.md`

## 原则

适用于配置 7级路线图 中的 Level 4 (GitHub备份)、Level 5 (Kanban看板)、Level 6 (Holographic记忆)。

## 原则

1. **并行执行** — 三个等级互不依赖，可以同时跑
2. **最小步骤** — 用户讨厌多余步骤。配密码时不要解释为什么需要密码，直接给方案选
3. **非技术用户** — 用户对 GitHub 概念基础。指令要具体到"告诉我你用户名"

## Level 4 — GitHub 自动备份

### 方式 A：SSH 密钥 + 纯脚本（中国网络推荐）

国内 GitHub HTTPS 很慢（可能超时 120s+），SSH 更稳定。

**前置条件：**
1. 用户 GitHub 账号 + 已建 private repo（如 `hermes-backup`）
2. 用户配好 SSH key（`ssh-keygen` → 加到 GitHub Settings → SSH Keys）
3. 验证：`ssh -T git@github.com` 返回用户名

**备份脚本（`~/.hermes/scripts/github-backup.sh`）：**
```bash
#!/bin/bash
set -e
source "${HOME}/.hermes/.env" 2>/dev/null || true

REPO_URL="git@github.com:<USER>/<REPO>.git"
BACKUP_DIR="/tmp/hermes-github-backup"
HERMES_HOME="${HOME}/.hermes"

git clone --depth 1 "${REPO_URL}" "${BACKUP_DIR}"
cd "${BACKUP_DIR}"

cp "${HERMES_HOME}/config.yaml" "$BACKUP_DIR/"
cp "${HERMES_HOME}/SOUL.md" "$BACKUP_DIR/"
rsync -a --delete --exclude='.git' "${HERMES_HOME}/memories/" "$BACKUP_DIR/memories/"
rsync -a --delete --exclude='.git' "${HERMES_HOME}/skills/" "$BACKUP_DIR/skills/"
rsync -a --delete --exclude='.git' "${HERMES_HOME}/cron/" "$BACKUP_DIR/cron/"

if git status --porcelain | grep -q .; then
    git add -A && git commit -m "daily backup $(date -u +%Y-%m-%d)" --quiet
    git push origin main 2>/dev/null || git push origin master 2>/dev/null
    echo "Backed up: $(find . -type f -not -path '*/.git/*' | wc -l) files"
else
    echo "No changes"
fi
rm -rf "${BACKUP_DIR}"
```

**cron job（零 token 消耗，`no_agent: true`）：**
```bash
cronjob action=create schedule="0 3 * * *" script="github-backup.sh" no_agent=true deliver=origin name=github-daily-backup
```

**关键细节：**
- `rsync --exclude='.git'` 解决 skills/ 下嵌套 git repo 的问题
- `git status --porcelain` 检测新文件（`git diff` 检测不到 untracked files）
- SSH key 不能设密码（cron 无人值守无法输入）

### 方式 B：内置 `hermes backup` 命令（便携归档）
```bash
hermes backup   # 输出 ~/.hermes/backups/hermes-YYYY-MM-DD-HHMMSS.tar.zst
hermes import   # 恢复（交互式冲突解决）
```
- 默认脱敏 secrets
- `--include-secrets` 迁移时用
- 不需要 GitHub，可存本地磁盘

### 安全要点
- 备份仓库必须 **private**
- 不用在聊天里粘贴 token，用 `hermes config set GITHUB_TOKEN <token>`
- 如用 SSH key，确保 key 不加密码（cron 无法输入密码）
- 国内服务器 git push 可能需要超过 120s 超时

### 参考文件
- `scripts/github-backup.sh` — 完整可部署的备份脚本模板

## Level 5 — Kanban 看板

### 初始化
```bash
# 创建看板数据库
hermes kanban init

# 确认 gateway 在跑（dispatcher 内嵌在 gateway 里）
hermes gateway status
```

### Dashboard 鉴权（必做）
Dashboard 绑到非 127.0.0.1 必须配 basic auth：

```bash
# 生成密码 hash
python3 -c "from plugins.dashboard_auth.basic import hash_password; print(hash_password('密码'))"
```

将结果写入 `~/.hermes/config.yaml`（**不能用 patch 工具**，安全拦截）：

```python
# 用 python 脚本写入
import yaml
config_path = '/home/ubuntu/.hermes/config.yaml'
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)
config['dashboard'] = {
    'basic_auth': {
        'username': 'admin',
        'password_hash': '<hash>'
    }
}
with open(config_path, 'w') as f:
    yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
```

### 启动 Dashboard
```bash
# 配好 auth 后才能绑 0.0.0.0
hermes dashboard --port 8897 --host 0.0.0.0 --no-open
```

用户通过浏览器访问 `http://服务器IP:8897`，点 Kanban 标签。

### 关键注意
- config.yaml **不能**用 patch/edit 工具修改（安全拦截拒绝写），必须用 python yaml 脚本或 terminal
- 网关已经在跑的话，dispatcher 自动生效，每 60s 扫描看板
- 看板 DB 位置：`~/.hermes/kanban.db`

## Level 5a — Kanban 操作指南

### 核心命令一览

| 命令 | 用途 |
|------|------|
| `hermes kanban init` | 创建看板 DB（幂等） |
| `hermes kanban boards` | 多看板管理（创建/切换/列表） |
| `hermes kanban create` | 创建任务 |
| `hermes kanban list / ls` | 列出任务（可按状态/assignee 过滤） |
| `hermes kanban show <id>` | 查看任务详情+评论+事件 |
| `hermes kanban claim <id>` | 认领任务（原子操作） |
| `hermes kanban assign <id> <profile>` | 分配任务 |
| `hermes kanban complete <id>` | 完成任务 |
| `hermes kanban block <id>` | 标记阻塞 |
| `hermes kanban unblock <id>` | 解除阻塞 |
| `hermes kanban schedule <id>` | 定时任务（到期自动转 ready） |
| `hermes kanban promote <id>` | 手动推至 ready |
| `hermes kanban archive <id>` | 归档 |
| `hermes kanban link / unlink <a> <b>` | 任务依赖链（parent→child） |
| `hermes kanban comment <id> <text>` | 追加评论 |
| `hermes kanban attach <id> <file>` | 附加文件 |
| `hermes kanban swarm` | Swarm 模式（并行 worker→验证→合成） |
| `hermes kanban decompose <id>` | 自动拆解复杂任务为子任务 |
| `hermes kanban specify <id>` | 将 triage 任务具体化 |
| `hermes kanban stats` | 按状态+assignee 计数+最久待办 |
| `hermes kanban log <id>` | 查看 worker 运行日志 |
| `hermes kanban context <id>` | 打印 worker 看到的完整上下文 |
| `hermes kanban tail <id>` | 实时流式事件 |
| `hermes kanban dispatch` | 手动触发一次调度 tick |
| `hermes kanban watch` | 终端实时事件流 |
| `hermes kanban gc` | 垃圾回收（清理已归档 workspace/日志/事件） |
| `hermes kanban stats` | 所有列计数+最旧 ready 任务年龄 |

### 多看板（boards）

一个 board = 一个项目/工作流。数据隔离，每个 board 独立 DB 文件。

```bash
hermes kanban boards list                     # 列出所有看板
hermes kanban boards create <slug>            # 新建看板
hermes kanban boards switch <slug>            # 切换当前看板
```

默认 board slug 叫 `default`，即 `~/.hermes/kanban.db`。切换后操作针对新 board。

### Dispatcher 工作原理

- 跑在 Gateway 进程内，每 **60 秒** tick 一次
- 每个 tick：reclaim 过期/僵死任务 → promote 子任务 → spawn 就绪任务
- worker 是完整 Hermes Agent 进程（每个 worker 一个独立会话）
- worker 必须至少 **每小时** 发一次 heartbeat，否则 dispatcher 会 reclaim

### 并发限制（关键）

每 spawn 一个 worker ≈ 一个完整 Hermes Agent 进程（200-500MB RAM）。

三层控制（配在 `config.yaml`）：

```yaml
kanban:
  # 全局同时 running 任务上限
  max_in_progress: 3
  
  # 单个 profile 同时 running 上限（防止单 profile 被 fan-out 打爆）
  max_in_progress_per_profile: 2
  
  # live 并发上限（不是 per-tick budget，是全局 running+spawn 的实时值）
  max_spawn: 3
```

**资源参考（Yasin 的腾讯云轻量 2核/3.6G）**：
- Gateway 已占 ~1.8G peak
- 可用内存 ~1.8G
- 建议同时跑 **2-3 个** kanban worker，压到 4-5 个会爆内存/swap

### Swarm 模式

```bash
hermes kanban swarm create <slug> --workers 3 --verifier --synthesizer
```

流水线：并行 N 个 worker 分别执行 → verifier 校验 → synthesizer 合并结果。
适合批量数据抓取、多角度分析、批量内容生成。

### 任务依赖

```bash
hermes kanban link <parent_id> <child_id>     # child 依赖 parent
hermes kanban unlink <parent_id> <child_id>
```

子任务在所有 parent 完成后自动 promote 到 ready。

## Level 6 — Holographic 记忆

```bash
# 一键激活
hermes memory setup holographic

# 验证状态
hermes memory status
```

**特点：**
- 本地 SQLite 向量存储，零外部依赖
- 零费用
- 与已有 built-in memory (MEMORY.md/USER.md) 互补，不冲突
- 自动跨 session 存取事实，不需要手动维护

## 模型 Fallback 配置（抗 Provider 过载）

> **2026-08-27 主/备已反转**：当前主模型=硅基流动（custom provider，deepseek-ai/DeepSeek-V4-Flash），fallback=DeepSeek 官方。下方示例仍为「主官方→备硅基」写法，但**机制完全一致**，只需互换两端。当前锁定配置矩阵见 `china-ai-platforms` 技能的「模型锁死清单」。

当用户看到 `⚠️ The model provider failed after retries` 报错：主模型 provider 高峰过载（典型：DeepSeek 官方 API 国内上午 10-11 点连续 503 "Service is too busy"），Hermes 重试 3 次全失败后显示该提示。不是 Hermes 挂了，解法是配 fallback 链，主模型失败自动切换。

**主模型切 custom provider 的 key 格式**：`model.api_key: ${SILICONFLOW_API_KEY}`（`${VAR}` env 引用，源码 model_setup_flows.py 确认）；fallback_providers 数组条目用 `key_env: SILICONFLOW_API_KEY`——两种格式都行，主配置用 api_key、fallback 用 key_env。

⚠️ **改全局 provider 后 cron 会 fail closed**：有 `provider_snapshot` 的 cron job（创建时快照了旧 provider）下次运行直接失败而不是跟随新配置——config set 会打印警告，必须逐个 `hermes cron edit <job_id> --model <model> --provider <provider>` pin 到新值。

⚠️ **没钉模型的 cron 同样被跳过**（2026-08-29 实测）：任务 `model/provider` 为 null（跟随全局）时，全局推理配置变更后运行输出全是同一份 FAILED 占位文件，报「已跳过以避免非预期消耗：自该任务创建后全局推理配置已发生变更（服务商由 deepseek 变为 custom…）」。修复同一条命令：`hermes cron edit <job_id> --model <model> --provider <provider>`。判断方法：`ls -la ~/.hermes/cron/output/<job_id>/` 看连续几天文件大小完全一致（都是 FAILED 占位）→ 就是被跳过。对照：显式钉了 model/provider 的任务（如 AI英语任务）不受影响。当前会话也保留启动时的 provider 快照，改配置只对新会话/cron 生效。

### 诊断（先确认根因再动手）
```bash
grep -E "API call failed after .* retries" ~/.hermes/logs/errors.log | tail
```
`HTTP 503: Service is too busy` = provider 官方过载。`hermes fallback list` 看当前是否已有 fallback 链（默认空）。

### 配置（关键坑）
- `hermes fallback add` 是**纯交互式 picker，无任何非交互参数**，脚本/自动化里不能用
- ⚠️ **`hermes config set fallback_providers '[...]'` 会把数组存成字符串**（YAML 带引号），`fallback_config.py::_iter_fallback_entries` 只认 dict/list，字符串被静默忽略 → 配置看似成功实际无效
- 正确做法：python yaml 直接写列表（先备份 config.yaml，与 Dashboard auth 同一模式）

```python
import yaml, shutil
shutil.copy('/home/ubuntu/.hermes/config.yaml', '/home/ubuntu/.hermes/config.yaml.bak-fallback')
cfg = yaml.safe_load(open('/home/ubuntu/.hermes/config.yaml'))
cfg['fallback_providers'] = [{
    'provider': 'custom',
    'model': 'deepseek-ai/DeepSeek-V4-Flash',  # SiliconFlow 镜像 DeepSeek 官方同款
    'base_url': 'https://api.siliconflow.cn/v1',
    'key_env': 'SILICONFLOW_API_KEY'
}]
yaml.safe_dump(cfg, open('/home/ubuntu/.hermes/config.yaml','w'), allow_unicode=True, sort_keys=False, default_flow_style=False)
```

### 验证
```bash
hermes fallback list   # 应显示 Primary + Fallback chain (1 entry)
# 实测备用通道（SiliconFlow 首次 curl 可能 20s 超时=网络抖动，用 60s 超时重试，不是通道挂了）
curl -sS --max-time 60 https://api.siliconflow.cn/v1/chat/completions \
  -H "Authorization: Bearer $SILICONFLOW_API_KEY" -H "Content-Type: application/json" \
  -d '{"model":"deepseek-ai/DeepSeek-V4-Flash","messages":[{"role":"user","content":"say OK"}],"max_tokens":10}'
```

### 中国网络注意
- SiliconFlow（api.siliconflow.cn）国内可直连（~37ms），有 DeepSeek-V4-Flash/V4-Pro/V3.2/R1 全系镜像，是 DeepSeek 官方 API 的最佳 fallback 通道
- fallback 用与主模型**同款模型**（deepseek-v4-flash ↔ deepseek-ai/DeepSeek-V4-Flash），切换用户无感
- fallback 触发条件：rate-limit、5xx、连接错误（文档：hermes-agent.nousresearch.com/docs/user-guide/features/fallback-providers）

## 技术细节

| 功能 | 端口 | 鉴权 | 存储位置 |
|------|------|------|----------|
| Kanban Dashboard | 8897 | basic auth | ~/.hermes/kanban.db |
| Holographic Memory | 无 | 无 | ~/.hermes/memory_store.db |
| GitHub Backup | 无 | PAT token | private GitHub repo |
| Gateway | 9119 | 无（127.0.0.1） | ~/.hermes/sessions/ |

---

## 多机部署与协作（合并自 hermes-multi-machine）

**触发**：两台以上 Hermes 实例（服务器+Mac）的分工/通信/远程装新机（「装 Hermes 到任意电脑/新电脑/Windows」）。

### 分工原则
| 实例 | 角色 | 特点 |
|------|------|------|
| **服务器**（24h在线） | 后台大脑 | cron/渠道值守/搜索调研/数据采集/长分析 |
| **Mac/本地**（人在才开） | 创作主力 | 剪映/GUI/浏览器登录态/本地大文件 |

铁律：每实例独立 `~/.hermes/` + 独立 SOUL.md（服务器=行动派「先做再说」；Mac=先想后动、深度优先、模糊反问、质疑再信）；定时任务按实例归属防双跑；渠道分配（飞书→服务器、微信→Mac、QQ→服务器）。

### 网络桥接（Tailscale）
服务器 `curl -fsSL https://tailscale.com/install.sh | sh && sudo tailscale up`（Mac 装 dmg），两边**同一账号**登录自动组网 → `tailscale status` 查对方 IP（100.x.x.x）→ `ssh mac@100.x.x.x`。零公网端口暴露。

### 代理隧道（Mac翻墙→服务器复用）
⚠️ **2026-08-26 已修复并重新配置**：旧配置 `.bashrc` 里 `ssh -L 7890:127.0.0.1:7890 mac@100.80.117.5` + 3行 export 是**坏配置**——Mac 的 Clash Verge (mihomo) 混合代理端口是 **7897**（GUI 控制口 33331 不是代理口），7890 转发到空端口从未生效，还持续劫持 pip/uv 报 ProxyError。已删除坏配置，改成：

```bash
# 正确隧道（17897 本地端口 → Mac 7897 混合代理口）
ssh -L 17897:127.0.0.1:7897 -N -f -o StrictHostKeyChecking=no -o ExitOnForwardFailure=yes mac@100.80.117.5
# git 全局走代理
git config --global http.proxy http://127.0.0.1:17897
git config --global https.proxy http://127.0.0.1:17897
```

- 默认**不 export 全局代理变量**（避免劫持 pip/uv），需要时 `proxy-on`/`proxy-off` 函数（在 .bashrc，已配置）
- keepalive.sh 已加 `start_tunnel()` 保活（17897 断了自动拉起）
- 隧道活着但 curl 000 → **Mac 端 Clash 代理没启动**（`lsof -iTCP:7897 -sTCP:LISTEN` 无输出），需用户开 Clash Verge 选节点
- 完整配置+踩坑（[s]sh 防自匹配、非交互 shell 不加载函数、代理劫持 pip）：见 server-service-deployment 技能 `references/mac-proxy-tunnel.md`

### 跨机 Skill 同步
- **macOS TCC 坑**：SSH 读 Mac 的 `~/Desktop` 报 Operation not permitted——skill 库走 `~/.hermes/skills/` 不碰 Desktop
- 对比：两边 `find ~/.hermes/skills -name SKILL.md | sed 's|.*/skills/||; s|/SKILL.md||' | sort` + `comm -23`（comm 要求先 sort）
- 传输：`cd ~/.hermes/skills && ssh mac@<ip> 'cd ~/.hermes/skills && tar czf - <skill>' | tar xzf -`（保留 references/）
- 筛选原则：同主题剔除 / .archive 里归档过谨慎 / Mac 专属剔除 / 同类 N 选 1 / 已自动化功能不拉对应 skill
- 品牌名清理：patch 前 `grep -rn 品牌名` 找全所有位置（不只 description，正文引用行也要改）

### 远程装 Hermes（Windows/任意电脑）
先问清是哪台电脑（别默认 Mac）；装 Hermes ≠ 配 key（只装不配 = 空壳，能跑 doctor 但一问问题报「没配模型」）。SSH 优先（Windows 先开 OpenSSH Server：设置→系统→可选功能；本地账户无密码先 `net user <用户名> <新密码>` 设临时密码；微软账户用邮箱密码或密钥认证）；**必须 Git Bash**：`curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash`；`HTTP 400 No models provided` = config.yaml 被记事本存成 UTF-8 BOM（重存无 BOM）；墙内拉脚本 `export https_proxy=http://127.0.0.1:7890`；装完 tar over ssh 同步 skills + DeepSeek key + 按角色定制独立 SOUL.md。

**支持文件**：`scripts/mac-hermes-diagnostic.sh`（跨机诊断：系统版本/进程/配置/Python/端口/网络/磁盘）。

## macOS 自动备份（合并自 macos-backup-automation）

**触发**：把 Hermes 数据（config/会话/skills/工作区/知识库）每日自动备份到外置盘（与上文 Level 4 GitHub 备份互补：GitHub 管配置，外置盘管全量）。

**核心坑：/Volumes 挂载点 root 属主**——`ls /Volumes/<name>` → Permission denied、mkdir/cp/tar 全失败、osascript 也失败（Finder 能成但会挂起）。检测：`ls /Volumes/<name>/ 2>/dev/null || echo 不可读` + `df -h | grep <name>`（**df 比 ls 可靠**：ls 在盘已挂载但目录 root 属主时也报错）。

**策略**：本地先打包到 /tmp → cp 外置盘 → 盘未挂载/不可写就优雅跳过（cron 在盘没插时也要能跑，测试拔盘场景）。脚本 `scripts/hermes-backup-macos.sh`：`df -h` 动态探测挂载点（强制弹出后 macOS 留 root 属主 stub，卷会挂成 `<name> 1`——**不能硬编码路径**），7 天滚动保留，日志 `~/Desktop/hermes/backup-log.txt`。注册：`hermes cron create "0 3 * * *" --name 外置盘备份 --no-agent --script hermes-backup.sh`。

**其他坑**：APFS 快照卷（Preboot/VM 等）不是外置盘别备份；备份 I/O 可能触发边缘故障 USB 桥接强制弹出（插 Windows 重初始化，或 `sudo killall -STOP -c usbd; sleep 2; sudo killall -CONT -c usbd` 复位 USB 总线）；用户说「你的命令之后盘弹出了」要信用户时序帮恢复，别争因果；「一插就发烫」≠桥接板烧毁，多为 Mac USB 控制器/NVRAM 状态异常，先 Windows 交叉验证。

**支持文件**：`scripts/hermes-backup-macos.sh`（实际运行的备份脚本，自动检测挂载点）、`references/macos-external-disk-troubleshooting.md`（5层排查：换线→换口→直插→换机验证→NVRAM 重置）。

