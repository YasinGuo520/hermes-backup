# 电商公司Agent矩阵 — 落地清单（2026-09实测版）

> 会话依据：Yasin 7岗位JD + AI增强 → 扩展为16职能自用Agent矩阵；决策=自用版+全部网页前端挂Hub导航。

## 16个Agent总表（端口/形态/可行档）

| # | Agent | 页面形态 | 端口 | 可行档 | token策略 |
|---|-------|---------|------|:------:|-----------|
| ① | 统筹运营 | 运营驾驶舱：GMV/UV/转化/客诉卡片+异常预警+周趋势 | 8924 | 🟡 | LLM日报 |
| ② | 销售分析 | 洞察报告页：类目/价格带/竞品对比+优化建议 | 8928 | 🟡 | LLM周报 |
| ③ | 趋势监控 | 竞品雷达：动态时间线+风险预警 | 8929 | 🟢 | 规则+LLM周析 |
| ④ | 培训 | 对话窗（Dify RAG或独立聊天页） | 8927 | 🟢 | LLM问答（最大变量138万/月） |
| ⑤ | 招聘筛选 | 简历墙：候选人卡片+评分排序 | 8925 | 🟢 | 按需LLM |
| ⑥ | 流程自动化 | 流程图监视：五环节状态灯（自动上下架减配为建议清单） | 8930 | 🔴部分 | LLM周复盘 |
| ⑦ | 绩效评估 | 绩效看板：成员卡片+雷达图+激励建议 | 8926 | 🟢 | LLM月报 |
| ⑧ | 内容生产 | 脚本/话术/种草文案生成 | 8932 | 🟢 | 按量LLM |
| ⑨ | 合规审查 | 广告法违禁词/平台规则前置检查 | 8933 | 🟢 | 规则库为主+抽查LLM |
| ⑩ | 舆情监控 | 差评预警+回复建议 | 8934 | 🟢 | 规则扫描+LLM建议 |
| ⑪ | 选品 | 爆品池+5层信号成功率打分+首单量建议 | 8935 | 🟢 | LLM打分（已有douyin-data-intelligence技能） |
| ⑫ | 数据分析 | 类目/价格带/趋势报告+问数 | 8936 | 🟡 | LLM报告 |
| ⑬ | 供应链 | 1688供应商档案+比价+采购建议 | 8937 | 🟡 | 档案RAG+规则+LLM建议 |
| ⑭ | 库存管控 | 安全库存预警+滞销识别+库龄监控 | 8938 | 🟢 | **纯规则0 token** |
| ⑮ | 物流跟踪 | 异常件预警+发货通知 | 8939 | 🟢 | **API规则0 token**（快递100） |
| ⑯ | 财务 | 多平台利润日报/月报+毛利+费用归集 | 8940 | 🟢 | 脚本0token+LLM月解读（已有ecommerce-pnl-analysis技能） |

**零token原则**：能脚本/规则/API解决的绝不动LLM。合规主体、库存、物流、财务计算=0 token。

## 费用测算

| 账 | token | 金额 |
|----|-------|------|
| 一次性开发 | 160-260万（16个×5-8万含调试×保守2） | ¥3-5 |
| 每月运行 | ≈310万（④培训138万占大头；自用砍半可¥2-3） | ¥4-6 |
| 首月 | — | ¥8-11 |
| 年化 | — | ¥50-80 |

测算方法：月token = 频次×单次(输入+输出)，价格 DeepSeek-V4-Flash ¥1/M入 ¥2/M出（混合≈¥1.5/M）。
**结论：费用不是瓶颈（≈服务器日开销的1/10），瓶颈是数据源拍板+开发节奏。**

## 数据墙（不可自动化的边界）

- 抖音：TikHub API ✓（已打通，api.tikhub.io Bearer）
- 淘宝/天猫/拼多多/京东后台：**无公开API** → 手工导出Excel喂管道（半自动）
- 1688：无API → 用 `superjack2050/1688-cli`（扫码登录+CLI查询，AI可调）
- 上下架自动化：需平台开放平台企业资质 → 减配为"上下架建议清单"

## GitHub现成件结论

| 项目 | 处理 |
|------|------|
| superjack2050/1688-cli ⭐72（活跃） | **直接装**（供应链管道：选品/供应商评分/询盘/下单/物流） |
| nexscope-ai/eCommerce-Skills ⭐839（157个技能） | **选核心装**（增长/定价/竞品/转化/留存/退货/补货/反馈）——⚠️ frontmatter格式需转换（见find-skills技能） |
| JC0v0/Customer-Agent ⭐826 | 参考拼多多WebSocket接入方案（服小助补拼多多通道） |
| didilili/shopkeeper-agent ⭐341 | 借鉴NL2SQL问数架构（不装：教学项目，要自建数仓） |
| isunswang/tiktok-ecommerce-automation ⭐21 | 借鉴全链路编排蓝图（不装：MVP弃坑风险） |
| upsidelab/enthusiast ⭐172 | 不装（Django栈太重，自写成本更低） |

判断：全链路成品不存在；单点管道直接装、方法论包吸收、架构借鉴——主体自写（DeepSeek成本¥3-5/月级，改造别人的重栈不划算）。

## Hub导航挂载模式

```html
<div class="section-title">⚙️ 公司流程化Agent</div>
<div class="project-grid">
  <a class="card" href="http://43.138.221.174:8924" target="_blank" style="--accent:#6c5ce7">
    <div class="card-icon" style="background:#6c5ce722">🎛️</div>
    <div class="card-body">
      <div class="card-name">🎛️ 统筹运营</div>
      <div class="card-desc">全平台数据汇总 · 异常预警 · AI每日运营日报</div>
      <div class="card-meta">
        <span class="port-badge" style="color:#6c5ce7">8924</span>
        <span class="tag">数据中台</span><span class="tag">日报</span><span class="tag">预警</span>
      </div>
    </div>
    <div class="card-arrow">→</div>
  </a>
  <!-- 每agent一张卡，accent色独立区分 -->
</div>
```

- 新分类位置：插在"🌐 页面"段之后、"🆕 新项目"之前（`</a></div><div class="section-title">🆕 新项目</div>`为锚点）
- 端口从已用最大(8923)→8924起顺序分配，登记避冲突
- Hub路径：`~/Desktop/hermes/hermes-hub/index.html`

## 工具分工

| 活 | 工具 | 理由 |
|----|------|------|
| 数据管道/规则/报告/页面 | **Hermes直接写脚本** | 一次成型，改一行就完事 |
| ④培训RAG+对外演示工作流 | Dify（已部署8850/8851/8852） | 自带知识库+可视化，对外卖点 |
| n8n（5678待放行） | **暂缓** | 活全能cron脚本替代，维护成本高 |

## 修改文件的操作习惯

大批量改HTML/Obsidian：**用脚本读→替换→写回**（execute_code），比逐个patch可靠（patch大段插入易因参数传错反复失败）；替换前assert锚点唯一。