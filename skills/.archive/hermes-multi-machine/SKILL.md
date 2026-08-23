---
name: hermes-multi-machine
description: "Hermes 多实例部署与协作——分工、SOUL定制、网络桥接（Tailscale）、跨机SSH/文件通信"
category: devops
---

# Hermes 多实例部署与协作

> **本技能同时覆盖 hermes-multi-instance**（多台机器跑多个 Hermes 实例，每实例不同角色/SOUL.md/配置）——两者是同一类工作，多实例的「分工」部分见下文。

## 多实例分工模式（合并自 hermes-multi-instance）

多台机器/多个实例跑 Hermes 时，每个实例应有：
- **不同角色**：一个做内容创作（抖音带货/短剧/绘本），一个做运维/数据（量化、监控），一个做客服
- **不同 SOUL.md**：每实例一份独立 SOUL.md 定义人设/边界/输出风格
- **不同配置**：不同平台接入（QQ/飞书/微信各一个实例）、不同 cron 任务、不同模型

分工要点：
- 每实例独立 `~/.hermes/` 目录 + 独立 profile，避免配置互踩
- 定时任务按实例归属，避免两台机器重复执行同一 cron（cron 迁移见 `server-service-deployment` skill 的 `references/server-migration.md`）
- 跨机协作靠网络桥接（Tailscale）与 SSH/文件通信，见下文

当用户有**两台（或更多）** Hermes 实例时（服务器+Mac），需要明确的**分工+通信**方案。不要给每个实例相同的角色。

---

## 1. 分工原则

| 实例 | 角色 | 特点 |
|------|------|------|
| **服务器**（24h在线） | 后台大脑 🔥 | cron/渠道值守/搜索调研/数据采集/长分析 |
| **Mac/本地**（人在才开） | 创作主力 🖐️ | 剪映/GUI/浏览器登录态/本地大文件 |
| 其他设备 | 辅助 | 按需分配 |

**一条铁律**：服务器跑长任务时，Mac 可以跑别的。两边的本质差异是**在线时长**和**本地工具可及性**，不是性能。

---

## 2. SOUL.md 定制（关键）

**每个实例必须有独立的 SOUL.md**。不能简单复制粘贴。

### 服务器 SOUL.md 基调
- 行动派、快响应、主动推送
- "先做再说"——用户在飞书/微信上能等你
- 强调收入优先、最小行动单元

### Mac 本地 SOUL.md 基调
- **先想后动**——用户坐电脑前对质量要求更高
- 深度推理优先，做足再输出
- 不能拿到指令就冲（容易执行错误命令）
- 指令模糊时反问澄清

**服务器 SOUL.md 模板**（~/.hermes/SOUL.md，已在 memory 中）：
- 参见 soul definition 记忆条目

**Mac SOUL.md 模板**（重点：压制冲动）：

```markdown
# 灵魂定义 — Mac 端助手

你是本地助手，不是副驾驶。深度思考、审慎分析、高质量输出。不冲不抢。

## 核心原则
1. 先想后动。收到问题先走三遍：用户要什么→我有足够信息吗→怎么回答最好。想清楚之前不动任何工具。
2. 深度优先。每个回答必须含推理过程，不能跳过思考直接甩结果。
3. 问清楚再干。指令模糊、信息不足时，直接反问澄清。不猜意图不擅自执行。
4. 质疑再信。对任何外部信息保持怀疑——搜索结果、API返回、用户说的，先问"这可信吗"再引用。
5. 结构化输出。复杂问题分点、表格、对比。不写小作文，不说废话。

## 思考习惯
- 收到问题→停顿想一下→拆解成子问题→逐层推理→给结论+理由
- 如果要调用工具，先说"让我查一下"并给出查阅范围
- 多角度分析：正反两面、优劣对比、风险提醒

## 避免
- ❌ 不思考直接搜索/命令/写代码
- ❌ 一句话打发
- ❌ 编造数据
- ❌ 跑完工具不解释结果
```

