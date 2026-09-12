# Memory Consolidation Technique

## When to Consolidate

- Agent seems to be "getting dumber" (context bloat symptom)
- Multiple contradictory entries exist (e.g., 阿里云 vs 腾讯云 server references)
- Memory usage exceeds **~80% of the live budget**（本机实测：memory 上限 5,000 chars / user 上限 3,000 chars）。**以 `memory` 工具返回的 `x/y` 为准**，别照抄这里或任何 skill 里写死的旧数字（旧文档曾写 2200/1375，早已失效）
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
| `memory` (personal notes) | ~2,000 chars | **5,000 chars**（`config.yaml` → `memory.memory_char_limit`） | > 80% full |
| `user` (user profile) | ~2,000 chars | **3,000 chars**（`memory.user_char_limit`） | > 90% full |

## Common Patterns Found

| Pattern | Example | Action |
|---------|---------|--------|
| Contradictory server info | 阿里云 vs 腾讯云 | Keep the latest version, remove the old |
| Repeated project detail | Project paths/stacks in 3+ entries | Merge into one compact entry |
| Session-specific procedures | "WeChat watchdog cron configured" | Move to skill, remove from memory |
| Old preferences superseded | Communication style notes from months ago | Keep latest, remove superseded |

## ⚠️ `replace` 替换整条，`old_text` 只做定位（会丢数据）

`memory(action='replace', old_text='片段', content='新文本')` = 用 `old_text` **找到那条**，然后把**整条内容换成 `content`**。不是「把片段替换成新文本」。

**实测事故（2026-09-12）**：想改 A 条目末尾的 6 个字，只传了 11 字的 `content` → 整条 195 字被覆盖，其余内容当场丢失，且当时没察觉。

**正确做法**
- `content` 必须是该条目的**完整新文本**：先把原文抄全，改完再提交
- 合并两条 → 用完整合并文本 `replace` 一条 + `remove` 另一条，放进同一个 batch（原子提交）
- 改完核对返回的 `entry_count` 与 usage，确认没有条目被意外吞掉

**应急恢复**：被覆盖的原文通常还在**当前会话的系统提示词**里（记忆每轮注入）→ 从那里抄回，用一次 `replace` 把完整内容写回去，再 `remove` 掉误建的那条。
