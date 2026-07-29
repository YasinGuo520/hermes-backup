---
name: scheduled-content-pipeline
description: "Use when setting up cron jobs that regularly aggregate web content, filter, format, and push structured reports to the user. Covers multi-source search strategy, filtering criteria, fixed-format output templates, and delivery configuration."
version: 1.0.0
author: Yasin's AI副驾驶
license: MIT
metadata:
  hermes:
    tags: [cron, content-pipeline, daily-briefing, automation]
    related_skills: []
---

# Scheduled Content Pipeline

## Overview

This skill captures the pattern of building **daily cron jobs that aggregate, verify, filter, format, and push structured content reports** to the user. Used for setups like daily AI news digests, curated industry briefings, or any recurring content roundup requiring web research + structured output.

The user already runs this pattern for:
- AI英语每日一练 (daily English snippet from trending AI docs, 8:00 AM)
- 今日AI资讯含Agent变现实战 (daily AI news + Agent monetization, 8:30 AM)

## When to Use

- User asks: "set up a daily X push" / "定时推送Y" / "每天早上Z点推给我"
- Deliverable is a cron job that **sources, filters, and formats** external content — not just a static reminder
- Output has a **fixed-format structure** (multiple sections, annotations per item)

**Do NOT use for:**
- Simple reminders — use basic cron with no web search
- Static daily tips without research
- One-shot content without recurring delivery

## Five-Layer Prompt Architecture

Every scheduled content pipeline prompt is composed of five layers:

### Layer 1: Role + Mission
```
你是每日X全自动推送机器人，执行以下任务：
## 任务目标
采集并整理当日（今天/最新）X内容，按固定格式推送。
不得重复旧闻，不添加多余开场白结束语。
```

### Layer 2: Search Strategy — Multi-Source Coverage (CRITICAL)

**Why this matters:** A single search pool (e.g. only Chinese general web search) produces heavy daily overlap — AI news in one language has limited new items per day. The solution is **structured multi-source categories** mixing domestic + overseas platforms.

```
## 信息采集步骤 — 多源并行

### 必须覆盖以下三个方向（每个方向至少搜2个源）：

**① 海外源（补国内源的空缺，避免内容撞车）**
- Hacker News AI → 直接搜 `site:news.ycombinator.com AI` 或用 buzzing.cc（中文翻译版）
- Product Hunt 今日 → 搜 `site:producthunt.com today AI` 或直接看首页
- GitHub Trending → 搜 `GitHub trending repositories today AI`
- Reddit → `site:reddit.com/r/MachineLearning top day`、`site:reddit.com/r/SaaS`
- 海外AI博客 → TechCrunch, The Verge, Ars Technica, The Rundown AI, TLDR AI

**② 国内源（精确到公众号/垂直媒体，不只是通用网搜）**
- 公众号文章 → `site:mp.weixin.qq.com 量子位 AI`、机器之心、新智元
- 36氪/虎嗅/钛媒体 → `site:36kr.com AI`、`site:huxiu.com AI`
- AI创业投资 → 海外独角兽、Founder Park
- 工具/消费级 → 少数派、APPSO
- 知乎AI热榜 → `site:zhihu.com AI`

**③ 领域补充（可选项）**
- arXiv当日论文 → `site:arxiv.org AI` + 当天日期
- 官方博客 → OpenAI/Google DeepMind/Anthropic/Meta AI官方

2. 重要链接 → web_extract 提取全文验证，不能只看标题判断
3. 仅保留：权威媒体 + 官方发布 + 真实案例
4. 彻底过滤：营销软文、小道消息、重复内容、纯娱乐
```

### Cross-Source Dedup Rules（必须写进prompt）

同一事件出现在多个源时：
- 国内外撞车 → 选信息更全那条，标注"双源验证"
- 跨日重复 → 和昨/前天重复的内容跳过，标[续]不展开
- 同一事件换标题重复发 → 认出来只留一条

### Quality Gates（宁少勿滥）

```
## 筛选标准（至少满足2条才保留）
- ✅ 有具体信息量（数字：参数/定价/用户数/收入）
- ✅ 对创业者/开发者有参考价值
- ✅ 有可验证的源头（URL可点开看）
- ✅ 角度新鲜（不是昨天炒过的冷饭）

## 输出规范
- 宁可5条好料不要10条水货
- 无开场白/结束语，直接给内容
```

### Layer 3: Fixed Format Structure (strict order, never deviate)
```
## 固定排版结构（顺序不可更改）
标题：《今日XX汇总》

① 头条重点（N条）
每条格式：**标题**｜一句话核心摘要

② [Section Name]（N条）
每条格式：**标题**｜一句话核心摘要

③ ...
```
Rules: consistent per-item format (bold title | summary), no emoji clutter, no extra symbols, direct output with no 开场白 or 结束语.

### Layer 4: Domain-Specific Annotation
When content has special metadata, annotate per item. Example for Agent monetization:
```
每条格式：**标题**｜核心摘要 + **【智能体】**工具名 + **【变现】**模式
```

### Layer 5: Quality Gates
```
## 输出规范
- 重点关键词用 **加粗**
- 篇幅适中（合计X-Y条）
- 当天搜不到足够新内容时，宁少勿滥，不凑数
- **核心要求**：[domain-specific quality bar]
```

## USER CONTENT PREFERENCES (must embed)

From session history with Yasin:

1. **变现/赚钱 section**: prioritize **personal/small-team** over enterprise. At least **4 out of 6-8 items** must be individual-level.
2. Each item must specify: **【智能体】** which tool + **【变现】** which model + concrete earning number.
3. Enterprise cases: max **1-2** per section.
4. Everything must be **"拿来就能参考"** — immediately actionable, not theoretical.
5. "写清楚XX用XX工具通过X方式赚了多少钱" — not vague claims like "可月入过万" but specifics like "月入$1,400".

