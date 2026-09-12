# Next.js 静态导出 → nginx 直出：构建阻塞项 + 验收方法

> 2026-09-12 实测（APEX 驾驶舱 → apex.midage.icu，Next.js 15.3.8 + node v22 + nginx 1.24）
> 配套：`references/domain-subdomain-demo-hosting.md`（DNS/证书/nginx 那一半先看它）

**触发**：要把一个前端项目挂到域名下给外部看（演示物/客户入口），产物是 Next.js。

---

## 一、构建前必查：`app/api/*` 会让 `output: 'export'` 直接失败

**Next.js 静态导出不允许存在 API Route**。项目里只要有 `app/api/<name>/route.ts`，`next build` 就报错，整个导出做不出来。

```bash
find app -type f              # 先摸清 app/ 结构，别等 build 报错
ls -d app/api 2>/dev/null && echo '⚠️ 有 API 路由 → 静态导出会失败'
```

**处理**：把 API 路由**移到基线目录**（不是删），改成前端直连上游：

```bash
mkdir -p .baseline-<日期> && mv app/api/<name>/route.ts .baseline-<日期>/ && rmdir app/api
```

前端对应改动：`fetch("/api/weather")`（自有路由）→ 直连上游 URL。
⚠️ 副作用：原来靠自有路由隐藏访客 IP 的（如天气接口用 Vercel geo 头判断城市）在静态站上没了 → 把城市/lat-lon 写成常量，并在文件里注明「换城市改这两行」。

**先例**：APEX 的 `app/api/weather/route.ts` 就是这一刀，移走后才导出成功。

---

## 二、`next.config.mjs`（三行就够）

```js
const nextConfig = {
  output: "export",              // 静态导出：产物纯 HTML/CSS/JS，nginx 直出，不起 Node 进程
  images: { unoptimized: true }, // 导出不支持 Next 的图片优化服务
  trailingSlash: true,           // 生成目录式 index.html，配 try_files 更稳
};
```

构建：`npm install`（腾讯云已配 `mirrors.tencentyun.com/npm`，337 包约 23s）→ `npm run build` → 产物在 `out/`（本例 2.1M）。
`next build` 末尾的 `Exporting (n/n)` 出现才算导出成功；只看到 `Compiled successfully` 不算。

---

## 三、演示版 ≠ 自用版：按 hostname 决定渲染（一个 build 两处跑）

静态站上没有本机桥（如 Mac 的 `127.0.0.1:3210`）。照常渲染会**每个访客的浏览器都去敲自己的 localhost**（必失败、拖慢首屏）。

两个固定改法（别做两套 build，维护会散）：

**① 轮询本机服务前先判 hostname**
```tsx
const hn = typeof window !== "undefined" ? window.location.hostname : "";
if (hn !== "localhost" && hn !== "127.0.0.1") return;   // 演示站直接不敲
```

**② 本机专属组件用 `<LocalOnly>` 包住**（`components/LocalOnly.tsx`，`"use client"` + `useEffect` 里判 hostname 后 `setState`）——包住语音控制台这类「只有本机有后端」的面板。**页面组件是 server component 时不能直接判 window**，所以要这个小包装。

---

## 四、多端共用的名单：单一来源 + 生成器

名单/文案要同时被**前端**和**服务端脚本**（状态网关）读到 → 别两处各写一份（必然漂移）。

```
<project>/agents.json          ← 唯一真相源（人只改这里）
   ↓ scripts/gen_agents_ts.py  ← 生成器（断言替换数量，别静默改）
   ↓ frontend/lib/agents.ts    ← 前端 import
   ↓ gateway 直接 json.load()  ← 服务端读同一份
```

生成的文件顶部写明 `⚠️ AUTO-GENERATED —— 不要手改，改 agents.json 后重跑生成器`。生成器里把 tuple 形状也固定下来（例：`[key, label, layer, x, y, live, bend, r]`），前端 SVG 布局参数和业务字段一起维护。

**收益**：给光点加一个部门 = 改 JSON 一处；网关和前端同时认识它。

---

## 五、「实时状态」的第二种形态：常驻状态网关（vs cron 生成 JSON）

本 skill 已有 cron 生成 `real_data.json` 的形态（适合分钟级、无实时要求）。当**页面要显示 N 个服务的在线/离线**时，用常驻小网关更合适：

```python
# agent_status.py —— 纯标准库，零依赖、零 token、内存约 15MB
# 监听 127.0.0.1:8898，由 nginx 以 https://<域名>/api/status 对外暴露
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen

CACHE_TTL = 10   # 快照 10 秒内复用，防被刷

# 探活：urlopen(..., timeout=2.0)，200<=status<400 算在线，记录耗时 ms
# ThreadPoolExecutor(max_workers=12) 并发探全部端口
# 响应头：Content-Type: application/json; charset=utf-8 + Access-Control-Allow-Origin: * + Cache-Control: no-store
# log_message() 覆写为空 → 不写访问日志
```

