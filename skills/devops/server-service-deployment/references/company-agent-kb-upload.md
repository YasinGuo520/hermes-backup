# 公司 Agent 页「知识库批量文件上传」模式（train/8927 实测 2026-09-02）

**触发**：用户说「XX 导师/Agent 页面要加整个文件上传，一条条录入很麻烦」「拖文件批量导入知识库」。
16 个公司 Agent 页共用同一套骨架（FastAPI + static/index.html + common/db.py + common/llm.py），加批量上传 = 复制 train 的做法到目标 agent。

## 端到端三步

### 1. 建独立知识库表（别借用 selection_pool！）

原 train 页把文档塞进选品表 `selection_pool(title/price/sales/source)`，sales 字段只存 `text[:2000]`——**超 2000 字直接截断丢内容**。正确做法：common/db.py 的 `init()` 加独立表：

```sql
CREATE TABLE IF NOT EXISTS kb_docs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fname TEXT, title TEXT, content TEXT,
    csize INTEGER, created_at TEXT DEFAULT (datetime('now','localtime'))
);
```

粘贴入库（/api/doc）和文件上传（/api/upload）统一写 kb_docs，问答只查 kb_docs。

### 2. 依赖 + multipart 端点

```bash
cd ~/Desktop/hermes/company-agents && unset http_proxy https_proxy all_proxy
./venv/bin/pip install -q python-docx python-multipart pymupdf   # docx解析 / FastAPI UploadFile / pdf解析
```

FastAPI 处理 `UploadFile`/`File(...)` **必须装 python-multipart**，否则启动即报错/请求 422。

端点骨架：
- `POST /api/upload`：`files: list[UploadFile] = File(...)`，循环 `await f.read()`，按扩展名解析 → 逐篇 INSERT
- `POST /api/doc`：单条粘贴（保留旧 UI），写同一张表
- `GET /api/docs`：返回总数 + 最近 12 条（前端列表用）
- `POST /api/ask`：`SELECT title, content FROM kb_docs ORDER BY id DESC LIMIT 8`，每篇 `content[:1200]` 截断拼 ctx → `llm.chat`（资料没有的明确说不知道）

### 3. 文件解析函数（按扩展名，带降级）

```python
TEXT_EXT = {'.txt','.md','.markdown','.csv','.json','.py','.js','.ts','.html','.htm','.css','.xml',
            '.yaml','.yml','.ini','.cfg','.conf','.log','.sql','.sh','.bat','.cmd','.java','.go',
            '.c','.cpp','.h','.vue','.jsx','.tsx','.rb','.php','.lua','.r','.sass','.scss'}

def _extract(fname, data):  # -> (text, note)
    ext = os.path.splitext(fname)[1].lower()
    # .docx → python-docx：paragraphs + tables（row 用 ' | ' 连接）；空文字报"docx 无文字内容"
    # .pdf  → pymupdf：'import pymupdf as fitz'（旧 fitz 名 deprecated 仍可用）逐页 get_text；
    #         空 → "pdf 无文字层（可能是扫描件，请转txt）"
    # .xlsx → openpyxl read_only 逐行 '\t'.join 非空值
    # 其余按文本：utf-8-sig → utf-8 → gbk → gb18030 → latin-1 依次尝试 decode
    # .doc（旧版二进制）直接跳过："请另存为docx"
```

边界：单文件限 8MB；内容 <20 字跳过；入库截 MAX_STORE=100_000 字符；返回体给 `{ok, added, skipped, total, msg}`，msg 带跳过原因（最多列 6 条）。

## 前端要点（深蓝科技风页面）

- `<input type="file" id="fileInput" multiple hidden>` + 点击/拖拽区（`dragover` preventDefault、`drop` 取 `e.dataTransfer.files`）
- 用 `pending[]` 数组攒文件（拖拽/点选都 append），「上传文件」按钮 disabled 直到有文件；`acceptFiles` 后清 `fi.value=''` 允许重复选同一文件
- fetch：`FormData`，`fd.append('files', f, f.name)`，POST /api/upload
- 所有用户可见文本经 `esc()` 转义（标题/回答插入 innerHTML 前）
- 页面载入 + 上传/粘贴成功后调 `loadDocs()` 刷新计数+最近列表

## 重启与验证

- **改 app.py 要重启该端口**（静态页改动免重启）：`ps aux | grep "uvicorn train.app:app" | grep -v grep | awk '{print $2}'` → kill → `terminal(background=true)` 重新 uvicorn（禁止前台 `&`/nohup，见 SKILL.md 工作方式铁律）
- 实测闭环：造 md/docx/xlsx/pdf 4 个测试文件 curl `-F "files=@..."` 上传 → `GET /api/docs` 核对逐条 → `POST /api/ask` 问一个跨文档问题验证 LLM 带库回答 → **测完 DELETE 测试数据**（`DELETE FROM kb_docs WHERE title LIKE 'kb_test%'`），别污染真库

## 已装依赖记（company-agents 公共 venv，2026-09-02）

python-docx ✓ / pymupdf ✓（fitz import 有 deprecation warning 不影响）/ python-multipart ✓ / openpyxl ✓（原本就有）
