#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""懒加载 / 分页形态探针 —— **只读**：不点任何业务按钮、不改任何数据。

为什么要有这个脚本：拿到一个后台列表页时，「猜接口 + 猜下一页按钮」的写法实测零产出。
先跑本探针一次，就能知道：真接口叫什么、列表是分页按钮还是无限滚动、真正的滚动容器
是哪个、滚轮能不能触发下一页请求。**判定完再写采集器。**

用法::

    python lazy-load-probe.py --url "https://host/path" --api-hint square/search_feed_author
    python lazy-load-probe.py --url "https://host/path" --scrolls 6 --wait 4

依赖：playwright（装在独立 venv；用系统真实 Chrome，免下 chromium）::

    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple playwright
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlparse


def main() -> int:
    ap = argparse.ArgumentParser(description="探针：判定列表页是懒加载滚动还是分页按钮")
    ap.add_argument("--url", required=True, help="列表页 URL")
    ap.add_argument("--api-hint", default="",
                    help="目标数据接口的 URL 关键字（留空则用同源 xhr/fetch 计数判断）")
    ap.add_argument("--profile", default=str(Path.home() / ".probe-profile"),
                    help="持久化 profile 目录（复用用户登录态，别每次重登）")
    ap.add_argument("--scrolls", type=int, default=4, help="试滚动次数")
    ap.add_argument("--scroll-step", type=int, default=1500,
                    help="每次滚轮像素（实测字节系表格 1500 ≈ 一页）")
    ap.add_argument("--wait", type=float, default=3.5, help="每次滚动后等待秒数")
    ap.add_argument("--headless", action="store_true",
                    help="默认有头：风控最干净，且用户能看到窗口")
    ap.add_argument("--channel", default="chrome", help="浏览器 channel，默认系统 Chrome")
    args = ap.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("缺 playwright：pip install -i https://pypi.tuna.tsinghua.edu.cn/simple playwright")
        return 2

    host = urlparse(args.url).hostname or ""
    xhr: list[str] = []
    hits: list[str] = []

    with sync_playwright() as p:
        Path(args.profile).mkdir(parents=True, exist_ok=True)
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=args.profile,
            channel=args.channel,
            headless=args.headless,
            viewport={"width": 1680, "height": 950},
            # 不传 user_agent：用浏览器原生 UA，避免与真机指纹不一致
            args=["--disable-blink-features=AutomationControlled"],
        )
        pg = ctx.pages[0] if ctx.pages else ctx.new_page()

        def on_request(req):
            try:
                u = req.url
                rt = req.resource_type
            except Exception:
                return
            if rt not in ("xhr", "fetch"):
                return
            if host and host not in u:
                return                      # 只看同源，挡掉 CDN/埋点噪声
            xhr.append(u)
            if args.api_hint and args.api_hint in u:
                hits.append(u)

        pg.on("request", on_request)

        print("[1] 打开 %s" % args.url)
        try:
            pg.goto(args.url, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print("    打开失败: %s" % e)
        pg.wait_for_timeout(9000)

        # ---- 形态判定 ----
        info = pg.evaluate("""() => {
          const out = {scrollables: [], pageish: [],
                       docH: document.documentElement.scrollHeight,
                       winH: window.innerHeight};
          document.querySelectorAll('*').forEach(el => {
            if (el.scrollHeight > el.clientHeight + 150 && el.clientHeight > 200) {
              out.scrollables.push({tag: el.tagName,
                                    cls: (el.className || '').toString().slice(0, 70),
                                    sh: el.scrollHeight, ch: el.clientHeight});
            }
          });
          out.scrollables = out.scrollables.slice(0, 6);
          document.querySelectorAll('button,[role=button],a,li').forEach(el => {
            const t = (el.innerText || '').trim().slice(0, 16);
            const c = (el.className || '').toString();
            if (/下一页|下页|next|pagination|page-next/i.test(t + ' ' + c)) {
              out.pageish.push({text: t, cls: c.slice(0, 60), visible: !!el.offsetParent});
            }
          });
          out.pageish = out.pageish.slice(0, 8);
          return out;
        }""")
        same = abs(info["docH"] - info["winH"]) < 5
        print("[2] 文档高 %s / 视口高 %s%s" % (
            info["docH"], info["winH"],
            "  <- 相等=内部容器滚动，滚 document 无效" if same else ""))
        print("    可滚动容器: %s" % json.dumps(info["scrollables"], ensure_ascii=False))
        print("    分页按钮候选: %s" % json.dumps(info["pageish"], ensure_ascii=False))

        base_xhr, base_hits = len(xhr), len(hits)
        print("[3] 初始同源 xhr/fetch %d 个；命中 api-hint %d 个" % (base_xhr, base_hits))

        # ---- 试滚动（鼠标必须先落在列表区域内） ----
        try:
            pg.mouse.move(840, int(min(620, max(200, info["winH"] // 2))))
        except Exception:
            pass
        triggered = 0
        for i in range(args.scrolls):
            before = len(hits) if args.api_hint else len(xhr)
            try:
                pg.mouse.wheel(0, args.scroll_step)
            except Exception as e:
                print("    滚动异常: %s" % e)
                break
            pg.wait_for_timeout(int(args.wait * 1000))
            after = len(hits) if args.api_hint else len(xhr)
            if after > before:
                triggered += 1
                print("    第%d次滚动 -> 触发新请求: %s"
                      % (i + 1, (hits[-1] if args.api_hint else xhr[-1])[:150]))
            else:
                print("    第%d次滚动 -> 无新请求" % (i + 1))

        # ---- 结论 ----
        if triggered:
            verdict = ("LAZY_LOAD：滚动加载。采集器用 mouse.move 进列表区 + mouse.wheel 逐页取；"
                       "每滚一次比对请求计数，连续 2 次无新增即到底停止。")
        elif any(x.get("visible") for x in info["pageish"]):
            verdict = ("PAGINATED：有可见分页按钮。用文本精确匹配 + is_visible()/is_enabled() "
                       "确认后再点，点完必须确认接口有新请求，否则立即停止。")
        else:
            verdict = ("NEITHER：既没滚出新请求、也没找到分页按钮。逐项排查："
                       "(1) 是否要先设筛选条件才会发列表请求 (2) 列表是否在 iframe 里 "
                       "(3) 登录态/权限是否有效 (4) 数据是否在弹窗或新标签页")
        print("[4] 结论: %s" % verdict)

        print("[5] 探到的同源 xhr/fetch（去重后前 25 个）：")
        seen: list[str] = []
        for u in xhr:
            if u not in seen:
                seen.append(u)
        for u in seen[:25]:
            print("    %s" % u[:170])
        ctx.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
