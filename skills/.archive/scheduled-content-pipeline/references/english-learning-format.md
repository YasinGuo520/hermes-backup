# AI 英语每日一练 — 输出格式模板（2026-08 现行版）

Output template for the daily English learning cron job. The cron prompt requires: ① web_search today's trending AI tool/project/news (English query), ② 3-5 English sentences with source link, ③ 2-3 sentence Chinese summary, ④ 2-3 fill-in-the-blank sentences for listening/grammar practice.

## Output Format (exact structure — cron prompt enforces this)

```
---
# AI英语每日一练
**Topic**: <English topic name>
**Date**: YYYY-MM-DD

---

## 📰 English Intro (3-5 sentences)
<3-5 grammatically correct, medium-difficulty English sentences>

**Source**: [<Outlet> — <Headline>](<URL>) (<date>, by <author>)

## 🇨🇳 中文总结
<2-3 clear conversational sentences>
**生词**：word 释义 | word 释义 ...

## ✍️ 填空练习 (Fill in the blanks)
1. <sentence with ____ blank — target keyword or preposition/collocation>
2. ...
3. ...

<details>
<summary>答案</summary>

1. **answer**（释义）— 简短说明（介词搭配/词形等易错点）
2. ...
3. ...

</details>

**今天能记住的一个搭配**：<one high-value collocation with example, e.g. work on — I'm working on a new project.>
```

## Formatting Rules

- **Topic 必须新鲜**：today/yesterday 的真实新闻，经权威媒体验证，绝不写旧闻或编造
- **英文**：语法正确、难度适中（雅思 6-7 水平），3-5 句
- **中文总结**：清晰口语化 2-3 句 + 生词表（带中文释义）
- **填空练习**：2-3 句，每句挖 1-2 个空，优先挖关键词（acquisition）或介词搭配（work __ → on）；答案放 `<details>` 里并给一句易错点说明
- **搭配提示**：给一个用户当天能直接套用的短语，不要方法论
- **词汇优先级**：技术术语 > 高频动词 > 其他

## Content Sourcing — 新鲜度验证流程（CRITICAL，2026-08 实战总结）

### 问题：web_search 搜 "today" 返回旧闻/垃圾
Query 如 "trending AI tool today" / "OpenAI today" 会混入大量过时文章（GPT-4 Turbo 时代、o3-mini 发布）和不可验证的 AI 生成 clickbait（典型：LinkedIn pulse 上编造的 "GPT-5.4" 类文章）。**绝不轻信单条搜索结果，写之前必须验证。**

### 已验证可行路径：curl The Verge AI feed
openai.com/news 对 curl 和 browser_navigate 都被 Cloudflare 拦截（curl 返回 cf_chl JS challenge，浏览器显示 "Just a moment..."）——**别在它身上浪费时间**。

```bash
# 1) 抓 AI feed，带浏览器 UA
curl -sL --max-time 25 -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36" \
  "https://www.theverge.com/ai-artificial-intelligence" -o /tmp/verge_ai.html
# 2) 解析 h2 标题：每行自带 作者+日期+标题（如 "Emma Roth Aug 14 Cursor is officially part of SpaceX"）
grep -oE '<h2[^>]*>.*?</h2>' /tmp/verge_ai.html | sed -E 's/<[^>]+>//g' | head -20
# 3) 拿文章 URL
grep -oE 'href="[^"]*<keyword>[^"]*"' /tmp/verge_ai.html | sort -u
# 4) 抓文章并验证日期+摘要
curl -sL --max-time 25 -A "<browser UA>" "<article URL>" | python3 -c "
import re, html, sys
raw = sys.stdin.read()
m = re.search(r'\"datePublished\":\"([^\"]+)\"', raw)
if m: print('DATE:', m.group(1))
m = re.search(r'<meta name=\"description\" content=\"([^\"]+)\"', raw)
if m: print('META:', html.unescape(m.group(1)))
"
```

`datePublished` 确认新鲜度（当天/昨天），meta description 即官方摘要，可直接作为英文介绍的事实基础。重磅消息（如 "$60B 收购"）必须等权威媒体确认后再写。

### 反 clickbait 规则
LinkedIn/pulse 和大量 Medium 的 "新版 GPT" 文章常是 AI 生成或纯编造。在真实媒体（The Verge / TechCrunch / Ars Technica）上查不到 datePublished 的，一律丢弃。

