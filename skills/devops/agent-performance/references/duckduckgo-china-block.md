# DuckDuckGo 中国限流问题

## 症状

```
web_search 返回：DuckDuckGo search timed out after 30s
日志：ddgs.ddgs: Error in engine brave/google/yahoo/startpage: TimeoutException
```

## 根因

从中国大陆服务器访问 DuckDuckGo 的各引擎后端（brave、google、yahoo、startpage、grokipedia、wikipedia）均被限流或超时。这不是临时故障，是持续性问题。

## 影响范围

- `web_search` 工具超过一半调用会超时（30秒等待）
- 超时后 Agent 只能凭训练数据回答 → 答不准、绕圈子
- 整体响应时间被拉长（每次搜索拖30秒）

## 临时修复（无需重启）

1. **不用 web_search**，改用 MCP 搜索（AnySearch）
2. AnySearch 免费额度耗尽时去 https://www.anysearch.com 充值
3. 如果要用 web 插件，考虑付费的 Tavily / Exa / Firecrawl

## 怎么确认当前搜索是否健康

```bash
# 查最近搜索超时次数
grep "timed out" ~/.hermes/logs/agent.log | wc -l

# 查 MCP 搜索状态
hermes mcp list
hermes mcp test anysearch
```
