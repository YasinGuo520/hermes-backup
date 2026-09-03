# 公司流程化Agent矩阵 — 自动化改造评估（2026-09-03）

用户原话：「感觉昨天做这些都不太自动化的呢？能如何改进下？」——诊断结论：16个agent是
**仪表盘+手动按钮**，不是**自动流水线**。所有改进方案已提出、用户当时「先不搞了」，
方案保留，下次说要做时按本文档直接实施（A+B+C 约30分钟）。

## 自动化程度的物理瓶颈（先讲清，避免用户以为是代码问题）

| 环节 | 现状 | 卡点 |
|---|---|---|
| 抖音热榜/达人搜索 | 有API但手动点按钮 | TikHub通了，无定时触发 |
| 竞品动态(趋势8929) | 手动触发 | `search_accounts` 是**付费端点按次计费**（勿高频调度） |
| 自家GMV(淘宝/天猫/拼多多/京东/快手/小红书/视频号) | Excel手动上传 | **平台后台无开放API**，导出只能手工（物理卡死，非代码问题） |
| 财务/库存/销售 | Excel手动上传 | 同上 |
| 规则预警(流程8930) | 规则引擎已有(`/api/alerts`) | 无人定时跑 → 从不触发 |
| 结论输出 | 散在各页面 | 无每日汇总推送 |

**两大物理瓶颈**：①平台后台数据只给导出不给API（Excel上传无法消除，除非RPA冒账号风险）；
②已有HTTP端点没人按点触发。第二条是纯代码能解决的。

## 快速摸底方法（下次评估别逐个读16个app.py）

`~/Desktop/hermes/company-agents/<agent>/app.py` 是 FastAPI 单文件。正则扫全目录即可分类：

```python
import os, re
base = '/home/ubuntu/Desktop/hermes/company-agents'
for d in sorted(os.listdir(base)):
    app = f'{base}/{d}/app.py'
    if not os.path.exists(app): continue
    src = open(app, encoding='utf-8').read()
    routes = re.findall(r'@app\.(?:get|post)\(([\'"])([^\'"]+)\1', src)
    uses = sorted({k for k in ['tikhub.','llm.','db.q','excel.'] if k in src})
    has_timer = any(k in src.lower() for k in ['apscheduler','threading.timer','schedule.'])
    print(f"{d}: {[p[1] for p in routes]} | {uses} | 定时={'Y' if has_timer else 'N'}")
```

判断口径：
- `tikhub.` = 数据可自动拉（区分免费/付费，见下）
- `excel.`/`upload`/`import` = 依赖手工Excel/粘贴 → 无法自动（物理卡死）
- `llm.` = 该端点是LLM调用（烧token），纯规则端点=0 token
- 无定时器 = 全是手动触发

## 端点能力速查（2026-09-03 实测摸底）

| Agent(端口) | 自动潜力 | 说明 |
|---|---|---|
| 统筹/流程(8924/8930) | 部分 | `PLATFORMS_GMV` 只有 douyin 标 auto=True 但实为外部榜；淘宝/PDD等 auto=False 只能Excel；`/api/alerts` 规则引擎(0 token)有端点无触发 |
| 选品(8935) | ✅高 | `/api/hot` 拉热榜（**免费端点** hot_billboard）+ 5层信号规则打分入库，纯0 token，最适合先自动化 |
| 趋势(8929) | ⚠️付费 | `/api/search` 用 `tikhub.search_accounts` = **付费按次**，调度要控频 |
| 舆情(8934) | 手动 | `/api/comments` 收前端粘贴的评论数组（无自动拉取源） |
| 财务/销售/库存/供应链/物流/绩效/招聘(8940/8928/8938/8937/8939/8926/8925) | 手动 | Excel上传/表单录入为主 |
| 培训(8927) | RAG问答 | 知识库上传+ask，本质问答不是自动化对象 |
| 内容/合规(8932/8933) | 手动 | generate/check 是LLM按钮 |

## 自动化路线（按性价比排序，已与用户对齐）

| 层 | 做法 | 成本 | 效果 |
|---|---|---|---|
| **A. 0成本先做** | cron定时 curl/python 调本地端点：选品热榜自动打分入库、流程sync+alerts每日跑 | ¥0（纯规则不烧token） | 醒来数据已齐 |
| **B. 每日早报** | 一个LLM cron ~7:30 汇总各agent库 → 飞书推《今日经营简报》 | ~¥0.1/天 | 用户只看一条消息 |
| **C. 触发式预警** | GMV跌>20%/差评率超线才推飞书，平时静默 | ¥0 | 有异常才打扰 |
| **D. RPA自动导后台** | Playwright模拟登录抖店/拼多多自动下载报表，替换Excel手传 | 开发1-2天+**账号风控/封号风险** | 真正全自动 |

**决策**：建议先 A+B+C（今天能上、纯赚），D 等跑顺再评估——动店铺账号有封号风险必须用户知情。
用户2026-09-03拍板「先不搞了」→ 方案原样保留。

## 实施要点（未来真做时）

- A层调度全部走 **no_agent 脚本 cron**（0 token，见主SKILL「watchdog模式」）：curl `http://127.0.0.1:89XX/api/xxx` 或直接 python 调 common/db.py 读库生成文件
- TikHub 免费端点=hot_billboard 可每日；付费端点（search_accounts等）频率压到周级，先查 `references/tikhub-endpoints.md`（在 china-ai-platforms 技能）
- B层早报先跑A层脚本再汇总，同一条消息分「已自动完成/需你上传/异常」三块，让用户一眼看到哪半自动
- 已有平台Excel结构（`common/excel.py` parse_platform_excel 列名约定：日期/GMV/订单数/UV/转化率）是后续RPA导出格式对齐基准
