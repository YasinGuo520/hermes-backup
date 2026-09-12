# 自建语音/演示前端的可靠性（APEX 类）—— 实战配方

适用：页面跑在 **Chrome kiosk** 里 + 一个自建 **Python 桥**（录音/转写/TTS/唤醒/流式对话）
+ 通过 Hermes 的 **API server（:8642 `/v1/chat/completions`）** 让 agent 干活的架构。
三个坑都在真实演示中踩过，各附症状指纹与修法。

---

## 坑 1｜kiosk 里点 `target="_blank"` 等于「回不去主页面」

**症状**：用户在驾驶舱/看板里点了个入口跳走，然后说「**没法回退到主页面了**」。

**根因**：kiosk（`--kiosk` + 专用 `--user-data-dir`）**没有标签栏也没有地址栏**。
`target="_blank"` 确实开了新标签，但标签栏不可见 → 新页面盖在 kiosk 上，
用户看不到、也点不到任何返回入口，主观上就是「页面被换掉了/回不去」。

**救急（用户当场卡住时）**：

| 办法 | 说明 |
|:--|:--|
| 拍一下手 / 触发一次唤醒 | 桥的 `_RAISE_CHROME` AppleScript **会遍历所有窗口的所有标签，找 URL 含目标页的标签并切到前台** → 主页面标签其实一直都在 |
| `⌘ + W` | 关掉遮住的那个标签（标签其实存在，只是不可见） |
| `⌃ + Tab` | 在标签间切换 |

**根治（改设计，别指望用户记键位）**：

1. **入口按钮一律不跳新标签** —— 改成就地**全屏浮层**（同页 `position:fixed` overlay + iframe 内嵌目标页）。
   既拿到「像打开了新页面」的完整感，又永不离开主页面。
2. 浮层**顶部一条醒目的「← 返回驾驶舱」** + 底部提示「按 Esc 或左上角返回」。
3. 想边看主图边看子页面 → 再给一个「并排」按钮把浮层收窄到 ~76vw（**默认全屏**，因为侧滑会压住主图右侧一半，演示时主图的卖点就没了）。
4. **全仓搜一遍 `target="_blank"` 并删干净** —— 只改主按钮、留一个「单独打开 ↗」次要链接，用户照样会点到同一个坑（本次实测就是这么漏的）。

**iframe 能不能嵌，先查头（别猜）**：
```bash
curl -s -D - -o /dev/null --max-time 8 'https://<子域>/agent/8924/' | grep -iE 'x-frame|content-security|^HTTP'
# 无 X-Frame-Options / 无 CSP frame-ancestors → 可以嵌
```
⚠️ 用 `curl -I` 很可能撞 `405 Method Not Allowed`（不少 FastAPI 只挂 GET）——**用 `-D -` + `-o /dev/null` 拿头**，别用 `-I`。

