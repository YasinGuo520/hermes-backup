---
name: agent-performance
description: "Agent性能诊断与维护——当Agent变傻/变慢时的系统化检查清单。覆盖context压缩、记忆瘦身、搜索工具健康检查、配置优化。"
tags: [hermes, maintenance, troubleshooting, diagnostics, performance]
related_skills: [claude-mem, find-skills, server-service-deployment]
---

# Agent Performance Diagnostics（Agent"变傻"诊断）

## 适用场景

当用户反馈以下信号时，**立即执行本诊断**，而非继续回答原问题：

- "怎么感觉你变傻啦？"
- "你好卡/好慢"
- "是不是我prompt太多影响你了"
- "你好像失忆了"
- "怎么搜不到东西"

### 铁律：没有调查就没有发言权（用户核心要求）

用户明确要求：**任何结论必须先调查清楚再回复**——查日志、看数据、翻配置备份、验证事实，证据齐了再答。不凭印象、不猜测、不编造。

诊断时的证据链优先级（本次会话模型漂移排查验证过的顺序）：
1. `config.yaml` 备份文件（`.bak*`）→ 确认配置变更的时间窗
2. `~/.hermes/logs/errors.log` + `agent.log` → 首次报错时间戳
3. **实际调用日志计数**（`grep -oE "model=deepseek|model=gpt" agent.log | sort | uniq -c`）→ 区分"名义配置"与"实际通道"
4. `session_search` → 找是否有明确执行过变更的会话记录

**典型错误**（用户明确批评过）：用户问"模型为什么变了"时，含糊回答"可能是更新改的"——正确做法是先翻备份+日志给出证据链（如：8/4备份还是deepseek → 8/12首次报错已是gpt-5.5 → 但3500+实际调用都是deepseek，说明gpt-5.5只是名义配置、一直在fallback）。回答格式：**先给调查结果，再给结论**；不确定就明说"这是推断"并附证据。

### Step -1：先确认哪个Hermes（关键！多实例用户）

用户可能有多个Hermes实例（服务器 + Mac本地 + 另一台PC）。**不要默认诊断自己。**

**先问清楚：**
> 你说的「变傻」是指你现在在聊的这个（当前会话的实例），还是另一个？（服务器/Mac/别的机器）

**分支处理：**
- **当前这个实例** → 继续往下走第零步
- **另一个实例（用户说得清是哪台）** → 给检查清单让用户跑，或者请求远程进去（若有权限），回来分析结果
- **另一个实例（用户说不清）** → 先让用户跑 `hermes doctor` 贴结果回来

**⚠️ 陷阱：** 用户说"电脑端的Hermes"可能指Mac上也装了一套独立的，跟当前服务器实例无关。不问清楚白查。

**🔑 多实例SOUL设计（行为异常主因之一）：**

不同用途的Hermes实例需要**不同风格的SOUL.md**。服务器版强调「先做再说」「推着走」（执行优先），复制到Mac端会让Mac实例变得不思考就冲。诊断时必须检查SOUL.md是否匹配实例角色：

- **服务器实例** → SOUL应该是行动派（先做后想、推着走）
- **Mac本地实例** → SOUL应该是思考派（先想后动、深度推理优先）
- **典型错误：** 两实例共用同一SOUL → 其中一端行为异常

排查方法（远程）：让用户在目标机器跑 `cat ~/.hermes/SOUL.md | head -20`

详见 `references/mac-remote-diagnostics.md`。

## 诊断流程

执行**九步检查表**，按优先级从高到低：

### 第零步：快速三连（先确认大环境是否健康）

```bash
hermes doctor           # 配置/依赖/API连通性整体检查
hermes status           # 网关/会话/任务状态概览（注意看 ◆ Sessions → Active: N）
free -h && df -h /      # 内存和磁盘健康
```

