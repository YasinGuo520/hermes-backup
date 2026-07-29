# AI 英语每日一练 — 输出格式模板

This is the output template for the daily 8:00 AM English learning cron job. Produces a structured English snippet from trending AI content.

## Output Format (exact structure)

```
📖 【今日AI英语片段】
───────────────
🔤 原文
[2-3句英文原文，标明出处]
───────────────
🀄 中文翻译
[整段自然翻译，不机器味]
───────────────
📝 核心词汇

| 单词 | 词性 | 释义 | 例句 |
|------|------|------|------|
| word1 | n/v/adj | 中文释义 | 原文中用到的例子 |
| word2 | ... | ... | ... |
（列出3-5个词）
───────────────
💡 一句话用法提示
[教一个实用的造句模式，比如"你今天可以用xx句型来写Prompt"]
```

## Formatting Rules

- **原文来源**：必须是今日热门/真实内容，不编造
- **词性标记**：准确标注 n/v/adj/adv 等
- **中文翻译**：自然口语化，不要机器翻译腔
- **单词优先级**：技术术语 > 高频动词 > 其他词汇
- **词汇数量**：3-5个词，宁缺毋滥
- **用法提示**：给出一个可立即套用的句型，结合AI/编程场景
- **总长度**：控制在500字以内
- **分隔线**：用 `───────────────` 共15个全角横线

## Content Sourcing

Source content from **trending English-language AI content** published today:
- Trending GitHub repositories (README descriptions)
- AI papers (abstracts from arxiv)
- Tech blogs / announcements (OpenAI, Anthropic, Google, Meta)
- AI tool launch posts (Product Hunt, Hacker News)
- Technical documentation excerpts

### Recommended Sourcing Flow

**Step 1: Find trending content via HN Firebase API (most reliable)**

Use terminal + curl to fetch HN top stories — avoid browser tools (CDP timeout in cron):

```bash
# Get top story IDs
IDS=$(curl -s --max-time 8 "https://hacker-news.firebaseio.com/v0/topstories.json" | python3 -c "import json,sys; print(' '.join(str(i) for i in json.load(sys.stdin)[:10]))")

# Fetch details for each
for id in $IDS; do
  curl -s --max-time 5 "https://hacker-news.firebaseio.com/v0/item/$id.json" | \
    python3 -c "import json,sys; d=json.load(sys.stdin); print(f\"[{d.get('score',0)}pts] {d.get('title','')}\")"
done
```

**Known issue**: Python `urllib.request` is significantly slower than `curl` piped into `python3 -c` in this environment. Always use curl for the HTTP fetch.

**Step 2: Filter for AI/tech content with >200 points**

Look for: AI papers, new APIs, open-source tools, model releases, benchmarks. Skip general news, opinion pieces, non-tech articles.

**Step 3: Extract article body**

For HTML articles, strip tags with regex and filter for meaningful lines:

```bash
curl -s --max-time 15 "<URL>" | python3 -c "
import sys,re
html=sys.stdin.read()
# Remove script/style blocks first
html=re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
html=re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
text=re.sub(r'<[^>]+>', '\\n', html)
# Deduplicate and filter short lines
seen=set()
for l in text.split('\n'):
    l=l.strip()
    if len(l)>30 and l not in seen:
        seen.add(l); print(l)
"
```

For GitHub READMEs, use the GitHub API (base64 decode) instead of `raw.githubusercontent.com` (known blank-response issue):

```bash
curl -s "https://api.github.com/repos/{owner}/{repo}/readme" | \
  python3 -c "import json,sys,base64; d=json.load(sys.stdin); print(base64.b64decode(d['content']).decode())"
```

**Step 4: Pick 2-3 paragraphs** containing concrete technical claims (benchmark numbers, speed comparisons, accuracy metrics) — these produce the best vocabulary targets.

For each session:
1. Search for a trending AI tool/project/news (HN Firebase API)
2. Find an English article/README/blog from the results
3. Extract 2-3 sentences with substantive technical vocabulary (3-5 words worth learning)
4. Produce the structured output above

## Cron Job Command

```bash
cronjob action='create' \
  name="AI英语每日一练" \
  schedule="0 8 * * *" \   # 8:00 AM Beijing daily
  deliver="origin"
```

## Adapting

For other language-learning pipelines:
- Adjust the header emoji (📖 → 📰 for news, 🎧 for listening, etc.)
- Keep the 4-section structure (原文→翻译→词汇→用法提示)
- The core vocabulary table format is highly effective — maintain it
