---
name: skill-creator
description: 创建/编写 Hermes Skill：SKILL.md 结构、frontmatter 规范、质量原则。
---

# Skill Creator（Skill 编写与创建）

当你发现一个重复出现的工作流要固化成 Skill，或要修改现有 Skill 时使用。覆盖两条路径：**用户级**（`~/.hermes/skills/`，`skill_manage` 创建）和 **in-repo**（随 hermes-agent 包发布的 `skills/<category>/<name>/SKILL.md`，write_file + git）。

## 两条创建路径

| 路径 | 位置 | 创建方式 | 适用 |
|------|------|---------|------|
| 用户级 | `~/.hermes/skills/<maybe-category>/<name>/SKILL.md` | `skill_manage(action='create')` | 个人技能，不随包分发 |
| in-repo | `/path/to/hermes-agent/skills/<category>/<name>/SKILL.md` | `write_file` + `git add` + commit | 要随 hermes-agent 发布给所有人 |

⚠️ `skill_manage(action='create')` **不会**写到 in-repo 树。in-repo 用 write_file；小修改可用 `skill_manage(action='patch')`。

## Required Frontmatter（校验硬性要求）

源：`tools/skill_manager_tool.py::_validate_frontmatter`：

- 文件**第一个字节就是 `---`**（前面不能有空行/BOM）
- 以 `\n---\n` 闭合再进正文
- 是合法 YAML mapping
- `name` 必填：小写+连字符，≤64 chars
- `description` 必填：≤1024 chars。**系统提示词索引只显示前 57 chars + "..."**，触发词类必须塞进前 57 字窗口，用 "Use when <trigger>." 或同等句式开头
- 正文非空

建议补齐（不强制但同行都有）：`version` / `author: Hermes Agent` / `license: MIT` / `metadata.hermes.{tags, related_skills}`。

```yaml
---
name: my-skill-name
description: Use when <trigger>. <one-line behavior>.
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [short, descriptive, tags]
    related_skills: [other-skill]
---
```

## Size Limits

- description ≤ 1024 chars（强制）；前 57 chars 出现在系统提示词索引
- 整个 SKILL.md ≤ 100,000 chars（强制，~36k tokens）
- 优秀体积 8-14k chars；超 20k 就该把分支细节拆进 `references/*.md`

## 结构模板

```
# <Title>
## Overview          — 一两段：是什么、为什么
## When to Use       — 触发词列表 + "Don't use for:" 反触发
## <主题章节>          — 速查表 / 精确命令 / Hermes 配方
## Common Pitfalls   — 编号的坑+修法
## Verification Checklist — 勾选式验收
## One-Shot Recipes（可选）
```

## 写作质量原则（每条都要过）

1. **为流程可预测性优化**：这一行会不会改变 Agent 行为？不改变就删。
2. **控制上下文负担**：description 每个 turn 都付费，聚焦触发类，细节进正文/references。
3. **信息分层**：常用步骤进 SKILL.md；分支/大块资料进 `references/`、`templates/`、`scripts/`，按需引用。
4. **步骤带完成标准**：每步说清怎么算做完（可检查、尽量穷尽）。
5. **规则就近存放**：定义、坑、示例、验证放一起，不要散落。
6. **用强引导词**：用模型已懂的概念（"tight loop"、"root cause"）省 token。
7. **去重**：同一含义只留一个出处；不改行为的句子删掉。
8. **防提前完成**：Agent 容易跳过的步骤，先强化该步的完成标准。

常见质量失败：**提前完成**（活没干完就move on）/ **重复**（同规则多处出现后漂移）/ **沉积**（只加不删的旧行）/ **臃肿**（常显内容过多，分支应放 references）/ **无操作散文**（"要小心"、"要彻底"——改成可检查的完成标准或强引导词）。

## 完整工作流（in-repo 版）

1. **先看同行**：`ls skills/<category>/`，读 2-3 个同行 SKILL.md 对齐风格。
2. **查校验约束**：不确定时看 `tools/skill_manager_tool.py`。
3. **起草**：write_file 到 `skills/<category>/<name>/SKILL.md`。
4. **本地校验**：
   ```python
   import yaml, re, pathlib
   content = pathlib.Path("skills/<category>/<name>/SKILL.md").read_text()
   assert content.startswith("---")
   m = re.search(r'\n---\s*\n', content[3:])
   fm = yaml.safe_load(content[3:m.start()+3])
   assert "name" in fm and "description" in fm
   assert len(fm["description"]) <= 1024
   assert len(content) <= 100_000
   ```
5. **git add + commit**。
6. **注意**：当前会话的 skill 加载器有缓存——新 skill 要新会话才可见，`skill_view`/`skills_list` 看不到是正常的。

## 编辑现有 Skill

- 小改（typo/加坑/收紧触发）：`skill_manage(action='patch', name=..., old_string=..., new_string=...)`
- 大改：write_file 整个 SKILL.md 或 `skill_manage(action='edit')`
- 加支持文件：`skill_manage(action='write_file', file_path='references/<x>.md')`（限 references/templates/scripts/assets 子目录）

## Common Pitfalls

1. **in-repo 用 `skill_manage(action='create')`** → 写到了 `~/.hermes/skills/` 而不是 repo 树。用 write_file。
2. **`---` 前有空白/BOM** → 校验失败（`content.startswith("---")`）。
3. **description 太泛 / 触发词埋在 57 字之后** → 索引截断丢路由信号。好：`Use when debugging Hermes skill discovery failures.`；坏：`This skill contains detailed guidance for agents working on Hermes skill discovery failures.`
4. **缺 author/license/metadata** → 不强制但显得半成品。
5. **重复造轮子** → 创建前先 `ls skills/<category>/` 看同行，优先扩展现有 skill 而不是造窄兄弟。
6. **指望当前会话立刻看到新 skill** → 加载器会话开始时初始化，新会话或精确路径 `skill_view` 才可见。
7. **沉积** → skill 应该越改越短/越准；加规则时删掉被取代的旧表述。
8. **无操作散文** → "be careful"/"be thorough" 不改变行为，换成可检查的完成标准。
9. **related_skills 引用仅用户级存在的 skill** → 你自己能用，别人 clone repo 后失效。in-repo 只链 in-repo。

## Verification Checklist

- [ ] 文件位置正确（用户级 `~/.hermes/skills/` 或 in-repo `skills/<category>/`）
- [ ] frontmatter 从字节 0 开始 `---`，`\n---\n` 闭合
- [ ] name（≤64 小写连字符）/ description（≤1024，触发词在前 57 字内）
- [ ] 总长 ≤100k chars（目标 8-14k）
- [ ] 结构：Overview → When to Use → 正文 → Pitfalls → Verification Checklist
- [ ] 每步有可检查的完成标准
- [ ] 大块/分支内容已拆进 references/templates/scripts
- [ ] 无 no-op 散文、无重复规则
- [ ] in-repo 已 `git add` + commit
