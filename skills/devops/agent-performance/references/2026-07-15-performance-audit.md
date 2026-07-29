# 2026-07-15 Performance Audit Reference

## Context

Yasin reported "怎么感觉你有点变傻啦" — agent felt slower/dumber than usual.

## System State at Audit Time

| Metric | Value | Status |
|--------|-------|--------|
| CPU idle | 90.9% | ✅ |
| Memory | 1.6GB/3.6GB used, 643MB free | ✅ |
| Swap | 516MB/1.9GB used | ⚠️ High (reduced free memory) |
| Disk | 14GB/69GB (22%) | ✅ |
| Sessions in DB | 37 | Normal |
| DB size | 32MB | Normal |

## Issues Found & Fixed

| # | Issue | Config State Before | Fix |
|---|-------|--------------------|-----|
| 1 | **No compression** | Not configured | `compression.enabled: true`, threshold=0.50, target_ratio=0.20 |
| 2 | **No auxiliary models** | Not configured — defaulted to OpenRouter/Nous which had payment errors | All 3 aux providers set to `deepseek/deepseek-v4-flash` |
| 3 | **Memory bloated** | 1,335/2,200 chars (60%) | Trimmed to 617 chars, removed contradictions |
| 4 | **User profile bloated** | 1,350/1,375 chars (98%) | Trimmed to 688 chars |
| 5 | **No context_length** | Not configured | Set to 32,000 |
| 6 | **Language not set** | Not configured | `display.language: zh` |

## Deep Dive: Search Provider Diagnosis

Yasin corrected: "你之前调用的搜索不是Tavily这个吗" — confirming the agent had been using Tavily before.

### Key Finding: All Web Plugins Are "Not Enabled"

```
hermes plugins list | grep web-
→ web-tavily, web-exa, web-firecrawl, web-parallel, web-brave-free, web-ddgs — ALL "not enabled"
```

**This means:** The `web` toolset is enabled at the toolset level, but NO individual web backend plugin is registered. The `web_search` tool has ZERO active providers. Calls return empty (no provider error).

Previously (before plugin migration), Tavily was the default built into the web toolset. Post-migration, plugins must be explicitly enabled — but none were.

### Available Free Options

DDGS (DuckDuckGo) works without any API key:
```
from plugins.web.ddgs.provider import DDGSWebSearchProvider
DDGSWebSearchProvider().is_available() → True
```

### Search Priority Established

AnySearch MCP (4 tools: `search`, `batch_search`, `extract`, `get_sub_domains`) is the **primary** search. Falls back to `web_search` only when AnySearch returns no results.

### AnySearch Tool Description Bloat

AnySearch MCP tool descriptions are extremely verbose (~500+ words each for `search`, `batch_search`, etc.). Each time any search tool is called, the full tool schemas (including these massive descriptions) are injected into the system prompt. This contributes to context bloat. Mitigated by:
- Using `batch_search` instead of multiple `search` calls (fewer tool invocations)
- Compression keeping context manageable

## Skills Bloat

113 SKILL.md files in `~/.hermes/skills/` (84MB total). At session start, the system prompt enumerates all available skills — the descriptions alone consume significant context tokens. Not a direct performance issue but contributes to startup token usage.

## Log Clues

```
grep -i "error\|exception\|traceback\|timeout" ~/.hermes/logs/agent.log
```

Found repeated:
```
Auxiliary: marking openrouter unhealthy for 60s (payment / credit error)
Auxiliary: marking nous unhealthy for 60s (payment / credit error)
```

**Meaning**: Compression was enabled but the auxiliary provider (OpenRouter/Nous) had payment errors, so compression silently failed. This was the root cause.

## Key Commands Used

```bash
# Diagnostic
hermes doctor
hermes status --all
hermes mcp list
hermes mcp test anysearch
cat ~/.hermes/config.yaml
grep -i "error\|exception\|traceback" ~/.hermes/logs/agent.log | tail -20
grep -E "EXA_API_KEY|TAVILY_API_KEY|BRAVE_SEARCH_API_KEY|PARALLEL_API_KEY|FIRECRAWL_API_KEY|SEARXNG_URL" ~/.hermes/.env
python3 -c "
from agent.web_search_registry import list_providers, get_active_search_provider
print(f'Registered providers: {[p.name() for p in list_providers()]}')
print(f'Active search provider: {get_active_search_provider().name() if get_active_search_provider() else \"NONE\"}')
"

# Fixes
hermes config set compression.enabled true
hermes config set compression.threshold 0.50
hermes config set compression.target_ratio 0.20
hermes config set agent.context_length 32000
hermes config set auxiliary.compression.provider deepseek
hermes config set auxiliary.compression.model deepseek-v4-flash
hermes config set auxiliary.vision.provider deepseek
hermes config set auxiliary.vision.model deepseek-v4-flash
hermes config set auxiliary.session_search.provider deepseek
hermes config set auxiliary.session_search.model deepseek-v4-flash
hermes config set display.language zh
```

## Verification

```bash
hermes config check
# → All settings applied, no config version issues
```

**Important**: Config changes take effect on new session (`/reset`). The session that performed the audit still runs on old config.

## Recovery Path (next-use actions)

1. Optionally enable a free web fallback: `hermes plugins enable web-ddgs`
2. The skill was already updated to include all findings.
3. Needs a `/reset` to get the new config active.
