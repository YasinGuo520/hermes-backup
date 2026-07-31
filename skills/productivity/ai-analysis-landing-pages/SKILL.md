---
name: ai-analysis-landing-pages
description: 把方法论/分析框架做成「输入想法→AI出结论」的落地页——FastAPI 单服务同端口 + DeepSeek JSON 输出 + 独立视觉风格 + systemd 守护 + 工具箱挂载。已落地：红蓝(8920)/六分身(8921)/市场调研(8922)/行业调研(8923)。
version: 1.0
author: Yasin + Agent
created_by: agent
---

# AI 方法论落地页（Methodology → Landing Page）

当用户要把某个分析框架/方法论（红蓝验证、六分身、市场调研、行业调研……）变成**访客可用的网页**——输入想法/方向，AI 按方法论跑流程给出结论——用本 skill。

核心模式：**FastAPI 单服务同端口** = 静态页面 + `POST /api/analyze` → DeepSeek → JSON → 前端渲染。页面顶部展示分析逻辑（方法论产品化），卡片挂到工具箱（8900）。

## 已落地实例（端口段 8920+）

| 端口 | 页面 | 服务目录 | 视觉风格 |
|:---:|:---|:---|:---|
| 8920 | 红蓝分析法 | ~/Desktop/hermes/red-blue-method | 红蓝双色对决 |
| 8921 | 六分身全方位分析 | ~/Desktop/hermes/six-persona | 六色渐变六宫格 |
| 8922 | 中国市场调研 | ~/Desktop/hermes/market-research | 雷达青蓝 |
| 8923 | 中国行业调研 | ~/Desktop/hermes/industry-research | 星图金色 |

## 标准架构

```
~/Desktop/hermes/<项目名>/
├── server.py          # FastAPI：静态页 + /api/analyze + /health
├── index.html         # 页面（内联CSS/JS，零外部依赖）
├── venv/              # fastapi + requests + uvicorn
└── static/ images/    # 空目录（FastAPI mount 需要存在，否则启动报错）
```

### server.py 关键点

- **同端口服务页面+API** → 无 CORS 问题，fetch 用相对路径 `'api/analyze'`（兼容子路径反代）
- **DeepSeek key 读取**：从 `~/.hermes/.env` 的 `DEEPSEEK_API_KEY` 读（回退内置）。⚠️ `~/.hermes/config.yaml` 里 `sk-gaw...` 开头的是 **SiliconFlow** 的 key（auxiliary.vision 用），不是 DeepSeek 的——拿错会 401
- **response_format json_object**：DeepSeek 支持，输出稳定 JSON，前端直接渲染。提示词里必须出现"JSON"字样且要求"严格 JSON，不要 markdown 代码块"
- **parse_json 容错**：剥离 ```json 围栏 + 正则提取 `{...}`，解析失败返回 raw
- `@app.mount("/static"...)` 前必须确保目录存在（FastAPI 启动即校验，缺目录直接 RuntimeError）
- 端口用 `os.environ.get("PORT", 892X)`，systemd 里 `Environment=PORT=892X`

### 提示词设计（方法论产品化的灵魂）

1. **内置方法论框架**：把对应 skill 的流程压缩进 system prompt（如六分身=六人设+每人含财务/周期/前瞻；行业调研=五维评分+年入千万公式）
2. **内置用户铁律**（每页必带）：
   - 收入预测打折扣，给保守值，不确定标「需验证」
   - 明确区分「有数据支撑的结论」和「推断/猜测」
   - 空市场可能是黑海不是蓝海，诚实判断
   - 结论必须给一个**今天就能做**的最小行动单元
   - 语气直接犀利，不废话不鸡汤
3. **数据诚实机制**（调研类页面）：
   - 所有数字标注来源类型：【训练知识】=模型训练数据 /【估算】=推算 /【需验证】=无法确认
   - 禁止编造具体报告名称和精确数字冒充实时数据
   - 页面顶部渲染 disclaimer：「基于模型知识综合，非实时爬取，关键数字需用数据源验证」
4. **max_tokens 给足**：六分身内容量大，4500；调研 3000-3500。单次请求超时 150-180s

### 前端页面要点

- **每个页面独立视觉风格**（用户铁律：不重复用同一套设计）。已用：红蓝双色 / 六色渐变 / 雷达青蓝 / 星图金色。新页面换新主题
- **页面顶部展示分析逻辑**：方法论步骤条 + 关键公式/金字塔卡片——这是"方法论产品化"的卖点
- 输入区：textarea（maxlength 800）+ 按钮 + loading 轮播文案 + hint
- 结果渲染：JSON 字段 → 结构化卡片/表格。`esc()` 转义防 XSS，禁止直接 innerHTML 拼 raw LLM 输出
- 交互：Enter 提交（keydown 监听）、结果 scrollIntoView

## 部署流程

```bash
cd ~/Desktop/hermes/<项目名> && python3 -m venv venv
./venv/bin/pip install -q fastapi requests 'uvicorn[standard]'
# systemd 服务 /etc/systemd/system/<名>.service：
#   WorkingDirectory + ExecStart=venv/bin/python server.py + Environment=PORT=892X
sudo systemctl enable <名> && sudo systemctl start <名>
curl -s http://127.0.0.1:892X/health
```

**公网**：腾讯云安全组需开对应端口（用户会自己加，但先测 `curl http://43.138.221.174:892X/`）。没开时可用 Nginx 子路径反代（80 端口已开）：
```nginx
location /<名>/ { proxy_pass http://127.0.0.1:892X/; proxy_read_timeout 180s; }
```
子路径部署时前端 fetch 必须用相对路径 `'api/analyze'`。

**工具箱挂载**：`build_toolbox.py` 的 SKILLS_DATA 条目加 `"url": "http://43.138.221.174:892X/"` → 重跑脚本 → 卡片出现「打开页面 →」（详见 html-project-hub skill）。Hub(8895) 也顺手加入口。

## 常见坑（实战教训）

1. **改版已有端口前必须查部署方式**：红蓝页 8920 原本是 `python3 -m http.server` 纯静态服务，没有 API 后端 → 用户点击"开始验证" fetch POST 无人处理 = 没反应。改版前先 `ss -tlnp | grep <端口>` + `readlink /proc/<PID>/cwd` 确认现有部署是静态还是 API 服务
2. **pkill/pgrep 自伤**：`ps aux | grep "[s]erver.py" | xargs kill` 或 `pgrep -f "server"` 可能匹配到当前 shell 命令行把自己杀了（exit -15）。用 `ss -tlnp` 找监听 PID 再 kill 最安全
3. **长 HTML 修改用 Python 精确替换**：patch 工具对长 old_string + 页面重复结构会模糊匹配误报（"Found 7 matches"）。用 `python3` 脚本 `s.count(old)` + `assert == 1` + `str.replace` 写回
4. **browser_click 可能点不中按钮**（自动化环境），但 `document.getElementById('x').click()` 有效。页面本身没问题时先用 JS click 验证，别误判成页面 bug
5. **vite/uvicorn 命令被误判为长驻进程**：终端工具看到命令含 uvicorn 关键词会拦截。拆开跑（venv 创建、pip install、import 验证分开）
6. **kill 后 systemd restart 顺序**：先停旧进程（nohup 起的），再 `systemctl daemon-reload && restart`

## 参考

- `references/red-blue-server-pattern.py` — 红蓝分析法 server.py 完整骨架（四段式文本解析版，改提示词即用）
- `references/six-persona-server-pattern.py` — 六分身 JSON 版骨架（response_format json_object）
- 对应方法论本体：project-four-persona-analysis / china-market-research / china-industry-research skills