**iframe src 的自适应**（同域直接相对路径；本机 localhost 版本跨域要走公网域名）：
```ts
function agentUrl(port: number): string {
  const h = typeof window !== "undefined" ? window.location.hostname : "";
  return (h === "localhost" || h === "127.0.0.1")
    ? `https://<公网域名>/agent/${port}/`
    : `/agent/${port}/`;
}
```
这些 URL 只在**点击之后**才渲染，所以没有 SSR/hydration 不匹配问题。

---

## 坑 2｜流式回答突然截断：客户端读取超时 vs 服务端心跳的**边界竞态**

**症状指纹**（桥日志）：
```
[ask] stream ended early after 47s: timed out
```
且用户侧表现为「**说一半就停了/像卡住了**」。同期日志里还能看到正在跑的工具被中断：
`[Command interrupted]`、`exit_code 130`（SIGINT）——**连接被关 → 服务端取消回合 → 工具吃 SIGINT**。

**根因（两边数值相等）**：

| 家伙 | 值 | 位置 |
|:--|:--|:--|
| Hermes 服务端 SSE 心跳间隔 | `CHAT_COMPLETIONS_SSE_KEEPALIVE_SECONDS = 30.0` | `gateway/platforms/api_server.py` |
| 自建桥的 socket 读取超时 | `VOICE_SILENCE = 30.0` | 桥源码 |

服务端只在**空闲满 30s** 时才补一个 `: keepalive\n\n`（0.5s 的 tick 只是轮询间隔，不是心跳频率）；
客户端读取超时也是 30s → **谁先到全看运气**。撞上「客户端先超时」就关连接、回合被打断。

⚠️ 桥源码里那句注释「keepalives land every 0.5 s」是**把 0.5s 的轮询 tick 误当成心跳间隔**，据此把
`VOICE_SILENCE` 设成 30 才埋下这个雷。**读别人的注释也要回服务端核对常量。**

**修法（改客户端，服务端常量不属自己）**：客户端读取超时设为心跳的 **2.5×**：
```python
# 必须明显大于服务端 SSE 心跳间隔，否则是「两边都 30s」的边界竞态
VOICE_SILENCE = 75.0        # 真正的死回合由 VOICE_HARD_CAP（总时长上限）兜底
```

**通用规则**：任何自建客户端消费 SSE/长连接，**读取超时必须显著大于服务端心跳间隔**（≥2×，
推荐 2.5×）。数值相等或客户端更小 = 定时炸弹。

---

## 坑 3｜问「介绍一下这个页面」，agent 却去抓网页 + `ls` 源码目录

**症状**：一句纯介绍性问题，耗时 **47 秒**（还撞上坑 2 被截断）。日志里 agent 真的在干活：
抓页面 HTML、提文本、`ls` 源码目录 —— 方向全对、力气全废。

**根因**：语音通道的 system prompt 里写着「**要动手查就直接动手**」（本意是鼓励干活、别怕用工具），
而 agent 并不知道这个页面是什么 → 最自然的动作就是去查证。**缺上下文，工具就成了唯一出路。**

**修法：把「它已经知道的东西」显式写进 system prompt**，并列一条禁止项：
```python
PAGE_CONTEXT = (
    "【当前场景】用户正对着 <页面名> 跟你说话：这个页面跑在你本机 <URL>（源码在 <路径>）。"
    "它就是 <一句话定位>，内容如下：<把页面上有什么、点了会发生什么、各种视觉状态的含义，"
    "逐条写清楚>。"
    "被问到「这个页面」「这是什么」「介绍一下」这类问题时：直接照上面这段回答，"
    "不要抓网页、不要读源码、不要 ls 目录 —— 那些信息你手上已经有了。"
)
# 语音路径：{"role": "system", "content": VOICE_STYLE + "\n\n" + PAGE_CONTEXT}
# 键盘路径同样注入（同一个坑在左侧面板打字时也会踩）
```

**实测效果**（同一句话，只改 system prompt）：

| | 改前 | 改后 |
|:--|:--|:--|
| 耗时 | 47s（还被截断） | **2.5s / 3.4s** |
| 工具调用 | 抓网页 + ls 目录 | **0 次** |
| 结果 | 断在半句 | 完整 339 字，事实全对 |

**通用原则**：给「省事就乱查」的 agent 提速，**最省力的做法是补上下文，不是加禁令**。
把「它该知道的事实」喂进去，工具自然就不再是唯一出路。

---

## 坑 4｜判断「要不要自己造语音能力」前，先盘官方有什么

**结论：Hermes 官方早就有这套，自建基本是重复造轮子。** 盘完再决定。

| 能力 | 官方状态 |
|:--|:--|
| Voice（麦克风说话 + 听回复） | ✅ CLI / TUI / desktop 三端同一套 |
| **唤醒词**（默认「hey hermes」，模型自带免训练；本地检测不联网） | ✅ 三端；引擎 openWakeWord / sherpa（任意词零训练）/ Porcupine |
| HUD 悬浮条（`⌘+Shift+H`） | ✅ 桌面端；**条的位置决定它理解你在问哪个窗口**（"这个/这里/那个页面"） |
| 打断（barge-in）、防幻听过滤、静音检测、流式 TTS | ✅ 均有 |
| **光点/星座式可视化总览** | ❌ **官方没有** —— 这是自建方真正独有的部分 |

**音频端点的归属（容易找错地方）**：

| 端点 | 位置 |
|:--|:--|
| `POST /api/audio/transcribe`、`GET /api/audio/voice-config`、`POST /api/audio/speak`、`WS /api/audio/speak-stream` | **dashboard web server**（`hermes_cli/web_server.py`），需 session token |
| `/v1/*`、`/api/sessions` | **API server（:8642）** —— **没有任何 audio 路由**，往它上面打 `/api/audio/*` 只会 404 |

也就是说：`hermes dashboard` 起着的机器上，自建前端可以直接复用官方 STT/TTS；
只起 gateway 的机器上不行。edge TTS 这类「只能在宿主跑」的 provider 会自动走 relay path。

**分工结论（本次拍定）**：

| 用途 | 用哪个 |
|:--|:--|
| 日常干活 | 官方桌面版（官方维护、不会再撞坑 2 这种自建雷） |
| 对外演示 / 客户门面 | 自建页面（官方没有可视化总览） |

**先查再答**：官方桌面版可能**早就装在用户机器上**了 ——
`ls -d /Applications/*Hermes*` + `defaults read <app>/Contents/Info.plist CFBundleShortVersionString`
（本次实测：用户以为没有，实际 `/Applications/Hermes.app` 已在，只是没在用）。

---

## 验收清单（改完必跑，别只说「我以为好了」）

1. **产物里有新内容**：`grep` 构建产物（含所有 chunk）确认新字符串存在；
   注意 minifier 会把 `·` 之类转义成 `\xb7` → 精确整串可能搜不到，**改搜不含特殊符号的子串**。
2. **旧东西真清掉了**：`grep` 模板作者残留（社媒链接/他人品牌）应为 0。
3. **资源全 200**：抓首页引用的 `/_next/static/...` 逐个 curl。
4. **入口不留坑**：全仓搜 `target="_blank"`，确认只剩注释。
5. **跨域可控**：iframe 内嵌前先验 `X-Frame-Options`（用 `-D -` 不用 `-I`）。
6. **用户视角实测**：让用户手机打开公网地址看一眼 —— 服务端 curl 通不代表用户端体验对。
