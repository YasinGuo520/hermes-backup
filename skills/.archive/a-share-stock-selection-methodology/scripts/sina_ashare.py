#!/usr/bin/env python3
"""
sina_ashare.py — A股实时行情查询工具
基于新浪财经免费API (hq.sinajs.cn)
零依赖，Python stdlib only。
"""

import json
import os
import re
import subprocess
import sys
import urllib.request
import urllib.parse

SINA_API = "https://hq.sinajs.cn"
HEADERS = {"Referer": "https://finance.sina.com.cn"}

# 东方财富板块排行API
EASTMONEY_SECTOR = "https://push2.eastmoney.com/api/qt/clist/get"
EASTMONEY_CONCEPT = "https://push2.eastmoney.com/api/qt/clist/get"


# ---------------------------------------------------------------------------
# 新浪实时行情
# ---------------------------------------------------------------------------

def fetch_quotes(codes: list[str]) -> list[dict]:
    """批量获取A股实时行情"""
    symbol_list = ",".join(codes)
    url = f"{SINA_API}/list={symbol_list}"
    
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read()
            # 自动检测编码
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                text = raw.decode("gbk")
    except Exception as e:
        return [{"error": str(e), "codes": codes}]
    
    results = []
    for line in text.strip().split("\n"):
        if not line.strip():
            continue
        match = re.search(r'var hq_str_(\w+)="(.*?)"', line)
        if not match:
            continue
        code = match.group(1)
        fields = match.group(2).split(",")
        if len(fields) < 32:
            continue
        
        entry = {
            "code": code,
            "name": fields[0],
            "open": _float(fields[1]),
            "prev_close": _float(fields[2]),
            "price": _float(fields[3]),
            "high": _float(fields[4]),
            "low": _float(fields[5]),
            "bid": _float(fields[6]),
            "ask": _float(fields[7]),
            "volume": _int(fields[8]),   # 手数
            "turnover": _float(fields[9]),  # 元
            "date": fields[30] if len(fields) > 30 else "",
            "time": fields[31] if len(fields) > 31 else "",
        }
        
        # 计算涨跌幅
        pc = entry["prev_close"]
        pr = entry["price"]
        if pc and pc > 0 and pr:
            entry["change"] = round(pr - pc, 2)
            entry["change_pct"] = round((pr - pc) / pc * 100, 2)
        else:
            entry["change"] = None
            entry["change_pct"] = None
        
        # 判断是否涨停/跌停
        entry["is_limit_up"] = False
        entry["is_limit_down"] = False
        if pc and pr and pc > 0:
            # 科创板688/创业板300 — 20%涨跌幅
            if code.startswith("sh688") or code.startswith("sz300") or code.startswith("sz301"):
                if pr >= round(pc * 1.199, 2):
                    entry["is_limit_up"] = True
                elif pr <= round(pc * 0.801, 2):
                    entry["is_limit_down"] = True
            # 主板 — 10%涨跌幅
            else:
                if pr >= round(pc * 1.099, 2):
                    entry["is_limit_up"] = True
                elif pr <= round(pc * 0.901, 2):
                    entry["is_limit_down"] = True
        
        results.append(entry)
    
    return results


def _float(v: str) -> float | None:
    try:
        f = float(v)
        return f if f != 0.0 else None
    except (ValueError, TypeError):
        return None


def _int(v: str) -> int | None:
    try:
        return int(float(v))
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# 东方财富板块排名
# ---------------------------------------------------------------------------

def fetch_sector_ranking(sector_type: str = "industry", top: int = 15) -> list[dict]:
    """
    获取板块涨跌幅排名
    sector_type: 'industry' (行业板块) 或 'concept' (概念板块)
    """
    if sector_type == "industry":
        fs = "m:90+t:2"
    elif sector_type == "concept":
        fs = "m:90+t:3"
    else:
        return [{"error": f"Unknown sector type: {sector_type}"}]
    
    params = {
        "cb": "",
        "pn": 1,
        "pz": top,
        "po": 1,  # 降序
        "np": 1,
        "fs": fs,
        "fields": "f12,f14,f3,f62,f184,f66,f20,f21",
    }
    url = f"{EASTMONEY_SECTOR}?{urllib.parse.urlencode(params)}"
    
    req = urllib.request.Request(url)
    req.add_header("Referer", "https://quote.eastmoney.com")
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8")
            # Remove callback wrapper
            if raw.startswith("("):
                raw = raw.strip("();")
            data = json.loads(raw)
    except Exception as e:
        return [{"error": str(e)}]
    
    items = data.get("data", {}).get("diff", [])
    results = []
    for item in items:
        results.append({
            "code": item.get("f12"),
            "name": item.get("f14"),
            "change_pct": item.get("f3"),
            "up_count": item.get("f20"),
            "down_count": item.get("f21"),
            "leader": item.get("f66", ""),
            "leader_change": item.get("f184"),
        })
    
    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cmd_quote(args):
    codes = args.codes
    # 自动添加 sh/sz 前缀
    resolved = []
    for c in codes:
        c = c.strip()
        if not c.startswith("sh") and not c.startswith("sz"):
            # 按代码首数字判断
            if c.startswith("6") or c.startswith("688"):
                c = "sh" + c
            else:
                c = "sz" + c
        resolved.append(c)
    
    results = fetch_quotes(resolved)
    if len(results) == 1:
        print(json.dumps(results[0], ensure_ascii=False, indent=2))
    else:
        print(json.dumps(results, ensure_ascii=False, indent=2))


def cmd_sectors(args):
    results = fetch_sector_ranking("industry", top=args.top)
    print(json.dumps(results, ensure_ascii=False, indent=2))


def cmd_concept(args):
    results = fetch_sector_ranking("concept", top=args.top)
    print(json.dumps(results, ensure_ascii=False, indent=2))


def main():
    import argparse
    parser = argparse.ArgumentParser(
        prog="sina_ashare",
        description="A股实时行情 + 板块排名 — 新浪/东方财富"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    
    # quote
    p_quote = sub.add_parser("quote", help="查询A股个股实时行情")
    p_quote.add_argument("codes", nargs="+", help="股票代码，如 688432 或 sh688432")
    
    # sectors
    p_sec = sub.add_parser("sectors", help="行业板块涨幅排名")
    p_sec.add_argument("--top", type=int, default=15, help="返回条数（默认15）")
    
    # concept
    p_con = sub.add_parser("concept", help="概念板块涨幅排名")
    p_con.add_argument("--top", type=int, default=15, help="返回条数（默认15）")
    
    args = parser.parse_args()
    
    if args.command == "quote":
        cmd_quote(args)
    elif args.command == "sectors":
        cmd_sectors(args)
    elif args.command == "concept":
        cmd_concept(args)


if __name__ == "__main__":
    main()
