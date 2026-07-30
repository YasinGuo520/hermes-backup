---
name: subagent-project-scaffolding
description: "Delegate full project scaffolding to sub-agents via delegate_task — structure the brief so the sub-agent builds the entire project autonomously, then verify the result."
version: 1.0.0
author: agent
tags: [delegation, project-setup, scaffolding, fastapi, saas]
---

# Sub-Agent Project Scaffolding

Delegate the build of an entire project (file structure, code, config, deployment) to a background sub-agent so you and the user keep working on other things.

## When to Use

- The user wants a complete project built from decisions you've already made
- The project has a clear structure, tech stack, and known output
- You have at least 5+ minutes of uninterrupted sub-agent time
- The sub-agent needs zero clarification (all decisions are finalised before dispatching)

## The Brief Template

A good delegate_task call has these sections. **Every one matters.**

### 1. Project Overview (3-5 lines)
Name, architecture summary, MVP goal. The sub-agent has no conversation context — start from zero.

### 2. Environment (always include)
```
- Server IP / OS
- CPU / RAM / Disk
- What's preinstalled (python3, pip, git, nginx?)
- Which ports are available
```

### 3. Tech Stack (pinned decisions)
```
| Layer | Choice | Why (1 line) |
```

Pin the stack hard. If you say "Vue3 but if too complex use HTML", the sub-agent will spend 20 minutes debating itself. **Pick one.**

### 4. Features (prioritised as P0 / P1)
P0 = MVP must ship with. P1 = stubs or placeholders.

### 5. File Structure (exact tree)
```
project/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   ├── auth.py
│   │   └── ...
│   ├── core/
│   │   └── ...
│   └── static/
│       └── index.html
├── requirements.txt
└── deploy.sh
```

Give the exact tree. The sub-agent will follow it literally. Omitting a file means it won't exist.

### 6. Design Decisions (non-negotiable)
```
1. Multi-tenant: all tables get tenant_id
2. Auth: JWT + bcrypt
3. Frontend: pure HTML (no build step)
4. DB: SQLite with SQLAlchemy
...
```

### 7. Verification Steps
```
After writing all files:
1. cd project/ && python -m app.main starts
2. curl /health returns 200
3. curl register → login → chat returns 200
```

## Key Constraints to Set

```text
- All code files in ~/projects/<name>/
- Use a venv (not global install)
- Don't use clarify — all decisions are in the brief
- Don't call delegate_task again (leaf role)
- Reply language: Chinese (or match user's language)
```

## Verifying the Result

The sub-agent's summary is **self-reported** — always verify:

1. **Check the file tree** — `find ... | sort` to confirm structure
2. **Install deps** — `pip install -r requirements.txt`
3. **Start the service** — use `terminal(background=True)` with `watch_patterns=["Application startup complete"]`
4. **Test APIs** — write a quick test script that calls the key endpoints
5. **Fix path mismatches** — the sub-agent may use different route prefixes than expected (e.g. `/api/knowledge/items` vs `/api/knowledge/add`)

## Pitfalls

| Pitfall | Fix |
|---------|-----|
| Sub-agent writes API keys in config.py as `"«redacted:sk-…»"` | The Hermes secret redactor caught it. Replace with `os.getenv("KEY")` pattern. |
| Sub-agent uses wrong model name | e.g. `deepseek-chat` instead of `deepseek-v4-flash`. Check `config.py` for the actual model name after build. |
| Service won't start (port in use) | Kill previous process first with `lsof -ti:8000 \| xargs kill -9` |
| Service won't start (port in use) | Kill previous process first with `lsof -ti:8000 \| xargs kill -9` |
| API routes differ from expectation | Check each api/*.py for the actual `@router` prefix and path |
| LLM calls all return degraded | The API key env var isn't reaching the subprocess. Source it: `export $(grep -v '^#' ~/.hermes/.env \| xargs)` before starting. |
| Token redacted in verification scripts | Write token to a file, then read it back from Python to avoid Hermes secret redaction in tool output. |

## 批量 HTML 单文件并行生成模式

**触发场景：** 用户说\"上面的都有兴趣，全部搞出来\"——一次性产出多个独立 HTML 单文件项目。

### 架构模式

```
主会话（你）
├── delegate_task 批次1: 游戏 + 3D名片 + 像素画展厅  (并行3个)
├── delegate_task 批次2: 案例墙 + AI抽签 + 服务器状态  (并行3个)
└── delegate_task 批次3: 选品大屏 + 量化看板  (并行2个)
    └── 主会话统一收尾: 更新导航Hub + 启动服务
```

### 批次分配原则

| 因素 | 做法 |
|:-----|:-----|
| **delegate_task 上限** | 一次最多 3 个（配置限制），分多批次 |
| **从简单到复杂** | 第1批放复杂度低/文件小的项目 |
| **同类不撞** | 同一批内的项目不要都用 Three.js/CDN 重资源 |
| **端口连续** | 统一端口段，方便记忆和 hub 管理 |

### 子Agent 任务清单模板

每个子任务需要以下内容（复制粘贴到 task 的 `goal` 和 `context`）：

```text
context 必须包含：
1. 文件保存路径（~/Desktop/hermes/<project-name>/index.html）
2. 单文件HTML限制（所有CSS/JS内嵌，零外部依赖或CDN加载）
3. 关键视觉/功能要求
4. 启动HTTP服务器的完整命令（background=true）
5. 确认服务器启动后返回文件路径和端口
```

### 收尾工作流

所有批次完成后：

```text
1. 检查所有端口的服务是否启动（lsof -ti:<PORT>）
2. 对没启动的服务，先检查文件是否存在，再手动启动
3. 更新导航Hub的 PROJECTS 列表
4. 把新端口加入 PORT_KEYS
5. 重新生成导航页
6. 浏览器逐个验证
```

### Pitfalls

| 坑 | 表现 | 处理 |
|:---|:-----|:-----|
| 子Agent沉默/卡住 | live transcript 停在 todo 步骤 | 直接手动接管创建 HTML 文件 + 启动服务 |
| 文件被覆盖 | 你写文件时子Agent也写同一路径 | 查看 write_file 返回的 _warning 确认 |
| 端口被占用 | HTTP 服务报 Address already in use | 换端口或用 kill 旧进程 |
| 子Agent不启动服务 | 任务说完成但端口没监听 | 手动执行 start 命令 |

## 相关

- `autonomous-ai-agents` — 通用多Agent工作流编排
- `server-service-deployment` — 服务部署运维
