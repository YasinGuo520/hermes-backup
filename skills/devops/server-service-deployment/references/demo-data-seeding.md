# 演示数据灌入纪律（把空系统变成可演示样板）

**场景**：内部系统要拿去给客户演示，但库里是空的。空表 = 自曝弱点。
**实测**：2026-09-12，16 个 Agent 服务 + 驾驶舱页，最终 15/15 个服务页面非空。

---

## 铁律 1：走各服务真实 API 灌，不要手写 SQL

**原因**：共享表会被多个服务复用（本项目 `selection_pool` 被 9 个服务当通用存储、按 `source` 前缀分区），手写 INSERT 极易把字段语义搞错、显示格式对不上。

**先摸清地图**：
```bash
grep -n 'INSERT INTO\|SELECT.*FROM' <agent>/app.py     # 拿到 source 前缀 + 字段顺序
```
本项目实测的「一表多租」格局：

| 服务 | 落库 | source 前缀 |
|:--|:--|:--|
| 内容生产 / 合规审查 / 舆情监控 | `selection_pool` | `content/` `compliance/` `comment/` |
| 供应链 / 物流跟踪 / 绩效 / 招聘 / 竞品 | `selection_pool` | `supplier/` `logistics/` `staff/` `resume/` `comp/` |
| 统筹运营 / 销售分析 / 数据分析 | `platform_data` | — |
| 财务 / 库存 / 培训 | `finance_rows` / `inventory` / `kb_docs` | — |

### ⚠️ 共享解析器可能一直是坏的——而「上游调用方自己绕过」正好把它掩盖了

本项目实测（2026-09-12）：`common/excel.py` 的 `parse_platform_excel(content, filename, default_platform)`
**拿到了「平台」列却不用，也没用传入的 `default_platform`**，而是把**日期**写成平台的返回值：

```python
# 坏：platform 字段被填成日期（date_c 的值）
"platform": str(r[date_c])[:10] if date_c is not None else "",
# 好：优先后解析 Excel 的「平台」列，没有再用调用方传入的 default_platform
plat_c = find_col(df, COL_MAP["platform"])
"platform": (str(r[plat_c]).strip()[:20] if plat_c is not None else default_platform),
```

**为什么一直没被发现**：统筹运营(8924) 在解析后自己覆盖了一遍（`r["platform"] = platform` 再入库）→ 它没事；
而销售分析(8928)、数据分析(8936) 直接写 `r["platform"]` → 平台列全是日期串。**一个调用方的 workaround 恰好掩盖了共享层的 bug。**

诊断信号：查 `/api/overview`、`/api/summary` 这类返回里出现 `2026-09-01` 这种值当“平台名”。
修完**必须重启两个受影响的服务**（共享模块是 import 时加载的）。

**可携带的启发**：函数签名里收了 `default_*` 却在任何返回分支都没用到 → 默认值很可能就是被丢的那个值，值得回头看一眼。

**两类接口**：
- **JSON 型**：直接 POST（先 `grep -oE '(?:body|item|data)\.get\(["'\'']\w+' <agent>/app.py` 拿字段名）
- **Excel 上传型**：`POST /api/upload[/{platform}]`，multipart。环境里常常没有 `requests` → 用标准库手搓 multipart（十几行），别为一次性脚本加依赖

---

## 铁律 2：灌之前存干净快照，一键还原

```python
# 只在第一次灌之前存 —— 否则第二次灌会把干净版覆盖掉
if not os.path.exists(BACKUP):
    shutil.copy2(DB, BACKUP)
```

**还原要连 WAL 一起清**（WAL 模式不删干净会读到旧数据）：
```python
for suf in ("", "-wal", "-shm"):
    if os.path.exists(DB + suf): os.remove(DB + suf)
shutil.copy2(BACKUP, DB)
```

留 `--dry-run` / `--clear` 两个开关，脚本头写清「灌进去的全是演示样例数据」。

---

## 铁律 3：必须显式标注「演示环境 · 样例数据」

**不标注的演示数据 = 客户可能当真实经营数据，是诚信问题。**

- 驾驶舱/入口页：左下角角标
- 每个下游页面：在 `<body>` 后插固定横幅
  ```html
  <div id="demo-badge" style="position:fixed;left:0;right:0;bottom:0;z-index:99999;
      background:rgba(4,8,15,.86);border-top:1px solid rgba(245,166,35,.45);color:#f5a623;
      font:12px/1.7 system-ui;padding:5px 12px;text-align:center">
    演示环境 · 本页数据为<b>样例数据</b>，非真实经营数据</div>
  ```
  **用 `bottom:0` 而不是顶部**——顶部会盖住页头。
- 批量插 16 个文件时：先查 `if "demo-badge" in s: continue` 保证幂等，并备份原文件到 `.baseline-<日期>/banner-before/`
- 验证：`curl -s http://127.0.0.1:<port>/ | grep -c demo-badge` → 1；**再走一遍域名**验证反代链路也带标注

---

## 铁律 4：故意埋异常值，让预警功能在演示时有反应

否则所有指标都是绿的，客户看不出预警能力。实测埋点：

| 埋点 | 触发什么 |
|:--|:--|
| 某平台最后 3 天 GMV 连跌 45% | 「跌超 20% 标红」 |
| 某平台退款率 6.4% | 「退款率超 5% 标红」 |
| 库存里放 3 个 SKU 分别落进 缺货/滞销/清库 三档 | 红/黄/橙三级预警 |

---

## 成本控制：先查哪些接口会调 LLM

```bash
# 用正则切出每个 POST 函数体，看里面有没有 llm.
```
本项目 15 个可用服务里**只有 3 个 POST 调 LLM**（内容生成/简历解析/评估建议）——其余纯规则 0 token。只给必须的几步喂真实 LLM，每个 3 条左右即可。

⚠️ **LLM 步可能返回 200 但内容为空**（实测 2/3 条 `content: ''`）→ 灌完检查长度，`< 50 字就重跑一次`，不要当成成功。

---

## 验收（量化，别目测）

逐个服务打它的**列表 API**、数条目数，打印表格：

```
服务        HTTP  条目数  判定
统筹运营     200   12     ✅ 有数据
...
非空页面: 15/15
```

数条目要兼容多种返回结构（`items`/`rows`/`list`/`docs`/嵌套 dict），写个 `size_of(d)` 兜底。
**这条同时验了三件事**：数据落库了、服务活着、nginx 反代链路通。
