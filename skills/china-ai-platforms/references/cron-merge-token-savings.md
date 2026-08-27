# Cron 合并省 token（2026-08-27 实测）

**背景**：DeepSeek/硅基流动按前缀缓存计费——同一会话内连续轮次命中率 80%+，新会话首调只有 19-26%。每个新会话首调都要付 5-6 万 token 的 system prompt 行李（大部分全价）。把互不相关的同类 cron 任务合并进**一个会话**跑，只付一次首调，后续部分共享前缀高命中。

**实测数据**（usage.jsonl）：
- 长会话第 5 轮：输入 10 万，缓存命中 84.2%
- cron 新会话首调：命中率 19-26%
- 合并后估算：4 个独立 job（4 次首调 ≈ ¥0.43/天）→ 1 个合并 job + 1 个保留 job（≈ ¥0.23/天），输入费省 **40-50%**

## 触发场景

用户有多个每日 LLM cron 任务（如 8:00 英语 / 8:30 资讯 / 8:35 变现案例 / 8:55 GitHub）跑在同一个时段，各自开新会话。

## 流程

1. **读完整 prompt**：`cat ~/.hermes/cron/jobs.json`，提取要合并的 job 的 `prompt` 字段（注意是 `{"jobs":[...]}` 结构，字段名 `prompt` 不是 `prompt_preview`）
2. **构造合并 prompt**：一个自包含 prompt，按执行顺序分部分（第1部分/第2部分/第3部分），每部分嵌入原 prompt 全文。**加搜索共享规则**——第1部分搜过的 GitHub trending/Product Hunt/HN，后面部分直接复用不重复搜（省搜索也省输出）
3. **建合并 job**：`cronjob action=create`，schedule 用最早的时段，skills 带上所有原 job 的 skill（如 `monetization-case-daily-pipeline`），enabled_toolsets 取并集（web/terminal/file）
4. **暂停旧 job**（不要删）：`cronjob action=pause`——保留配置可回滚，不满意随时恢复
5. **保留 UX 关键 job 独立**：如英语每日一练是用户早上要单独练的，合并后会拖到 9 点才交付——这种保留单独跑

## 坑

- **单点失败**：合并后一个 job 挂了全挂——prompt 里必须写「某部分数据不足时保底输出（如 GitHub Trending 页面兜底），不能卡住拖垮其他部分」
- **交付时机**：合并 job 最终一次性交付全部报告（跑完才发），不是每部分单独发——用户会晚收到，且是一大坨
- **时长**：合并 job 跑 3 个部分要 20-30 分钟（原分开 4+6+4 分钟），要确保 9 点前跑完避开高峰价
- **旧 job 是 paused 不是 deleted**——这是回滚开关
- 合并 prompt 写文件留档（如 /tmp/merged_morning_prompt.txt），方便审查和复用

## 验证

`cronjob action=list` 确认新 job scheduled、旧 job paused；首跑后对比 usage 或账单确认命中率提升。
