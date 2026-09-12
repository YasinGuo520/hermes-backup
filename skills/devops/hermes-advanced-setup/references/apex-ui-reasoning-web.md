# APEX-UI 光点图（ReasoningWeb）：是什么 / 为什么不亮 / 怎么点亮

> 场景：Mac 上那张全息语音页（`~/apex-src/APEX-UI`，Next.js:3000）+ Python 桥(:3210)。
> 用户拿的是 **开源模板 APEX-UI**（作者 Ruben Mouradian / Reznikov Engineering，MIT，**只有 UI**）。
> 2026-09-12 实地核代码得出。

## 一、先搞清楚它是谁的清单

README 里有一段「Not included (on purpose)」：作者生产版才有 **spoken-voice layer** 与 **“story” 剧情**，
开源版只给 UI 骨架。18 个光点（Chief of staff / Memory / Strategist / Researcher / Finance / Editor /
Sales / Marketing / Ops / Social / Engineering / Design / Developer / Analytics / CRM / Calendar / Email / Drive）
**是作者自己那家 3D 打印公司的 Agent 名单**（因此才有 Engineering=3D 打印参数）。
→ 用到真实业务上必须**重新映射**，别照抄。

| 光点数据 | 位置 |
|---|---|
| 18 节点 | `components/ReasoningWeb.jsx` L29-48 的 `ROSTER` |
| 每个节点的 role / caps / asks / status | `components/ApexWorld.tsx` L62+ 的 `INFO` |
| 点击后的卡片 | `AgentOverview`（`ApexWorld.tsx` L121 起，可拖拽窗口） |
| 三层颜色 | `COL = { consultant:#00e5ff, doer:#f5a623, tool:#7f9bb3 }`；节点半径 = 职责权重 |
| 左上 HUD | `ApexOverviewPanel.tsx`（时钟/天气/**作者残留社媒链接**） |
| 左侧操作台 | `ApexConsolePanel.tsx`（消费桥 `/log`；连不上桥就全死） |

**`ROSTER` 每条是 8 个字段的数组**（2026-09-12 读源码确认）：
```js
['chief_of_staff', 'Chief of staff', 'consultant', 250, 212, true, 18, 9]
//  key            label           layer          x    y   live bend  r
```
- `layer` ∈ `consultant | doer | tool`，决定颜色
- `live`（索引 5）= **常驻亮/暗**，手写布尔值；`live=false` 的节点画成虚线（`stroke-dasharray:'2 2'`）、半径压到 5.5、标签用 `labelDorm` 色
- `r` = 半径 = 职责权重（作者按自己公司画的）
- ⚠️ `ApexWorld.tsx` L47-61 **另有一份 ROSTER 副本**（支撑 `.visually-hidden` 的键盘/读屏 nav）——改名单**必须两处同步**，否则无障碍列表与图不一致。

⚠️ **对外演示前必清**：`ApexOverviewPanel.tsx` L26-28 还挂着模板作者的 Instagram / Facebook / LinkedIn（reznikov_engineering、ruben-mouradian）。这是最容易被忽略、演示时最尴尬的翻车点。

## 二、主功能是「看」，不是「点」（作者原意）

`ReasoningWeb` 由**后端 `trace` 事件**驱动：
```js
useEffect(() => { const ids = (trace.trace||[]).map(h=>nodeIdFromHelper(h.helper)).filter(id=>META[id]);
                   if (ids.length) apiRef.current.fire(ids) }, [trace?.n])
```
`fire(ids)` 做的事：被调用的节点端子发光 + 粒子沿路径流 ~1.15s、节点放大（5660ms 后回落）、2s 后复位；
**同一轮多个 agent 之间画临时连线**（~2.4s 消失）= 「这轮谁在干活、谁跟谁协作」。
`nodeIdFromHelper()` 剥掉 `ask_/call_/run_/fetch_/get_/delegate_to_/delegate_` 前缀后把工具名映射成节点 id
（`create_visual/render_visual/visual → design`）。

→ **方向上永远是：语音/打字 → 核心思考 → trace → 光点亮**。不存在「语音命令去打开某个光点」；
点击只是次要功能（原版弹该 agent 的 cockpit，开源副本弹 overview 卡）。别把用户往「语音开窗」带。

## 三、本机这份为什么是张死画

`ApexWorld.tsx`：`<ReasoningWeb state={webState} mode="full" coreless onSelect={…} />` —— **没传 `trace`**，
`fire()` 永远不被调用，只剩呼吸光晕 + 点击弹窗。这不是用户错觉，也不是配置出错，是开源版本来就缺神经。

### ⚠️ 别把两层「亮」搞混（2026-09-12 修正）

| 层 | 由什么决定 | 表现 | 能不能改 |
|---|---|---|---|
| **常驻亮/暗** | `ROSTER` 里的 `live` 布尔，**硬编码** | 一直亮着 vs 虚线暗点 | ✅ 换成实时健康探测 → **装饰画变仪表盘** |
| **瞬时脉冲** | `trace` prop → `fire(ids)` | 1.15s 端子发光 + 粒子流 + 2.4s 协作连线 | ✅ 从桥 `/log` 喂 |

所以「为什么是张死画」有两个独立答案：①脉冲层没接 `trace`；②常驻层是作者手写的 `live`，跟你系统的真实状态**毫无关系**。
只修 ① = 会动但不真（脉冲随机、状态假）；**修 ②才是把它变成仪表盘的关键**，且成本更低（前端定时探一次健康）。

## 四、点亮它的现成数据源（不用改后端）

桥 `apex-hermes-bridge.py` 的数据面：

| 端点 | 内容 | 能不能驱动光点 |
|---|---|---|
| `GET /state` | `{state: idle\|thinking\|speaking, session:{...}, source}` + `listening{active,conversation}` + `wake.seq` | ❌ 拿不到「这轮用了谁」 |
| `GET /log?limit=N` | 真实消息流：`role: user\|assistant\|tool`、`text`、`reasoning`、`tool`、`tools[]` | ✅ 有 tool 名 |
| `POST /listen` `/wake` `/ask` `/new` | 起止录音 / 拍手唤醒 / 打字问 / 清屏 | — |

做法：页面轮询 `/log`，把新出现的工具名包成
`trace={{n: 递增序号, trace:[{helper: 工具名}]}}` 传给 `ReasoningWeb`；再补一张「工具名 → 节点 id」映射表
（`nodeIdFromHelper` 已有前缀剥离逻辑，可扩展）。`ApexConsolePanel` 已是 `/log` 的参考消费者（渲染 ⚙ 工具链）。

⚠️ **未验项**：实际一轮会调到哪些工具名，要从真实对话的 `/log` 里拓（本机实测 `/log` 曾因会话重置返回 0 条）。
报方案时把这一条写清「未验」，别拿猜的映射表当交付。

## 五、端口绑定 / 跨机访问 / 安全边界（2026-09-12 实测）

| 件 | 绑定（`lsof -nP -iTCP -sTCP:LISTEN` 实测） | 含义 |
|---|---|---|
| 页面 Next :3000 | **`TCP *:3000`** | 页面**本来就能跳机/手机打开**（Tailscale 内） |
| 桥 :3210 | `TCP 127.0.0.1:3210` | 只回环，别的机器连不上 |
| Hermes API server :8642 | `TCP 127.0.0.1:8642` | 同上 |

- 桥的绑定是**硬编码**：`ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()`（约 1549 行）。
- 页面里 `http://127.0.0.1:3210` **写死 5 处**：`ApexConsolePanel.tsx:20,61`；`ApexWorld.tsx:260,297,306`。
  → 手机打开这张图时，它去连「**手机自己**」的 3210 → 控制台全死。**所以「手机端不能用」不是端口没开，是桥绑回环 + 地址写死。**

一条命令区分「服务挂了」vs「只绑回环」（从另一台机测）：
```bash
curl -s -o /dev/null -w "%{http_code}\n" -m 6 http://100.80.117.5:3000/    # 200 → 页面跳机可达
curl -s -o /dev/null -w "%{http_code}\n" -m 6 http://100.80.117.5:3210/state # 000 → 拒连（只绑回环）
```

### 🔴 桥没有入站鉴权，绝不绑 0.0.0.0
桥里的 `KEY`（读 `~/.hermes/.env` 的 `API_SERVER_KEY`）**只用于出站**调 Hermes API；
进来的 `/listen` `/wake` `/speak` `/log` **不校验任何 token**。而桥背后的 Hermes 有 **Mac 的 Desktop 全权限**
（读文件、跑任意命令）→ 一旦绑 `0.0.0.0`，网内任何设备都能拿这台 Mac。
要跳机访问只能：**只绑 Tailscale IP（100.80.117.5）+ 自己加一层 token**。
上报方案时先说这条，别说「把它绑 0.0.0.0 就能手机用了」。

### 「能不能把页面搬到服务器」的正确答法

| 部件 | 能搬 | 搬了有用吗 |
|---|---|---|
| 页面（Next） | ✅ | 有：不依赖 Mac 开机、多设备访问 |
| **桥（录音+ASR+TTS 调度）** | ⚠️ 技术上能 | ❌ **没用**：服务器没麦克风没喇叭，它听不见你、说不了话 |
| Hermes 本体 | ✅ 已在服务器 | — |

**页面搬走 = 只搬了脸**；耳朵嘴还在 Mac，Mac 一关机这张脸就只是装饰。
- 「人在 Mac 附近，手机当遥控器」：桥绑 Tailscale + token + 页面桥地址改可配置即可（录音仍是 Mac 的麦）。
- 「出门也能对着手机说」：手机浏览器 `getUserMedia` **必须 HTTPS**（iOS Safari 强制）→ 独立工程，别和「搬页面」混。
- 只想手机语音聊 → 走 **IM 渠道的语音消息**（飞书按住说话 + `/voice on`），0 开发，见 `china-im-channels` 的 `references/feishu-voice.md`。

## 六、改动前先核对 Mac 上那一份（不是镜像）

本地镜像 `~/Desktop/hermes/mac-apex-src/APEX-UI` 可能落后于 Mac 真身 `~/apex-src/APEX-UI`。
结论前先 `ssh mac@<ip> 'cd ~/apex-src/APEX-UI && grep -rn "trace" components/ app/ && git log --oneline | head'`。
构建：本地改 → rsync 到 Mac → **在 Mac 上** `bash -lc "cd ~/apex-src/APEX-UI && npm run build"`（node_modules 在 Mac）。

## 七、答用户这类「这功能是干嘛的」问题

先给**作者原意 + 代码/注释原文（带行号）**，再给中英对照表；不要只丢翻译。
然后把「能变真吗」拆成两层：**接线（纯前端改动，0 token）** vs **补服务（建分身/写服务，要时间要钱）**，
并推荐先做接线。未验的项明写未验。

---

## 八、接线成真驾驶舱：点击链路其实已经通了（2026-09-12 实测）

结论：**光点本来就能点**，卡住的不是交互，是「点开之后没出口」。

```
ReasoningWeb.jsx L186-189   透明热区 circle，r = max(rr+13, 17)
  hit.style.pointerEvents = 'all'   ← 父层是 pointerEvents:'none'（L315 + ApexWorld 包裹 div），
  hit.style.cursor = 'pointer'        靠子元素重新开启事件，注释原话「re-enables events for itself only」
  click → onSelectRef.current({ name: node.label, key: node.id, color: node.col })
ApexWorld.tsx L341          openAgent(n) → setSelected(n)
ApexWorld.tsx L472          {selected && <AgentOverview sel={selected} onClose={…} />}
```

**缺的三样**（这才是「装饰画」的真正原因）：
1. `AgentOverview` 卡片里**没有跳转真页面的按钮** → 只能看介绍，进不去
2. 卡片文案（`INFO` 的 caps/asks）是**模板作者的业务**（Engineering=3D打印参数等）
3. `live` 是硬编码，跟服务器真实状态无关（见第三节修正）

**改法（纯前端，0 token）**：改 `ROSTER` + `INFO` → 卡片底部加「进入驾驶舱 →」按钮 href 到真服务 → `live` 接健康探测。

## 九、演示版部署：两版分离 + 单网关绕 CORS

### 决策 1：状态探测走单网关，别改 N 个服务
前端直接 `fetch` 各 Agent 端口会被 **CORS 拦**；逐个给 N 个 FastAPI 加 `CORSMiddleware` = N 处改动易漏。
✅ 只在服务器加**一个** `/agent-status`：读各端口健康 → 返回 `{agents:[{key,port,online,ms}]}` + CORS 头 → 前端只认这一个地址。

### 决策 2：自用版 vs 演示版分开，不混用

| 版本 | 跑在哪 | 内容 | 用途 |
|---|---|---|---|
| 自用版 | Mac :3000 | 全功能：语音 + 桥(:3210) + `ApexConsolePanel` + 拍手唤醒 | 自己用 |
| **演示版** | 服务器静态导出 | 只要光点图 + HUD + 状态 + 跳转；**隐藏 `ApexConsolePanel`** | 发链接给客户 |

为什么必须分：`ApexConsolePanel` 依赖 Mac 的桥（且地址写死 `127.0.0.1:3210` × 5 处，见第五节）→ 静态导出到服务器后**控制台面板必然全死**，留着只会显得像坏了。

### 2026-09-12 网络实测（决定演示怎么发）
```bash
for p in 8924 8928 8930 8933 8935 8940 8895; do
  curl -s -o /dev/null -w "$p -> %{http_code}\n" --max-time 4 http://43.138.221.174:$p/
done   # → 全部 200
```
→ **服务器业务端口公网可达，演示可以直接发链接**，不必让客户碰 Mac。
端口占用实测：`8895` Hub、`8900-8903`/`8910-8917` 玄学站、`8920-8941` Agent 矩阵 → **8896-8899 空闲**（演示版候选）。

## 十、演示物四要素 + 防呆（给客户看之前自查）

| # | 要素 | 检查方法 | 常见翻车 |
|:--|:--|:--|:--|
| 1 | 公网可达 | 逐个 `curl -s -o /dev/null -w '%{http_code}'` | 只在 Mac 本地跑 → 客户打不开 |
| 2 | 状态是真的 | **停一个服务**，看光点 60s 内是否变暗 | 硬编码 `live` → 客户问「亮着是啥意思」答不上 |
| 3 | 点得进去 | 每个入口点一遍，到真页面而非介绍卡 | 卡片只有文案没出口 |
| 4 | 有内容 | 每个页面点进去不是空表 | 空表=自曝弱点 → 灌样例数据并**标注「演示数据」**，别冒充真实经营数据 |

**防呆（重要）**：不要为了让展示物「看起来完整」去建缺失模块。缺的**如实标 standby / 待建**（灰、虚线、暗点）——客户看得出这是真系统而不是 PPT，**「待建」比「假装都有」更可信**；建新模块 = 又一个多星期 0 收入。

**交付标准一句话**：不是「N 个光点全亮」，是**「发链接给客户，客户看得懂、点得进去、觉得这帮人有产能」**。

改码纪律（复用第六节）：本地镜像改 → rsync 到 Mac → **在 Mac 上** `npm run build`；源码 git 有 as-found 基线可退，不在 Mac 上手改。
