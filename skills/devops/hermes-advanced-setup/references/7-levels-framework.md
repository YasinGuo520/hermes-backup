# 7-Level Hermes Agent Framework Reference

**Source:** David Ondrej, "100 hours of Hermes Agent lessons in 46 minutes" (May 2026)
**Video:** https://www.youtube.com/watch?v=G47mnkGkYwQ
**Community context:** 133K+ GitHub stars at time of publication. Framework used to build Vectal ($155K ARR startup, $6-10K/mo API costs).

## The Framework

The 7 levels are **additive and cumulative** — each level assumes the one below it is stable. Users stop at whatever level serves their needs.

## Full Level Details

### Level 1 — VPS Deployment
**Goal:** Give Hermes its own always-on computer.

- Spin up Ubuntu instance (minimum 4GB RAM, 8GB recommended)
- Provider choice: Hostinger (David uses), Tencent Cloud (Yasin uses), AWS Lightsail, etc.
- Install: `curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash`
- Outcome: Agent runs 24/7, independent of user's laptop, isolated from personal machine

### Level 2 — Messaging Integration
**Goal:** Remote control from any device, no SSH needed.

- Create Discord bot (video demo) or Feishu/QQ/Telegram bot
- Configure gateway: `hermes gateway setup`
- Outcome: Send tasks from phone in 5 seconds, built-in audit trail in chat history

### Level 3 — Curator
**Goal:** Token cost control — prevent context bloat from auto-generated skills.

- Config: `curator.consolidate: true`
- Compacts auto-generated skills, marks stale ones, deletes long-unused
- Outcome: Significant API cost reduction for always-on agents
- David's context: $6-10K/mo API budget — Curator is essential at that scale

### Level 4 — GitHub Backup
**Goal:** Insurance against disk failure / accidental config loss.

**Two approaches:**

**A. Community script approach (no-agent, zero LLM cost):**
- Private GitHub repo + fine-grained PAT (contents: read/write)
- Bash script syncs `config.yaml`, `SOUL.md`, `skills/`, `memories/`, `cron/`
- Secrets handled: `.env` and `auth.json` templated (values stripped)
- Safety: script enforces private repo via GitHub API check
- Restore: clone repo, copy files back, recreate `.env` from template

**B. Built-in `hermes backup` (official, portable archive):**
- `hermes backup` → produces `.tar.zst` with config, skills, memories, sessions
- Secrets redacted by default; `--include-secrets` for full migration
- `hermes import` for restore with interactive conflict resolution
- Does NOT need GitHub (can back up to local disk or SCP target)

### Level 5 — Kanban Board
**Goal:** Visual multi-agent task orchestration + observability.

**Setup:**
```bash
hermes kanban init        # creates ~/.hermes/kanban.db
hermes dashboard           # visual board in web UI
# Gateway dispatcher auto-runs (60s tick) — no extra service
```

**Core concepts:**
- Board → Task → Link → Comment → Workspace
- Status flow: triage → todo → ready → running → blocked → done → archived
- Worker lifecycle: spawn → `kanban_show()` → work → `kanban_complete()` / `kanban_block()`
- Orchestrator pattern: decompose goal → assign child tasks → link dependencies → step back
- Goal-mode cards: auto-judge loop keeps worker going until acceptance criteria met
- Multi-board support: separate projects in isolated queues

**Use cases:**
- Research triage: parallel researchers + analyst + writer, human-in-the-loop
- Scheduled ops: recurring briefs building a journal over weeks
- Engineering pipelines: decompose → implement → review → iterate → PR
- Fleet management: one specialist managing N subjects

### Level 6 — Holographic Memory
**Goal:** Structured long-term fact storage with vector retrieval.

**Setup:**
```bash
hermes memory setup holographic
# No external service required — local SQLite
```

**Capabilities:**
- FTS5 full-text search
- Entity-aware retrieval (probe: all facts about X)
- Compositional queries (reason: facts connected to X AND Y)
- Trust scoring with feedback mechanism (+0.05 helpful, -0.10 unhelpful)
- Contradiction detection — finds conflicting facts
- `auto_extract: true` for session-end automatic fact extraction

**Comparison with other memory providers:**
| Provider | Storage | Cost | Dependencies | Standout Feature |
|----------|---------|------|-------------|-----------------|
| Holographic | Local SQLite | Free | None | Zero deps, trust scoring |
| Honcho | Cloud | Paid | honcho-ai | Dialectic user modeling |
| Hindsight | Cloud/Local | Free/Paid | hindsight-client | Knowledge graph + synthesis |
| Mem0 | Cloud/Self-hosted | Free/Paid | mem0ai | LLM auto-extraction |
| Supermemory | Cloud/Self-hosted | Free/Paid | supermemory | Context fencing |

### Level 7 — MCP Server
**Goal:** Transform Hermes from tool to infrastructure — expose as backend for other AI agents.

- Claude Code, Codex, Cursor, Pi Agent connect via MCP protocol
- Heavy reasoning stays on VPS; IDE becomes thin client
- David's stack: Vectal runs fully on this pattern

**When to skip:** User doesn't use Claude Code/Codex/Cursor locally.

## User Profiles

| User Type | Recommended Stop Level | Reason |
|-----------|----------------------|--------|
| Chat-based assistant user | Level 2 | Just needs remote control |
| Solo builder with API budget | Level 3 | Cost control matters |
| Any user with server config | Level 4 | Insurance, near-zero cost |
| Multi-project orchestration | Level 5 | Visibility + coordination |
| Long-running multi-stream user | Level 6 | Cross-session recall |
| Developer with IDE agents | Level 7 | Delegation pattern |

## Cost Notes

- David Ondrej: $6-10K/mo API cost, $155K ARR startup (Vectal)
- Levels 1-6 can run on $4-12/mo VPS + ~$100-200/mo API if using cheap models (DeepSeek Flash)
- Curator (Level 3) saves 10-30% on token costs depending on usage pattern
- Holographic memory (Level 6) adds retrieval token cost but reduces re-context overhead
