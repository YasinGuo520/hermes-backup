# Gemini 接入 / 订阅 / 低价会员风险（2026-09-17 实测）

> 触发：用户问「Gemini 官网/下载地址」「Gemini 能像 GPT 那样干活吗」「闲鱼买的会员靠谱吗」「GPT 能调 Gemini 模型吗」。
> 所有 URL 均为本次实测可访问的官方入口；价格/额度带核查日期，转发给用户前若隔月请复核。

## 0. 一句话结论（先给判断，再给细节）

| 需求 | 走哪条 | 成本 |
|---|---|---|
| 只想用 Gemini 干活 | AI Studio 免费 key，或 **Gemini CLI**（个人 Google 账号登录） | **¥0** |
| 要官方订阅 | 美区 Apple ID 走 App Store 内购（App 内购才吃得进礼品卡余额） | 首年 $99.99 ≈ ¥720 |
| 想在别的客户端 / Hermes / n8n 里用 Gemini 模型 | Gemini 官方有 **OpenAI 兼容端点** —— 改端点 + key + 模型名三处 | 按量（有免费层） |
| 闲鱼「18 个月会员」 | ❌ 不买 | 见 §5 |

## 1. 官方入口（实测可用，全部需支持地区节点）

| 用途 | 网址 |
|---|---|
| Gemini 网页版 | https://gemini.google.com |
| 订阅 / 价格 | https://gemini.google/subscriptions |
| 桌面版总下载页 | https://gemini.google/desktop/ |
| Mac 版下载 | https://gemini.google/mac |
| iPhone App（美区） | https://apps.apple.com/us/app/google-gemini/id6477489729 |
| Mac 版使用帮助 | https://support.google.com/gemini/answer/17011627 |
| **支持国家/地区名单** | https://support.google.com/gemini/answer/13575153 |
| **AI Studio 拿 API Key** | https://aistudio.google.com/app/api-keys |
| Key 使用文档 | https://ai.google.dev/gemini-api/docs/api-key |
| API 定价 | https://ai.google.dev/gemini-api/docs/pricing |
| **OpenAI 兼容层文档** | https://ai.google.dev/gemini-api/docs/openai |
| Gemini CLI（开源仓库） | https://github.com/google-gemini/gemini-cli |

名单细节：加拿大 **在** 支持列表内；名单里另注「中国大陆（仅限 Workspace）」= **企业版 Workspace 账号在境内 IP 下是官方支持的**，这是唯一的合规路径。

## 2. ⚠️ 桌面 App 硬门槛：Apple Silicon —— 先查机器再推荐下载

官方要求（support.google.com/gemini/answer/17011627）：**macOS Sequoia 15.0+ 且 Apple Silicon**、8GB+ RAM、200MB 空间。

**教训（2026-09-17 实录）**：直接按官网把下载链接发过去，一查机器才发现用户这台是 **Intel i7-1068NG7（macOS 15.0.1 / 16GB）** —— 版本和内存都过，**芯片不达标，原生 arm64 应用装不了**。白跑一轮。

**动手前先查目标机（一条命令，跨机经 SSH 也一样）**：
```bash
sw_vers; uname -m; sysctl -n machdep.cpu.brand_string
# x86_64 = Intel → 官方桌面 App 免谈；arm64 = Apple Silicon → 可用
echo $(( $(sysctl -n hw.memsize) / 1073741824 ))   # 内存 GB
```
**别见着「MacBook Pro」就假设是 M 系**（2020 款 13" 是 Intel）。同类判断适用于任何「只有新版芯片能用」的桌面应用。

**Intel Mac 的替代**：① Chrome 打开 gemini.google.com → 菜单 → 保存和分享 → **创建快捷方式** → 勾「在窗口中打开」（Dock 有图标，接近 App 体验）② Gemini in Chrome ③ **Gemini CLI**（终端里干活，不挑芯片）。

