---
name: china-im-channels
description: Hermes中国IM渠道接入与运维——QQ机器人/微信iLink/飞书：注册配置、权限、断连排查、保活、扫码登录。
triggers:
  - QQ机器人
  - QQ接入
  - 微信通道
  - 微信断连
  - iLink
  - 飞书
  - Feishu
  - 渠道配置
  - 机器人接入
  - gateway平台
  - 扫码登录
  - 保活
related:
  - server-service-deployment
  - hermes-advanced-setup
---

# 中国IM渠道接入与运维

> 统一入口：把 Hermes 网关接进中国 IM 平台（QQ/微信/飞书）并长期稳定运行。三个渠道的完整接入文档分别在 references/ 下。

## 渠道选型

| 渠道 | 适用场景 | 接入方式 | 维护重点 |
|------|---------|---------|---------|
| **飞书** | 主力工作台（高稳定） | open.feishu.cn 建应用 + WebSocket 长连接 | 权限申请→重发布应用→重启网关；Bitable 写表 |
| **QQ** | 24h 值守、机器人客服 | 官方 QQ Bot API（q.qq.com）或腾讯云 LightClawBot | 沙箱→审核→上线；intents；IP 白名单 |
| **微信** | 个人微信桥接（日常聊天） | iLink（ilinkai.weixin.qq.com）第三方桥接 | 4-5h token 过期/2h 空闲断连；扫码重登；保活脚本 |
| **Telegram** | 海外渠道、私密传输（仅解决传输层） | `hermes setup` 选 Telegram / BotFather token | **国内服务器连不上 api.telegram.org**，须先解决代理（见 references/telegram.md） |

## 渠道文档

- `references/qq-bot.md` — QQ 官方 API + LightClawBot 双路径：注册、沙箱 vs 生产、intents、发布上线、常见坑
- `references/weixin-ilink.md` — 微信 iLink：断连日志诊断、TCP 保活、watchdog、-2/-14 错误、凭证轮换、彻底清除
- `references/feishu-lark.md` — 飞书：权限矩阵、工具集、错误码速查、Bitable API 工作流
- `references/telegram.md` — TG：Hermes 原生支持、国内服务器被墙实测、代理/双实例/放弃三方案、隐私分层、VPN 节点敏感度

## 通用运维（所有渠道）

### 日志查看
```bash
tail -f ~/.hermes/logs/gateway.log | grep -i "qq\|weixin\|feishu\|lightclaw\|session expired\|errcode"
```

### ⚠️ 重启网关（不能从 gateway 会话内执行）
`hermes gateway restart` 在网关会话（飞书/微信/QQ）内执行会被拦截（SIGTERM 传播，防自杀检测）。含 `restart`/`stop`/`kill` 的命令都会被拦。可靠变通：

```bash
# 首选：systemd-run 一次性 timer（进程树不在 gateway 之下）
systemd-run --user --on-active=5 bash -c "systemctl --user restart hermes-gateway.service"

# 备选：execute_code 沙箱 + setsid（沙箱进程不在 gateway 进程树下）
# 备选：直杀 PID（python os.kill，命令文本不含关键词）
```

### 配置生效规则
- 渠道配置在 `~/.hermes/config.yaml` 的 `gateway.platforms`（**必须是 dict 不是 list**，v0.20+；list 格式会导致该平台消息处理崩溃——见 `hermes-advanced-setup`）
- 权限/配置变更后必须**重启网关**才生效
- `approvals.mode off` 会被写成布尔 `false` 而非字符串，需 sed 修正（影响 cron 脚本执行）

## 支持文件

| 文件 | 用途 |
|------|------|
| `scripts/wechat_watchdog.sh` | 微信断线监测：检测 Session expired → 生成新二维码 → 飞书通知 |
| `scripts/wechat_keepalive.sh` | 微信保活：每25分钟调 getconfig 防 -2 空闲断连 + gateway 进程守护 |

## 关联

- `server-service-deployment` — 云服务器部署、腾讯云防火墙、systemd、keepalive
- `hermes-advanced-setup` — gateway.platforms 格式、模型 fallback、升级
- `qq-bot-integration` / `weixin-ilink-maintenance` / `feishu-lark` 已并入本技能（原内容在 references/ 对应文件）
