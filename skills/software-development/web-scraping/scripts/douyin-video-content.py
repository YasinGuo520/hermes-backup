#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抖音视频内容速取（无需登录）—— 在【真实桌面机】上跑，别在无头服务器上跑。

为什么：抖音详情接口有 Argus 风控（服务器/无头 curl 一律被拦），
但真实桌面机的系统 Chrome 打开 www.douyin.com/video/<id> 时，
页面免登录就把「章节要点」（平台 AI 生成的视频摘要）、标题、互动数、
评论区、推荐视频全部渲染进 DOM —— 读 innerText 即可，不用截图。

用法
----
  python douyin-video-content.py 7657446598594616390
  python douyin-video-content.py "https://v.douyin.com/E5yLsA5zhBs/"   # 短链自动解析
  python douyin-video-content.py <id> --chars 9000 --json /tmp/dy.json

依赖：playwright + 系统 Chrome（channel="chrome"，不要下 chromium，UA 才是真机）
  Mac 上现成环境：~/luopan-collector/venv/bin/python
  ssh mac@<mac-ip> "cd ~/luopan-collector && ./venv/bin/python /tmp/douyin-video-content.py <id>"

坑：
  - launch 用 headless=False（有头），别新建无痕 headless 实例
  - 不需要用户登录态 → 不必占用采集器那个持久 profile
  - 服务器侧只能做第 ① 步（curl 解析短链拿 aweme_id），渲染必须换机器
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request

UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 "
      "(KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1")


def resolve_aweme_id(s: str) -> str:
    """纯 HTTP 解析短链 → aweme_id（这一步服务器上也能跑，无风控）"""
    if re.fullmatch(r"\d{15,25}", s.strip()):
        return s.strip()
    req = urllib.request.Request(s, headers={"User-Agent": UA})
    final = urllib.request.urlopen(req, timeout=20).geturl()
    m = re.search(r"/(?:share/)?video/(\d{15,25})", final) or re.search(r"(\d{15,25})", final)
    if not m:
        raise SystemExit(f"无法从跳转结果解析 aweme_id: {final}")
    return m.group(1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="aweme_id 或分享短链")
    ap.add_argument("--chars", type=int, default=6000, help="innerText 截断长度")
    ap.add_argument("--shot", default="", help="可选：截图保存路径")
    ap.add_argument("--json", default="", help="可选：把结果写成 JSON")
    a = ap.parse_args()

    aweme_id = resolve_aweme_id(a.target)
    url = f"https://www.douyin.com/video/{aweme_id}"

    from playwright.sync_api import sync_playwright  # 延迟导入，方便只跑解析

    out: dict = {"aweme_id": aweme_id, "url": url}
    with sync_playwright() as p:
        b = p.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        ctx = b.new_context(locale="zh-CN", viewport={"width": 1400, "height": 900})
        pg = ctx.new_page()
        pg.goto(url, wait_until="domcontentloaded", timeout=60000)
        pg.wait_for_timeout(9000)  # SPA 拉取详情/章节要点需要这几秒
        out["title"] = pg.title()
        out["final_url"] = pg.url
        try:
            out["text"] = pg.inner_text("body")[: a.chars]
        except Exception as e:  # noqa: BLE001
            out["text_error"] = str(e)
        if a.shot:
            pg.screenshot(path=a.shot)
            out["shot"] = a.shot
        b.close()

    text = out.get("text", "")
    if "argus" in text.lower() and len(text) < 500:
        print("[WARN] 疑似命中 Argus 风控或 SPA 未渲染：换个真实桌面机重跑", file=sys.stderr)
    print(json.dumps(out, ensure_ascii=False, indent=1))
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