官方 Mac App 的独有能力（值得知道，免得说错）：`Option + Space` 呼出；**Speak to Window** 按住 `fn` 在任意 App 里改文字/插内容/按描述生图（**暂仅英文**）。

## 3. 免费路径（首选，先推这个再谈付钱）

| 路径 | 额度 | 备注 |
|---|---|---|
| **Gemini CLI + 个人 Google 账号登录** | 60 次/分、**1000 次/天** | 开源 Apache 2.0、TypeScript、支持 MCP；`npm i -g @google/gemini-cli`（需 Node ≥20） |
| **Gemini API 免费层** | 约 10-15 次/分、**1500 次/天** | AI Studio 生成 key，**免绑卡** |
| Gemini CLI 用 API key | 250 次/天 | 低于账号登录额度，别混用 |

免费层模型分配会变（如 Pro 只给几次就降级到 Flash）——额度表要按时点复核，别当永久承诺转发。

## 4. 官方订阅价格（2026 春季后口径）

| 档 | 价格 |
|---|---|
| Google AI Plus | $4.99-7.99/月 |
| **Google AI Pro**（原 Gemini Advanced） | **$19.99/月** 或 **$199.99/年**，首年常促销 **$99.99** |
| Google AI Ultra | $99.99 / $199.99 月 |

**关键**：官方阶梯里**根本没有 18 个月这一档** —— 这是判断闲鱼货的第一把尺。

## 5. 闲鱼/淘宝低价会员：机制与风险分层

**四条门路（对号入座）**：

| 门路 | 商家怎么操作 | 用户怎么死 |
|---|---|---|
| 赠送资格拼接（最常对应「18 个月」） | 批量开短期套餐套取 Google 赠送的会员资格后倒卖 | 赠送期一过不续费 → 订阅中途失效，回头找商家已消失 |
| 共享号 | 一号卖几十人 | 随时被踢；**对话/文件在别人视线内** |
| 代充（黑卡/漏洞） | 盗刷卡或漏洞充值 | Google 追拒付 → 订阅取消，**甚至封号** |
| 学生优惠倒卖 | 转卖教育免费资格 | Google **正在成批清退**（2025-10~12 申领批次被回收） |

**价格 → 实为 什么（经验判据）**：<¥50「一年/18 个月」= 共享号或赠送资格拼接（高危）；¥100-300 = 代充（拒付/封号）；¥300+ = 可能是正常代购年付（仍需确认是否用自己的账号正规付款）。

**铁律：绝不把自己的主 Google 账号交给别人代充** —— 关联封号 = Gmail / Drive / 相册一起废，远贵过省下的钱。要试也只能用小号。

## 6. 「GPT 能不能调 Gemini 的模型」分层答案

| 问的是 | 答案 |
|---|---|
| ChatGPT 那个 App/网页里选 Gemini 模型 | ❌ 不能，OpenAI 自家产品模型锁死 |
| OpenAI 官方 API 调 Gemini | ❌ 不能，只出 OpenAI 模型 |
| **用「OpenAI 格式」的任意工具/客户端调 Gemini** | ✅ **能** —— Google 官方提供 **OpenAI 兼容层**（ai.google.dev/gemini-api/docs/openai），改端点 / key / 模型名三处 |
| 让 ChatGPT 主动「调用」Gemini | ⚠️ 需中间件或 MCP 桥接，社区有实现，非官方支持、不稳 |

**落地口径**（对不懂代码的用户就这么说）：凡是「OpenAI 兼容」的东西都能一键切 Gemini —— **Hermes** 加一个 Gemini provider、**n8n** 用 OpenAI Chat Model 节点改 baseURL、**服小助**同理。所以「想用上 Gemini 的模型」不需要买会员、也不需要绕 ChatGPT，一条 API key 就够。

## 7. 地区判定（把用户引到 SKILL.md 的结论）

`在此国家/地区无法使用 Gemini` 的排查顺序（先 IPv6 → 再 IP 干净度 → 最后才是账号地区）见本技能 SKILL.md 的「先查 IPv6，再查 IP 干净度」节。**加拿大在支持名单内**，别一上来就改 Google 账号地区（一年只能改一次）。