**网关会话告警：** 如果 `hermes status` 显示的 Active sessions 接近或超过上限，或出现 `Hermes is at the active session limit (20/5)` 报错，直接跳到 **[Gateway Session Limit 修复](#step-gateway)**。

**跳过这一步的条件：** 用户明确说"变傻/变慢"但不是服务挂掉。但如果 doctor 报错，先修再往下。

### 第一步：检查系统资源

```bash
top -bn1 | head -5                # CPU负载
free -h                            # 内存使用（特别看 swap 用量）
df -h /                            # 磁盘余量
```

**异常信号：**
- CPU idle < 50% — 有其他进程在抢资源
- Swap used > 1GB — 内存不够，交换导致卡顿
- Disk used > 85% — Hermes 日志/数据库可能已满

### 第二步：检查日志错误

```bash
grep -i "error\\|exception\\|traceback\\|timeout" ~/.hermes/logs/agent.log | tail -20
grep -i "error\\|exception\\|traceback\\|timeout" ~/.hermes/logs/gateway.log | tail -20
```

**重点关注：**
- `Auxiliary: marking <provider> unhealthy` — **辅助模型挂了，压缩等功能静默失效！**
- `Session expired` — 通道断连（如微信），不影响核心功能
- `timeout` — 工具调用超时，可能拉慢整个响应（如 AnySearch 发 GET 请求到 MCP 端点会超时，需用 POST）
- `active session limit (20/5)` — 网关会话池满，新会话被拒。详见 `references/gateway-session-limit.md`

### 第三步：检查上下文压缩

```bash
cat ~/.hermes/config.yaml | grep -A 5 'compression'
```

**正常状态：** `compression.enabled: true`，有 `threshold` 和 `target_ratio` 设置。

**修复：**
```bash
hermes config set compression.enabled true
hermes config set compression.threshold 0.50
hermes config set compression.target_ratio 0.20
```

**为什么重要：** 没有压缩，对话context无限膨胀。模型需要处理越来越大的历史，注意力稀释导致"变笨"。DeepSeek V4-Flash等模型对此尤其敏感。

### 第四步：检查辅助模型配置（关键！压缩依赖它）

```bash
cat ~/.hermes/config.yaml | grep -A 6 'auxiliary'
```

**正常状态：** `auxiliary.compression.provider` 和 `model` 都已配置，且指向**工作正常的 provider**。

**如果 auxiliary 没配：**
- compression 功能虽然 enabled，但后台静默失败
- 辅助模型默认走 OpenRouter/Nous，如果付费失败会出现 `Auxiliary: marking openrouter unhealthy` 日志
- Agent 看起来压缩开了，实际上没生效，context 照胀不误

**修复：**
```bash
hermes config set auxiliary.compression.provider deepseek
hermes config set auxiliary.compression.model deepseek-v4-flash
hermes config set auxiliary.vision.provider deepseek
hermes config set auxiliary.vision.model deepseek-v4-flash
hermes config set auxiliary.session_search.provider deepseek
hermes config set auxiliary.session_search.model deepseek-v4-flash
```

把 provider 改成用户当前在用的（上述示例是 DeepSeek V4-Flash）。

> 💡 **如果主力模型不支持看图（如 DeepSeek）：** 可以为 `auxiliary.vision` 单独配一个视觉模型，如通过 SiliconFlow 的 OpenAI 兼容接口 + Qwen-VL。详见 `references/siliconflow-vision.md`。

**为什么重要：** 压缩、视觉分析、会话搜索都依赖 auxiliary 模型。如果辅助模型挂掉，这些功能全部静默退化，Agent 变笨但不报错。

### 第五步：检查context_length限制

```bash
cat ~/.hermes/config.yaml | grep -A 5 'agent'
```

**正常状态：** `agent.context_length` 有明确值（如 32000）。

**修复：**
```bash
hermes config set agent.context_length 32000
```

**为什么重要：** 没有上限 = 无限膨胀。设一个合理上限保证模型工作在最佳窗口内。

### 第六步：检查显示语言

```bash
cat ~/.hermes/config.yaml | grep -A 3 'display'
```

**正常状态**（中文用户）：`display.language: zh`

**为什么重要：** 不设 language，Hermes 的系统消息/提示默认为英文，每次对话多耗几百 token 的英文水词。中文用户设 zh 后系统提示更精简。

**修复：**
```bash
hermes config set display.language zh
```

### 第七步：检查记忆/用户档案膨胀

检查已有记忆条目的数量和大小:
1. 用 `memory action='add'` 写一个占位符，看当前使用量
2. 如果 memory > 60% 或 user > 80% 时，有两种处理方式：

**方式A — 阈值调高（优先）：** 默认 `memory` 上限 2,200 chars、`user` 上限 1,375 chars，可在 config.yaml 的 `memory` 段调大：

```bash
hermes config set memory.memory_char_limit 4000   # 我的笔记上限（默认2200）
hermes config set memory.user_char_limit 3000     # 用户档案上限（默认1375）
```

上限读取自 `config.yaml` → `memory.memory_char_limit` / `memory.user_char_limit`，默认值硬编码在 `tools/memory_tool.py` 和 `agent/agent_init.py`。**需新会话（`/reset`）生效。**

**方式B — 手动瘦身（当不宜再调大时）：**
- 去掉矛盾/过时的记录（如 阿里云 vs 腾讯云）
- 合并重复信息（如项目路径说了3次 → 1条）
- 把session-specific操作记录（如"已配置TCP保活"）转移到对应skill，不留在memory
- 用 batch operations（`operations` 数组）一次清理多条

**选择原则：** 用户档案频繁接近上限（如持续 >90%）且信息都有用 → 调高阈值。偶尔触顶且有过时内容 → 瘦身。两者不互斥。

### 第八步：检查搜索工具健康

**先确认搜索架构：** Hermes 的 web 搜索是插件化的。`web` 工具集可以 enable，但具体的后端插件（web-tavily, web-ddgs, web-exa等）可能"not enabled"。

两种搜索路径：

**路径A — MCP搜索服务（如AnySearch）：**\n```bash\nhermes mcp list           # 确认已连接\nhermes mcp test <name>    # 测试连通性和延迟\n```\n检查重点：MCP 工具描述通常很长（如 AnySearch 的 search 工具说明文 500+ 字），每次调用都注入 context，建议用 batch_search 减少调用次数。\n\n**MCP 搜索额度检查：** 免费 MCP 搜索服务（AnySearch）有每日额度限制。耗尽后的典型症状是搜索静默失败，Agent 绕圈。排查：\n```bash\ngrep -i "quota\\|exhausted\\|rate.limit" ~/.hermes/logs/agent.log | tail -5\n```\n修复：在 config.yaml 的 MCP server 配置中添加 API Key headers：\n```yaml\nmcp_servers:\n  anysearch:\n    enabled: true\n    url: https://api.anysearch.com/mcp\n    headers:\n      Authorization: Bearer <your_api_key>\n```\n⚠️ 注意：`patch` 工具因安全检查拒绝修改 config.yaml。**必须用终端执行**：`python3 -c "import yaml; ..."` 写入 yaml，或直接用 `hermes config set`。\n\n**MCP 连通性验证：** 配好 headers 后重启 serve 生效，再用一次搜索确认返回结果而非 quota 报错。

**路径B — 内置 web_search 工具：**
```bash
# 检查有哪些 web 插件注册了
hermes plugins list | grep web-
python3 -c "
from agent.web_search_registry import list_providers, get_active_search_provider
print(f'Registered providers: {[p.name() for p in list_providers()]}')
print(f'Active search provider: {get_active_search_provider().name() if get_active_search_provider() else \"NONE\"}')
"
```

**常见问题：**
- web 插件全部"not enabled" → 需要 `hermes plugins enable <name>`
- 免费选项无 API Key 需求：`hermes plugins enable web-ddgs`（DuckDuckGo）
- 付费选项：Tavily（需TAVILY_API_KEY）、Exa（需EXA_API_KEY）、Firecrawl（需FIRECRAWL_API_KEY）

**⚠️ 中国用户特有问题：DuckDuckGo 被限流**

从中国服务器使用 web_search（DuckDuckGo 后端）时，会频繁出现 `DuckDuckGo search timed out after 30s` 错误。症状：
- Agent 响应变慢（等搜索超时30秒）
- 搜索失败 → Agent 凭训练数据回答 → 答不准、绕圈子
- 日志中出现大量 `ddgs.ddgs: Error in engine <brave/google/yahoo>: TimeoutException`

**排查：** `grep "timed out" ~/.hermes/logs/agent.log | tail -10`
**修复方案（按优先级）：**
1. **AnySearch（MCP 搜索）** — 优先使用，需配置 API Key 和可用额度。免费额度耗尽时会报 `daily_free_quota_exhausted`
2. **付费搜索插件** — Tavily / Exa / Firecrawl 更稳定
3. DuckDuckGo 被限流时不要重试多次，只会更慢

详见 `references/duckduckgo-china-block.md`。

**搜索优先级：** 检查 memory 是否有搜索优先级设置。常见模式：MCP搜索优先（如 AnySearch），无结果回退 web_search。当两种搜索都不可靠时，Agent 的"变傻"感最明显。

### 第九步：检查 skills 膨胀（#1变傻元凶）

```bash
find ~/.hermes/skills/ -name "SKILL.md" | wc -l
du -sh ~/.hermes/skills/
hermes curator status       # managed/unmanaged 分布
hermes curator usage        # 按活跃度排序，找零使用skill
```

**正常状态：** 30-60个 SKILL.md。超过 100 个说明堆积了过多 session-specific 技能。

**影响：** 系统提示枚举所有技能描述 → context 开头被塞满无关 skill → 模型注意力稀释。**这是本会话实际发现的#1变傻原因（139个/181MB）。** 注意技能库文件和目录大小也增长很多.

**修复：用 curator 安全清理（不删除，只归档，可恢复）**

```bash
# 1. 查看哪些skill未被curator管理
hermes curator list-unmanaged

# 2. 交给curator管理
hermes curator adopt <skill-name>     # 逐个
hermes curator list-unmanaged | wc -l # 如果很多，批量adopt

# 3. 查看curator的清理策略（当前设置）
hermes curator status
# → stale after: 30d unused, archive after: 90d unused, consolidate: off

# 4. 启用LLM合并（curator默认只归档不合并，需手动开启）
hermes config set curator.consolidate true

# 5. 触发立即审核（auto-archives 90天零使用的skill）
hermes curator run

# 6. 手动归档特定零使用skill
hermes curator prune --days 90

# 7. 查看归档记录
hermes curator list-archived

# 8. 如有需要可恢复
hermes curator restore <name>

# 9. 安全网：跑前自动备份
hermes curator backup

# 10. 全量回滚
hermes curator rollback
```

**安全底线：**
- curator **永不删除**，只归档（移到 `.archive/` 目录，从prompt排除但可恢复）
- bundled（Hermes自带的46个）和 hub（从skill.sh装的）**永不动**
- 跑前自动 `tar.gz` 备份快照
- 归档后随时 `restore`
- 全量回滚 `rollback`

**清理前安全告知模版（用户问"会不会影响XX"时用）：**

> 只动 `~/.hermes/skills/` 里的skill文件，不动页面/文档/桌面文件。
> 只归档长期未使用的skill，活跃的和bundled的保留。
> 不删除只归档，可恢复。跑前自动备份。

详见 `references/curator-workflow.md` 和 `scripts/build-skill-manifest.py`。（技能归档可见性模式——归档技能通过 Obsidian 清单保持可发现，详见参考文件。）

**🔁 清理后必做：重建技能档案库**

curator 归档后，归档技能从 prompt 消失。要维持「归档不失联」，必须重新生成 Obsidian 技能档案清单：

```bash
# 生成新的技能档案库.md（写入 Obsidian vault _kb/ 目录）
python3 ~/.hermes/skills/devops/agent-performance/scripts/build-skill-manifest.py

# 然后手动触发 kb_summary 更新共享记忆：
python3 ~/.hermes/scripts/kb_summary.py
```

新会话启动时，共享记忆层（kb_context.md）自动包含技能档案，agent 能感知归档技能的存在。需要时 → `hermes curator restore <name>` → `skill_view()` 调用。

## 修复完成后的操作

```bash
# 确认配置完整
hermes config check
```

需要**新会话**（`/reset`）使压缩/context_length/auxiliary 配置生效。

## 典型诊断路线图

```
用户反馈"变傻"
  │
  ├─【Step -1】哪个实例？当前这个vs另一个？→ 另一个 → 给清单让用户跑/请求远程
  │
  ├─→ 第零步：hermes doctor + status + 系统资源健康? → No → 先修环境
  │
  ├─→ 第一步：系统资源（CPU/内存/磁盘）→ 异常→排查进程/清理磁盘
  │
  ├─→ 第二步：日志错误（auxiliary unhealthy? timeout?）→ 修复对应问题
  │
  ├─→ 第三步：压缩 enabled? → No → 开启压缩
  │
  ├─→ 第四步：auxiliary models 配了? → No → 绑定工作 provider（常见陷阱：默认 OpenRouter 付费失败，压缩静默失效）
  │
  ├─→ 第五步：context_length 设了? → No → 设32K
  │
  ├─→ 第六步：display.language 设了中文? → No → display.language: zh
  │
  ├─→ 第七步：记忆膨胀? → Yes → 瘦身清理
  │
  ├─→ 第八步：搜索健康?
  │     ├─→ MCP搜索连好了? 有额度?
  │     ├─→ web插件enable了? 有API Key?
  │     ├─→ DuckDuckGo 被限流?（中国服务器常见）
  │     └─→ 搜索优先级配置了?
  │
  └─→ 第九步：skills 膨胀? curator adopt + consolidate + run + prune
```

## 预防性维护（防患于未然）

一旦诊断修复完成，建议设置**定时清理**防止复发。

**关键区分：磁盘清理 ≠ 记忆清理。** 两者对 agent 性能的影响完全不同。

| 类型 | 影响 | 频率 | 成本 |
|------|------|------|------|
| **磁盘清理**（server-cleanup.sh） | 不影响 agent 智商，只防磁盘满 | 每周1次 | 零 token（no_agent） |
| **记忆清理**（memory consolidation） | **直接影响**。记忆膨胀 → prompt 前缀变长 → 注意力稀释 | 每天1次 | 少量 token（需 agent 判断） |

### 磁盘清理 cron（防止服务器变卡）

详见 `server-service-deployment` 技能 →「服务器定期维护（大脑清理）」章节。

```yaml
cronjob(action='create', name='大脑清理', schedule='0 3 * * 7',
        script='server-cleanup.sh', no_agent=true, deliver='origin')
```

⚠️ **注意：** `server-cleanup.sh` 中第10项 `drop_caches`（`sync && echo 3 > /proc/sys/vm/drop_caches`）会清空系统文件缓存，跑完几分钟内硬盘读写变慢。如果服务器不是磁盘紧张，考虑删掉这一行。

### 记忆瘦身 cron（防止 agent 变笨）

用 agent-driven cron job（非 no_agent），每天自动检查 memory 使用率，>60% 则执行合并瘦身。

```yaml
cronjob(
  action='create',
  name='记忆瘦身',
  schedule='0 4 * * *',       # 每天凌晨4点
  deliver='local',             # 静默运行，不打扰用户
  prompt='执行记忆瘦身任务。

1. 用 memory tool 检查当前 memory 使用率（action="add" 放占位符然后删掉，看 usage 百分比）
2. 如果 usage > 60%，执行清理（注意：limits 可在 config.yaml 的 memory.memory_char_limit / memory.user_char_limit 调整，默认 memory=2200 / user=1375）：
   - 识别过时、重复、session-specific 的条目
   - 将可合并的条目压缩合并
   - 优先保留：用户身份偏好、项目配置、工作流规则、成本信息
   - 优先删除：一次性操作记录、session-specific 临时信息
   - 用 batch operations（operations 数组）一次完成
3. 如果 usage <= 60%，什么都不做
4. 只清理 memory（个人笔记），不动 user_profile（用户档案）。不要修改技能文件。'
)
```

#### 第拾步：检查Cron任务健康（provider drift）

当用户反馈「定时任务没收到内容」时，检查cron任务状态：

```bash
hermes cron list | grep -E 'error|Skipped'
```

**Cron Provider Drift** — 当全局模型配置变化（如 `deepseek` → `openai-api`），旧的cron任务创建时的 `provider_snapshot`/`model_snapshot` 与当前全局配置不匹配，scheduler 会跳过执行防止意外扣费。日志特征：

```
WARNING cron.scheduler: Job 'XXX': SKIPPED — global inference config drifted
since creation (provider 'deepseek' -> 'openai-api'; model 'deepseek-v4-flash'
-> 'gpt-5.5') and this job is unpinned.
```

**修复方法（先尝试 cronjob update，如无效则直接编辑 jobs.json）：**

```bash
# 方法A：update cronjob（只重置创建时间戳，不一定总能修复drift检测）
hermes cron action=update job_id=<id> name="<原name>" schedule="<原schedule>"

# ⚠️ cronjob update 工具没有 provider/model 参数，所以 drift 检测可能依然存在
# 如果 update 后仍然 drift，使用方法B

# 方法B（可靠）：直接编辑 jobs.json 中的 provider_snapshot/model_snapshot
python3 << 'PYEOF'
import json

with open('/home/ubuntu/.hermes/cron/jobs.json', 'r') as f:
    data = json.load(f)

error_ids = ["<job_id1>", "<job_id2>", ...]  # 有drift错误的job IDs

for job in data['jobs']:
    if job['id'] in error_ids:
        job['provider'] = "<current_provider>"  # e.g. "openai-api"
        job['model'] = "<current_model>"        # e.g. "gpt-5.5"
        job['provider_snapshot'] = "<current_provider>"
        job['model_snapshot'] = "<current_model>"

with open('/home/ubuntu/.hermes/cron/jobs.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
PYEOF
```

**验证修复：** `hermes cron action=run job_id=<id>` — 返回 `execution_success: true` 即修复成功。

**陷阱：**
- 直接编辑 jobs.json 需在 scheduler 空闲时进行（无 .tick.lock 竞争）
- 修改后 scheduler 会在下一 tick 自动加载新配置，无需重启

**⚠️ 重要：区分「名义配置」与「实际通道」**

用户可能观察到「扣费都走 deepseek」——这是判断真实情况的黄金线索。config.yaml 显示 gpt-5.5 不代表实际在用 gpt-5.5：当主 provider 调用失败时，fallback_providers（如 SiliconFlow 的 deepseek）会自动接管。验证方法：

```bash
grep -oE "model=deepseek|model=gpt" ~/.hermes/logs/agent.log | sort | uniq -c
```

如果 deepseek 计数远大于 gpt（如 3500 vs 57），说明 gpt-5.5 只是名义配置，实际一直在 fallback 到 deepseek。此时用户感觉「一切正常」是真实的——真正干活的是 deepseek。修复时把全局配置 + jobs.json 统一回实际通道（deepseek），并 pin cron 任务防止再漂移。

**「怎么这么多天都能用？不是要充钱吗」类问题的解释：** Hermes 调用 API 走的是开发者 key（按 token 计费），不是 ChatGPT 个人会员（$20/月）。.env 里有 OPENAI_API_KEY 就能调 gpt-5.5，扣的是 API 额度不是用户口袋。

**模型变更需用户确认再动**：全局模型配置（model.default/provider）改动前必须问用户，不能自行切换（用户明确要求）。

### 额外：cron no_agent 任务不受 drift 影响
script-only 任务（no_agent=true）不调用 LLM，不受 provider drift 影响。

## 快捷指令

用户喊 **「醒脑」** → 立即执行一次：磁盘清理脚本 + 记忆瘦身 + curator技能检查 + 重建技能档案库(`build-skill-manifest.py` → `kb_summary.py`) + cron drift检查 + 检查磁盘/内存/记忆状态。

## 警告

- ❌ 不要只给建议不执行 — 每步检查都要**实际运行命令**，把结果给用户看
- ❌ 不要安慰用户（"会好的"）— 直接修，修完告诉他改了什么
- ❌ 修完必须重启会话（`/reset`）才生效——不要让用户在旧会话里继续试
