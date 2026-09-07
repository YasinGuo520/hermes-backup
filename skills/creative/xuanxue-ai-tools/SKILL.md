---
name: xuanxue-ai-tools
description: 玄学占卜类AI娱乐Web工具搭建：八字排盘/塔罗/面相/抽签，含排盘库与视觉特效配方。
triggers:
  - 玄学
  - 塔罗
  - 八字
  - 面相
  - 抽签
  - 排盘
  - 占卜
  - 星盘
  - 紫微
  - 六爻
  - 娱乐工具
related:
  - china-ai-platforms
  - ux-pro-max
  - server-service-deployment
---

# 玄学 AI 工具站（塔罗/八字/面相/抽签…）

> 一人公司娱乐工具页生产线。已上线参考：`~/Desktop/hermes/{tarot 8901, bazi 8902, face 8903}` + `fortune-wheel 8914`，入口 `http://43.138.221.174:8895/xuanxue.html`。

## 架构（每工具一个目录，互不干扰）

- **FastAPI 单服务同端口**：静态页 + `POST /api/*` → DeepSeek。key 一律服务端读 `~/.hermes/.env`（`DEEPSEEK_API_KEY`），前端零暴露。参考红蓝 `~/Desktop/hermes/red-blue-method/server.py`。
- 每个目录自带 venv（`python3 -m venv venv && venv/bin/pip install fastapi uvicorn requests`，另按需加库）。
- 启动：`terminal(background=true)` 直接 `exec venv/bin/python -m uvicorn server:app --host 0.0.0.0 --port N`（**禁 &/nohup**，进程由 hermes 托管）。
- server.py mount `/static` 前目录必须存在（`mkdir -p static`），否则 starlette 启动即崩。
- 模型锁死：`MODEL = "deepseek-v4-flash"` 硬编码（铁律，见 china-ai-platforms）。

## 八字排盘 → 用 6tail lunar-python（GitHub 现成历法库，零自写）

- `pip install lunar_python`（lunar-javascript 的官方 Python 移植，API 同源）。
- 公历：`Solar.fromYmdHms(y,m,d,h,0,0).getLunar()`；农历：`Lunar.fromYmdHms(y,m,d,h,0,0)`。
- 四柱：`ec.getYear()/getMonth()/getDay()/getTime()` 返回干支串（如 `庚午`）。十神：`getXXXShiShenGan()` 单字符串（日干是「日主」）；`getXXXShiShenZhi()` **数组**（对应地支藏干多个十神）。藏干：`getXXXHideGan()` 数组。纳音：`getXXXNaYin()`。
- 大运：`ec.getYun(1男/0女)`（顺逆自动）→ `getStartYear/Month/Day`（起运岁数）+ `getStartSolar()`（起运阳历）；`getDaYun()` 第 0 项是出生-起运前**空干支段，必须跳过**，从 1 开始；流年 `daYun[i].getLiuNian()`。
- 五行分布：天干五行 + 地支本气各计 1（展示层映射表手写即可，不算自写历法）。
- 前端农历日期：日期下拉上限 30（农历小月 29 会让库抛错）；公历日期要随月份联动 `new Date(y,m,0).getDate()`。**年份别用 select**（百项下拉移动端没法选），用 `<input type=number>`。

## 塔罗牌图源（Wikimedia 被墙）

Wikimedia Commons/upload 在国内服务器 curl 不通 → GitHub 图库 + jsDelivr 下载到本地 static：
`mixvlad/TarotCards` 的 `tarot/rider-waite/720px/{NN_Name}.jpg`（00-21 大牌；Wands/Cups/Swords/Pents + 01-14 = Ace..10,Page,Knight,Queen,King），78 张 ≈21MB。命名探路：`api.github.com/repos/<repo>/git/trees/HEAD?recursive=1` 拿全文件清单再批量 `xargs -P 8` curl jsDelivr。卡名中文映射用脚本生成 cards.js（勿手写 78 项）。

## 面相 AI 解读（vision 模型）

- 模型 `deepseek-v4-flash-vision-exp` 是**推理模型**：思考占 `reasoning_content`、正文在 `content`，长解读 max_tokens **≥6000** 否则正文截断；空正文自动回退硅基 `Qwen/Qwen3-VL-4B-Instruct`（MODEL_CHAIN 双链写法参考 face/server.py）。详见 china-ai-platforms「官方视觉模型实测」。
- 照片只过内存：前端 canvas 压到 ≤900px JPEG0.85 → dataURL → POST → 后端直转 LLM，不留存。
- **五段解读链 prompt（用户认可配方）**：特征 → 传统相法 → 性格翻译 → 现状印证 → 往前看。「往前看」必须写成趋势/选择（「你正在往…走，宜…」），禁承诺具体事件。模块：一眼印象/五官解码/没人明说你的（制造被说中惊喜）/接下来这半年/今日锦囊金句收尾。**必禁万能话术**（「你重感情」类任何照片都套得上的），强制从照片可见细节出发。

## 沉浸式视觉：只加层，不动功能 JS

- 背景特效全部独立注入（fixed inset 0 层 + 自包含 IIFE canvas），**不碰原功能代码**——四页已验证零破坏。
- 纪律：背景层 `position:fixed;inset:0;z-index:0;pointer-events:none`；内容容器 `.wrap` 需 `position:relative;z-index:1`（原静态内容会被 fixed 层盖住，这是最常见的「加了背景内容点不到」坑）。
- canvas JS：`const cv=document.getElementById('fx'); if(!cv) return;` 开头 guard，独立 IIFE 命名避免冲突。
- 风格库（每站一主题，用户要「各自神秘玄幻」）：塔罗=星空薄雾+旋转三层法阵环；八字=太极☯慢转+五行五色灵光按方位呼吸；面相=顶部月华呼吸+月白星光+上传框 hover 光晕；抽签=红金庙宇+香火烟雾(自带)。
- **环动画 transform 坑**：父环 `transform:translate(-50%,-50%)` + 动画要保留 translate；子伪元素环若复用同一 keyframes 会被 translate 带偏——拆两个 keyframes（带 translate 的父 / 纯 rotate 的子）。
- 字体标题辉光用 `-webkit-text-fill-color:transparent` + `drop-shadow` 动画时 filter 会被 animation 覆盖，keyframes 里要重复 filter 全值。

## 合规红线（硬性）

- 全站可见「仅供娱乐/文化参考」声明（页头+页脚）；照片不留存声明。
- 禁：收费/改运/消灾/医疗断言/投资建议/宿命化（注定/大灾/克X）。**扫描要覆盖旧内容**（抽签原有签文里查出「投资…都可一试」照样替换）。
- AI system prompt 里同步钉红线，输出风格给正例+负例。

## 导航入口（hermes-hub）

- **`build_hub.py` 是唯一数据源**：index.html 由它生成，手改 index.html 下次 rebuild 会被覆盖（公司Agent 入口因此丢过一次）。加项目只改 PROJECTS + PORT_KEYS 后 `python3 build_hub.py`。
- 工具集合做**单卡入口 → 同目录二级页**（如 `8895/xuanxue.html`，agent-hub.html 同款），build_hub.py 卡片支持 `path` 字段拼 URL。
- 玄学类卡片 desc/tag 都带「仅供娱乐」。
