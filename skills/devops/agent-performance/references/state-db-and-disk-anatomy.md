# state.db 与磁盘解剖（Hermes 自检瘦身）

实测日期 2026-09-12，环境：腾讯云 Ubuntu / 用户 Yasin 的服务器实例。

## 一句话结论

**state.db 变大 ≠ agent 变傻。** 549MB 里约 350MB 是 FTS 索引（`session_search` 子串检索能力的代价），删掉只省磁盘、会废掉检索。判断「脏了」要看目录残留 + 自维护任务的**产出**，不是数据库文件大小。

用户问「你要不要清理下自己/保持最好状态」时，**别顺着情绪认领故障**：先把「当前会话多少条」和「DB 文件多大」分开说。

## 只读打开的姿势

服务器常没装 `sqlite3` CLI（`command not found`），直接用 python：

```python
import sqlite3, os
db = os.path.expanduser("~/.hermes/state.db")
con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)   # 只读，避免与网关切写打架
cur = con.cursor()
```

⚠️ 两个性能坑：
- `COUNT(*)` 打在 FTS 表上极慢（23976 行实测 ≈114s）→ 先按字符长度求和（`SUM(LENGTH(COALESCE(col,'')))`，秒级）
- 别在循环里对每列跑 `dbstat`（更慢）；宽表用「逐列 SUM(LENGTH)」就够定位大头

## 实测基线

| 项 | 值 |
|---|---|
| state.db | 549MB（`page_count × page_size`） |
| sessions / messages | 480 / 23976 |
| 最大单会话 | 1.41MB（507 条消息） |
| freelist | 2728 页 ≈ 11MB |
| sessions 目录 | 3.5MB |
| logs | 48MB → 清理后 26MB |
| cron/output | 5.9MB（71 文件，最老 7 月中） |
| state-snapshots | 416MB（1 份升级前快照）→ 用户点头后已删，释放 415MB |
| `~/.hermes` 总计 | 9.0G（其中 `hermes-agent/venv` 6.0G 是环境本体，**不是垃圾**） |
| 本次总释放 | **442MB**（26.6MB 残留 + 415MB 快照），磁盘 58%→57% |

逐列/逐表构成：

| 组成 | 大小 | 性质 |
|---|---|---|
| messages.content | 50.11MB | 真数据 |
| messages.tool_calls | 12.23MB | 真数据 |
| messages.reasoning / reasoning_content | 9.00 / 9.00MB | 同一内容两份列 |
| messages.api_content | 0.35MB | — |
| messages._compressed_summary | 0.02MB | 老会话几乎没有摘要 |
| system_prompts.prompt | 8.94MB | 277 行提示词副本，冗余但无害 |
| messages_fts_content | 82.91MB | FTS 内容副本 |
| messages_fts_trigram_content | 82.91MB | trigram 内容副本 |
| messages_fts_data | 36.64MB | FTS 索引 |
| messages_fts_trigram_data | 183.33MB | **trigram 索引，最大头** |

## 判定表

| 疑问 | 结论 |
|---|---|
| 549MB 是故障吗 | 不是。索引 ~350MB 是设计使然 |
| 该 VACUUM 吗 | 不值得。freelist 仅 11MB，且要停网关；只有 freelist 很大（>50MB）才考虑 |
| 能删 FTS 表省 300MB 吗 | 能，但 `session_search` 子串检索失效——**用户没明确要求就别动** |
| 单会话多大算大 | 实测 1.41MB/507 条仍正常。「超 60 条就 /new」是**行为纪律**，不是 DB 阈值 |
| 该删旧会话吗 | 默认不删（删了丢历史 + 老会话缓存命中率高反而省钱，见 `cost-billing-audit.md`） |

## 安全清理清单（本次清出 26.6MB）

```bash
# 1. 写文件写崩产生的垃圾目录（把 JSON 片段当目录名）
rm -rf '/home/ubuntu/{"content": "#!'
find /home/ubuntu -maxdepth 1 -name '{"content"*' -exec rm -rf {} + 2>/dev/null
# 2. 轮转日志（保留最近 2 个；gui.log 是原清理脚本的漏项）
rm -f ~/.hermes/logs/gui.log.1
find ~/.hermes/logs -maxdepth 1 -name '*.log.[123]' ! -newermt "$(date -d '30 days ago' +%F)" -delete
# 3. cron 输出 / session 调试转储 — 30 天保留
find ~/.hermes/cron/output -type f ! -newermt "$(date -d '30 days ago' +%F)" -delete
find ~/.hermes/sessions -maxdepth 1 -name 'request_dump_*' ! -newermt "$(date -d '30 days ago' +%F)" -delete
```

这些已补进 `~/.hermes/scripts/server-cleanup.sh`（每周日 3:00 的「大脑清理」跑）。

**升级前快照（本次释放最大头 415MB）**：先问用户「删还是留」，点头再删，并补保留期（脚本 6e）：
```bash
find ~/.hermes/state-snapshots -mindepth 1 -maxdepth 1 -type d -mtime +30 -exec rm -rf {} + 2>/dev/null || true
```

### ⚠️ 改清理脚本的两条验证纪律（2026-09-12 白跑两轮换来的）

1. **`bash -n` 只验语法**——通过 ≠ 能删。`find … -maxdepth 1 … -delete` 语法合法、真跑静默失败：`-delete` 隐含 `-depth`，与 `-maxdepth 1` 组合时降不进子项，删非空目录报 `Directory not empty`；被 `2>/dev/null || true` 吃掉后就变成「脚本跑了、啥也没删」。**删目录一律 `-exec rm -rf {} +`。**
2. **改完必须造沙盒实测**，且沙盒里 **先建子文件、后 `touch -d` 回拨 mtime**——建子文件会刷新父目录 mtime，顺序颠倒就会测出「永远删不掉」的假故障。

```bash
# 可复用的沙盒验证模板（期望：只剩 new-pre-update）
rm -rf /tmp/snaptest && mkdir -p /tmp/snaptest/old-pre-update/cache /tmp/snaptest/new-pre-update
echo x > /tmp/snaptest/old-pre-update/cache/f
touch -d "40 days ago" /tmp/snaptest/old-pre-update
find /tmp/snaptest -mindepth 1 -maxdepth 1 -type d -mtime +30 -exec rm -rf {} + 2>/dev/null || true
ls /tmp/snaptest
```

## 报告模板（用户问「要不要清理下自己」）

三层，别混：

1. **会话/记忆层**：本次会话 N 条（干净/不干净）+ 记忆 x/y chars
2. **体积层**：DB 里哪些是设计使然（列构成表），结论「不是我变傻」
3. **动作层**：清了什么（带 MB 数字）+ 补了哪个脚本/任务的洞 + 哪个自维护任务在空转 → 最后抛**一个**待用户拍板的决策项

一键只读探针：`python3 scripts/hermes-db-anatomy.py`