nginx 侧（注意是 `location =`，精确匹配）：
```nginx
location = /api/status {
    proxy_pass http://127.0.0.1:8898/agent-status;
    add_header Access-Control-Allow-Origin "*" always;
    add_header Cache-Control "no-store" always;
}
```

**前端消费 + 回写 SVG 外观的两个要点**：
- 图**只建一次**，状态更新要**原地改属性**（`circ.setAttribute('r'/'stroke-width'/'opacity'/'stroke-dasharray')`），**不要靠改 props 重建图** —— 重建会打断正在跑的动画。做法：组件内暴露 `setLive(map)`，父组件用 `useEffect([liveMap])` 调它；另建一个「只在图建好后触发」的 effect（声明顺序放在构建 effect 之后）。
- 图是 SVG 一次性构建时，**标签元素要存引用**（`n.tickText = t`）否则改不了它的明暗/字号。

---

## 六、部署

```bash
sudo mkdir -p /var/www/<name>
sudo rsync -a --delete out/ /var/www/<name>/
sudo chown -R www-data:www-data /var/www/<name>
```

`--delete` 必加（否则上一版残留的旧 chunk 永远躺在那里）。改 `root` 下的静态文件**即时生效**，不用 reload nginx。

---

## 七、验收：三层，缺一层都可能「看起来好了」

### 层1 — 验产物（不是验「我以为改了」）

**双层字符串法**：新内容必须命中 **且** 旧模板内容必须为 0。

```python
blob = "".join(open(f, encoding="utf-8", errors="ignore").read()
               for f in glob.glob(f"{out}/**/*.js", recursive=True))
for k in ["<新加的中文/标识>", "<新按钮文案>"]:  assert blob.count(k) > 0
for k in ["<模板作者社媒>", "<模板作者业务词>"]:  assert blob.count(k) == 0
```

**⚠️ terser 会转义非 ASCII 标点**：`·` 被输出成 `\xb7`，导致 `"在线 · 系统正在运行"` 这种**整串精确匹配返回 0 次（假阴性）**。
→ 校验中文串时**搜更短的纯中文子串**（`"系统正在运行"` 命中），或先 `grep -o` 把上下文打出来看真实字节。别据此判定「没部署成功」。

### 层2 — 验线上资源

```bash
curl -s https://<域名>/ -o /tmp/i.html
grep -oE '/_next/static/[a-zA-Z0-9._/-]+' /tmp/i.html | sort -u \
  | while read -r u; do printf "%s %s\n" "$(curl -s -o /dev/null -w '%{http_code}' https://<域名>$u)" "$u"; done
# 全部 200 才算部署完整（任一 404 = 页面白屏）
```

### 层3 — 验「能自己活着」

**光看页面通不算**。做完保活接入后必须做一次**真实断线恢复测试**：

```bash
fuser -k <PORT>/tcp; sleep 2
ss -tlnp | grep <PORT> || echo "已停"           # 确认真的死了
<keepalive.sh 绝对路径> start; sleep 3
ss -tlnp | grep <PORT> && echo "✅ 保活自动拉回" # 确认自己回来了
```

---

## 八、踩坑速查

| 现象 | 根因 | 处置 |
|:--|:--|:--|
| `next build` 直接失败 | 存在 `app/api/*` 路由 | 移到基线目录，前端直连上游 |
| 只看到 `Compiled successfully` 没有 `Exporting` | 同上 / 配置没写对 | 确认 `output: "export"` 生效 |
| 页面能开、数据全空 | 页面 `fetch('/api/...')` 绝对路径 + 前缀反代 | 见 `domain-subdomain-demo-hosting.md` 第三节；**注意 `/api/xxx` 会返回 200（SPA 的 index.html 兜底）而非 404，所以静默失败极难发现** —— 用 `r.json()` 抛错才暴露 |
| 校验中文串数不到 | terser 把 `·` 转义成 `\xb7` | 搜短子串 |
| 演示站控制台一直空转报错 | 组件在调访客自己的 `127.0.0.1` | 轮询前判 hostname / 用 `<LocalOnly>` |
| 服务重启后消失 | 没进 keepalive，或只加进数组没加进 `check_all`/`fuser -k` 列表 | 见主 SKILL.md「全部 5 处」 |

---

## 九、批量校验用 Python，别拼多行 shell

`execute_code` 里跑**多行 shell + 嵌套 `$()` + 反引号 + 多层引号**（如 for 循环里再套 `$(... | sed ...)`）会**静默返回空输出**——不是报错，是没结果，极易误判成「扫不到 / 没有匹配」。

**做法**：
- 扫几十个文件、找字符串、统计命中 → **直接用 Python `open()/glob/re`**（最稳，结果确定）
- 要 shell 就**拆成单条简单命令**，一次一件事
- 校验类输出**必须能看到数字**（命中次数、状态码表），别只说「检查完了」