## 8. GCP $300 免费试用：开不开？（2026-09-17 实测）

用户截到 Google Cloud「$300 赠金 / 90 天」注册页问「这个要开吗」时的判定链路：

| 你想要 | 结论 |
|---|---|
| 只是想用 Gemini 聊天 / 生图 | ❌ 不用开 —— AI Studio 免费层够，还免绑卡 |
| **想用 Gemini Pro 级模型的 API**（免费层只有 Flash） | ✅ 值得开：$300 抵 Vertex AI 侧 Gemini，是目前唯一免费摸到 Pro 的正规路 |
| GCP 服务器 / 云主机 | ❌ 用不上（用户主力在腾讯云，境内延迟高） |

**必须知道的覆盖边界**：`$300` **不覆盖 AI Studio 的 Gemini API**（2026-03-02 之后开的账号），只覆盖 **Vertex AI 上的 Gemini**（2026-05 起改名 Gemini Enterprise Agent Platform）。

**三个硬前提 / 坑**：
1. **需要国际信用卡**（Visa/Mastercard 双币或全币种）—— 礼品卡、银联单币卡不行。**没卡就别折腾**：虚拟卡验证失败可能连累刚修好的 Google 账号被风控。
2. **资料类型没有公司就选「个人」**，别选「组织」（否则要编组织名，还可能触发企业验证）；**姓名/地址必须与信用卡账单地址一致**，否则卡验证直接失败。
3. **GCP 项目的「国家」改不了**（跟随付款资料）→ 项目地区不对就永远被拒，不是配置能救的。

**安全性（可放心）**：官方 FAQ 口径 —— 花完 $300 或 90 天到期后，**试用结算账号自动关闭，除非用户手动升级，否则不会被收费**。不是自动续费陷阱。

## 9. key 有效 ≠ 能用：403「Your project has been denied access」排查（2026-09-17 实测）

**症状**：用户拿到一条 key 问「你看下行不」。**列模型 200，任何 generateContent 全部 403**。

**判据（两步探针，别只看第一步）**：

| 探针 | 结果 | 结论 |
|---|---|---|
| `GET /v1beta/models?key=…` | 200 | key 本身**有效**（认证通过） |
| `POST /v1beta/models/<m>:generateContent` | **403 `PERMISSION_DENIED` + "Your project has been denied access"** | **项目级被封，不是 key 写错** |

**403 的三个常见成因**（按概率）：① **地区不受支持**（Google 官方排错文档原话：403 = 使用方式不符合服务条款，**一个常见原因是所在地区不受支持**）② 免费试用注册没走完（付款验证页没提交 → 项目半激活）③ 国内 IP 注册新账号被风控打标。

**同类实证**：社区 2026-04~07 一大批同款案例，**全新项目、AI Studio 新建的 key 同样 403**；gemini-cli GitHub issue 里巴基斯坦地区用户同症状 → 指向地区而非配置。

**处置口径**：
- 30 秒确认死因 → 让用户开 https://aistudio.google.com/ 左侧 **Projects** 页看**红色横幅**（官方排错文档让先看 AI Studio 与 Billing 页的 banner）。
- 是地区 → **停**，别再让用户啃 GCP 控制台（项目国家不可改，这是死路）。
- 替代路线（按省事排序）：① **Gemini 网页版**（消费端不受项目限制，用户已能用）② **OpenRouter**（一个 key 调 Gemini/GPT/Claude，不用跟 GCP 缠）③ 继续用 DeepSeek 做主力。
- 用户把 key 明文发到聊天里 → **提醒删掉重建**。

**⚠️ 顺带一条控制台常识**：GCP 里「Gemini Enterprise Agent Platform（原 Vertex AI）」的 API 密钥页按钮置灰「您目前无权创建 API 密钥」+ 黄条「启用结算」= **项目没挂结算 / 半激活**；而且该页自己标着「**应用默认凭据（ADC）**」是推荐方式 —— Vertex AI 的标准认证本来就不是 API key，**在这个页面上纠结 key 本身就是绕路**。个人用途直接去 AI Studio 拿 key。

