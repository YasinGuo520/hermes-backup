#!/usr/bin/env python3
"""Hermes 自检探针（只读，不改任何东西）。

回答：「我是不是变傻了 / 要不要清理下自己」。输出四块：
  1. 当前会话干净度（条数才是影响注意力的量）
  2. state.db 逐列逐表构成（区分真数据 vs FTS 索引）
  3. 目录残留（logs / cron output / sessions / snapshots / skills）
  4. 记忆文件字节（真实 char 限制以 memory 工具返回的 x/y 为准）

用法: python3 hermes-db-anatomy.py
基线数字: references/state-db-and-disk-anatomy.md
"""
import glob
import os
import sqlite3
import time

HOME = os.path.expanduser("~")
DB = os.path.join(HOME, ".hermes", "state.db")
MSG_COLS = ("content", "tool_calls", "reasoning", "reasoning_content", "api_content")
TABLES = ("system_prompts", "messages_fts_data", "messages_fts_content",
          "messages_fts_trigram_data", "messages_fts_trigram_content")
DIRS = ("~/.hermes/logs", "~/.hermes/cron/output", "~/.hermes/sessions",
        "~/.hermes/state-snapshots", "~/.hermes/skills")


def human(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}TB"


def dir_size(path):
    total = 0
    for root, _dirs, files in os.walk(path):
        for name in files:
            try:
                total += os.path.getsize(os.path.join(root, name))
            except OSError:
                pass
    return total


def main():
    print("=== Hermes 自检（只读）===")

    if not os.path.exists(DB):
        print(f"!! 找不到 {DB}")
        return

    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    cur = con.cursor()

    print(f"\n[1] 会话干净度   state.db={human(os.path.getsize(DB))}")
    print("    最近会话（条数越多越该 /new，与 DB 大小无关）:")
    for sid, count, title in cur.execute(
            "SELECT id, message_count, title FROM sessions "
            "ORDER BY last_activity_at DESC LIMIT 5"):
        print(f"      {sid[:22]}  msgs={count:<5} {str(title)[:30]}")

    print("\n[2] DB 逐列逐表构成（慢的计数已避开；FTS 索引≈设计使然，别当故障报）")
    for col in MSG_COLS:
        got = cur.execute(
            f"SELECT SUM(LENGTH(COALESCE({col},''))) FROM messages").fetchone()[0] or 0
        print(f"      messages.{col:<18} {human(got)}")
    for table in TABLES:
        cols = [row[1] for row in cur.execute(f"PRAGMA table_info({table})")]
        total = 0
        for col in cols:
            total += cur.execute(
                f"SELECT SUM(LENGTH(CAST(COALESCE({col},'') AS BLOB))) FROM {table}"
            ).fetchone()[0] or 0
        print(f"      {table:<34} {human(total)}")

    free_pages = cur.execute("PRAGMA freelist_count").fetchone()[0]
    page_size = cur.execute("PRAGMA page_size").fetchone()[0]
    free = free_pages * page_size
    verdict = "值得考虑 VACUUM" if free > 50 * 1024 * 1024 else "VACUUM 收益很小，不值得停网关"
    print(f"      freelist={free_pages} 页 (≈{human(free)}) → {verdict}")
    con.close()

    print("\n[3] 目录残留")
    for raw in DIRS:
        path = os.path.expanduser(raw)
        size = human(dir_size(path)) if os.path.isdir(path) else "N/A"
        print(f"      {raw:<34} {size}")
    stale = [f for f in glob.glob(os.path.expanduser("~/.hermes/logs/*.log.[0-9]"))
             if time.time() - os.path.getmtime(f) > 30 * 86400]
    print(f"      30天前的轮转日志: {len(stale)} 个 "
          f"({human(sum(os.path.getsize(f) for f in stale))})" +
          ("  ← gui.log 常被清理脚本漏掉" if any("gui" in f for f in stale) else ""))
    junk = glob.glob(os.path.join(HOME, '{"content"*'))
    print(f"      写崩垃圾目录: {[os.path.basename(j) for j in junk] or '无'}")

    print("\n[4] 记忆用量（文件字节；真实 char 限制以 memory 工具返回的 x/y 为准）")
    for raw in ("~/.hermes/memories/MEMORY.md", "~/.hermes/memories/USER.md"):
        path = os.path.expanduser(raw)
        print(f"      {raw:<32} {human(os.path.getsize(path)) if os.path.exists(path) else 'N/A'}")

    print("\n[5] 别忘最后一步：审 ~/.hermes/cron/jobs.json 里自维护任务 prompt 内"
          "写死的阈值/路径是否与实测对齐 —— last_status=ok 只说明跑完，不说明干成活。")


if __name__ == "__main__":
    main()