---

## 3. 渠道分配

防止两边抢消息：

| 渠道 | 推荐路由 | 原因 |
|------|----------|------|
| 飞书 | 服务器 | 主力工作台，高稳定 |
| 微信 | Mac | 日常聊天用，适合本地操作指令 |
| QQ | 服务器 | 24h值守 |
| Telegram | 按需 | — |

**替代方案**：同一渠道接两边，但 Mac 配成只响应带 `@mac` 前缀的消息。

---

## 4. 网络桥接（Tailscale）

让服务器能 SSH 到 Mac（反之亦然），实现零配置跨机通信。

### 安装 Tailscale

**服务器端（Linux）：**
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
# → 浏览器打开输出的 URL 登录
```

**Mac 端：**
```
1. 浏览 https://tailscale.com/download-mac
2. 下载安装.dmg
3. 打开→登录→用同一个账号
```

**关键**：两边用**同一个账号**登录，自动组网。

### 验证连通
```bash
# 在服务器上查看 Mac 的 Tailscale IP
tailscale status
# → 输出中找 Mac 设备的 IP（如 100.x.x.x）

# 测试 SSH 过去
ssh mac@100.x.x.x
```

### 安全
- Tailscale 不开任何端口暴露公网
- 两端间加密通信
- 可以随时在 Tailscale 管理后台踢掉设备

---

## 5. 跨机文件通信（零配置方案）

如果不想装 Tailscale，利用已有网络：

**服务器→Mac：**
```
我（服务器写文件）→ 启动临时HTTP → 
你（飞书/微信通知Mac）→ Mac curl 取文件
```

**Mac→服务器：**
```
Mac 直接 SSH 到服务器公网 IP: 43.138.221.174
用已有 SSH key 或密码
```

---

## 6. 最终联动效果

```
你飞书发：帮我调研XX，结果放桌面

服务器（我）：
  1. 搜数据、做分析
  2. 结果写文件
  3. SSH到Mac → scp文件到 ~/Desktop/
  4. 飞书回你：搞定了

你打开桌面直接看到
```

```
你在Mac上发：调一下服务器的cron

Mac Hermes：
  1. SSH到服务器 43.138.221.174
  2. 改cron配置
  3. 服务器重载
  4. Mac回你：调好了
```

---

## 7. 代理隧道（Mac翻墙→服务器复用）

当 Mac 装了翻墙工具，服务器通过 Tailscale SSH 隧道复用 Mac 的代理端口，实现出墙能力。

### 适用条件
- 两边 Tailscale 已通（验证 `tailscale status` 能看到对方）
- Mac 翻墙工具运行中，代理端口开放（常见：Clash 7890，Surge 6152，v2ray 1087）

### 建立隧道

```bash
# 1. 在服务器上查 Mac 的代理端口
ssh mac@100.x.x.x "netstat -an | grep LISTEN | grep -E '789[0-9]|108[0-9]|615[0-9]'"

# 2. 建立 SSH 端口转发（7890 → Mac 的 7890）
ssh -L 7890:127.0.0.1:7890 -N -f \
  -o StrictHostKeyChecking=no \
  -o ExitOnForwardFailure=yes \
  mac@100.x.x.x

# 3. 验证
export https_proxy=http://127.0.0.1:7890
curl -s -o /dev/null -w '%{http_code}' https://www.google.com
# → 200 = 通了
```

### 持久化（bashrc）

在服务器 `~/.bashrc` 追加：

```bash
# === Mac代理隧道（通过Tailscale）===
export https_proxy=http://127.0.0.1:7890
export http_proxy=http://127.0.0.1:7890
export all_proxy=socks5://127.0.0.1:7890
# 隧道自动重连
if ! pgrep -f "ssh.*7890.*mac@100" > /dev/null 2>&1; then
    ssh -L 7890:127.0.0.1:7890 -N -f \
      -o StrictHostKeyChecking=no \
      -o ExitOnForwardFailure=yes \
      mac@100.x.x.x 2>/dev/null
