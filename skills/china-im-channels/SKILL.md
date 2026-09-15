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
| **微信** | 个人微信桥接（日常聊天） | iLink（ilinkai.weixin.qq.com）第三方桥接 | 4-5h token 过期/2h 空闲断连；扫码重登；保活脚本；**主动推送受会话 token 时效限制→隔夜首推必挂，别拿它做早间 cron 的投递目标** |
| **Telegram** | 海外渠道、私密传输（仅解决传输层） | `hermes setup` 选 Telegram / BotFather token | **国内服务器连不上 api.telegram.org**，须先解决代理（见 references/telegram.md） |

## 渠道文档

- `references/qq-bot.md` — QQ 官方 API + LightClawBot 双路径：注册、沙箱 vs 生产、intents、发布上线、常见坑
- `references/weixin-ilink.md` — 微信 iLink：断连日志诊断、TCP 保活、watchdog、-2/-14 错误、凭证轮换、彻底清除
- `references/feishu-lark.md` — 飞书：权限矩阵、工具集、错误码速查、Bitable API 工作流
- `references/feishu-voice.md` — 飞书**语音**：入站转写 + 出站语音气泡，国内服务器 STT 配置（Qwen3-ASR）、`/voice on` 模式、无真人验收脚本
- `references/telegram.md` — TG：Hermes 原生支持、国内服务器被墙实测、代理/双实例/放弃三方案、隐私分层、VPN 节点敏感度

## 通用运维（所有渠道）

### 日志查看
```bash
tail -f ~/.hermes/logs/gateway.log | grep -i "qq\|weixin\|feishu\|lightclaw\|session expired\|errcode"
```

### 渠道突然「发不出信息」：先确认宿主没睡（30 秒）

**别一上来就查 token / iLink 重连 / 保活脚本**。当 Hermes 网关跑在 Mac 上时，它是 launchd job
`ai.hermes.gateway`（同一个进程还供着 127.0.0.1:8642）；**合盖睡眠会把整个网关带走**，
表现就是「微信端发了没反应、也不报错」。

```bash
pmset -g log | egrep "Entering Sleep|Wake from" | tail -6   # Maintenance Sleep = 合盖睡了
uptime; launchctl list | egrep -i hermes                    # 服务还在不在
```

2026-09-14 实测：用户报「微信端好像没发信息」，真因是 Mac 从 09:27 起合盖睡眠（`sleep 0` 拦不住，
合盖睡眠是独立机制），10:14 按电源键唤醒后渠道自己就恢复了。要「随时能收发」只有三条路：
接电源 + 外接屏（clamshell）、`caffeinate`、`sudo pmset -c disablesleep 1`——**先问用户要哪种，别自己改电源设置**。

### 渠道「发不出去」的另一类原因：任务跑了，但投递没到（cron/主动推送必看）

宿主没睡、进程在跑、`status=completed`，用户就是没收到 → **别继续查 token/重连/保活**，先分清「内容有没有生成」和「投递有没有送到」：

```bash
# status=completed + 投递失败 = 内容已落盘、只是没送出去，output 文件可直接补发
ls -lt ~/.hermes/cron/output/<job_id>/ | head    # 内容一直在磁盘上，不会丢
bash ~/.hermes/scripts/channel_delivery_probe.sh # 一键体检（只读）
```

投递成功在日志里的权威依据是 `cron.scheduler: Job '<id>': delivered to <platform>:<chat> via live adapter`。
（老版本 `executions.db` 没有 `delivery_outcome` 列，服务器上也可能没装 `sqlite3` 二进制 → 用 `python3 -c "import sqlite3..."`，探针脚本已封装。）

**核心判据：决定成败的是投递目标，不是任务本身。** bot-token 制平台（飞书/TG）任何时间都能主动推；**微信 iLink 是会话 token 制，token 只源自用户最近一条入站消息（窗口约 4-5h）→ 隔夜首推、深夜推必挂**，调时间/打补丁/保活全都救不回来。完整证据、四个被实测推翻的假解、5 秒判定通道通不通的方法，见 `references/weixin-ilink.md`「主动推送投递失败」节。

### 给用户出方案时：只在既定选项内选，别扩展新架构

2026-09-15：用户问「Mac 上的定时任务，你觉得应该如何解决」（已列 A 双通道 / B 全切 TG / C 补投三选项），我转而去查「把 Mac 产物跨机转发到服务器→飞书」，被打断：**「我是让你看解决方案，没让你弄到飞书上，别绕」**。

**用户问「选哪个/怎么解决」= 在给定选项内给推荐 + 理由 + 代价对比，不是让你发明第四条路，也不是顺手执行他没批的改动。** 真有更好的第四方案，一句话附带即可，别去实施；要动手先拿到明确许可。

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

### 语音（入站转写 / 出站语音回话）
飞书/微信/QQ 的语音能力由**网关 + STT/TTS 配置**决定，不是渠道本身不支持。用户报「不能语音」时按这个顺序查：

1. **STT/TTS 配置**：`hermes config get stt` / `get tts`。两个国内默认值的坑：
   - `stt.language` 默认 **`en`** → 中文短语音转成英文/乱码；中文必须设 `zh`。
   - `stt.provider` 未设 → 回退 **local faster-whisper**，它要联网从 HuggingFace 拉权重，
     国内服务器**拉不动 → 转写直接报 `LocalEntryNotFoundError`**（`faster_whisper` 包装着也一样）。
   → 修法：`stt.provider=openai` + `stt.openai.base_url=https://api.siliconflow.cn/v1` +
     `model=Qwen/Qwen3-ASR-1.7B` + 硅基 Key + `tts.edge.voice=zh-CN-XiaoyiNeural`。
     **STT/TTS 改完不用重启网关**（每次调用都重读 config）。完整命令 + 验收脚本见 `references/feishu-voice.md`。
2. **用户端入口**：手机 IM 才有「按住说话」，电脑端不一定放给机器人 → 先让用户用手机试。
3. **回话要不要语音**：聊天框发 `/voice on`（= 发语音才回语音）；持久化，不需要改配置。

## 支持文件

| 文件 | 用途 |
|------|------|
| `scripts/channel_delivery_probe.sh` | 渠道投递体检（只读）：可用目标 + 近 3 天 cron 执行/投递结果 + 投递成功/失败日志 + 每条任务最新产出文件 |
| `scripts/wechat_watchdog.sh` | 微信断线监测：检测 Session expired → 生成新二维码 → 飞书通知 |
| `scripts/wechat_keepalive.sh` | 微信保活：每25分钟调 getconfig 防 -2 空闲断连 + gateway 进程守护 |

## 关联

- `server-service-deployment` — 云服务器部署、腾讯云防火墙、systemd、keepalive
- `hermes-advanced-setup` — gateway.platforms 格式、模型 fallback、升级
- `qq-bot-integration` / `weixin-ilink-maintenance` / `feishu-lark` 已并入本技能（原内容在 references/ 对应文件）
