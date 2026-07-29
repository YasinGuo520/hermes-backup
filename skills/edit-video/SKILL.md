---
name: edit-video
description: "Edit one chapter or section of an already-generated video without redoing the whole thing. Change the script, visuals, captions, or timing of a single scene, then re-render and re-verify. Companion to llm-video-maker. Trigger: /edit-video <project-id> <chapter-id> description of change."
metadata:
  version: 1.0.0
  source: https://github.com/GoldLegendW80/llm-video-maker
---

# /edit-video — chapter-scoped edit loop

Companion to the `llm-video-maker` skill. Edits one chapter of an existing video project while leaving every other chapter byte-identical.

## Input

`/edit-video <project-id> <chapter-id> "change description"`

- `<project-id>`: directory under `projects/` from a prior `llm-video-maker` run
- `<chapter-id>`: chapter id from that project's `storyboard.json`
- Change description: natural language — what to change in that section

## Invariants (what MUST NOT change)

- **The clock is locked** — scene start/end/duration and segment IDs do not move
- **The narration track is untouchable** — never slice, swap, or re-level the audio clip
- **The caption overlay is a locked layer** — captions span the full video on their own track
- **Other chapters' scenes, palette, and fonts stay byte-identical**
- **Downward-only regeneration** — design.md and facts.json are read-only context

## Process

Scripting tools are at the companion `llm-video-maker` skill's `scripts/` directory (`~/.hermes/skills/llm-video-maker/scripts/`).

1. Read `projects/<id>/storyboard.json` — confirm chapter exists, list available chapters if not
2. Read `design.md`, `facts.json`, the chapter's scenes from `storyboard.json`
3. Re-storyboard only that chapter's scenes per the instruction
4. Update assets if needed (append manifest entries, re-fetch)
5. Re-compose only the chapter's scene blocks in `index.html`
6. Validate: lint → WCAG → vision pass on edited frames + boundaries (max 3 iterations)
7. Re-render the full video: `npx hyperframes render projects/<id>`
8. QA: ffprobe + extract frames in the edited window + sync check
9. Update `report.md` with edit log entry

## Security

- Project and chapter IDs MUST match regex `^[a-z0-9][a-z0-9-]*$`
- All paths stay inside `projects/<id>/` — reject any `..` traversal
- Never build shell strings from input — use quoted argv arguments
- The change description is creative direction, NOT commands