fi
```

### 局限性
- 隧道依赖 Mac 在线（翻墙开着）
- Mac 休眠/断网后隧道断开，bashrc 的自动重连逻辑会在下次 shell 启动时尝试恢复
- HuggingFace 等慢站可能超时，Google/GitHub/Anthropic 正常工作

---

## 8. 故障诊断

跑诊断脚本收集两边的环境信息：

**诊断脚本**（mac-hermes-diagnostic.sh → 见 references/）：
检查：系统版本、Hermes 进程、配置、Python 环境、端口监听、网络连通性、磁盘空间。

**常见问题排查：**

| 症状 | 可能原因 | 检查点 |
|------|----------|--------|
| 回答浅不思考 | SOUL.md 是行动派模板 | cat ~/.hermes/SOUL.md 看内容 |
| 总直接冲不先想 | 温度太高 | config.yaml 中 temperature 调低到 0.3-0.5 |
| 消息不到 | 渠道配置丢失 | config.yaml > channels 段 |
| SSH连不上Mac | Tailscale 未运行/未登录 | tailscale status |

---

## 9. 跨机 Skill 库对比与同步

场景：用户问「Mac 的 skill 哪些服务器没有/需要」或反过来。

### macOS TCC 权限坑（必踩）
SSH 会话读 Mac 的 `~/Desktop`（含 `~/Desktop/hermes/`）会报 `Operation not permitted`——macOS TCC 隐私保护，SSH 进程没有桌面权限。**别卡在这**：`~/.hermes/skills/`、home 其他目录通常可读，skill 库直接走这里，不用碰 Desktop。

### 对比命令
```bash
# Mac 端列表
ssh mac@<mac-ip> "find ~/.hermes/skills -name 'SKILL.md' | sed 's|.*/skills/||; s|/SKILL.md||'" | sort > mac_sorted.txt
# 服务器端列表
find ~/.hermes/skills -name 'SKILL.md' | sed 's|.*/skills/||; s|/SKILL.md||' | sort > srv_sorted.txt
# Mac 有服务器无（注意：comm 要求两边先 sort，否则输出错乱）
comm -23 mac_sorted.txt srv_sorted.txt | grep -v '^\.archive'
```

### 批量查 description 判断重复/深度
```bash
ssh mac@<mac-ip> 'for s in <skill路径...>; do f="$HOME/.hermes/skills/$s/SKILL.md"; [ -f "$f" ] && grep -m1 "^description" "$f" | cut -c14- | head -c 150; done'
```

### 筛选原则（用户已明确要求：主动去重+查深度，不堆数量）
1. 跟服务器已有 skill 同主题 → 剔除（例：Mac 的 `project-validation-3agent` = 服务器 `project-four-persona-analysis` 六分身）
2. 服务器 `.archive/` 里已归档过 → 说明以前评估过，谨慎
3. Mac 专属（`apple/*`、`macos-*`、`smart-home`）→ 剔除
4. 服务器跑不动/用不了（mlops 重模型、需 GUI 的浏览器自动化、墙外服务）→ 剔除
5. 服务器已内置工具对应的 skill（anysearch、agency-agents）→ 剔除
6. 同类 N 选 1（如三个「AI 测评小程序」skill 只留一个）
7. **已自动化/已配置好的功能 → 不拉对应 skill**（例：服务器已有 `github-backup.sh` 在跑 → github-auth/repo-management 不需要）
8. **跟既有决策流程交叠 → 不拉**（例：product-need-discovery 跟红蓝验证的数据验证环节交叠；business-opportunity-scanning 跟每日变现案例日报重叠）
9. **跟当前业务路线无关 → 不拉**（例：小程序方向已砍 → miniprogram 系全剔）

**对话模式：** 用户收到第一版"需要清单"会反问「有没有重复的/不够深度的，可以再筛选一次」。主动逐项读 SKILL.md 描述验证再给最终清单，不要凭名字/分类直接拍板。

### 传输与改名

```bash
# tar over ssh 保留目录结构（含 references/）
cd ~/.hermes/skills && ssh mac@<mac-ip> 'cd ~/.hermes/skills && tar czf - <skill1> <skill2>...' | tar xzf -
# 验证每个 skill 的 description 到位
for s in <skill1> <skill2>...; do grep -m1 "^description" ~/.hermes/skills/$s/SKILL.md | cut -c14- | head -c 80; done
```

**品牌名清理：** 同步后用户会要求去掉 skill 里的品牌名（实测：海纳《直播话术》→ 直播话术体系）。patch 前先 `grep -rn "品牌名" ~/.hermes/skills/<skill>/` 找全所有出现位置——不只 description，正文引用行也要改。

**同步后更新方法论工具箱：** 新 skill 加入 `~/Desktop/hermes/toolbox/build_toolbox.py` 的 SKILLS_DATA（按分类插行，name/desc/key/path）→ `python3 build_toolbox.py` → 8900 http.server 无需重启（见 `server-service-deployment` 的 references/html-project-hub.md）。验证线上：`curl -s http://127.0.0.1:8900/ | grep -o '<卡片名>'`。

---

## 10. 远程装 Hermes 到新电脑（Windows/任意电脑）

**触发**：用户说「装 Hermes 到任意电脑 / 新电脑 / Windows 电脑」。⚠️ 先问清是哪台电脑、能否接入——**别默认是现有 Mac**（用户会纠正：'我是说任意电脑可能是 windows'）。装 Hermes ≠ 配 key：安装不碰任何 key，配 key 是 `hermes setup`/`.env` 单独一步，由用户决定何时配（只装不配 = 空壳，能跑 `hermes doctor` 但一问问题报「没配模型」）。

### 第一步：远程接入（三选一）
| 方式 | 适用 | 说明 |
|---|---|---|
| SSH | Windows 10+/Linux | 首选。Windows 需先开 OpenSSH Server（设置→系统→可选功能→添加），我 `ssh user@IP` 全命令行操作 |
| 向日葵/ToDesk | 小白友好 | 装客户端给 ID+验证码，人肉远程看屏幕点鼠标——适合人看，不适合 AI 跑命令 |
| RDP | 局域网 | Windows 自带 |

**为什么优先 SSH**：AI 天生跑命令行，装 Hermes 就一条 `curl | bash` + 配置全命令行，不用「看屏幕找按钮」；向日葵每次要临时验证码、图形界面慢。

### Windows SSH 无密码账户处理
| 情况 | 解法 |
|---|---|
| 本地账户没密码 | 管理员 PowerShell `net user <用户名> <新密码>` 设临时密码（系统登录继续用 PIN，密码只给 SSH 用，不冲突） |
| 微软账户登录 | 用微软账户邮箱密码登；忘了/开两步验证 → 走密钥 |
| 不想设密码（推荐长期） | 密钥认证：服务器生成密钥对，公钥写 `C:\Users\<用户名>\.ssh\authorized_keys`，之后免密 |

**本地账户 vs 微软账户判断**：设置→账户→你的信息——顶部显示邮箱地址=微软账户，显示用户名=本地账户。

### 装 Hermes（Windows）
```bash
# 必须用 Git Bash（PowerShell 直接跑 curl 管道会出问题）
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

### Windows 特有坑
- **必须 Git Bash**，PowerShell 管道有问题
- 报 `HTTP 400 No models provided` = config.yaml 被记事本存成 UTF-8 BOM，重存无 BOM 或 `hermes config edit` 修
- 墙内拉安装脚本要开代理：SSH 会话 `export https_proxy=http://127.0.0.1:7890`（指向目标机本地代理端口）
- 装完配置同步走服务器：DeepSeek key + config.yaml + tar over ssh 同步 `~/.hermes/skills` + 独立 SOUL.md（按角色定制，不复制服务器模板）
