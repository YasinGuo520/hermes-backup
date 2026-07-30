# Kanban 并发限制参考

看板有三层并发控制，都在 `config.yaml` 里配。

## 配置项

| 配置项 | 默认值 | 作用 |
|--------|--------|------|
| `kanban.max_in_progress` | `None`（无限） | 全局同时 running 的任务上限 |
| `kanban.max_in_progress_per_profile` | `None`（无限） | 单个 profile 同时跑的上限 |
| `kanban.max_spawn` | `None`（无限） | 每个 tick 最多 spawn 几个 |
| `kanban.failure_limit` | 3 | 失败N次后自动 block |
| `kanban.dispatch_stale_timeout_seconds` | 0（关） | 超时未 heartbeat 的任务自动 reclaim |

## 限流 vs 无限流

**不限流**：扔10个任务 → 10个同时跑 → 服务器OOM/API爆
**限流**：设 `max_in_progress: 3` → 3个跑，7个排队 → 单任务快，系统稳

## Yasin 服务器建议值

```
kanban:
  max_in_progress: 3
  max_in_progress_per_profile: 2
```

理由：2核CPU，3.6G内存，Gateway已占1.8G。每个worker约200-500MB。

## 工作原理

Dispatcher 每60s扫描看板，检查 running 数量。当 `in_progress >= max_in_progress` 时跳过本次 spawn，等已有任务完成后再放新的进来。类似水龙头限流。
