---
name: markitdown
description: 文件格式转换——将PDF/Word/Excel/PPT/HTML等格式转换为Markdown，方便AI读取和处理。
---

# Markitdown（文件格式转换）

当需要读取PDF/Word/Excel/PPT等文件中的文字内容时，将其转换为Markdown格式。

## 使用方式

```bash
# 安装
pip install "markitdown[all]"

# PDF转Markdown
python -m markitdown input.pdf

# Word转Markdown
python -m markitdown input.docx

# Excel转Markdown
python -m markitdown input.xlsx

# PPT转Markdown
python -m markitdown input.pptx

# HTML转Markdown
python -m markitdown input.html
```

## 适用场景

- 读取PDF报告中的数据
- 提取Excel表格内容
- 将Word文档内容喂给AI处理
- 转换PPT内容为可读文本
