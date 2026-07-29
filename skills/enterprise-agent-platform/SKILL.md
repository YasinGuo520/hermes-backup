---
name: enterprise-agent-platform
description: 企业多部门Agent平台搭建咨询——架构设计、各部门Agent功能定义、成本估算、部署规划。当用户问"公司用Agent怎么搭""多部门几十人怎么搞"等场景时加载。
---

# 企业多部门Agent平台搭建咨询

## 适用场景

用户问以下问题时加载此技能：
- "公司化agent如何搭建"
- "多部门几十人如何搭建Agent"
- "各部门的Agent功能作用是什么"
- "企业Agent平台需要多久/多少钱"
- 任何关于**真实公司多部门**使用AI Agent的架构咨询

## 核心框架：一问四答

当用户问公司Agent搭建时，按以下结构回答：

## 架构模式参考

加载本技能时一并加载 `references/managed-agents-architecture.md` 获取 Anthropic Managed Agents 三层解耦架构的完整参考。该模式是企业级 Agent 平台的基础设计范式。

### 三层解耦（Brain / Session / Sandbox）

| 层 | 角色 | 类比 |
|---|---|---|
| **Brain（Harness）** | 推理引擎+控制循环，完全无状态 | 像 OS 的调度器 |
| **Session（事件日志）** | append-only 持久化存储，独立于 harness | 像 OS 的文件系统抽象 |
| **Sandbox（执行环境）** | 隔离的代码/工具执行沙箱，统一接口 | 像 Unix `read()` 系统调用 |

### 核心设计原则

1. **Pet 变 Cattle**：任何组件可独立崩溃和恢复，不丢 session
2. **接口稳定 > 实现稳定**：抽象层 < 实现层，模型变强了 harness 不用重写
3. **凭据不进沙箱**：注入攻击拿不到 token，结构安全非模型安全
4. **一致性协议**：Brain ↔ Sandbox 通过 `execute(name, input) → string` 唯一接口通信，容器/浏览器/手机同接口

### 1. 架构模式（先说全貌）
核心概念映射：
| Agent概念 | 现实对应 |
|-----------|---------|
| 工作区(Workspace) | 一个部门 |
| Agent | 一个AI助手（部门可有多个） |
| 知识库 | 部门文件（本部门独享） |
| 工具 | 接的API（ERP/数据库/爬虫） |
| 机器人 | 员工对话入口（飞书/企微bot） |

### 2. 推荐平台对比

| 平台 | 最佳场景 | 多租户 | 自部署 | 上手难度 |
|------|---------|--------|--------|---------|
| **Dify** | 综合企业平台 | ✅ 原生 | ✅ Docker | ⭐ 低 |
| FastGPT | 知识库问答为主 | ✅ | ✅ | ⭐ 低 |
| Coze(扣子) | 快速验证/SaaS | ✅ SaaS | ❌ | ⭐ 最低 |
| RAGFlow | 复杂文档解析 | ❌ | ✅ | ⭐⭐ |

**首推 Dify**：全功能+自部署+中文社区最活跃。

### 3. 部门Agent模板（见 references/department-agents.md）
逐个部门列出可用的Agent类型（产品/运营/物流/财务/人事/市场）。

### 4. 成本估算

**搭建时间：**
- 第1天：部署Dify（~3小时）
- 第1周：搭好2个部门试点
- 第2周：全公司铺开

**Token费用（以DeepSeek V4 ¥5/亿tokens计）：**
| 公司规模 | 日费 | 月费 |
|---------|------|------|
| 10人 | ¥1-2 | ¥30-60 |
| 30人 | ¥3-6 | ¥90-180 |
| 50人 | ¥5-10 | ¥150-300 |
| 100人 | ¥10-20 | ¥300-600 |
| 实际建议 | | 在上述基础上×2做预算 |

**总成本（50人）：服务器¥100/月 + Token¥500-1000/月 ≈ ¥600-1100/月**

**省钱技巧：**
- 简单问答走便宜模型（DeepSeek V4-Flash）
- 复杂推理才用强模型
- Dify自带token缓存
- 按部门设月度配额

### 5. 权限/隔离设计
- 每个部门一个独立工作区
- 部门间数据不可见
- 普通员工只能用Agent，管理员才能改
- 员工通过飞书/企微bot对话，不学新系统

### 6. 用户状态判断
- 说"了解下/暂时不用"时 → 只给概念+成本，不push部署
- 说"帮我搭/想试试"时 → 转为执行模式
- 说"给我预算方案"时 → 细化到具体人数+部门

## 参考文件
- `references/department-agents.md` — 各部门Agent功能详细模板
- `references/managed-agents-architecture.md` — Anthropic Managed Agents 三层解耦架构完整参考（Brain/Session/Sandbox、SessionStore、Pets-vs-Cattle）
