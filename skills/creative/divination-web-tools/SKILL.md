---
name: divination-web-tools
description: 玄学/AI娱乐工具站搭建（塔罗/八字/面相/AI抽签）。触发：塔罗、八字、面相、排盘、占卜。
triggers:
  - 塔罗
  - 八字
  - 面相
  - 抽签
  - 玄学
  - 排盘
  - 占卜
  - 紫微
  - 六爻
  - 算命工具
---

# 玄学/AI娱乐Web工具搭建（自托管·中国服务器）

> Yasin 服务器 Hub 上的「🔮 玄学」分类线：AI抽签(8914)+塔罗(8901)+八字(8902)+面相(8903)。每加一个新工具照本流程跑。成熟参考实现：`~/Desktop/hermes/{tarot,bazi,face}/`。

## 用户工作流铁律（本类任务先背）

1. **先复述确认，等「干」才动手**：Yasin 发任务常带「你看清楚没？先回答我确认后再开始动」——此时只回确认+执行计划+存疑点，**不做任何文件修改**（连只读调查都别做太多，他会问「你在干嘛」）。
2. **有现成 GitHub 方案直接部署，不自己写**（Yasin 原话：「如果 github 上面有现成的你直接部署就行啦。不需要自己写浪费 token 啦」）——动手前先搜 GitHub 现成 repo/库，用现成库（lunar-python 这类）不算自己写历法。
3. 确认没有现成/现成货改造代价更高（如 bazi-master 要 node+Postgres）时，**按最快捷完美方案自主拍板执行，别再问**（原话：「没有就按照你决定的最快捷完美的方式部署就行啦」）。

## 架构模板（每工具一个独立目录+独立端口）

FastAPI 单服务同端口：`GET /` → index.html + `app.mount("/static", StaticFiles(...))` + `POST /api/*` → DeepSeek。key 读法照抄 red-blue-method/server.py（读 `~/.hermes/.env` 的 `DEEPSEEK_API_KEY`，MODEL 硬编码 `deepseek-v4-flash`，严禁前端暴露 key）。模板可参考 `~/Desktop/hermes/red-blue-method/server.py` 与 `~/Desktop/hermes/face/server.py`（含模型链回退）。

- ⚠️ **static 目录必须先 mkdir 再启动**：`StaticFiles(directory=...)` 目录不存在直接 RuntimeError 崩（八字踩过）。
- 启动：terminal background=true 直接 `exec venv/bin/python -m uvicorn server:app --host 0.0.0.0 --port N`——**禁 `&`/nohup**（外层 shell 退出会杀子进程，日志空白）。每工具独立 venv（pip 装 fastapi uvicorn requests，几十秒）。
- 端口分配：玄学线已用 8901/8902/8903，新增从 8901-8909 空闲位或 8941+ 取（8920-8940 留给 company-agents），先 `ss -tlnp` 确认空闲。

## 卡图/素材资源（中国服务器）

