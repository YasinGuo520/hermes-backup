#!/usr/bin/env python3
"""
Feishu Bitable API — 完整工作流
=================================
在 Mac 上通过 source ~/.hermes/.env 获取凭证后直接运行。

用法：
  1. 导入或用此脚本作为模板
  2. 调用 create_bitable(name) → 返回 (app_token, 各table_id字典)
  3. 参考 main() 中的示例添加表、字段、记录

作者：Hermes Agent feishu-lark skill
"""

import os, requests, json

# ── 凭证 ──────────────────────────────────────────────────
def get_credentials():
    """从 ~/.hermes/.env 读取飞书凭证"""
    env_path = os.path.expanduser("~/.hermes/.env")
    creds = {}
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("FEISHU_APP_ID="):
                    creds["app_id"] = line.split("=", 1)[1]
                elif line.startswith("FEISHU_APP_SECRET="):
                    creds["app_secret"] = line.split("=", 1)[1]
    return creds

def get_token(app_id, app_secret):
    resp = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": app_id, "app_secret": app_secret},
    )
    return resp.json()["tenant_access_token"]

# ── 表操作 ─────────────────────────────────────────────────
def create_bitable(token, name):
    """创建多维表格，返回 app_token + 默认表ID"""
    r = requests.post(
        "https://open.feishu.cn/open-apis/bitable/v1/apps",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"name": name},
    )
    d = r.json()
    return d["data"]["app"]["app_token"], d["data"]["app"]["default_table_id"]

def rename_table(token, app_token, table_id, new_name):
    """PATCH 重命名表（可以放 emoji）"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}"
    r = requests.patch(url, headers=headers(token), json={"name": new_name})
    return r.json()

def create_table(token, app_token, name):
    """
    创建子数据表。
    注意：name 先不要放 emoji，创建后用 rename_table 加上。
    """
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables"
    r = requests.post(url, headers=headers(token), json={"table": {"name": name}})
    return r.json()["data"]["table_id"]

def add_field(token, app_token, table_id, field_name, field_type=1):
    """
    添加字段。type: 1=文本, 2=数字, 3=单选, 5=日期, 7=复选框
    字段属性在顶层，不要用 {'field': {...}} 包装。
    """
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
    r = requests.post(url, headers=headers(token), json={"field_name": field_name, "type": field_type})
    return r.json()["data"]["field"]["field_id"]

def add_record(token, app_token, table_id, fields_dict):
    """
    新增记录。
    关键：fields_dict 的 key 必须用字段名（如 '目标'），不是字段ID（如 'fldxxx'）。
    """
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"
    r = requests.post(url, headers=headers(token), json={"fields": fields_dict})
    return r.json()

# ── 工具 ───────────────────────────────────────────────────
def headers(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

def list_tables(token, app_token):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables"
    r = requests.get(url, headers=headers(token))
    return r.json()["data"]["items"]

# ── 示例 ───────────────────────────────────────────────────
def main():
    creds = get_credentials()
    if not creds:
        print("❌ 未找到 FEISHU_APP_ID / FEISHU_APP_SECRET")
        return
    
    token = get_token(creds["app_id"], creds["app_secret"])
    print(f"✅ Token: {token[:20]}...")
    
    # 1. 创建多维表格本体
    app_token, default_tid = create_bitable(token, "项目名称")
    print(f"✅ Bitable: {app_token}")
    print(f"   默认表ID: {default_tid}")
    
    # 2. 重命名默认表（可以放 emoji）
    rename_table(token, app_token, default_tid, "🎯 目标表")
    
    # 3. 创建更多子表（先不加 emoji）
    prog_tid = create_table(token, app_token, "30天进度表")
    prod_tid = create_table(token, app_token, "货盘组合")
    
    # 3b. 重命名加上 emoji
    rename_table(token, app_token, prog_tid, "📅 30天进度表")
    rename_table(token, app_token, prod_tid, "🛒 货盘组合")
    
    # 4. 添加字段到「进度表」
    for fname, ftype in [("阶段",1), ("Day",1), ("任务",1), ("优先级",1), ("状态",1)]:
        add_field(token, app_token, prog_tid, fname, ftype)
        print(f"  Field {fname} → 已添加")
    
    # 5. 插入记录（key=字段名，不是字段ID）
    add_record(token, app_token, prog_tid, {
        "阶段": "准备期",
        "Day": "Day 1",
        "任务": "选品：爆品榜单扫描",
        "优先级": "P0",
        "状态": "未开始",
    })
    
    print(f"\n✅ 链接: https://ynfztrb0cp.feishu.cn/base/{app_token}")

if __name__ == "__main__":
    main()
