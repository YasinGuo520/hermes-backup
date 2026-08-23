# Anthropic Managed Agents 架构参考

> 来源：Anthropic 工程博客 "Scaling Managed Agents: Decoupling the brain from the hands" (2026-04-08)
> 本篇作为企业 Agent 平台架构设计的参考案例

## 为什么做

Model 在变好，但 harness（驱动 loop）写死的 workaround 会变废代码。

**例子**：Sonnet 4.5 有"context anxiety"（快满上下文就提前收工），加了 context reset。Opus 4.5 发布后该行为消失，reset 变死代码。

→ **Harness 不应假设模型有啥弱点**，要设计接口让 harness 本身可换。

## 旧设计的问题：Pets

最初把所有组件塞一个容器里：

```
┌─────────────────────────┐
│     单容器 (Pet)        │
│  ├─ Brain (Claude)       │
│  ├─ Hands (沙箱)         │
│  └─ Session (状态)       │
└─────────────────────────┘
```

| 问题 | 后果 |
|---|---|
| 容器挂了 → 整个 session 丢 | 没法恢复 |
| 调试要进容器，但里面没用户数据 | 等于不能 debug |
| 凭据和 LLM 代码放一起 | 注入攻击直接偷 token |
| 客户想连 VPC | 必须整容器搬过去 |

这是典型的 **pet 服务器**——命名、手养、死不起。从 pets-vs-cattle 类比（Bill Baker / Randy Bias）看，耦合 = pet。

## 三层解耦架构

```
┌──────────────────────────────────────────────┐
│             BRAIN (Harness)                  │
│  Claude + 控制循环                           │
│  ● 完全无状态                                │
│  ● 挂了就 wake(sessionId) 重建上下文          │
│  ● 像 OS 恢复进程寄存器                       │
│  ● 接口：wake(sessionId) → HarnessHandle     │
├──────────────────────────────────────────────┤
│             SESSION (事件日志)                │
│  ● append-only 持久化存储，在 harness 之外    │
│  ● 完整保存所有 user/assistant/tool 消息      │
│  ● 接口：emitEvent(id, event) → void         │
│  ● 接口：getSession(id) → 完整事件日志        │
│  ● 接口：getEvents({after, before, limit})    │
│  ● 类似 OS 的文件系统抽象 + 事件溯源模式       │
├──────────────────────────────────────────────┤
│             HANDS (沙箱)                     │
│  ● 隔离执行环境，统一接口                     │
│  ● execute(name, input) → string             │
│  ● 像 Unix read() 系统调用——接口不变        │
│  ● 纯受信资源/凭据不在沙箱内                  │
│  ● 可适配容器、浏览器、手机、模拟器等          │
└──────────────────────────────────────────────┘
```

## SessionStore 概念

在 Claude Agent SDK（自托管版本）中，SessionStore 是持久化 session transcript 的接口抽象：

```ts
interface SessionStore {
  save(sessionId: string, transcript: Transcript): Promise<void>
  load(sessionId: string): Promise<Transcript | null>
}
```

| 后端 | 适用场景 |
|---|---|
| S3 | 低成本、大容量、跨区域 |
| Redis | 低延迟、临时会话 |
| Postgres | 跟业务数据放一起 |
| 自定义 | 任何存储 |

Managed Agents 内置了 SessionStore（平台管），Agent SDK 需自接。

## Pets → Cattle 范式转换

| 旧（耦合） | 新（解耦） |
|---|---|
| 容器挂 = session 永久丢失 | Harness 崩溃被捕获为 tool-call 错误，新 harness 用 `wake()` 恢复 |
| 凭据在沙箱内 | 凭据在 vault 或 provision 时注入 |
| VPC peering 要求 | 沙箱可自托管到客户环境 |
| 每次都付全容器启动成本 | 沙箱 lazy 启动，TTFT 降 60%（p50）/ 90%+（p95） |

## 核心接口汇总

| 接口 | 签名 | 作用 |
|---|---|---|
| `wake(sessionId)` | → HarnessHandle | 从 session 日志恢复 harness |
| `getSession(id)` | → 完整事件日志 | 重启后重建上下文 |
| `emitEvent(id, event)` | → void | 写入持久化事件 |
| `getEvents({after, before, limit})` | → events[] | 时间切片查询 |
| `execute(name, input)` | → string | 沙箱执行（HANDS） |

## 设计原则（复用至任何企业 Agent 平台）

1. **Pet 变 Cattle**：任何组件可独立崩溃和恢复，不丢 session
2. **接口稳定 > 实现稳定**：`read()` 从 1970s 的磁盘皮到现代 SSD 不变，同理 `execute()` 应适配任何执行环境
3. **凭据不进沙箱**：结构安全 > 模型安全，注入攻击拿不到 token
4. **一致性协议**：Brain ↔ Sandbox 通过单一接口通信，不假设后端
5. **Session 即事件源**：任何数据都是 append-only 日志的重投影（event sourcing 模式）
