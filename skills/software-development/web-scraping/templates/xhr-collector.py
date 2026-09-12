#!/usr/bin/env python3
"""本机采集器模板：复用已登录浏览器 profile + 拦截 XHR → 上报中心服务器。

设计约束（务必遵守，见 references/china-platform-backend-monitoring.md）：
  1. 只读不写 —— 绝不模拟登录、绝不点后台按钮
  2. 复用用户已登录的持久 profile，不新建 headless 实例
  3. 采集频率 <= 数据源自身更新粒度（多数后台 1 分钟，60s 封顶）
  4. 跑在用户本机；Windows 上必须由「登录自启计划任务」拉起，不能由 SSH 启动
     （SSH 启动的 GUI 程序落在 session 0，没有可见桌面）

用法：改 CONFIG 段 → 首次运行让用户登录一次 → 之后可常驻。
依赖：pip install playwright requests  (playwright install chromium)
"""
import time
from datetime import datetime, timezone

import requests
from playwright.sync_api import sync_playwright

# ── CONFIG ────────────────────────────────────────────────
TARGET_URL = "https://example.com/backend/page"   # 后台页面（筛选条件写进 query 更好）
FILTER_QUERY = ""                                  # 例："?date=2026-09-12&page=1"
PROFILE_DIR = "./browser-profile"                  # 持久化登录态
API_KEYWORD = "/api/"                              # 只收 URL 含此串的响应
INTERVAL_S = 60                                    # >= 数据源更新粒度
REPORT_URL = "http://<center-host>:8941/ingest"    # 中心服务器接收端点
REPORT_TOKEN = ""                                  # 可选：上报鉴权
HEADLESS = False                                   # 首次登录用 False；确认 profile 已登录后可 True
# ──────────────────────────────────────────────────────────


def collect_once(page, captured):
    """载入目标页并回收本轮 XHR JSON。"""
    captured.clear()
    page.goto(TARGET_URL + FILTER_QUERY, wait_until="networkidle", timeout=60000)
    time.sleep(3)  # 给懒加载/二次请求留时间
    rows = []
    for r in captured:
        try:
            rows.append({"url": r.url, "json": r.json()})
        except Exception:
            continue
    return rows


def report(rows):
    """上报中心服务器。失败不要静默——断流必须告警。"""
    payload = {
        "source": "local-collector",
        "ts": datetime.now(timezone.utc).isoformat(),
        "rows": rows,
    }
    headers = {"Authorization": f"Bearer {REPORT_TOKEN}"} if REPORT_TOKEN else {}
    try:
        resp = requests.post(REPORT_URL, json=payload, headers=headers, timeout=20)
        print(f"[report] {resp.status_code} rows={len(rows)}")
    except Exception as e:
        print(f"[report][FAIL] {e}")  # 中心侧应另有心跳超时告警


def main():
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            PROFILE_DIR,
            headless=HEADLESS,
            viewport={"width": 1440, "height": 900},
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        captured = []
        page.on(
            "response",
            lambda r: captured.append(r)
            if API_KEYWORD in r.url and r.status == 200
            else None,
        )

        # 首次运行：让用户手动登录一次，profile 会记住
        page.goto(TARGET_URL, wait_until="domcontentloaded")
        input("如未登录请在打开的浏览器中登录，完成后按回车继续...")

        while True:
            try:
                rows = collect_once(page, captured)
                if not rows:
                    print("[warn] 本轮 0 条 —— 可能改版/断流/风控，需告警")
                report(rows)
            except Exception as e:
                print(f"[loop][error] {e}")
            time.sleep(INTERVAL_S)


if __name__ == "__main__":
    main()
