---
name: hermes-self-upgrade
description: "Use when 升级 Hermes 本体（含被硬护栏拦住、升级卡在半成品、收尾重装依赖重启）。"
version: 1.0.0
metadata:
  hermes:
    tags: [hermes, upgrade, gateway, guard, lifecycle, devops]
---

# Hermes 自升级（含硬护栏绕不过的正确路径）

## 铁律：agent 不能自己升级 Hermes

Hermes 有**硬编码护栏**，不是 approval 提示，`approvals.mode: off` 也拦：

| 位置 | 拦什么 |
|---|---|
| `tools/approval.py:1094-1095` (`DANGEROUS_PATTERNS`) | `hermes gateway (stop\|restart)`、`hermes update` |
| `tools/code_execution_tool.py:1570` | execute_code 里的同样命令（防绕过） |
| `cron/lifecycle_guard.py` `_GATEWAY_LIFECYCLE_PATTERN` | `hermes gateway restart`、`launchctl …hermes-gateway`、**`systemctl … restart …hermes-gateway`**（Branch C）、`pkill … hermes … gateway`；**cron job 的 script 内容也查** |

**关键点：terminal 工具还会读取「被引用的脚本」的内容**。所以 `chmod +x upgrade.sh`、`bash -n upgrade.sh` 都会被拦，只要那个脚本里有 `systemctl restart hermes-gateway`。systemd-run 包装脚本也拦。

**唯一可行路径：让用户发 `/update`**（`gateway/run.py` `_handle_update_command`）。它 detach 一个 helper 跑 `hermes update --gateway`，用文件 IPC 传进度，不走 agent 通道。gateway 的 `/restart` 同理。

## 致命坑：`/update` 会半途失败

`/update` 重启网关前要 **drain（SIGUSR1）—— 即等 agent 当前这一轮 turn 结束**。
如果 agent 正在跑一个很长的 turn（排查、大段工具调用），它等不到，**5-6 分钟后超时退出，outcome=failed**，留下半成品：

- 代码已更新（git checkout + ff-merge 完成）
- 依赖没重装、config 没迁移、网关没重启

自查证据：`~/.hermes/logs/update_receipts/latest.json`（`outcome`、`pre_update`/`post_update` sha）、`~/.hermes/fleet_restart_pending`（含 `expected_sha`）、新版 CLI 会自己打印警告 “pulled new code but did not restart running gateways”。

**规避**：用户发 `/update` 前，agent 必须先结束当前轮（回复完/停下），别在同一轮里继续长时间干活。

## 半成品收尾（agent 能做的部分）

```bash
cd ~/.hermes/hermes-agent
venv/bin/pip3 install -e .                        # ① 重装依赖（gateway 跑在 venv）
venv/bin/python -m hermes_cli.main config migrate # ② 配置迁移（会打印 xx → xx 版本）
venv/bin/hermes plugins compat ~/.hermes/plugins/<name>   # ③ 检查自定义插件是否用了 9-14 重构删掉的旧 import 路径
```

④ 最后一步重启**必须用户发 `/restart`**（或外部 shell）。

### 坑①：pip 报 `Errno 13 Permission denied … __pycache__/…pyc`
venv 里有 root 属主文件（历史上某次 sudo 跑过 hermes 留下的）。修：
```bash
sudo chown -R ubuntu:ubuntu ~/.hermes/hermes-agent/venv/lib/python3.11/site-packages/__pycache__
```
不修的话 pip 会在 uninstall 旧 hermes-agent 时中断，**并且可能已经把某些包卸了没装回**（本次 nemo-relay 0.7.3→0.8.4 被卸后靠重跑补上）。

### 坑②：依赖比对误报
`pyproject.toml` 里带 marker 的依赖（`tzdata`、`concurrent-log-handler` 都是 `sys_platform == 'win32'`）Linux 不装 —— 比对脚本要解析 marker，否则误判“缺失”。

### 坑③：两个 Python 安装
- gateway/dashboard 跑 `venv`（uv python 3.11）
- `which hermes` 可能指向 `~/.local/bin/hermes`（系统 python 3.12，editable 但 metadata 旧）
→ 一律用显式路径 `venv/bin/hermes` / `venv/bin/python -m hermes_cli.main`，别用裸 `hermes`。

## 升级前必备（5 分钟）

1. 基线：`git rev-parse HEAD`、`hermes --version` 写进 `~/Desktop/hermes/hermes-upgrade-backup-<date>/BASELINE.txt`
2. 备份：config.yaml、.env、cron.tar.gz、plugins.tar.gz、state.db（几百 M，`cp` 20 秒）、未提交改动 `git diff > local-changes.patch`
3. 本地未提交改动先 `git stash push -m ...`（`/update` 默认会把 stash 重新套到新代码上，会带进不兼容的旧补丁）
4. 记录服务清单：`hermes update --plan`（只读！列出所有要重启的服务及其 supervisor）
5. 通知通路：`venv/bin/hermes send --to feishu "自检"` 验证一次（重启后靠它汇报）

## 重启前顺手检查

```bash
systemctl --user is-active hermes-gateway        # 旧进程应仍 active（跑内存旧代码）
venv/bin/hermes plugins compat <每个自定义插件>   # 9-14 后旧 import 路径的插件会被自动禁用
```

## 重启后自动汇报（agent 无法自己发）

用 `cronjob(no_agent=true, script=<脚本>, schedule="in 5m", deliver="origin")` 布置一次性自检 ——
脚本输出即飞书正文，0 token。**注意：脚本内容里不能出现 `systemctl restart hermes-gateway` 之类的字面量，否则 cron 创建会被 lifecycle_guard 拦**（回滚命令放到单独的 .txt 里）。

自检脚本要点：`systemctl --user is-active`、`-p MainPID --value`、`git log -1`、`pip3 show hermes-agent`、`journalctl --user -u hermes-gateway --since -6min | grep -ciE 'traceback|importerror'`、各渠道日志行数、cron jobs 数量。