- **Wikimedia Commons 从国内服务器直连不通**（curl 000）——别浪费时间，直接走 GitHub repo + jsDelivr 拉回本地：`https://cdn.jsdelivr.net/gh/USER/REPO@branch/path`。
- 拉完**必须本地化到 static/**（Yasin 环境铁律：前端零外网依赖）；jsDelivr 串行慢，用 `xargs -P 8` 并行。
- Rider-Waite 78张图源（mixvlad/TarotCards，公有领域）：命名 `tarot/rider-waite/720px/{NN_Name}.jpg`（大牌 00-21 英文名；小牌 Wands/Cups/Swords/Pents+01-14）。完整清单+前端数据生成见 `references/rw-tarot-images.md`。

## 排盘库：lunar-python（6tail，GitHub 现成）

历法算法零自写。lunar-python 与任务指定的 lunar-javascript 同作者同算法（服务器无 node 时用 python 版正当——先跟用户报备这个替换）。四柱/十神/藏干/纳音/起运/大运/流年 API 实测细节见 `references/lunar-python-bazi.md`。

## AI 解读链

- 文字解读：DeepSeek 官方 `deepseek-v4-flash`（同 Hermes 主模型）。
- **视觉（面相）**：官方 `deepseek-v4-flash-vision-exp` 是**推理模型**——思考在 `reasoning_content`、正文在 `content`，`max_tokens` 必须 ≥3000（100 时 content 空、finish=length，别误判失败）；消息 content 用数组 + `image_url.url` 传 data URL。**做模型链回退**：官方失败自动切硅基 `Qwen/Qwen3-VL-4B-Instruct`。详见 china-ai-platforms「官方视觉模型实测」。
- **照片不留存**：前端 canvas 压缩到长边900px → toDataURL(jpeg .85) → POST base64 → 后端直接转发，用完即弃（imgData=''），服务器零落盘。

## 面相/玄学解读文案质量（Yasin 迭代 3 轮后的结论）

用户对解读文案的标准远高于「能用」——第一版 300-500 字结构化文案被评「太简单，不让人眼前一亮、不信任」。文案系统 prompt 是关键杠杆，先重写 prompt 再谈别的。最终验证有效的配方（测试 1926 字、结构完整、有「被说中」感）：

1. **必须从图片真实可见细节出发**（脸型/三庭/眉眼间距/鼻型/唇形/下巴/发际线/气色），先描述所见再解读；prompt 里明令禁止「你聪明善良重感情」类任何照片都套的万能话术。
2. **五段解读链**（用户亲自拍板的结构，比三段更有「断事感」）：特征 → 传统相法（一句老话点睛马上白话解释）→ 性格翻译 → **现状印证**（当下的你/别人怎么看你/行为模式）→ **往前看**（这半年/今年趋势：基于性格惯性的走向+「宜…」建议）。未来只讲趋势与选择、不承诺具体事件（天然合规）。
3. **惊喜模块**：【没人明说你的】2-3 条「被说中」式特质（制造共鸣）+ 俏皮金句收尾。敢下具体判断但保持积极建设性。
4. 完整结构：一眼印象 / 五官解码(每处走完五段链) / 没人明说你的 / 接下来这半年 / 今日锦囊。正文 900-1200 字。
5. **⚠️ 推理模型截断坑**：max_tokens 4000 时正文仍会断在结尾（finish=length 无提示，直接砍半句毁信任感）——用 **6000**，并 prompt 强制「结尾金句必须收完，宁可精简中间也不要中断」。
6. 照片不合规（非正脸/多人/光线差）开头先礼貌给重拍建议，再尽力解读。

已验证完整 system prompt 模板：`templates/face-reading-prompt.md`（直接可复用，含红线内嵌）。

## 合规红线（整个品类的安全底线）

每页 header/banner/footer 至少一处「仅供娱乐/文化参考」声明（做 3 处最稳）。**任何页面禁**：算命收费、改运、消灾、医疗健康断言、投资/收益承诺。系统性检查：`grep -nE '收费|付款|购买|改运|消灾|治病|医疗|投资|保证|注定|大灾|破解|开光' <所有 html>`——**既有页面内容也要扫**（AI抽签签文里「投资…都可一试」就是漏网，顺手替换成安全表述）。解读 system prompt 里也要内嵌红线（禁宿命化/恐吓，医疗投资引导到免责）。

## 导航 Hub 集成（hermes-hub）

导航页由 `~/Desktop/hermes/hermes-hub/build_hub.py` 生成（不是手写 html）。加工具三步：
1. PROJECTS 列表加/改分类 cat + item（port/name/desc/icon/color/tags，tags 带「仅供娱乐」）；
2. **PORT_KEYS 列表同步加新端口**（漏了在线检测不认）；
3. `cd hermes-hub && python3 build_hub.py` 重新生成（自动备份旧 index.html），grep 确认新 cat 落盘。

移动已有工具到新分类 = 从旧 cat items 删行 + 新 cat 加行，别留重复。

**⚠️ build_hub.py 是唯一真源（2026-09-07 事故）**：`python3 build_hub.py` 重新生成会**整页覆盖 index.html**——之前手动加进 index.html 的「⚙️ 公司流程化Agent」入口就这么丢了（用户发现投诉）。**任何 section/入口必须写进 PROJECTS，禁止手改生成产物**；公司Agent 现已在 PROJECTS 里。

**多工具分类 = 单入口卡 → 二级页（用户偏好）**：别在主 hub 平铺 4 张工具卡。分类只放一张入口卡，点进去是 hub 目录下的二级页再选工具（模式同 agent-hub.html）：玄学线 = `8895/xuanxue.html`（4工具：塔罗/八字/面相/AI抽签），公司Agent = `8895/agent-hub.html`。实现：build_hub.py 的 PROJECTS item 加 `"path": "/xuanxue.html"` 字段（URL = port+path，port 写 8895 让在线检测认），二级页直接放 `hermes-hub/` 目录由 8895 http.server 托管，样式抄 agent-hub 卡网格换主题色。

**前端日期/年份输入坑（八字踩过）**：`<select>` 年份做 100+ 项下拉移动端基本没法选；日期固定 1-31 不跟月份联动，农历小月选 31 后端报错「日期无法换算」像坏掉。正确做法：年份用 `input[type=number]`（隐藏 spin 箭头），日期下拉按公历大小月（`new Date(y,m,0).getDate()`）/农历 30 天上限联动刷新（月份/历法切换都触发）。

## 移动端「控件失灵」第一排查法：JS 语法崩（2026-09-07 八字血案）

八字页移动端症状：「年月日时性别都下拉不了、农历切换没反应、排盘点不动」。真凶**不是 CSS/遮挡**——是 render() 里一行超长嵌套内联 JS 括号写错（`WX[...'水')` 应为 `]`），**一个语法错误让整段 <script> 解析失败 → 全部 JS 不执行**：下拉没被填充（空，点了没反应）、事件监听没绑（按钮全挂）。

服务器无浏览器 console 时，排查顺序（**别先改控件类型/样式**——本次先改 input 类型、再怀疑 backdrop-filter，全白绕，最后 esprima 一把定位）：
1. **先静态验证 JS 语法**（30 秒）：`scripts/check_html_js_syntax.py <url|file>`（esprima parse 每个 <script> 块，报行号+上下文行）。
2. 语法 OK 再看：fixed 特效层遮挡（特效层 `pointer-events:none`，内容容器必须 `position:relative;z-index:1`）；iOS `backdrop-filter` 与原生 select/button 兼容（作为防御性移除无妨，但别当根因死磕）。
3. 最后才改控件实现（换 input 类型/静态 options 等）。

预防：别写超长一行「嵌套对象+三元链」的内联 JS（五行颜色映射那行就是坑），拆成常量 map；交付前对页面脚本跑一次语法检查（三个页面 tarot/bazi/face 都过 esprima 才算绿）。

## 验证节奏

每完成一个：curl `GET /` + 静态资源 + `POST /api/*` 真实跑一次（含真实图片/真实日期），再挂 hub。前端 JS 交互若服务器无浏览器，如实说明未做 UI 自动化验证，别假装。外网端口是否可达由腾讯云控制台防火墙决定，让 Yasin 浏览器自测，不通再给放行指引。

## 支持文件

- `references/lunar-python-bazi.md` — lunar-python 排盘 API 实测明细（Solar/Lunar 换算、EightChar 取数、大运/流年、男女顺逆）
- `references/rw-tarot-images.md` — R-W 78张图源命名规律+前端数据生成方式
- `templates/face-reading-prompt.md` — 面相解读已验证 system prompt 全文+请求体+模型链
- `scripts/check_html_js_syntax.py` — 服务器无浏览器时静态验证页面内嵌 <script> 语法（esprima），控件失灵第一排查工具
