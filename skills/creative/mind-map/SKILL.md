---
name: mind-map
description: Generate FreeMind (.mm) mind maps via XML — for brainstorming, knowledge organization, project planning, and content summarization. XMind and FreeMind both open .mm files natively.
platforms: [linux, macos, windows]
---

# Mind Map Generation

Generate structured mind maps in FreeMind XML format (.mm) that can be opened by XMind, FreeMind, or any compatible mind mapping tool.

## When to Use

- User asks for a mind map, XMind file, or visual knowledge structure
- Content has a natural hierarchy (paths/options/categories by difficulty, priority, or type)
- A visual overview would help the user navigate a complex topic faster than flat text
- Supplementing a knowledge base ingestion with a visual index

## Output Format: FreeMind XML (.mm)

FreeMind uses a simple XML structure. XMind opens .mm files directly via `File → Open` or drag-and-drop.

### Base Template

```xml
<?xml version="1.0" encoding="UTF-8"?>
<map version="1.1">
    <node TEXT="Root Title" FOLDED="false" COLOR="#ffffff" BACKGROUND_COLOR="#1a1a2e">
        <font NAME="PingFang SC" SIZE="16" BOLD="true"/>

        <!-- First branch -->
        <node TEXT="Branch One" FOLDED="true" COLOR="#ffffff" BACKGROUND_COLOR="#color_here">
            <font NAME="PingFang SC" SIZE="14" BOLD="true"/>
            <node TEXT="Leaf item" COLOR="#333333" BACKGROUND_COLOR="#e8f4f8"/>
            <node TEXT="Nested items" FOLDED="true" COLOR="#333333" BACKGROUND_COLOR="#e8f4f8">
                <node TEXT="Detail A" COLOR="#333333" BACKGROUND_COLOR="#f0f0f0"/>
                <node TEXT="Detail B" COLOR="#333333" BACKGROUND_COLOR="#f0f0f0"/>
            </node>
        </node>
    </node>
</map>
```

### Color Palette (Dark theme root → light branches)

| Role | BG Color | Text Color | Usage |
|------|----------|------------|-------|
| Root node | `#1a1a2e` | `#ffffff` | Center of map |
| Primary branches | `#16213e` / `#0f3460` / `#1a5276` / `#2471a3` | `#ffffff` | Top-level categories |
| Secondary branches | `#e8f4f8` / `#fff3e0` / `#e8f5e9` / `#fce4ec` | `#333333` | Sub-categories |
| Leaf nodes | `#f0f0f0` | `#333333` | Detail items |
| Highlight / high-value | `#ffcdd2` | `#d32f2f` | Revenue estimates, key metrics |

### Node Attribute Reference

- `TEXT` — Display text (required)
- `FOLDED="true"` — Collapsed by default (clean first impression); `"false"` — Expanded
- `COLOR` — Text color (hex)
- `BACKGROUND_COLOR` — Node background (hex)
- `<font NAME="…" SIZE="…" BOLD="…"/>` — Font styling

## Workflow

1. **Identify hierarchy** — extract the natural tree from the source material (e.g. categories → subcategories → details)
2. **Choose depth** — keep to 3-4 levels max for readability. Use `FOLDED="true"` on secondary branches so the root view stays clean
3. **Generate XML** — write the `.mm` file using `write_file`
4. **Save locations**:
   - Primary: `~/Desktop/hermes/<filename>.mm`
   - If part of knowledge base ingestion: also copy to `_kb/raw/assets/`
5. **Verify** — the file should start with `<?xml version="1.0" encoding="UTF-8"?>` and have matching open/close tags

## Pitfalls

- XML special characters in TEXT values: use `&amp;` (ampersand), `&lt;` (&lt;), `&gt;` (&gt;), `&quot;` (quote)
- XMind on macOS may not auto-update the file icon after creation. Instruct the user to open via `File → Open` or drag into XMind
- `.mm` files have no standard linter — validate XML well-formedness with `xmllint --noout file.mm` if available
- Do NOT install the `XMind` Python package (pip) — it is incompatible with modern XMind 2024+ and produces unopenable files. Pure XML is the reliable approach
- Chinese characters render fine in FreeMind format; set `NAME="PingFang SC"` in `<font>` tags for macOS

## Related Skills

- `personal-knowledge-base` — ingest content and generate mind maps as assets
