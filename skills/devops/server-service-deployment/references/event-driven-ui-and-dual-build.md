# 让本地事件驱动前端可视化 + 同源双版本构建

**场景**：本地有事件源（语音桥 / 日志 / Agent trace），要让它驱动前端可视化（点亮模块节点、高亮正在干活的那个）。
**实测**：2026-09-12，Mac 自研语音 UI（桥 127.0.0.1:3210）+ 服务器演示站（apex.midage.icu）。

---

## 0. 先认清前提：本地能力浏览器拿不到

- 麦克风授权在**本机 Python 桥**手里，不在浏览器（Chrome 拿不到麦且静默不报错）→ 页面自己听不见用户
- 演示站部署在服务器上，访客浏览器里**没有你那台机的桥** → 事件驱动只能在「有桥的那台机」上生效

**这决定了产品形态**：
| 版本 | 跑在哪 | 有什么 |
|:--|:--|:--|
| 自用版 | 本机（localhost:3000） | 全功能：语音事件 → 节点点亮 |
| 演示版 | 服务器（`https://<子域>`） | 只显示服务端健康状态 |

**交付时必须写清这是设计而不是缺陷**，否则用户会以为演示站坏了。

---

## 1. 同源双版本：用环境变量分流（别改 launchd/systemd）

静态导出会让 `next start` 直接报错 → **一份配置喂两台机必然崩**。用 env 变量分流：

```js
// next.config.mjs
const isStaticExport = process.env.APEX_STATIC === "1";
const exportConfig = isStaticExport ? { output: "export", images: { unoptimized: true } } : {};
export default { ...exportConfig, trailingSlash: true };
```

| 目标 | 构建命令 | 产物 | 谁跑 |
|:--|:--|:--|:--|
| 服务器演示站 | `APEX_STATIC=1 npm run build` | `out/` | nginx `root` 直出（0 进程） |
| 本机自用版 | `npm run build` | `.next/` | 原有 launchd `npm start`（**一个字都不用改**） |

比「复制两份源码」好的地方：改一份代码两端都吃到，不会漂移。

---

## 2. 运行时门控（不是构建时）：hostname 判断

```tsx
// 只有本机才去敲本机桥；演示站访客的浏览器没有这个桥
const hn = typeof window !== "undefined" ? window.location.hostname : "";
if (hn !== "localhost" && hn !== "127.0.0.1") return;
```

不门控的后果：**每个访客的浏览器都去 fetch 自己的 `127.0.0.1:3210`**（必失败，还拖慢首屏）。

配套两条：
- **组件级门控**：把依赖本地桥的面板（左侧对话/推理流）包进 `<LocalOnly>`，本机才渲染
- **跨机取数**：本机版要用服务器侧数据时，直接指向域名（`https://<子域>/api/status`），**不能用相对路径**——本机没那条路由

---

## 3. 事件 → 可视化映射：可维护的写法

### 3.1 单一来源注册表 + 生成前端常量

名单/文案/端口/关键词**只写一份 JSON**，脚本生成前端常量，避免两处漂移：

```
<project>/agents.json  ──gen_agents_ts.py──▶  lib/agents.ts  ──▶  前端 import
```

改名单 = 改 JSON + 重跑生成 + 重建。**别在前端源码里手改名单**（那是下次漂移的起点）。

### 3.2 关键词别名放注册表，长词优先

```json
{ "key": "chief_of_staff", "zh": "统筹运营", "ports": [{"port": 8924}],
  "aliases": ["统筹", "运营", "驾驶舱", "总览"] }
```

生成时按 `alias.length` 降序排，避免「运营」抢走「运营流程」这类更长匹配。

### 3.3 匹配范围要收窄（否则一片乱亮）

| 消息角色 | 用什么匹配 | 为什么 |
|:--|:--|:--|
| `role=user`（用户说的话） | **关键词别名** | 主信号：「我说什么就亮什么」 |
| `role=tool` / 工具名 / 工具结果 | **端口号** `:89xx` 或 `/agent/89xx/` | 精确、无歧义 |
| `role=assistant` / reasoning | **不匹配** | 一长段话会点亮一大片 |

### 3.4 轮询 + 指纹去重

```tsx
const fp = msgs.map(m => `${m.role}:${m.ts||0}:${(m.text||"").slice(0,24)}`).join("|");
if (!fp || fp === prevFp) return;   // 没变就跳过 → 同一句话不会被反复点亮
prevFp = fp;
for (const m of msgs.slice(-5)) { /* 只看末尾 5 条 */ }
```

轮询间隔 1.6s 足够；桥侧加缓存（如 10s TTL）可以再省。

---

## 4. 验收：不能替用户说话时，怎么验规则

把注册表的别名规则**在 Python 里复刻一遍**，喂①真实桥日志 ②一组拟真语句，打印命中表。

实测输出（可直接当回归用例）：

| 输入 | 应点亮 |
|:--|:--|
| 帮我看看选品 | 选品 |
| 财务这个月怎么样 | 财务 |
| 竞品最近在推什么 | 竞品雷达 |
| 库存哪些要补货 | 库存管控 |
| 给我写条带货脚本 | 内容生产 |
| 这文案合规吗 | 合规审查 + 内容生产（双亮，可接受） |
| 让我说嘞。 / 今天天气不错 | **不亮**（无误触） |

**最后一步必须由用户真人说一句**——规则对 ≠ 链路通（转写质量、桥的会话归属都可能出问题）。

---

## 5. 改前端源码的纪律（批量拼接替换）

本类工作几乎全是「几百行源码里精准改十几处」，踩过的坑：

### ⚠️ `\1` 只在 `re.sub` 里是回填

```python
# ❌ 手写拼接："\1" 就是字面量，会被原样写进文件
src = src[:m.start()] + "\\1\n  // 新注释" + src[m.end():]
# → 文件里出现 \1 → next build 报 `Expected unicode escape`

# ✅ 手写拼接就老老实实把原文重复一遍；要省事就改用 re.sub(pattern, r"\1...", src)
```

本次连踩两次（两个文件各一次），都是靠真跑 build 才暴露。

### 其余四条

1. **每处替换带断言** `assert src.count(old) == 1` —— 别让「匹配 0 次」静默通过
2. **正则别写太宽**：`(?:FROM|INTO)\s+(\w+)` 会把注释和无关词当表名 → 先小样本打印命中再批量
3. **每批改完必做两件事**：`grep` 残留（如残留 `\1`）+ **真跑一次 build**。只 grep 不 build 会漏语法错
4. **改前立基线**：非 git 仓库就 `cp` 到 `.baseline-<日期>/`；推送/覆盖远端前**先比对远端与你手上的指纹**（本次实测远端 3 个文件 md5 与基线完全一致 → 确认无别人的本地改动，才敢覆盖）

---

## 6. 一键回顾

```bash
# 服务器演示版
export APEX_STATIC=1 && npm run build && sudo rsync -a --delete out/ /var/www/apex/ && sudo chown -R www-data:www-data /var/www/apex
# 本机自用版：rsync 源码过去 → npm run build → 重启 launchd
launchctl kickstart -k gui/$(id -u)/<label>
```
