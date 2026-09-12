# 语音回合被截断：SSE 心跳 vs 客户端超时的边界竞态（2026-09-12 定位）

> 适用：任何「服务端 SSE 流式 + 自建客户端边收边念」的组合。本案是 Mac 端 APEX 语音桥（`~/apex-src/apex-hermes-bridge.py`）调本机 Hermes `127.0.0.1:8642/v1/chat/completions`。

## 用户看到的现象

对页面说一句（「介绍一下这个页面」）→ **听到半句就没声了**，像卡住；稍后对话自己「结束」。不是进程死了，桥和页面都还健康。

## 根因一：两边都 30 秒的边界竞态（机制层）

| 家伙 | 值 | 位置 |
|---|---|---|
| 服务端 SSE 心跳间隔 | `CHAT_COMPLETIONS_SSE_KEEPALIVE_SECONDS = 30.0` | `~/.hermes/hermes-agent/gateway/platforms/api_server.py:269`（发射点在 ~5505 `if now - last_activity >= 30: write(b": keepalive\n\n")`） |
| 客户端读取超时 | `VOICE_SILENCE = 30.0` | `apex-hermes-bridge.py`（`urlopen(req, timeout=VOICE_SILENCE)` + `for raw in resp`） |

两者相等时「谁先到全看运气」：服务端只在 idle ≥30s 才发一次心跳，而客户端 30s 就超时。撞上「客户端先超时」→ 连接被关 → 服务端取消该回合 → **正在跑的工具收到 SIGINT**。

### 日志签名（找这两条就锁定）

```
[ask] stream ended early after 47s: timed out
```
```
{"output": "...\n[Command interrupted]", "exit_code": 130}   # 130 = SIGINT
```

伴随的会话记录会看到 assistant 正在跑工具 → tool 结果被中断 → assistant 只回 `Operation interrupted.`

### 修法

**客户端读取超时必须 ≥2× 服务端心跳**（给心跳留出「总是能等到」的余量）：

```python
# 桥 apex-hermes-bridge.py
VOICE_SILENCE = 75.0        # 2.5 × 服务端 30s 心跳
VOICE_HARD_CAP = 180.0      # 真正的死回合由这个兜底，别靠静默超时
```

⚠️ **桥里原有的注释是错的**：`"keepalives land every 0.5 s"` —— 0.5s 是服务端消费队列的 `asyncio.wait_for(stream_q.get(), timeout=0.5)` **poll 间隔**，不是心跳发射间隔。当时按这个错误前提把 `VOICE_SILENCE` 定成 30，才留下这个竞态。改这个常量时把与服务端常量的关系写进注释，避免下一个人又调回去。

> 通用规则：**任何 SSE/长流客户端的读取超时要显著大于服务端心跳间隔**（2× 起步）。只改客户端，别去动 Hermes 核心常量——那是上游文件，升级会丢。

## 根因二：语音回合里「该直接答的别去调查」（行为层）

同一次 47 秒里，大部分不是模型慢，而是 agent 把一句「介绍一下这个页面」当成了调查任务：抓页面 HTML → 提文本 → 又 `ls` 源码目录找数据。

### 修法（2026-09-12 实测有效，比「禁止调查」更根本）

**别写「不要抓网页」这种禁令 —— 要把「所指对象是什么」作为事实块注入 system prompt。**
agent 之所以去调查，是因为它手上**没有任何关于「这个页面」的事实**；给它事实，它就没了调查的理由，而且答案才对。

桥里的落地方式（`apex-hermes-bridge.py`，**语音流式 + 键盘面板两条路径都要注入**，否则在面板里打字问同样的问题还是去抓网页）：

```python
PAGE_CONTEXT = (
    "【当前场景】用户正对着 APEX 驾驶舱页面跟你说话：这个页面跑在你本机 "
    "http://localhost:3000（源码在 ~/apex-src/APEX-UI，Next.js），公网版在 https://apex.midage.icu。"
    "它就是 Yasin 的「AI 部门驾驶舱」，已经上线，内容如下：中央一个发光核心；外围 18 个光点代表 20 个"
    "真实 AI Agent —— 统筹运营(8924)、销售分析(8928)、……；点任意光点会弹出卡片，卡片底部有"
    "「打开驾驶舱 →」按钮跳到对应 Agent 的真实页面；光点亮=服务在线、虚线暗=离线，30 秒刷一次；"
    "你说话提到某个部门时对应光点会脉冲点亮。左侧是对话与推理流面板，左下角标着「演示环境 · 样例数据」。"
    "被问到「这个页面」「这是什么」「介绍一下」这类问题时：直接照上面这段回答，"
    "不要抓网页、不要读源码、不要 ls 目录 —— 那些信息你手上已经有了。"
)

# 语音（流式，_ask_hermes_stream）
"messages": [{"role": "system", "content": style + "\n\n" + PAGE_CONTEXT},
             {"role": "user", "content": prompt}]
# 键盘面板（_ask_hermes）
"messages": [{"role": "system", "content": PAGE_CONTEXT},
             {"role": "user", "content": prompt}]
```

**实测（同一句话，改动前后）**：

| | 改动前 | 改动后 |
|---|---|---|
| 耗时 | 47 秒（且被超时截断） | **2.5 秒 / 3.4 秒** |
| 工具调用 | 抓网页 + `ls` 源码目录 | **零** |
| 结果 | 断在半句 | 339 字完整且内容准确 |

