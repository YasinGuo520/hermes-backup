---
name: qq-bot-integration
description: "在 Hermes Agent 中配置和运维 QQ 机器人（双路径：官方 QQ Bot API + 腾讯云 LightClawBot）。覆盖注册、沙箱、发布、intents 配置、网关调试全流程。"
version: 1.0.0
author: agent
tags: [qq, chat, china, tencent, gateway, messaging]
---

# QQ 机器人接入（Hermes Agent for China）

中国 IM 平台接入 QQ 有两种方式：**官方 QQ Bot API**（需注册 q.qq.com）和 **腾讯云 LightClawBot**（通过腾讯云服务器扫码一键接入）。

## 快速判断走哪条路

| 条件 | 推荐路径 | 说明 |
|------|----------|------|
| 已有腾讯云 Lighthouse 服务器部署了 Hermes/OpenClaw | **LightClawBot** | 扫码即用，免审核，但找不到机器人的 QQ 号 |
| 需要稳定、可配置的正式机器人 | **QQ Bot API** | 需走完审核上线流程 |
| 个人测试、不想折腾企业认证 | **QQ Bot API + 沙箱** | 个人主体即可注册 q.qq.com |

---

## 路径 A：QQ Bot API（官方渠道）

### 注册与创建机器人

1. 访问 [q.qq.com](https://q.qq.com) → 注册（个人主体即可，需实名+人脸识别）
2. 创建机器人 → 获取 **AppID** 和 **AppSecret**（AppSecret 仅首次可见，务必保存）
3. 在「开发设置」中确认 **intents** 已开启：
   - `C2C_MESSAGE_CREATE`（单聊/私信）
   - `GROUP_AT_MESSAGE_CREATE`（群 @消息）
   - `PUBLIC_GUILD_MESSAGES`（频道消息）

### Hermes 配置

**`.env` 中设置：**
```bash
QQ_APP_ID=your-app-id
QQ_CLIENT_SECRET=your-app-secret
```

**`config.yaml` 中设置：**
```yaml
gateway:
  platforms:
    - feishu
    - qqbot

platforms:
  qqbot:
    enabled: true
    extra:
      app_id: "your-app-id"
      client_secret: "your-secret"
      markdown_support: true
      dm_policy: "open"          # open | allowlist | disabled
      group_policy: "allowlist"
```

### 沙箱 vs 生产

| 状态 | 能收谁的消息 | 操作 |
|------|-------------|------|
| **沙箱（默认）** | 仅沙箱频道/群（<20人） | 在 q.qq.com → 沙箱配置 → 添加测试用户 |
| **已上线** | 所有QQ用户 | 功能配置+自测报告 → 提交审核 → 上线 |

### 发布上线流程

1. **功能配置** → 填名称、头像、简介
2. **自测报告** → 截图证明机器人能正常响应
3. **提交审核** → 当日16:00前提交，当日出结果
4. **上线** → 审核通过后手动点「上线」按钮

### ⚠️ 常见坑

- **私聊在沙箱模式不支持！** 沙箱只能走 QQ频道，私聊需要上线后才能用
- **审核不通过**：检查机器人名称是否含"腾讯""QQ"等敏感词
- **连接成功但收不到消息** → 检查 intents 是否开启
- **WebSocket 连不上** → 检查 IP 白名单（q.qq.com → 开发设置 → IP白名单）
- **重启 gateway**：`hermes gateway restart`（不能从 gateway 进程内执行，需另开终端或用 `kill` + systemd 重启）

---

## 路径 B：腾讯云 LightClawBot

### 条件
- 腾讯云 Lighthouse 服务器已部署 Hermes/OpenClaw
- lightclawbot 插件已安装在 `~/.hermes/plugins/lightclawbot/`

### 配置步骤

1. 登录 [腾讯云控制台](https://console.cloud.tencent.com) → **轻量应用服务器**
2. 点选你的服务器实例 → **应用管理**
3. 找到 **通道/Channel 配置** → 选择 QQ → 点击 **前往授权**
4. 用手机 QQ 扫码完成授权
5. 机器人自动出现在 QQ 消息列表中

### ⚠️ LightClawBot 坑

- `uin` 是腾讯云内部 ID，**不是 QQ 号**，搜不到
- 必须通过腾讯云控制台的扫码授权才能绑定自己的 QQ
- 日志中看到 `uin=100050621551` 类的是内部标识，不是可搜索的 QQ 号
- 环境变量：`LIGHTCLAW_API_KEY_${UIN}` 格式
- 已在 Hermes config 中启用则无需额外操作，gateway 重启后自动连接

### 网关日志查看

```bash
# 查看 QQ Bot 连接状态
tail -100 ~/.hermes/logs/gateway.log | grep -i "qq\|websocket\|lightclaw"

# 查看入站消息
grep "qqbot.*inbound\|lightclaw.*inbound" ~/.hermes/logs/gateway.log | tail -10
```

---

## Gateway 重启特殊说明

**不能从 gateway 进程内执行重启命令**（Hermes 会拦截，因为 SIGTERM 会传播到子进程）。

安全重启方法：
```bash
# 方法 1：找 PID 直接 kill（gateway 自动重启）
ps aux | grep '[h]ermes.*gateway' | awk '{print $2}' | xargs kill

# 方法 2：tmux 新会话
tmux new-session -d -s gw 'hermes gateway restart'

# 方法 3：通过 systemd（如果有）
systemctl --user restart hermes-gateway
```
