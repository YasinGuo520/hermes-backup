# Hermes Desktop DOM 自检（CDP over 127.0.0.1:9222）

> 吸收自 bundled `inspecting-hermes-desktop-dom`（curator 合并）。用于开发 `apps/desktop` 且用户正在跑同一个 app（`hgui` / `npm run dev`）时——直接读**跑着的那个窗口**的真实 DOM/CSS，而不是从 `.tsx` 猜。

Dev-server 运行会自动打开 Chrome DevTools Protocol 端口（`127.0.0.1:9222`）。渲染进程就是 Chromium 页面，DevTools 能读的脚本都能读。

**它不能替代“看一眼”。** CDP 只能回答**事实**类问题（computed padding 是多少、这个元素渲染了吗、哪条选择器赢了）；美观/色协调/“是不是丑”仍要用户的眼睛或截图。事实归 CDP，审美归用户。

## 何时用

- 验证 UI 改动是否在跑着的 app 里生效
- “这个元素为什么还是 X？”——改任何代码前先找到真正获胜的规则
- 为即将改的组件找稳定选择器
- 检查设计 token 在真实节点上的 computed 值
- 读用户提到但拷不出来的 renderer console 错误

**不要用于：** 性能剖析/堆分析（用 node inspect），或真实问题其实是“这好看吗”的场合。

## 端口

任何 dev-server 运行都会在 `127.0.0.1:9222` 开端口；仅两种情况不开（`apps/desktop/electron/dev-cdp.ts`）：**打包构建**永远不开（无环境变量可覆盖）；**没有 `HERMES_DESKTOP_DEV_SERVER`** 时（unpackaged `electron .` 跑 `dist/` 的行为等同打包版）。`HERMES_DESKTOP_CDP_PORT` 可改端口（`=9333`）或关闭（`=off`）。

```bash
curl -s --max-time 3 http://127.0.0.1:${HERMES_DESKTOP_CDP_PORT:-9222}/json/version
```

空响应 = 没开端口，别默默猜另一个端口。**永远不要为了腾端口重启用户的 app**（会毁掉他的会话和状态）——要自己实例就另起一个隔离实例。

## 读 DOM

```bash
cd apps/desktop
node scripts/eval.mjs "document.querySelectorAll('[data-slot]').length"
```

多步任务用共享 client（自带 target 发现与 promise-aware eval）：

```js
import { CDP, SELECTORS } from './scripts/perf/lib/cdp.mjs'
const cdp = await CDP.connect({ port: 9222, match: '5174' })
const out = await cdp.eval(`JSON.stringify({
  radius: getComputedStyle(document.documentElement).getPropertyValue('--radius-scalar').trim(),
  composer: !!document.querySelector('[data-slot="composer-rich-input"]')
})`)
cdp.close()
```

`scripts/perf/lib/cdp.mjs` 的 `SELECTORS` 收着稳定的 `data-slot` 钩子（composer / thread viewport / assistant message / turn pair / profile rail）——优先用它们，别自创 `querySelector`。

## 最擅长的问题：哪条规则赢了？

样式“不生效”时把所有调用点改一遍是典型浪费。先读真实节点：

```js
const el = document.querySelector('[data-slot="aui_assistant-message-root"] a')
JSON.stringify({
  ownClasses: el.className,
  weight: getComputedStyle(el).fontWeight,
  parents: (() => { const out = []; let n = el
    while ((n = n.parentElement) && out.length < 6) out.push(n.className); return out })()
})
```

节点自己没有 class = 值是**继承**来的，扫调用点没用，要找祖先规则。插件样式表（如 `@tailwindcss/typography` 的 `prose a { font-weight: 500 }`）常赢过 utility class——在共享 class 上覆盖，别在每个使用处覆盖。

## 自己的隔离实例（无端口或不能扰动用户窗口时）

```bash
cd apps/desktop
HERMES_HOME=/tmp/cdp-probe-home \
HERMES_DESKTOP_DEV_SERVER=http://127.0.0.1:5174 \
HERMES_DESKTOP_CDP_PORT=9333 \
  npx electron . --user-data-dir=/tmp/cdp-probe-userdata
```

单独的 `--user-data-dir` 绕开 Electron 单实例锁（不会与跑着的 `hgui` 冲突），单独的 `HERMES_HOME` 隔开真实会话；端口也换个（93xx）。后台跑，用完 kill。

## 坑

- **绝不 kill 用户的 dev server/app“腾东西”**——中途 kill 会搞崩 Chromium socket pool，随后的 `ERR_NETWORK_CHANGED` 会被归罪于你刚改的东西。
- **临时 `HERMES_HOME` 没有后端**：app 会报 `hermes:api` `ECONNREFUSED` 并可能自行退出；渲染进程仍会 mount、DOM 可读——尽快读，别把自退的探针误判成端口坏了。Chromium 会打印 `DevTools listening on ws://127.0.0.1:<port>/...`，那行才是端口真开了的证据。
- **要轮询，不要只探一次**：刚启动的 app 要一两秒才应答。
- **绝不 dump 整个 DOM**（`outerHTML` 会淹掉上下文）——在求值表达式里先投影成小 JSON。
- **给 `CDP.connect` 传 `match`**：否则可能接到宠物悬浮窗、quick-entry 或 devtools target。
- **`cdp.eval` 返回的就是值**；裸 `Runtime.evaluate` 会双层嵌套（`.result.result.value`）。
