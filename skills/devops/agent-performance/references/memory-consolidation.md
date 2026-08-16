# Memory Consolidation Technique

## When to Consolidate

- Agent seems to be "getting dumber" (context bloat symptom)
- Multiple contradictory entries exist (e.g., 阿里云 vs 腾讯云 server references)
- Memory usage exceeds ~60% of the 2,200-char budget
- User profile contains session-specific detail that's been superseded

## Consolidation Steps

### 1. Audit current entries

Use `memory` tool with `action='add'` and a throwaway placeholder to see what's currently stored. Note:
- Duplicate/redundant entries saying the same thing
- Contradictory entries (old info superseded by new corrections)
- Verbose entries that can be compressed (e.g., 3+ sentences → 1)

### 2. Plan the consolidation

Identify:
- **Remove**: entries that are superseded, contradictory, or session-specific detail
- **Keep**: entries that are still accurate and useful
- **Merge**: related entries that can be compressed into one

### 3. Execute in a single batch

Use `memory(action, target, operations=[...])` with multiple operations in one call. Batch is atomic — all or nothing. This avoids partial states.

### 4. Target sizes

| Store | Target size | Max | Signal to consolidate |
|-------|------------|-----|----------------------|
| `memory` (personal notes) | ~500 chars | 2,200 chars | > 60% full |
| `user` (user profile) | ~700 chars | 1,375 chars | > 80% full |

## Common Patterns Found

| Pattern | Example | Action |
|---------|---------|--------|
| Contradictory server info | 阿里云 vs 腾讯云 | Keep the latest version, remove the old |
| Repeated project detail | Project paths/stacks in 3+ entries | Merge into one compact entry |
| Session-specific procedures | "WeChat watchdog cron configured" | Move to skill, remove from memory |
| Old preferences superseded | Communication style notes from months ago | Keep latest, remove superseded |
