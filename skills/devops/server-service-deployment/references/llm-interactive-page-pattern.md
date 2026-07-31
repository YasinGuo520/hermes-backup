# 交互式 LLM 页面模式（静态页 + LLM 后端）

**适用场景：** 方法论落地页/营销页加"输入想法 → AI 出结论"交互。Yasin 的红蓝分析法页面（red-blue-method，**端口8920**，systemd 服务名 `red-blue`，公网 `http://43.138.221.174:8920/`）是完整实测案例（2026-07-31）。

**⚠️ 端口历史（改版部署的教训）：** 页面原先是 `python3 -m http.server 8920` 纯静态部署（用户已知的地址）。改版加 API 时**必须原地升级到 8920**——不要开新端口（8918 安全组没开；Nginx IP 反代 80 也没用，因为用户仍访问 8920 旧静态版 → "点击没反应"，静态服务不认 POST）。先查现有部署再动：`ss -tlnp` + `readlink /proc/PID/cwd` + `ps aux | grep "[h]ttp.server"`。

## 架构：FastAPI 单端口 = 页面 + API（免 CORS）

一个 FastAPI 服务同时干两件事，页面和接口同源，前端 fetch('/api/...') 无需任何 CORS 配置：

```python
BASE_DIR = Path(__file__).resolve().parent

# 读取 Hermes 的 DeepSeek key（三级回退：环境变量 → ~/.hermes/.env → 内置默认）
_env = {}
_env_path = Path.home() / ".hermes" / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1); _env[k.strip()] = v.strip()
API_KEY = os.environ.get("DEEPSEEK_API_KEY") or _env.get("DEEPSEEK_API_KEY")
DEEPSEEK_URL = (_env.get("DEEPSEEK_BASE_URL") or "https://api.deepseek.com/v1").rstrip("/") + "/chat/completions"

@app.post("/api/analyze")   # LLM 接口
@app.get("/")               # FileResponse(index.html)
app.mount("/images", StaticFiles(directory=BASE_DIR / "images"), ...)
```

**坑：** `StaticFiles(directory=...)` 目录不存在 → 启动即崩。先 `mkdir -p`。

## LLM 结构化输出：后端切四段，前端只管渲染

不要前端解析 Markdown。让 LLM 按固定段标题输出，后端正则切段，返回 JSON：

```python
def parse_sections(content: str) -> dict:
    markers = ["蓝方提案", "红方攻击", "数据验证清单", "结论"]
    text = re.sub(r"^#{1,6}\s*", "", content, flags=re.M)   # 去 markdown 标题
    text = re.sub(r"^\*{1,3}\s*", "", text, flags=re.M)     # 去加粗符号
    positions = {m: text.find(m) for m in markers if text.find(m) >= 0}
    if len(positions) < 4:
        return {"raw": content}                             # 切不动就整段返回，前端兜底
    ordered = sorted(positions.items(), key=lambda x: x[1])
    result = {}
    for i, (name, start) in enumerate(ordered):
        end = ordered[i+1][1] if i+1 < len(ordered) else len(text)
        seg = text[start:end].strip()
        result[name] = seg[len(name):].strip(":： \n")
    return result
```

## 复杂结构输出：DeepSeek JSON mode（六分身案例，更稳）

四段式文本切分够用，但**六分身（6人×多字段）用文本切分就脆了**。改用 DeepSeek 原生 JSON mode，提示词里定义完整 schema，返回直接 `json.loads`，前端字段级渲染：

```python
json={
    "model": MODEL,
    "messages": [
        {"role": "system", "content": SYSTEM_PROMPT},   # 提示词里写死 JSON schema + 每字段中文说明
        {"role": "user", "content": f"我的项目想法是：{idea}\n\n请用六分身框架输出JSON报告。"},
    ],
    "temperature": 0.6,
    "max_tokens": 4500,                                  # 六分身内容量大，红蓝1600→六分身4500
    "response_format": {"type": "json_object"},          # 关键：强制 JSON
}
```

- **提示词必须出现 "JSON" 字样**（json mode 的硬性要求），并给出完整 schema 示例
- 解析容错：剥 ```json 标记 → json.loads → 失败再正则抓 `\{.*\}` → 都失败返回 raw，前端兜底显示"输出格式异常"
- 前端不再 md() 渲染：按 schema 字段名循环生成「标签+值」行（标签如 市场判断/获客策略/合规成本），每分身卡片一个主色
- `response_format` json_object 在 deepseek-chat 上实测稳定；schema 越具体，字段名越不容易漂

## System Prompt 必须内嵌用户方法论铁律

红蓝分析法案例的关键：不是让 LLM 自由发挥，而是把用户的差异化方法论写死进 system prompt：
- 四段式固定结构（蓝方提案/红方攻击/数据验证清单/结论）
- 结论三段判定：✅通过 / ⚠️观望 / ❌否决
- 铁律：收入预测打折扣、区分数据结论与推断、空市场可能是黑海、给最小行动单元、语气直接不鸡汤

这就是"方法论产品化"的引擎 — 访客输入想法，AI 跑用户的框架出结论。

## 前端交互（实测可用的最小集）

```html
<textarea id="ideaInput" maxlength="500"> + <button onclick="runAnalysis()">
<div id="ideaLoading" style="display:none"> spinner + 轮播文案 </div>
<div id="ideaResult"></div>
```

- **加载文案轮播**（每 2.5s 换一条：蓝方就位→红方开火→数据核对→出结论）— 把等待变戏
- **轻量 markdown 渲染**：先 HTML 转义（防注入），再 `**bold**`→`<strong>`，`- `→`<li>`，空行收列表
- **结论判色**：正则匹配 → 绿（通过/立项）/ 黄（观望）/ 红（否决/不建议），边框变色
- 卡片配色沿页面既有视觉体系（蓝卡片=提案 #3b82f6，红卡片=攻击 #ef4444，琥珀=验证）
- `textarea` 监听 Enter 提交（Shift+Enter 换行）
- 出错显示 `.rbl-err` 红字，不弹 alert

## 成本与部署

- 成本：DeepSeek 每次分析约 ¥0.01-0.02（几百 token），服务器 0 新增费用
- 部署：venv + systemd 服务（见 SKILL.md「生产持久化用 systemd」）。**直接复用页面已有端口**（8920 安全组已开）；新端口才需要 Nginx IP直连反代（80端口免开安全组）
- 限流兜底：接口校验 idea 非空、≤500字；LLM 超时 90s、前端 fetch 无超时但 loading 兜底
