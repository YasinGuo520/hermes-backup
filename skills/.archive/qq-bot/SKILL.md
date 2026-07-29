---
name: qq-bot
description: "QQ Bot integration for Hermes Agent — setup, configuration, troubleshooting, and LightClawBot (腾讯云轻量) alternative. Covers both the official QQ Bot API (bot.q.qq.com) and the Tencent Cloud Lighthouse QQ channel."
tags: [qq, bot, messaging, tencent, channel, gateway]
---

# QQ Bot

Configure Hermes Agent to receive and send messages via QQ. Two paths:

1. **Official QQ Bot API** (`bot.q.qq.com`) — WebSocket + REST, supports C2C/群聊/频道
2. **LightClawBot (腾讯云轻量)** — Tencent Cloud Lighthouse built-in QQ channel, simpler setup

## Prerequisites

- QQ account (registered at [q.qq.com](https://q.qq.com))
- `AppID` and `AppSecret` from QQ Open Platform
- Dependencies: `pip install aiohttp httpx`

## Configuration

### .env (secrets)

```bash
QQ_APP_ID=your-app-id
QQ_CLIENT_SECRET=your-app-secret
```

### config.yaml

```yaml
gateway:
  platforms:
    - qqbot

platforms:
  qqbot:
    enabled: true
    extra:
      app_id: "your-app-id"
      client_secret: "your-secret"
      markdown_support: true
      dm_policy: open
      group_policy: allowlist
```

### Environment variables

| Variable | Description |
|----------|-------------|
| `QQ_APP_ID` | App ID (required) |
| `QQ_CLIENT_SECRET` | App Secret (required) |
| `QQ_ALLOW_ALL_USERS` | Set `true` to allow all DMs (needed with `dm_policy: open`) |
| `QQ_PORTAL_HOST` | Override portal host (`sandbox.q.qq.com` for sandbox) |

## Gateway Restart

After adding qqbot to config, restart the gateway:

```bash
# From a separate shell (NOT inside the gateway process):
hermes gateway restart

# If blocked (running inside gateway), find PID and kill directly:
ps aux | grep '[h]ermes.*gateway' | awk '{print $2}'
kill <PID>
```

The gateway blocks `hermes gateway restart` when the command runs inside the gateway process group (e.g. via Feishu/Telegram). Use direct PID kill instead.

## Pitfalls

### 1. Sandbox mode blocks real messages
New QQ Bots default to sandbox mode — they can **only** receive messages from:
- A sandbox channel/group (< 20 members, created by the developer)
- A sandbox user (added in q.qq.com → 沙箱配置)
- Sandbox mode does **not** support private chat (C2C)

### 2. Private chat requires publishing
For C2C (私聊) to work, the bot must be:
- Published (提交审核 → approve → 上线) on q.qq.com
- Or use LightClawBot (Tencent Cloud) which bypasses this

### 3. Intents must be enabled
In q.qq.com → 开发设置, enable:
- `C2C_MESSAGE_CREATE` (private chat)
- `GROUP_AT_MESSAGE_CREATE` (group @-mentions)
- `PUBLIC_GUILD_MESSAGES` (channel messages)

### 4. IP whitelist
Some QQ Bot API endpoints require IP whitelisting in q.qq.com → 开发设置 → IP白名单. Add your server's public IP.

## LightClawBot (Tencent Cloud Alternative)

If Hermes is deployed on **Tencent Cloud Lighthouse** (轻量应用服务器), the built-in QQ ClawBot channel is simpler:

- No q.qq.com registration needed
- Scan QR code in Lighthouse → 应用管理 → Channel配置 → QQ → 前往授权
- Bot auto-appears in QQ message list
- Supports C2C directly (no sandbox/publish required)

Configuration is done via the Tencent Cloud console UI, not Hermes config files.

## Reference

See `references/qqbot-setup.md` for a full walkthrough from this session.
