# Google Antigravity（反重力）2.x：实测配方

## 形态与入口（macOS）

| 形态 | 位置 | 能否脚本化 |
|---|---|---|
| 桌面 App | `/Applications/Antigravity.app`（Electron 外壳 + Go `language_server` 子进程） | ❌ 手动 |
| **`agentapi`** | `~/.gemini/antigravity/bin/agentapi` | ✅ |
| Remote Control | 浏览器 `antigravity.google.com` | 人机交互，非脚本 |
| `agy`（旧文档） | 2.x 上不存在 | — |

⚠️ **版本差异是大坑**：网上大量 `agy` CLI 文档、`--print`、`--print-timeout`、`--dangerously-skip-permissions` 全是 **1.x** 的。2.x 的本地入口叫 `agentapi`，而且它**不是独立二进制**——内容就一行：

```sh
#!/bin/sh
exec "/Applications/Antigravity.app/Contents/Resources/bin/language_server" agentapi "$@"
```

所以它**必须连到一个正在运行的 language_server**，桌面 App 关掉就全废。

## agentapi 三件套（本会话实测打通）

```bash
export PATH="$HOME/.gemini/antigravity/bin:$PATH"
LSPID=$(pgrep -f "language_server --standalone" | head -1)

# 1) CSRF：来自 language_server 的启动参数，每次启动随机，磁盘上没有 → 只能从进程 argv 读
export ANTIGRAVITY_CSRF_TOKEN=$(ps -p "$LSPID" -ww -o args= | tr ' ' '\n' | grep -A1 -- '--csrf_token' | tail -1)

# 2) 地址：language_server 监听多个口，逐个试（见下方探针阶梯）
export ANTIGRAVITY_LS_ADDRESS=127.0.0.1:<gRPC 口>

# 3) project_id：来自项目配置文件
export ANTIGRAVITY_PROJECT_ID=$(basename ~/.gemini/config/projects/*.json .json | head -1)
```

环境变量名的完整清单可以从语言服务器二进制里一次列全：

```sh
strings -a /Applications/Antigravity.app/Contents/Resources/bin/language_server \
  | grep -oE "ANTIGRAVITY_[A-Z_]*" | sort -u
# → ANTIGRAVITY_LS_ADDRESS / ANTIGRAVITY_CSRF_TOKEN / ANTIGRAVITY_LS_VERSION / ANTIGRAVITY_PROJECT_ID
```

**别猜**环境变量名，`strings` 一次列出比试错快十倍（`GOOGLE_GEMINI_BASE_URL` 也是同一批）。

## 子命令全集

```
agentapi new-conversation [--model=<flash_lite|flash|pro>] [--title=<t>] [--profile=<p>] <prompt>
agentapi get-conversation-metadata <conversation_id>
agentapi send-message [--title=<t>] <recipient_id> <content>
```

实测（flash_lite）。⚠️ **这条是写操作，不是探针**——它在用户账号里建了真实会话、烧了配额、在服务端留下记录。**跑之前必须先拿到用户明确同意**（见 SKILL.md 铁律 0）。要判链路通没通，用上面「探针阶梯」那条零配额命令，别用这条：

```sh
agentapi new-conversation --model=flash_lite --title="probe" "只回复两个字母：PONG"
# → {"response":{"newConversation":{"prompt":"只回复两个字母：PONG","conversationId":"<uuid>"}}}
# 同时生成 ~/.gemini/antigravity/conversations/<uuid>.db
```

**`--model` 只有 `flash_lite` / `flash` / `pro` 三档，全是 Gemini 系**——命令行选不了 Claude，Claude 要在 GUI 里切。这直接决定了「能不能把 Claude 自动化」的答案。

## 探针阶梯（0 配额，一条命令定故障层）

拿**只读且必然查不到**的调用当探针：`agentapi get-conversation-metadata probe-id`

| 返回 | 含义 |
|---|---|
| `connection reset by peer` / `error reading server preface: EOF` | 端口错（撞上非 gRPC 口），换口 |
| `code = Unauthenticated desc = missing CSRF token` | **端口对**，缺 CSRF |
| `project_id is required when providing project_env_config` | 认证已过，缺 project |
| `trajectory not found: probe-id` | **全通**，业务层正常 |

