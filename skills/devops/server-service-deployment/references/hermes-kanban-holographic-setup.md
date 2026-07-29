# Hermes Kanban + Holographic Memory 配置记录

配置日期：2026-07-29
用户：Yasin
服务器：腾讯云 43.138.221.174

## 当前状态

| 等级 | 功能 | 状态 |
|------|------|------|
| Level 3 | Curator（技能压缩） | ✅ 已启用（`consolidate: true`） |
| Level 5 | Kanban 看板 | ✅ DB已初始化，Dashboard已启动 |
| Level 6 | Holographic 记忆 | ✅ 已激活（`memory.provider: holographic`） |
| Level 4 | GitHub 自动备份 | ⏸ 待用户提供 GitHub 信息 |

## Kanban 配置

```bash
hermes kanban init              # 初始化看板数据库
# 输出: Kanban DB initialized at /home/ubuntu/.hermes/kanban.db

hermes gateway start            # 启动gateway（已运行，需确认dispatcher生效）
# gateway 内嵌 dispatcher，默认每60秒扫描一次待办任务

hermes dashboard --port 8897 --host 127.0.0.1 --no-open
# Web UI 访问方式：SSH隧道或Tailscale
```

## Holographic 记忆配置

```bash
hermes memory setup holographic    # 跳过交互选择器，直接激活
# 输出: Memory provider: holographic / Activation saved to config.yaml
```

验证：
```bash
hermes memory status
# 应显示: Provider: holographic / Plugin: installed ✓ / Status: available ✓
```

Holographic 是本地 SQLite 向量存储（`~/.hermes/memory_store.db`），零外部依赖，零费用。自动记录跨 session 事实，与现有 Obsidian 知识库互补（Obsidian=主动知识库，Holographic=自动记忆）。

## GitHub 备份 Level 4 尝试（未完成）

### 原因
- 用户 GitHub Web 端在国内访问慢
- 用 `gh` CLI 设备登录替代网页操作，但 timeout（需用户主动去 `github.com/login/device` 输入码）
- 用户改用 Fine-grained PAT 后，token 缺少 `Administration: write` 权限，POST 创建 repo 失败（`Resource not accessible by personal access token`）

### 教训：Fine-grained PAT 创建仓库所需权限
- 路径：Settings → Developer settings → Personal access tokens → Fine-grained tokens
- Repository access: Only select repositories（但新 repo 还不存在，需先手动建或用 classic PAT）
- **创建新仓库需要 `Administration: write`**，仅 `Contents: read/write` 不够
- 最佳方案：先用 classic PAT（repo 权限）建仓库+初始推，日常备份用 fine-grained（Contents RW 足够推代码，不用建仓库权限）

### gh CLI 设备登录要点
- `gh auth login --hostname github.com --git-protocol https`：打印一次性码 + URL，授权完成后自动写入 credential
- 有 timeout（120s 内未授权则超时退出），但 auth 实际已完成，重新跑会检测到已登录
- 适合没有浏览器的 headless 服务器

## 当前完成状态

| 等级 | 功能 | 状态 |
|------|------|------|
| Level 3 | Curator（技能压缩） | ✅ 已启用（`consolidate: true`） |
| Level 5 | Kanban 看板 | ✅ DB已初始化，Dashboard已启动（8897端口） |
| Level 6 | Holographic 记忆 | ✅ 已激活（`memory.provider: holographic`） |
| Level 4 | GitHub 自动备份 | ❌ 待用户创建 private repo + 配置 cron |

## 用户访问 Dashboard 的方式

公网直连 + basic auth：
```
http://43.138.221.174:8897
用户名：admin
密码：kanban
```

## 注意事项

- Dashboard 绑 `0.0.0.0` 必须配密码，否则拒绝启动
- 绑定 `127.0.0.1` 可通过 SSH 隧道或 Tailscale 访问
- Kanban dispatcher 跑在 gateway 内，gateway 必须运行
- Holographic 不冲突现有 MEMORY.md/USER.md，它们是叠加关系
- 密码 hash 用 `python3 -c "from plugins.dashboard_auth.basic import hash_password; print(hash_password('密码'))"` 生成
