---
name: qq-bot-setup
description: QQ机器人（QQ开放平台 q.qq.com）接入Hermes Agent全流程。从注册到上线，含沙箱测试、发布审核、LightClaw腾讯云直连方案。
version: 1.0
author: agent
tags: [qq, bot, gateway, messaging, china]
---

# QQ 机器人接入 Hermes Agent

## 概述

将 Hermes Agent 接入 QQ 有两种路径：

| 方案 | 难度 | 说明 |
|------|------|------|
| **A. QQ开放平台官方 Bot** | 中等 | 需注册 q.qq.com + 创建机器人 + 审核上线 |
| **B. 腾讯云 LightClaw (扫码)** | 简单 | 已有腾讯云 Lighthouse 服务器的首选，扫码即用 |

## 方案A：QQ开放平台官方 Bot

### 前置条件

- 注册 [q.qq.com](https://q.qq.com)（个人/企业均可）
- 创建机器人，获取 **AppID** 和 **AppSecret**
- 服务器已安装 `aiohttp`、`httpx`

### 配置步骤

#### 1. 配置 Hermes

```bash
# .env 添加
QQ_APP_ID=your-app-id
QQ_CLIENT_SECRET=your-app-secret

# config.yaml 添加
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
      dm_policy: "open"
      group_policy: "allowlist"
```

#### 2. 沙箱测试（审核前）

QQ 机器人创建后默认在 **沙箱模式**，只能收测试环境消息。

操作路径：
1. 在 QQ 上创建一个 **QQ频道**（<20人）
2. q.qq.com → 应用管理 → 点机器人 → **「使用范围与人员」** → 添加频道/群到沙箱
3. 把机器人添加到沙箱频道
4. 在频道里 @机器人 发消息测试

> ⚠️ 沙箱模式**不支持私聊**，只能通过频道或群测试

#### 3. 发布上线

1. q.qq.com → 应用管理 → 机器人 → **「发布设置」**
2. 填 **功能配置**（名称、简介、头像）
3. 填 **自测报告**（沙箱测试截图）
4. 提交审核（16:00前提交当天出结果）
5. 审核通过 → 手动点 **「上线」**
6. 上线后所有 QQ 用户可搜索添加机器人

### 机器人QQ号在哪找

q.qq.com → 应用管理 → 点机器人 → **「开发设置」**，页面显示 **机器人QQ号**

### 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| WebSocket连上了但收不到消息 | 沙箱模式/intents未配置 | 检查沙箱配置，确认intents已开 |
| 搜不到机器人QQ号 | 沙箱模式不可搜索 | 用二维码添加，或发布上线 |
| "机器人去火星了" | 未配置AppID/Secret | 检查.env和config.yaml |
| 找不到沙箱配置 | q.qq.com改版 | 进应用管理→点机器人→找「使用范围与人员」 |
| gateway重启失败（从聊天会话操作时） | 在gateway进程内执行 restart，SIGTERM会传播到子进程被拦截 | 另开终端执行，或手动 kill gateway PID |
| "open policy without allow-all opt-in" 错误 | dm_policy/group_policy设为open却没设ALLOW_ALL_USERS | 在.env加 `LIGHTCLAWBOT_ALLOW_ALL_USERS=true` 或 `QQ_ALLOW_ALL_USERS=true` |
| 找不到二维码 | q.qq.com UI版本不同 | 直接发布上线，上线后搜QQ号加好友最简单 |

## 方案B：腾讯云 LightClaw（推荐，需Lighthouse）

已有腾讯云 Lighthouse + OpenClaw/Hermes 的用户，扫码即可。

### 步骤

1. 登录 [腾讯云控制台](https://console.cloud.tencent.com)
2. 轻量应用服务器 → 点实例 → **「应用管理」**
3. 找 **通道/Channel 配置** → 选 QQ → **「前往授权」**
4. 手机 QQ 扫码完成授权
5. QQ 消息列表自动出现机器人，直接对话

配置无需去 q.qq.com，扫码自动完成。

### Gateway 重启注意事项

配置完成后需要重启 gateway。**如果在会话进程内（通过飞书/QQ等聊天操作），不能直接 `hermes gateway restart`**，因为 gateway 会拦截 SIGTERM。

正确做法：
```bash
# 方案1：另开终端/SSH 执行
hermes gateway restart

# 方案2：直接 kill gateway 进程（会自动重启）
ps aux | grep '[h]ermes.*gateway' | awk '{print $2}' | xargs kill
```

## 验证方法

配置完成后在 QQ 给机器人发消息，Hermes gateway 日志中出现 `inbound message: platform=qqbot` 或 `lightclaw.*inbound` 即成功。

```bash
tail -f ~/.hermes/logs/gateway.log | grep -i "qq\|lightclaw"
```