**业务错误 = 认证通过**，这是成功信号。同理 `new-conversation` 报 `failed to start conversation: ... project_id is required` 说明前面链路都已经对了。

一次把所有候选口试完：`scripts/antigravity-env.sh`。

## 未验证 / 别踩

- ⚠️ **`get-conversation-metadata` 返回的是会话配置**（workspace URI、plannerConfig、modelName、migrate 状态…），**不是对话正文**。要拿模型回复文本得走 `~/.gemini/antigravity/conversations/<id>.db` 或 `~/.gemini/antigravity/brain/<id>/` 的轨迹——**这条提取路径本会话没跑通，未验证**。别据此对用户承诺「已接进流水线」。
- 别按旧文档找 `agy`、`--print-timeout`、`--dangerously-skip-permissions`（1.x 旗标，2.x 不存在）。

## Remote Control（现成可用，先推这条）

开关在 `~/.gemini/config/config.json` → `userSettings.remoteControlEnabled`（同段还有 `remoteControlHostname`，形如 `192-168-1-102-super-aurora`，是显示名不是地址）。开了之后：任意浏览器登录 `antigravity.google.com` → 同一 Google 账号 → 实例切换里选机器 → 看/发任务、审计划、批工具调用、收完成推送（手机可加成 PWA）。

- **人机交互路径，不能脚本化**，但不需要装任何东西——是「让用户马上用起来」的最短路径，先给这条。
- 硬前提：宿主机器**开机 + 联网 + 未睡眠**（官方原话 must not be asleep or suspended）。机器睡眠后网络端口全断，必须先唤醒。

## 订阅能力边界（决策用；口径有冲突，必须实测）

- ⚠️ **「Pro 能不能选 Claude Opus 4.6」各路说法互相矛盾**：官方定价页把 Claude Sonnet & Opus 4.6 列在 `$0/month` 个人档，社区 issue 里却是直白的「opus 4.6 only for ultra sub」+ 选模型报 `may not exist or you may not have access`。**不要照搬任何一方的说法**——要判定就跑一次真实调用 / 看模型列表，以实测为准。
- **Antigravity 内的 Claude 是残血版**（社区口径）：思考预算被压到 ~1K token 量级，远低于模型上限，复杂多文件推理明显变浅。**Gemini 3.1 Pro 是原生模型、不受此限**，还有更大上下文和浏览器子代理——需要深推理优先用 Gemini 而不是在 Antigravity 里用 Claude。
- **配额池按模型系列独立**：吃掉 Claude 的额度不影响 Gemini 的额度；第三方模型另有**单独的固定限额**，所以「会员 token 很充足」这个前提对第三方模型不成立。
- **Scheduled Tasks 固定跑 Gemini Flash**，不能选模型——指望它无人值守跑 Claude 会落空。
- 具体额度数字官方不公布，**要实测**：斜杠命令（`/usage`、`/model` 一类）能打印真实剩余额度，但**必须单独跑一条命令**，塞进流式会话会把 JSON 流打断。

## 成本口径（回答「会员闲置是不是浪费了」）

- **包月订阅在配额内的调用不产生额外 token 费**；真正的持续开销来自按量付费的 API 渠道。所以「把它当后端用」边际成本≈0，**闲置才是纯亏**。
- 反过来说：让这类订阅接管原本走按量 API 的部分任务，省下的是 token 费，不是电费——别把两个账混在一起算。
- ⚠️ **但「边际成本≈0」不等于「应该接流水线」**——见下节。

## 结论：这个订阅该怎么用（定案）

**不要接自动化流水线，反代更不要碰。** 判据不是技术可行性（agentapi 已实测打通），而是风控看**请求模式**：人工触发、离散任务是正常用户；7×24 无人值守、高频、并行就是被清洗的特征。即使用官方二进制也只是踩灰线，做成常驻照样触发。

完整的封号实证（含付费订阅者、连坐 AI Studio/GCP、申诉无效、影子封禁不可恢复）与红线清单见 SKILL.md「封号红线」一节。

**给这个订阅的定位**：人工用 —— IDE 干活 + 手机/浏览器 Remote Control 远程盯任务；偶尔用 agentapi 跑**单次**任务可以，别做成 cron/常驻/网关。真要自动化，走按量付费的官方 API。

「会员闲置是不是浪费」的正确答案：**是浪费，但解药是「人拿它干活」，不是「把它变成 API」。**
