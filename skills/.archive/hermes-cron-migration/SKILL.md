---
name: hermes-cron-migration
description: 将 Hermes Agent 的定时任务（cron jobs）、脚本和数据文件从一台机器迁移到另一台。覆盖 jobs.json 导出、prompt 任务重建、脚本路径调整、delivery 重定向。
category: autonomous-ai-agents
---

# Hermes Cron 任务迁移

当用户需要把 Hermes 的定时任务从一台机器（如本地 Mac）搬到另一台（如云端 Linux 服务器）时使用。

## 适用场景

- 用户说「把本地的定时任务迁移上去」
- 用户换了 Hermes 运行的机器
- 需要把 Mac 上的 cron 任务搬到云端服务器

## 检查清单

- [ ] 源机器能访问 `cat ~/.hermes/cron/jobs.json`
- [ ] 已确认目标机器的 Hermes 网关运行正常
- [ ] 已确认目标机器连接了哪些平台（飞书/微信/Telegram 等）
- [ ] 脚本依赖的工具在目标机器已安装

## 迁移步骤

### 1. 获取源机器的 cron 配置

```bash
# 方法一：完整导出（推荐）
cat ~/.hermes/cron/jobs.json
```

从中提取每个任务的完整 JSON（id, name, prompt, schedule, deliver, origin, model_snapshot, repeat, script, no_agent, enabled_toolsets 等关键字段）。

**注意：`hermes cron job view <id>` 命令在某些版本可能不存在。直接用 `cat ~/.hermes/cron/jobs.json` 最可靠。**

如果用户不熟悉命令行，也可以让他们直接执行：
```bash
hermes cron list
```
然后把任务 ID 发给你，你再指导他们执行 `cat ~/.hermes/cron/jobs.json`。

### 2. 分析哪些任务可迁移

判断规则：
- **备份/本地专属脚本**（如 macOS 外置盘备份、hermes-backup.sh） → 跳过
- **纯 prompt 任务**（无 script 字段） → 直接重建
- **脚本任务**（有 script 字段引用本地路径） → 需要获取脚本文件 + 调整路径

### 3. 迁移纯 prompt 任务

直接用 `cronjob create` 重建：

```bash
hermes cron create ...  # 或通过工具调用
```

关键参数：
- `deliver` → 改为目标机器支持的平台（如本地是 weixin，服务器也连了微信则保持一致）
- `model` → 可留空（使用目标机器默认模型），或根据 `model_snapshot` 锁定
- `enabled_toolsets` → 根据 prompt 内容推断（如用了 web_search 则加 `["web"]`）
- `repeat` → 根据原始配置复刻

### 4. 迁移脚本任务

**4.1 获取脚本文件**

用户本地 Mac 上有脚本文件（如 `daily_stock_brief.py`），需要用户发文件过来：

> 「把 xxx.py 文件发给我，我来放到服务器上」

如果用户直接拖文件到聊天，文件会存到 `~/.hermes/cache/documents/`，需要 copy 到项目目录。

**4.2 调整脚本中的路径**

常见需要修改的路径：

| 源路径（macOS） | 目标路径（Linux 服务器） |
|---|---|
| `~/Desktop/hermes/xxx.json` | `~/projects/xxx.json` |
| `/Users/mac/Desktop/hermes/` | `~/projects/` |
| Mac 特有的 `/Volumes/` 路径 | 映射到 Linux 路径 |

用 `patch` 工具做替换。

**4.3 创建 cron job**

prompt 格式参考：
```
运行 ~/projects/<script_name>.py 脚本，将输出结果直接返回给我。

[简要说明脚本功能]

注意：脚本运行需要约X秒，请耐心等待。不要添加额外开场白或结束语，直接返回脚本输出。
```

### 5. 验证

```bash
hermes cron list
```

检查：
- 任务数量和名称是否正确
- `next_run_at` 时间是否合理
- `deliver` 目标是否正确
- 脚本语法检查：`python3 -m py_compile <path>`

## 常见陷阱

- **路径写死**：Mac 的 `~/Desktop/hermes/` 在 Linux 上不存在，必须改成 `~/projects/` 或其他存在的目录
- **delivery 平台**：源机器的 `deliver` 字段可能指向特定 chat_id。如果目标机器也连了同平台（如都连了微信），可以保持 chat_id 一致。目标机器的 chat_id 可以从 `gateway_state.json` 中查到
- **脚本依赖**：Python 脚本中用到的包（如 openpyxl, playwright, openai）需要先在目标机器安装
- **shebang 行**：macOS 默认 Python 路径是 `/usr/bin/python3`，Linux 可能是 `/usr/bin/python3` 或 `/usr/bin/python3.11`，确保脚本的 shebang 兼容
- **文件权限**：复制脚本后记得 `chmod +x`
- **repeat 次数**：检查源任务的 `repeat.times`，如果是有次数限制的（如 30 次或 600 次），保持一致。用 `cronjob create` 时通过 `repeat` 参数设置
- **Prompt 脚本任务的性能**：如果 cron prompt 是运行一个 Python 脚本，在 prompt 中注明脚本运行时间（如"需要约45-60秒"），避免 agent 超时
- **`~` 在双引号内不展开**：Shell 命令中 `~/projects/` 不会在双引号中展开成 `/home/ubuntu/projects/`。在 cron prompt 中可以用 `~/projects/xxx.py`（会被 Hermes 解析），但在 terminal 命令中要用完整路径

## 相关命令

```bash
# 查看所有任务
hermes cron list

# 查看 cron 目录结构
ls -la ~/.hermes/cron/
cat ~/.hermes/cron/jobs.json   # 完整的任务配置
```