## Delivery Configuration

```
cronjob action='create' name="..." schedule="30 8 * * *"
  deliver="origin"                   # push to current chat
  enabled_toolsets=["web","terminal"]# restrict tools, save tokens
```

- Schedule in **Beijing time** (UTC+8)
- `enabled_toolsets=["web","terminal"]` prevents loading unnecessary tools
- For the first run, manually verify before leaving on cron: `cronjob action='run' job_id=xxx`

## Server Migration / Cron Handover

When moving from one Hermes instance to another (e.g., local Mac → cloud server), cron jobs do **NOT** migrate automatically. They live in the local SQLite DB and must be re-created on the new server.

### Migration Checklist

- [ ] List existing cron jobs on the OLD server: `cronjob action='list'`
- [ ] For each job, capture: name, schedule, prompt, skills, enabled_toolsets, deliver target
- [ ] On the NEW server, re-create each job: `cronjob action='create' ...`
- [ ] Run once manually to verify: `cronjob action='run' job_id=xxx`
- [ ] Check that `enabled_toolsets` are available (some tools like `weixin` gateway may not be installed on new server)
- [ ] If deliver target was `origin` on old server, ensure the new server's gateways (feishu/weixin) are connected

### Configuration That Does NOT Migrate

| Item | Why | How to Fix |
|------|-----|------------|
| Cron jobs | Stored in local state.db | Re-create with `cronjob action='create'` |
| Custom scripts in `~/.hermes/scripts/` | Files, not in DB | Copy files manually |
| Project files | Not part of Hermes | Copy to `~/projects/` or similar |
| Channels/connections | Tied to new server env | Re-authenticate (weixin QR, feishu bot token) |
| Auth credentials | Stored in `.env`/`auth.json` | Copy or re-enter API keys |

## Content Sourcing Fallbacks

Not all environments have `web_search` or `web_extract` tools. This tiered fallback strategy handles missing tools gracefully:

### Tier 1: web_search / web_extract (preferred)
Used when `enabled_toolsets` includes `"web"`:
- `web_search(query)` for discovery
- `web_extract(url)` for page content

### Tier 2: browser_navigate (fallback when web_search unavailable)
When `web_search` doesn't exist as a tool:
- Use `browser_navigate("https://www.google.com/search?q=...")` or similar search engine URL
- Follow up with `browser_snapshot()` to get text content
- **Known issue**: `browser_navigate` can fail with "CDP command timed out: Page.navigate" in headless/VNC environments
- When that happens, drop to Tier 3

### Tier 3: terminal + curl (when browser times out)
When both web tools and browser fail:
- **GitHub trending repos**: `curl -s "https://api.github.com/search/repositories?q=<query>&sort=stars&order=desc&per_page=5"`
- **GitHub README**: When `raw.githubusercontent.com` returns empty/blank (known CDN behavior), use the API endpoint and base64-decode:
  ```bash
  curl -s "https://api.github.com/repos/{owner}/{repo}/readme" | \
    python3 -c "import json,sys,base64; d=json.load(sys.stdin); print(base64.b64decode(d['content']).decode())"
  ```
- **News sites**: `curl -s --max-time 10 "https://news.ycombinator.com/"` (may need custom parsing)
- **Search engines**: `curl -s "https://html.duckduckgo.com/html/?q=<query>"` (returns HTML)
- Always set `--max-time 10` to avoid hanging

## Common Pitfalls

1. **Old news repeated.** Cron agent has no memory of past runs. Prompt must say "不得重复旧闻" — trust the agent to search today's content.
2. **Too many enterprise examples.** For 变现 sections, explicitly constrain ratio (个人级≥4, 企业级≤2).
3. **Vague earnings.** Force concrete numbers in the prompt — not "可月入过万" but specify the format.
4. **No source verification.** Force `web_extract` on important links to verify claims.
5. **Over-stuffing.** "当天搜不到足够新内容时，宁少勿滥，不凑数" prevents inventing or rehashing old content.
6. **All tools loaded.** Without `enabled_toolsets`, cron agent loads every tool — wasteful and risky.
7. **raw.githubusercontent.com returns blank.** This CDN endpoint often returns empty responses from headless servers. Always have the GitHub API + base64 workaround ready as a fallback.
8. **browser tools timeout in cron.** Browser tools (browser_navigate, etc.) are unreliable in cron/background sessions that lack a real display server. Design content pipelines to work with terminal + curl as the primary path, not the browser.
9. **Chinese-only search causes repetition.** Without海外 sources, the agent rehashes the same ~3 domestic stories every day. Always structure search into海外 + 国内 + domain-specific tiers (see Layer 2).

## Verification Checklist

- [ ] Prompt has all 5 layers (Role, Search, Format, Annotation, Quality)
- [ ] Chinese + English search queries included
- [ ] 变现 section has personal-level ratio enforced (≥4 personal, ≤2 enterprise)
- [ ] Concrete earning numbers required
- [ ] Tool and monetization model annotated per item where relevant
- [ ] Output format specifies: no greetings/closings, bold for keywords
- [ ] "宁少勿滥" fallback rule included
- [ ] `enabled_toolsets` restricted to `["web","terminal"]`
- [ ] Schedule is Beijing time (UTC+8)
- [ ] Run manually once to verify output before leaving on cron

See `references/ai-news-agent-monetization-prompt.md` for the full agent monetization prompt template, and `references/english-learning-format.md` for the English-learning daily snippet output format.