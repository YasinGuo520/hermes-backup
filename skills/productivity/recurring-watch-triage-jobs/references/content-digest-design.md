# Content Aggregation Digest — job design (5-layer prompt)

> Job class: **daily/recurring push of aggregated content** (AI news, curated briefing, 变现日报, English daily drill). Same cron plumbing as watches/triage, different deliverable: the output is a *filtered digest*, not an alert.
> Live examples in this skill: `references/ai-news-agent-monetization-prompt.md`（AI资讯+变现）、`references/english-learning-format.md`（英语每日一练）。

## Five-layer prompt architecture

### Layer 1 — Role + mission
```
你是每日X全自动推送机器人，执行以下任务：
## 任务目标
采集并整理当日（今天/最新）X内容，按固定格式推送。
不得重复旧闻，不添加多余开场白结束语。
```

### Layer 2 — Multi-source search strategy (the part that decides quality)
A single search pool (e.g. only Chinese general web search) produces heavy daily overlap — one language's news has limited new items per day. Pin **three tiers, ≥2 sources each**:

| 层 | 源 | 为什么 |
|---|---|---|
| **海外** | Hacker News / Product Hunt today / GitHub Trending / Reddit（r/MachineLearning、r/SaaS）/ 海外科技媒体（TechCrunch、The Verge、Ars）/ 官方博客 | 补国内源空缺，避免内容撞车 |
| **国内** | **具体公众号/垂直媒体**（量子位、机器之心、新智元 → `site:mp.weixin.qq.com`）+ 36氪/虎嗅/钛媒体 + 领域社区（知乎/掘金） | 泛搜拿不到垂直号的内容 |
| **领域补充** | arXiv 当日论文、厂商官方博客（OpenAI/DeepMind/Anthropic） | 一手源、最不易被二手转述污染 |

2. 重要链接要**提取全文验证**，不能只看标题判断；仅保留权威媒体 + 官方发布 + 真实案例；彻底过滤营销软文、小道消息、重复内容、纯娱乐。

### Layer 3 — Cross-source dedup rules (must be in the prompt)
- 国内外撞车 → 选信息更全那条，标注「双源验证」
- 跨日重复 → 与昨/前天重复的跳过，标 [续] 不展开
- 同一事件换标题重复发 → 认出来只留一条

### Layer 4 — Fixed format (strict order, never deviate)
```
《今日XX汇总》YYYY-MM-DD
① 头条重点（N条）
② [分类]（N条）
③ ...
```
每条统一：`**标题**｜一句话核心摘要`（+ 链接）。**无开场白/结束语、无 emoji 堆砌、不用额外符号。**
带特殊元数据时逐条标注，例（变现类）：`**标题**｜核心摘要 + **【智能体】**工具名 + **【变现】**模式`。

### Layer 5 — Quality gate + output discipline
```
## 筛选标准（至少满足2条才保留）
- 有具体信息量（数字：参数/定价/用户数/收入）
- 对目标读者有参考价值
- 有可验证的源头（URL可点开）
- 角度新鲜（不是昨天炒过的冷饭）
## 输出规范
- 重点关键词加粗；篇幅适中；当天搜不到足够新内容时宁少勿滥，不凑数
```

## User content preferences (embed as hard ratios)

- 变现/赚钱类：**优先个人/小团队**，6-8 条里至少 4 条个人级；企业案例最多 1-2 条。
- 每条必须给出：**【智能体】**哪个工具 + **【变现】**哪种模式 + 具体收入数字（「月入 $1,400」而不是「可月入过万」）。
- 全部要「**拿来就能参考**」——可直接照做，不是理论。

## Delivery configuration

```
cronjob action='create' name="..." schedule="30 8 * * *"
  deliver="origin"                     # push to the originating chat
  enabled_toolsets=["web","terminal"]  # restrict tools, save tokens
```
- Schedule in **Beijing time (UTC+8)**；`enabled_toolsets` 不限制的话 cron agent 会加载全部工具（浪费 + 风险）。
- **首次必须手动验证再挂 cron**：`cronjob action='run' job_id=xxx`。

## Content sourcing fallbacks

| Tier | 用什么 | 注意 |
|---|---|---|
| 1 | `web_search` / `web_extract` | 后端是 ddgs 时是 search-only，抓 URL 必失败 |
| 2 | AnySearch MCP（`mcp__anysearch__search` / `extract`） | 单 query 超时不拖垮整批（try/except）；批量多 query 用 `execute_code` 最稳（直接 tool_call 易报 "arguments is not valid JSON"） |
| 3 | **curl RSS feeds**（→ `references/rss-feed-news-sourcing.md`） | 10 秒拿到带 pubDate 的新鲜料，不过 Cloudflare |
| 4 | curl GitHub API（trending/README base64） | `raw.githubusercontent.com` 在无头服务器常返回空白 |

## Server migration / cron handover

Cron jobs do **not** migrate between Hermes instances（本地 SQLite/state DB）→ 逐个 `cronjob action='create'` 重建；`~/.hermes/scripts/` 脚本手动拷；通道/凭据重新配置（微信扫码、飞书 token、`.env`）。迁移后逐个手动 run 一次验证。

## Pitfalls

1. **旧闻重复** — cron agent 不记得上次跑过什么 → prompt 必须写「不得重复旧闻」+ 跨日去重规则。
2. **企业案例过多** — 变现类显式约束比例（个人≥4 / 企业≤2）。
3. **收入数字模糊** — 强制给出具体数字格式。
4. **没验源** — 要求对重要链接提取全文验证，不能只看标题。
5. **凑数** — 写入「当天搜不到足够新内容时宁少勿滥」。
6. **工具全加载** — 不设 `enabled_toolsets` 会加载所有工具。
7. **`raw.githubusercontent.com` 空白** — 备用 GitHub API + base64。
8. **cron 里浏览器必超时** — 主路径设计成 terminal + curl。
9. **只有中文源 → 每天重复同样故事** — 必须分海外/国内/领域三层。
10. **「today」搜索返回旧闻/clickbait** — 单条命中不算证据，去真实媒体验 freshness（feed pubDate / `datePublished`）。
11. **国内 ddgs 超时 → 50 次搜索保护 → 空壳报告（`last_status=ok` 的假象）** — prompt 顶部注入搜索通道铁律；改完必须真跑一次并**检查输出文件体积**（空壳 ~21KB / 一行拒绝说明；健康 30KB+）。