> 通用化：任何「用户指着一个东西说话」的场景（看板 / 画布 / 正在编辑的文件），都要把**那个东西是什么**随消息显式注入，
> 不能假设模型知道用户在看什么。网页/桥拿不到别的窗口位置（那是桌面 App 的能力），所以只能显式注入 ——
> 这也解释了官方桌面版 HUD 为什么好用：`⌘+Shift+H` 那个**条的位置**就是这种注入的替代品。


## 排查顺序（别跳步）

```bash
# 1. 桥活着吗（idle 是正常的，不代表没卡）
ssh mac@<ip> 'curl -s --max-time 6 http://127.0.0.1:3210/state'
ssh mac@<ip> 'curl -s --max-time 5 http://127.0.0.1:3210/health'

# 2. 桥日志找截断签名（唯一能区分「真卡死」和「被超时截断」的证据）
ssh mac@<ip> 'tail -40 /tmp/apex-bridge.log'

# 3. 这次的会话实际发生了什么（tool 调用 → 中断）
ssh mac@<ip> "curl -s 'http://127.0.0.1:3210/log?limit=5'"   # 本地 parse，别在 ssh 里嵌 python heredoc

# 4. 两边超时值对齐检查
ssh mac@<ip> 'grep -nE "VOICE_SILENCE|VOICE_HARD_CAP" ~/apex-src/apex-hermes-bridge.py'
grep -n 'CHAT_COMPLETIONS_SSE_KEEPALIVE_SECONDS' ~/.hermes/hermes-agent/gateway/platforms/api_server.py | head -1
```

`/state` 里 `state: idle` + `speaking.active: false` + `listening.active: false` = **没有东西真的卡住**，是被截断后自己收尾了。别据此下「服务挂了」的结论。

## 改这个文件的纪律（Mac 端）

1. 改**本地镜像**（`~/Desktop/hermes/mac-apex-src/apex-hermes-bridge.py`），不在 Mac 上直接手改
2. **先比指纹确认 Mac 无本地漂移**：`md5 -q ~/apex-src/apex-hermes-bridge.py` vs 本地改动前的备份；不一致先查清楚
3. `rsync -az <本地> mac@<ip>:~/apex-src/apex-hermes-bridge.py`
4. 重启：`launchctl kickstart -k gui/$(id -u)/ai.hermes.apex-bridge`
5. 验证：`/health` 回 `{"ok": true}` + `grep -n 'VOICE_SILENCE = '` 显示新值

## 可复用的验收脚本（怎么证明「行为改好了」而不是「我觉得改好了」）

用**同一份 payload 直击 `8642` 计时对比**，别靠听。两个关键技巧：

**① 用 `ast` 取桥里的常量，不要 `import` 桥**（import 会启动服务/开线程）：

```python
import ast
tree = ast.parse(open(BRIDGE, encoding="utf-8").read())
consts = {}
for node in tree.body:
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id in {"VOICE_STYLE", "PAGE_CONTEXT"}:
                consts[t.id] = ast.literal_eval(node.value)   # 安全取值，不执行整个模块
```

**② `8642` 要鉴权，key 在 `~/.hermes/.env` 的 `API_SERVER_KEY`**（照抄桥的 `_api_key()`），
请求头 `Authorization: Bearer <key>`。忘了带 → `HTTP 401 Unauthorized`（**那不是模型问题，是没带 key**）。

脚本写在本地 → `scp` 到目标机 → 用该机 venv 的 python 跑。**别在 ssh 里嵌 python heredoc**（引号会被 shell 吃掉，
表现为「命令静默无输出」而不是报错）。同理：扫多文件/多分支的判断一律用 Python 写，不要用复杂 shell 一行流。

## 官方音频接口在哪（想把自己的 UI 接到官方语音管线时先看这里）

**`8642`（API server）没有任何 audio 路由** —— `/api/audio/*` 全在 **dashboard web server**
（`hermes_cli/web_server.py`）：

| 端点 | 行号 | 作用 |
|---|---|---|
| `POST /api/audio/transcribe` | ~5306 | 服务端转写（relay 路径，带幻听过滤） |
| `GET /api/audio/voice-config` | ~5400 | 取当前 profile 解析好的 STT/TTS 配置（含凭证） |
| `POST /api/audio/speak` | ~5549 | 服务端 TTS |
| `WS /api/audio/speak-stream` | ~5660 | 流式 TTS（WebSocket） |

要到这些端点得**跑 `hermes dashboard`**（桌面 App 的后端就是它；`web_server` 是独立进程/端口，不在 8642 上），
接口带 session token 校验。

官方桌面版自己怎么走（文档「Desktop remote: client-direct voice」）：开语音会话时先从
`GET /api/audio/voice-config` 取配置，然后**直连 provider**（录音直送 STT、回复文本在客户端本地合成）；
**只有「必须在宿主跑」的 provider（本地 whisper、`edge` TTS、command providers、插件）才回落到 relay**
（`/api/audio/transcribe` + speech WebSocket）。Yasin 的 TTS 正是 `edge` → 走 relay。

⚠️ **换成官方音频接口并不会修上面那个截断竞态**（竞态在 chat SSE 上，与音频链路无关）。
它是「少维护一套自研 STT/TTS」的收益，别当成 bug 修复承诺给用户。

## 相关

- 光点图的数据契约（`live` vs `trace`、桥只有 `/state /health /log /speaking /listen /wake /transcribe /speak`、无入站鉴权别绑 0.0.0.0）→ 本技能 `references/apex-ui-reasoning-web.md`
- 同一台机的 Hermes 网关修复配方 → `server-service-deployment` 技能 `references/mac-hermes-remote-ops.md`
- 自研语音 vs 官方桌面版（Voice / 唤醒词 / HUD）的能力对照 → 本技能 SKILL.md「语音·唤醒词·HUD 官方桌面版已有」节