### 主路径：AnySearch MCP（2026-08-21 实战验证 — DDG 与 curl 双超时）
中国服务器上 DDG web_search 持续超时；本会话连 `curl news.ycombinator.com` 也 exit 28 超时。
**优先用 AnySearch MCP 搜索**（可靠、结果带日期）：
- `mcp__anysearch__search`（Path 1 general，直接 query，无需 get_sub_domains）
- 并行打多路 query 交叉验证：通用路（"trending AI news today OpenAI Anthropic Google announcement"）
  + 垂直路（"new AI model release this week August 2026"）
  + 具体产品验证路（"<candidate> release announcement"）
- 新鲜度校准源（带日期，能确认"本周到底发了什么"）：aireleasetracker.com、llm-stats.com/llm-updates、
  llmgateway.io/timeline、releasebot.io/updates/<vendor>

### 2026-08-29 增补：批量多路搜索优先 execute_code；tool_call 直调 AnySearch 传参易断
当日实战（英语每日一练 cron）：DDG 单发 web_search 30s 超时，但 **execute_code + hermes_tools.web_search 批量多 query 一把跑最稳**：
```python
from hermes_tools import web_search
for q in ["<candidate> release announcement", "<candidate> news <month year>", ...]:
    try:
        r = web_search(q, limit=6)
        for it in r.get("data", {}).get("web", []):
            print("-", it.get("title"), "|", it.get("url"))
    except Exception as e:
        print("ERR", q, e)
```
- 单 query 超时不拖垮整批（try/except 兜底），一次循环 4 路 query 3 路有结果
- 直接 tool_call 调 `mcp__anysearch__search`/`batch_search` 时，`arguments` 必须是最外层合法 JSON 对象；嵌套/字符串会反复报 "arguments is not valid JSON"，链路长（tool_search→tool_describe→tool_call）不如 execute_code 一条命令
- curl 抓官方 dev docs（例 ai.google.dev/gemini-api/docs/latest-model）可能返回空（重 JS/反爬），不要死磕；改打精确多角度 query，用 官方 blog 标题 + 科技媒体日期（9to5google/The Verge）+ 定价平台（OpenRouter/Artificial Analysis）三源交叉拼出 发布日期/定位/价格/上下文窗口，即可支撑英文介绍，无需抓到正文
- 当日走通案例：Gemini 3.7 Flash（2026-08-13 发布，官方 blog + 9to5google + OpenRouter 三源）——"most intelligent workhorse model for coding and agents"，intro 价 $0.75/1M in、$3.75/1M out（至 2026 年底），1M token 上下文、多模态，驱动 Gemini Spark 与 Google Search AI Mode。距查询日 16 天仍算"本月新模型"热点，满足新鲜度

### web_extract 后端限制（重要）
当前环境 `web_extract` 后端是 ddgs（search-only），抓 URL 直接报错：
"DuckDuckGo (ddgs) is a search-only backend and cannot extract URL content. Set web.extract_backend to firecrawl, tavily, exa, or parallel."
→ 替代：`mcp__anysearch__extract`。但它也抓不动 paywall/反爬站（axios.com、openai.com 均失败）。
→ OpenAI 发布信息用 releasebot.io/updates/openai 提取可行（内容全、带日期、无 Cloudflare 拦截）。

### 多候选选题启发式（英语学习素材）
多个新鲜候选并存时，选：①日期最新 ②贴近日常生活（词汇难度适中）③故事性强。
例：ChatGPT for Teens（8/18，家长控制+青少年学习，生活化）> GLM-5.3（8/14，benchmark 术语，对雅思 6-7 水平太技术）。

### 备用源（旧方法仍有效）
- HN Firebase API（topstories.json）→ 过滤 >200 pts 的 AI/技术内容（curl 优先，urllib 慢）
- GitHub README：用 API base64 解码，不用 raw.githubusercontent.com（已知 blank 问题）
- 文章正文提取：先删 script/style 块再剥标签，过滤 >30 字符行

## Cron Job Command

```bash
cronjob action='create' \
  name="AI英语每日一练" \
  schedule="0 8 * * *" \
  deliver="origin"
```

## Adapting

- 其他语言学习管道：改头部 emoji 即可（📰 新闻 / 🎧 听力）
- 填空练习结构对听力训练同样适用（挖空 → 播音频 → 填词）