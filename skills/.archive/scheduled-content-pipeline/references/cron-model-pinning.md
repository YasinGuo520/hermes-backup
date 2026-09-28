# Cron 任务钉模型（防全局配置变更后静默跳过）

> 2026-08-29 实测教训：Yasin 的「晨间AI情报三合一」(e88a6c79fe52) 连挂3天无告警，根因是创建 cron 时没显式钉 model/provider。

## 故障表现

- `cronjob action='list'` 显示该 job `last_status: error`
- 任务输出目录里多个日期文件**大小完全一样**（都是 FAILED 占位，如 21670 bytes 连挂 27/28/29 三天）
- 首次收到通知的形态：cron 执行失败消息「已跳过以避免非预期消耗：自该任务创建后全局推理配置已发生变更（服务商由『deepseek』变为『custom』；模型由『deepseek-v4-flash』变为『deepseek-ai/...』）」

## 根因

创建 cron job 时没显式传 model/provider → 任务沿用**创建时的全局配置快照**。之后 `hermes config set` 换了 provider/model（deepseek → custom 硅基），Hermes 安全阀检测到配置变更，为避免非预期消耗直接跳过任务，**不发告警**。

对照组：同环境「AI英语每日一练」正常，因为它显式钉了 `provider=custom, model=deepseek-ai/DeepSeek-V4-Flash`。

## 修复

```bash
hermes cron edit <job_id> --model <model> --provider <provider>
```

实测实例：

```bash
hermes cron edit e88a6c79fe52 --model deepseek-ai/DeepSeek-V4-Flash --provider custom
# 输出 "Updated job: e88a6c79fe52" 即成功
```

## 验证

1. `cronjob action='list'` 确认该 job 的 model/provider 已显式显示（不再是 null）
2. 手动跑一次确认：`cronjob action='run' job_id=<id>`

## 铁律

**任何 LLM cron 任务创建/编辑时必须显式钉 model+provider，不能依赖继承全局配置。**

Yasin 环境参考值：`--provider custom --model deepseek-ai/DeepSeek-V4-Flash`（硅基，模型锁死 v4-flash，见记忆「模型锁死铁律」）。

## 排查顺序

怀疑 cron 挂了 →
1. `cronjob action='list'` 看 last_status
2. 对比输出目录文件大小（连挂几天 = 同大小 FAILED 文件）
3. 查错误原文是否「全局推理配置已变更」