## 10. 免费版的额度真相（2026-09 口径，转发前复核）

| 版本 | 上下文 | 额度规则 |
|---|---|---|
| **App/网页 免费版** | **32K**（不是 1M！） | 2026 起改成**按算力计、每 5 小时刷新**（不再是固定条数）；主要跑 Flash |
| AI Plus | 128K | 配额放大 |
| AI Pro / Ultra | **1M** | 大配额 |
| **API 免费层** | **1M** | 约 10-15 次/分、**1500 次/天** |
| Gemini CLI（账号登录） | 1M | 60 次/分、1000 次/天 |

**反直觉但关键**：**API 免费层比 App 免费版大方得多**（1M 上下文 vs 32K）→ 要长上下文就别在网页版里点，走 API/CLI。

**付费墙变化**：**2026-03-25 起 Gemini Pro 模型只对付费订阅开放，免费层用户只能用 Flash 模型** —— 所以「免费版能用」≠「免费版是最强的脑」。

## 11. 生图 / 生视频能力与取舍（用户问「Gemini 能生图片视频不」）

| 能力 | 免费版 | 付费 | 对电商的实际取舍 |
|---|---|---|---|
| **生图**（Nano Banana / Nano Banana Pro = Gemini 3 Pro Image、Imagen 4） | ✅ 有额度（按算力、5 小时刷新，**额度分散在 App / AI Studio / API 三处**，AI Studio 最集中） | 更高配额 | ✅ **值得用**：保持商品一致性（换背景/换场景不变形）是它的看家本事，正是主图/详情页要的 |
| **生视频**（Veo 3.1 Fast，App 内） | **基本没有** | AI Pro 3 条/天、Ultra 5 条/天（$20/月起） | ❌ **别为它订阅**：量太小；短视频批量还是国内（火山 Seedance / 可灵 / 即梦）划算，且不需要梯子 |

## 12. 来源（防编造，可复核）

- 支持地区名单：support.google.com/gemini/answer/13575153（列 Canada / 中国大陆仅 Workspace）
- Mac 版要求与功能：support.google.com/gemini/answer/17011627
- Mac 版上线公告：blog.google「The Gemini app is now available on Mac OS」+ workspaceupdates.googleblog.com/2026/04
- 免费额度：github.com/google-gemini/gemini-cli（README 免费层）+ geminicli.com/docs/resources/quota-and-pricing
- 定价：gemini.google/subscriptions、ai.google.dev/gemini-api/docs/pricing
- 闲鱼机制：X @aulaylab 拆解帖（赠送资格批量套取）、什么值得买《官方价近两千一年，网上卖 15 块：Gemini 低价会员的 4 条门路》、知乎学生优惠清退分析
- GCP 试用/赠金：cloud.google.com/signup-faqs（到期自动关闭、不手动升级不收费）、docs.cloud.google.com/free/docs/free-cloud-features、klymentiev.com「Gemini Free Credits 2026: Why the $300 Trial No Longer Works」（2026-03-02 后 AI Studio API 不在覆盖内，Vertex AI 仍在）
- 403 项目被拒：ai.google.dev/gemini-api/docs/troubleshoot-ai-studio（403 = 不符 ToS / 常见原因是地区不受支持）、discuss.ai.google.dev 多个同款帖、github.com/google-gemini/gemini-cli issue #25749
- 免费版额度/付费墙：userightai.com/gemini-limits（算力计 + 5 小时刷新 + 32K/128K/1M）、blog.buildfastwithai.com（32K）、github.com/google-gemini/gemini-cli discussions/22970（2026-03-25 起 Pro 仅付费）
- Veo 配额：costgoat.com/pricing/google-veo（App 内 Veo 3.1 Fast = Pro 3 条/天、Ultra 5 条/天）
