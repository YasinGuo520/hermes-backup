---
name: markitdown
description: 文档转Markdown与OCR提取：markitdown、pymupdf、marker-pdf 三工具。
---

# 文档转 Markdown / OCR 提取

> 统一入口：把 PDF / Word / Excel / PPT / HTML / 扫描件变成 AI 可读的 Markdown 文本。
> 三条路径：① 有 URL → `web_extract` 优先；② 常规本地文件 → markitdown CLI（一键多格式）；③ 扫描件/公式/复杂版式 → pymupdf / marker-pdf（带脚本）。
> Word 结构化读取用 `docx` skill、PPT 用 `powerpoint`、PDF 增删改/表单用 `pdf`。

## 路径选择

| 场景 | 工具 | 说明 |
|------|------|------|
| 文档有 URL（arxiv/网页报告） | `web_extract(urls=[...])` | Firecrawl 转 Markdown，零本地依赖，**永远先试** |
| 常规 PDF/Word/Excel/PPT/HTML 本地文件 | markitdown CLI | 一键转换，`pip install "markitdown[all]"` |
| 文本型 PDF 批量/精细提取 | pymupdf（~25MB） | 秒级、含表格/图片/元数据，脚本 `scripts/extract_pymupdf.py` |
| 扫描件 OCR / 公式 / 复杂版式 | marker-pdf（~3-5GB） | 90+ 语言 OCR、LaTeX、阅读顺序，脚本 `scripts/extract_marker.py` |

## 1. 有 URL：先 web_extract

```python
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])
web_extract(urls=["https://example.com/report.pdf"])
```

本地提取仅在：文件在本地 / web_extract 失败 / 需要批处理时使用。

## 2. markitdown CLI（多格式一键）

```bash
pip install "markitdown[all]"
python -m markitdown input.pdf     # PDF
python -m markitdown input.docx    # Word
python -m markitdown input.xlsx    # Excel
python -m markitdown input.pptx    # PPT
python -m markitdown input.html    # HTML
```

适用：读取 PDF 报告数据、提取 Excel 表格、把 Word/PPT 内容喂给 AI。

## 3. pymupdf（轻量文本提取）

```bash
pip install pymupdf pymupdf4llm
# 用脚本（支持 --markdown / --tables / --images / --metadata / --pages）
python scripts/extract_pymupdf.py document.pdf --markdown
```

```python
import pymupdf
doc = pymupdf.open('document.pdf')
for page in doc:
    print(page.get_text())
```

**拆分/合并/搜索**也由 pymupdf 原生搞定（无需额外依赖）：
```python
# 拆分 1-5 页
new = pymupdf.open()
for i in range(5):
    new.insert_pdf(pymupdf.open("report.pdf"), from_page=i, to_page=i)
new.save("pages_1-5.pdf")
# 全文搜索
for i, page in enumerate(doc):
    if page.search_for("revenue"):
        print(i, page.get_text("text"))
```

## 4. marker-pdf（扫描件 OCR / 高质量提取）

```bash
# 先查磁盘空间（~5GB 需求）：python scripts/extract_marker.py --check
pip install marker-pdf
python scripts/extract_marker.py scanned.pdf                # OCR
python scripts/extract_marker.py document.pdf --json        # 带元数据
python scripts/extract_marker.py document.pdf --use_llm     # LLM 增强
```

marker 能力：扫描件 OCR（90+ 语言）、表格高精度、LaTeX 公式、代码块、表单、页眉页脚去除、阅读顺序检测。
**决策**：文本型 PDF 用 pymupdf；需要 OCR/公式/表单/复杂版式才上 marker（首次使用下载 ~2.5GB 模型到 `~/.cache/huggingface/`）。

磁盘不足时的答复话术："这份文档需要 OCR/高级提取（marker-pdf），需 ~5GB 装 PyTorch 和模型。可选：释放空间 / 提供 URL 走 web_extract / 用 pymupdf 只提文本型 PDF。"

## 5. Arxiv 论文

```python
web_extract(urls=["https://arxiv.org/abs/2402.03300"])   # 摘要（快）
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])   # 全文
web_search(query="arxiv GRPO reinforcement learning 2026")
```

## 坑 & 注意

- `web_extract` 永远是 URL 文档的第一选择。
- pymupdf 是安全默认：秒级、无模型、处处可用。
- marker-pdf 只在需要 OCR/扫描件/公式/复杂版式时安装；两个脚本都支持 `--help`。
- Word 用 `python-docx` 解析真实结构（优于 OCR）；PPT 见 `powerpoint` skill。
- 两个提取脚本：`scripts/extract_pymupdf.py`（文本/表格/图片/元数据/分页）、`scripts/extract_marker.py`（OCR/JSON/LLM 增强/磁盘检查）。
