#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""静态验证 HTML 内嵌 <script> 的 JS 语法 — 服务器无浏览器 console 时的第一排查法。

背景: 页面 JS 一个语法错误会让整段 <script> 解析失败、全部 JS 不执行,
症状表现为"下拉打不开/按钮没反应/控件空"(八字页 2026-09-07 血案)。

用法:
  python check_html_js_syntax.py <url|html文件> [<url2> ...]
  依赖: pip install esprima (放进任一项目 venv 即可)
"""
import re
import sys
import urllib.request

try:
    import esprima
except ImportError:
    sys.exit("需要 esprima: 先 pip install esprima (如 venv/bin/pip install esprima)")


def check_source(name, html):
    blocks = re.findall(r"<script>(.*?)</script>", html, re.S)
    print(f"{name}: {len(blocks)} 个内嵌 script 块")
    all_ok = True
    for i, s in enumerate(blocks):
        if not s.strip():
            continue
        try:
            esprima.parseScript(s)
        except Exception as e:
            all_ok = False
            pos = getattr(e, "lineno", 0)
            lines = s.split("\n")
            print(f"  ✗ 块{i}: 语法错误 L{pos}: {e}")
            for j in range(max(0, pos - 3), min(len(lines), pos + 2)):
                print(f"    L{j+1}: {lines[j][:110]}")
    if all_ok:
        print(f"  ✓ 全部语法 OK")
    return all_ok


ok = True
for arg in sys.argv[1:]:
    if arg.startswith("http://") or arg.startswith("https://"):
        html = urllib.request.urlopen(arg, timeout=15).read().decode("utf-8", "ignore")
    else:
        html = open(arg, encoding="utf-8").read()
    ok = check_source(arg, html) and ok

sys.exit(0 if ok else 1)
