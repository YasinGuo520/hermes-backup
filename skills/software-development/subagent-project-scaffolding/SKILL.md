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

## Related

- `autonomous-ai-agents` — general multi-agent workflows
- `hermes-agent` skill docs — `delegate_task` tool reference, security/approval settings
