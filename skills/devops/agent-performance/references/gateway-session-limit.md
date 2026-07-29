# Gateway Session Limit 诊断与修复

## 报错原文

```
Hermes is at the active session limit (20/5). Try again when another session finishes.
```

格式含义：`(当前活跃数/上限)` — 20个活跃 > 5个上限，拒绝新会话。

## 快速确认

```bash
hermes status
# 看 → ◆ Sessions → Active: N session(s)
```

## 修复命令（按优先级）

### 1. 重启网关 — 清空积压会话

```bash
hermes gateway restart
```

### 2. 检查后台进程 — 是否有卡住的 delegate_task

```bash
process action=list     # 查看 Hermes 后台进程
# 如有卡住进程：process action=kill session_id=<id>
```

### 3. 调大上限（频繁出现时）

```bash
hermes config set delegation.max_concurrent_children 20  # 调高并发数
hermes config set gateway.max_sessions 50                  # 调高网关会话池
```

### 4. 调整后验证

```bash
hermes gateway restart   # 使配置生效
hermes status            # 确认 Active 数正常
```

## 常见原因

| 原因 | 特征 | 解决 |
|------|------|------|
| delegate_task 堆积未回收 | 同时 spawn 了多个 background subagent | 调高 max_concurrent_children |
| cron job 卡住 | cron 列表中有长时间未完成的 job | `hermes cron` 查看，删掉/重跑 |
| 网关重启未回收旧会话 | gateway restart 后仍有残留 | 调高 max_sessions |
| 同时多平台高频请求 | Feishu + QQ 同时发多条消息 | 调高两项上限即可 |

## 默认值与推荐值

| 配置项 | 默认值 | 推荐值 |
|--------|--------|--------|
| delegation.max_concurrent_children | 5 | 20 |
| gateway.max_sessions | 未显式设置（默认5） | 50 |
