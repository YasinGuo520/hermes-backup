# 量化 cron 配置漂移诊断（2026-08-12 实测）

当 v2 选股日志缺失时，区分「非交易日」vs「cron 失败」。

## 故障签名（2026-08-12 实况）

- `~/Desktop/hermes/quant-skill/logs/` 无当日 `YYYY-MM-DD.json`（最新为前一交易日）
- 早盘 cron 输出异常小：`~/.hermes/cron/output/ea324446676f/` 当天 md 仅 1.7KB（正常 4-10KB）
- 输出文件头部带 `# Cron Job:` 和 `(FAILED)` 标记

## 报错原文

```
RuntimeError: Skipped to prevent unintended spend: global inference config drifted
since this job was created (provider 'deepseek' -> 'openai-api'; model
'deepseek-v4-flash' -> 'gpt-5.5'), and this job is unpinned. No inference call was
made. To run on the new config, pin it explicitly: `cronjob action=update
job_id=ea324446676f provider=<provider> model=<model>` (or pin the original values
to keep them). See #44585.
```

含义：cron 快照（deepseek/deepseek-v4-flash）与全局配置（openai-api/gpt-5.5）不一致时，安全守卫**直接跳过不跑**，防止意外扣费。这是有意设计——比 2026-08-12 之前「OPENAI_API_KEY 调用常失败、实际大量 fallback 走 deepseek 扣费」的事故更安全。

## 诊断步骤

```bash
# 1. 看当天 cron 输出大小（正常 4-10KB，失败 ~1.7KB）
ls -la ~/.hermes/cron/output/ea324446676f/

# 2. 读输出确认报错（strings 处理超长行/二进制误判）
head -c 2000 ~/.hermes/cron/output/ea324446676f/YYYY-MM-DD_HH-MM-SS.md | strings | head -60

# 3. 核对全局配置修复状态
stat -c '%y' ~/.hermes/config.yaml   # 应为 deepseek/deepseek-v4-flash

# 4. 核对 cron job 四字段
python3 -c "
import json
jobs = json.load(open('/home/ubuntu/.hermes/cron/jobs.json'))
for j in (jobs if isinstance(jobs, list) else jobs.get('jobs', [])):
    if j.get('id') in ('ea324446676f','4b176d3f9c5e','084374e236cc'):
        print(j.get('id'), j.get('provider'), j.get('model'),
              j.get('provider_snapshot'), j.get('model_snapshot'))
"
```

## 关键事实

- 修复动作：`~/.hermes/config.yaml` 改回 `provider: deepseek / model: deepseek-v4-flash` + jobs.json 四字段同步（`cronjob update` 不支持 provider/model 参数，须直接编辑 jobs.json；config.yaml 用 `hermes config set`，patch 被安全保护拒绝）
- **时间线坑**：config.yaml 修复时间（10:20）晚于早盘 cron 运行时间（08:45）时，当天日志仍会缺失——修复只影响次日 cron
- 连带影响：量化看板数据同步 cron `084374e236cc`（08:50）同天也缺数据，次日自动补齐，无需手动补
- 影响面：仅 v2 糅合系统（quant_ensemble.py）日志缺失；旧因子自进化系统（quant_self_evolve.py）独立运行不受影响
- 手动补跑当日 v2 输出仅能看模型结果，不能当早盘推荐复盘（收盘后数据无推荐意义）

## 报告注意事项

任务模板说「今日无 v2 日志（非交易日）则跳过」——但 cron 失败不是非交易日，报告必须写明失败根因，不能简单套用非交易日跳过逻辑。
