# Structured Reference Notes from Data Sources

A repeatable pattern for generating comprehensive, well-organized Obsidian reference notes from structured data sources (JSON, CSV, YAML, API responses, etc.).

## When to Use

You have a structured data source (large JSON file, CSV export, API response) and the user wants a readable Obsidian reference note documenting all entries — a lookup table they can browse in the vault.

## Workflow

### 1. Understand the data structure

Read a small sample — enough to see the schema, not the whole file. For large files that `read_file` truncates (~100K char limit), read the first ~50 lines to understand shape, then use Python to parse the raw file.

```python
# Quick structure peek
import json
with open('path/to/data.json') as f:
    data = json.load(f)
print(f'Records: {len(data)}')
print(json.dumps(data[0], indent=2)[:2000])
```

### 2. Group and categorize

Find the natural grouping key (e.g. `division`, `category`, `type`, `status`). Count records per group:

```python
from collections import Counter, OrderedDict
groups = Counter(item['group_key'] for item in data)
for k, v in sorted(groups.items()):
    print(f'{k}: {v}')
```

### 3. Generate the note

Write a standalone Python script that reads, groups, formats, and writes. Essential structure:

```
# 🏢 Title (中文)
> **N entries** across **M categories**.

## 🔍 Quick Reference
Usage instructions / navigation tips

## 📑 Table of Contents
- [[#anchor1|Section 1]] — N entries
- [[#anchor2|Section 2]] — N entries

## 📊 Overview
| Category | Count |
|----------|------:|
| Cat 1    | N     |

## anchor-name Section Name
| # | Name | Slug | Description |
|---|------|------|-------------|
| 1 | **Name** | `slug` | Description... |
```

### 4. Table formatting rules

- **Bold** names so they stand out in reading mode
- Backticks for slugs/identifiers (copy-friendly)
- Truncate descriptions to ~100 chars with `...`
- Escape pipe `|` in descriptions as `\\|`
- HTML anchors: remove hyphens (`game-development` → `#gamedevelopment`)

### 5. Writing to the vault

Resolve the vault path, write with `write_file` (not shell heredocs):

```python
import os
vault = os.environ.get('OBSIDIAN_VAULT_PATH',
                       os.path.expanduser('~/Documents/Obsidian Vault'))
```

## Pitfalls

- **Truncated read budget**: Don't try to read a 3.9MB file with `read_file`. Script the JSON parse directly — Python reads raw bytes, not formatted output.
- **Pipe characters**: Breaks markdown tables. Escape every `|` in data with `\\|`.
- **Long descriptions**: Truncate at ~100 chars. Full info is accessible via other means.
- **Divisions with hyphens**: HTML anchors strip hyphens. `"game-development".replace("-", "")` → `gamedevelopment`.
- **Cleanup**: Delete the temp generation script after use.

## Canonical Example

The **Agency Agents** note (`Agency Agents 专家角色库.md`):
- 269 agents from a 3.9MB JSON file
- 17 category sections
- TOC with wikilinks + overview table + per-category tables (name/slug/description/#
- Output: 465 lines, ~48KB
