# Telegram（TG）接入 — 国内服务器实测版

## 状态（2026-08 实测）

- **Hermes 原生支持 TG**：适配器内置在 `plugins/platforms/telegram/adapter.py`，setup 注册完整
- 配置入口：`hermes setup` 选 Telegram——可自动创建 bot（`hermes_cli/telegram_managed_bot.py`）或手动填 BotFather token（setup.py `_is_valid_telegram_bot_token` 校验）
- 配置落在 `~/.hermes/config.yaml` 的 `gateway.platforms.telegram`（dict 格式，同其他平台）
- 用户侧需要先建 bot：@BotFather → /newbot → 拿 token

## ⚠️ 硬性障碍：国内服务器连不上 TG API

```bash
curl -s -o /dev/null -w "%{http_code}" --connect-timeout 8 https://api.telegram.org/
# → 000（被墙，连接失败）
```

**不解决网络，配好 bot 也白接**——网关 polling 会一直失败。这是接 TG 的第一步诊断，先测连通再谈配置。

## 可行路径

| 方案 | 做法 | 风险/代价 |
|------|------|----------|
| A. 服务器代理 | xray/sing-box + 机场订阅，HTTP/SOCKS5 出口 | 腾讯云会扫异常外联，跑翻墙代理有风控警告/封机风险（需用户知情同意）；机场订阅通常限设备数，手机+服务器共用可能超 |
| B. Mac 本地跑 | Mac 有 Shadowrocket 翻墙环境，本地装 Hermes 接 TG | 双实例：记忆/技能/session 各自独立，需跨机同步，维护成本翻倍 |
| C. 放弃 | 继续飞书/QQ | 零成本 |

## 隐私分层（用户问"聊天会被监控吗"的标准答案）

- **链路**：飞书(字节服务器) → 用户腾讯云(Hermes) → DeepSeek API——三方技术上明文可见
- **Hermes 本身无遥测**：`~/.hermes/config.yaml` 无 telemetry/analytics 项，对话不上传任何第三方（已实测确认）
- **存储**：`~/.hermes` 数据库在用户自己的服务器上
- **风险本质**：国内平台受《网络安全法》《数据安全法》约束，政府可依法调取；不是恶意监控，是平台共性
- **TG 只解决传输层**：内容照样发给 DeepSeek 处理。真端到端加密要 Signal / TG secret chat（Hermes 走 TG Bot API 不是 secret chat，Bot API 消息也过 TG 服务器）
- 更私密的替代：CLI 本地模式（不经飞书）或 Signal

## 多实例：一个 TG 账号连 N 个 Hermes

- 一个 TG 账号可以同时跟**无数个 bot** 聊天；想连几个 Hermes 就建几个 bot（@BotFather /newbot 随便建）
- **一个 bot token 只能挂一个 Hermes 实例**——两个进程抢 getUpdates 长轮询会 409 Conflict，别共用
- 多实例做法：每个 bot 配一个独立 Hermes profile（`~/.hermes/profiles/<name>/`），记忆/技能/人设完全隔离
- 一个 TG 账号 = 控制台，N 个 bot = N 个分工不同的助理

## 平台对 VPN 节点国家的敏感度（用户常问）

| 平台 | 切英国/换节点 | 说明 |
|------|-------------|------|
| X / TG / Discord / YouTube / WhatsApp | ✅ 无影响 | 不查 IP 归属 |
| FB / IG | ✅ 基本无影响 | 偶尔弹"确认是你本人"验证；FB 广告账户会校验投放地区+IP，投广告时别乱切 |
| TikTok | ⚠️ 敏感 | **唯一对 IP 国家高度敏感的平台**：切节点=换地区内容+可能触发风控；保持美国节点+English(US) |
| 通用 | 账号风控 | 短时间美英多国横跳才触发风控，一天内固定一个地区就没事 |
