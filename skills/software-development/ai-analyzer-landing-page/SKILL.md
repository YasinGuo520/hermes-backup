---
name: ai-analyzer-landing-page
description: 方法论/技能产品化落地页——把任意分析框架(红蓝/六分身/市场调研/行业调研)做成网页：输入想法→DeepSeek按框架出结构化结论→卡片渲染。FastAPI单服务同端口(页面+API无CORS)+JSON模式+systemd+工具箱8900挂链。已在8920-8923验证4次。
---

# AI分析落地页（方法论产品化）

## 触发条件
用户要求把某个方法论/skill/工具做成网页，典型句式：「做成一个html页面，让人输入…给出结论，挂到工具箱/工具库下面」「跟红蓝一样」。这是 Yasin 产品化其方法论IP的标准模式（工具箱 130 工具都可能逐个产品化）。

## 架构（验证 4 次：8920红蓝/8921六分身/8922市场/8923行业）
```
FastAPI 单服务 = 静态 index.html + POST /api/analyze（同端口，无CORS）
  └─ POST /api/analyze → DeepSeek chat/completions（JSON模式）→ 前端卡片渲染
```
一个端口一个服务。**不要用 `python3 -m http.server`**——它不能处理 POST，页面会"点击没反应"。

## 标准步骤
1. **先查端口占用**：`ss -tlnp | grep <端口>` + `readlink /proc/<PID>/cwd` 确认该端口是否已在服务同一项目（用户可能之前已部署过，改版必须保持原端口——8920事故：改版前没查，用户点按钮无反应）
2. 建目录 `~/Desktop/hermes/<project>/`：server.py + index.html + images/ + static/
3. venv（PEP 668 必须）：`python3 -m venv venv && ./venv/bin/pip install fastapi requests 'uvicorn[standard]'`
4. systemd 服务（模板 templates/systemd.service），端口从 8920 起顺延
5. 工具箱 8900 卡片加链接（见下）
6. Hub 8895 加入口
7. 公网验证：页面 GET + POST /api/analyze 真实调用一次

工具箱卡片链接（加在 card-meta 之后）：
```html
<a class="card-link" href="http://43.138.221.174:<port>/" target="_blank" onclick="event.stopPropagation()">打开页面 →</a>
```

## 后端要点（脚手架 templates/server.py）
- **DeepSeek key 读 ~/.hermes/.env 的 DEEPSEEK_API_KEY**。config.yaml 里的 sk-gaw... 是 SiliconFlow 的（auxiliary.vision 用），拿去调 DeepSeek 报 401
- URL：`DEEPSEEK_BASE_URL`（https://api.deepseek.com/v1）+ `/chat/completions`；模型 `deepseek-chat`
- `response_format: {"type": "json_object"}` 强制 JSON 输出
- **max_tokens 按内容量**：单段结论 1600，六分身/多段 4500
- SYSTEM_PROMPT 必须内置 Yasin 铁律：
  1. 收入预测打折扣，不确定标「需验证」
  2. 区分「有数据支撑的结论」和「推断」，推断标注
  3. 空市场可能黑海不装蓝海
  4. 结论给「今天就能做的最小行动单元」
  5. 语气直接犀利，不鸡汤
- parse_json：剥 ```json 包裹 + 正则 `\{.*\}` 兜底
- 请求超时 150-180s（多段分析 30-40s 常见），前端 loading 文案轮播 3-4 条

## 前端要点
- **每个页面独立视觉风格**（Yasin 硬性要求，不重复）：红蓝=红蓝双色、六分身=六色渐变+六边形网格、市场调研=雷达青蓝、行业调研=星图金色
- 页面顶部展示「分析逻辑」面板（方法论步骤/公式/评分维度）——这是产品化的核心卖点
- 输入区：textarea + 按钮 + hint + loading（spinner + 轮播文案）
- 结果区：JSON 字段→分卡片渲染（summary/表格/清单/结论），判定自动变色
- fetch 用**相对路径** `'api/analyze'`（不带前导斜杠），兼容端口直连和 Nginx 子路径两种部署
- 所有动态内容过 esc() 防 XSS

## 陷阱
1. **点击没反应 = 静态服务器**：`python3 -m http.server` 服务的页面 POST /api/analyze 无人处理（501）。修法：把静态服务换成带 API 的 FastAPI（同端口）。
2. **config.yaml 的 key 不是 DeepSeek 的**：401 时先查 ~/.hermes/.env 的 DEEPSEEK_API_KEY。
3. **kill 服务用 `ss -tlnp` 找 PID**：`pgrep -f "<路径>/server"` 会匹配当前 shell 命令行把自己杀掉（exit -15）。
4. **browser_click 可能点不中按钮**：调试时用 `document.getElementById('btn').click()` 触发，再查 loading/result innerHTML 验证。
5. FastAPI mount /static 目录不存在直接启动失败（RuntimeError）——先 `mkdir -p static images`。
6. Nginx 反代后 `nginx -t` + `curl | grep <title>` 验证。

## 支持文件
- templates/server.py — 后端标准脚手架（.env key 读取/JSON模式/parse_json/health/静态挂载）
- templates/systemd.service — systemd 单元模板
