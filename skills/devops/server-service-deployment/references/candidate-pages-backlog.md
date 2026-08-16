# 方法论落地页候选池（2026-08 筛选）

从工具箱 139 个技能卡（创业立项13/电商实战16/内容创作31/视觉设计22/AI工具链25/音频媒体7/系统运维25）筛出的可产品化候选。筛选标准见 SKILL.md「候选页面筛选」。

## 🟢 第一梯队：纯推理+高频+直接关联赚钱

| 技能 | 页面功能 | 输入→输出 | 亮点 |
|:---|:---|:---|:---|
| content-risk-detector | 内容安全审查 | 贴文案→敏感词/违规点/风险等级/修改建议 | 最简，引流价值最高 |
| survival-filter | 生存模式筛选 | 填方向/预算→30天月入1万可行性+0成本方案 | Yasin 核心需求 |
| douyin-livestream-scripts | 直播话术生成器 | 填产品/人群→一圈半话术+八大话术+逼单模板 | 桌播直接可用 |
| viral-copywriter | 爆款文案生成 | 填产品→标题+钩子+卖点+逼单结构 | 输入3秒出文案 |
| competitive-analysis | 竞品深度调研 | 填竞品名/链接→定价/技术/营销/弱点机会 | 与8922/8923互补不重复 |
| traffic-acquisition-sop | 流量获客SOP | 填产品→内容到私域全自动流水线 | 匹配「流量>产品」认知 |

## 🟡 第二梯队：有价值但输入复杂或场景窄

| 技能 | 页面功能 | 注意点 |
|:---|:---|:---|
| ai-saas-productization | AI工具SaaS化方案 | 定价/架构/租户/排期 |
| enterprise-agent-platform | 企业Agent平台咨询 | Yasin 感兴趣方向 |
| douyin-livestream-ecommerce | 桌播选品货盘方案 | 货盘组合+收益测算 |
| humanizer-zh | 反AI润色 | 工具型不是分析型，价值偏弱 |
| course-sop-distillation | 课程SOP蒸馏 | 需上传PPTX，输入复杂 |

## 🔴 第三梯队：暂不做（数据/工具依赖）

- a-share-stock-selection（需实时行情，纯LLM会编数据）
- ecommerce-pnl-analysis（需本地Excel/CSV）
- douyin-data-intelligence / agent-reach（实时爬虫）
- deep-research（需联网搜索）
- 所有视频/图片/音频/剪映/PPT 类（文件工具链）

## 推荐建设顺序

1. 内容安全审查（最简，引流价值最高）
2. 直播话术生成器（桌播直接赚钱）
3. 生存模式筛选（Yasin 核心需求）

架构完全复用 server.py 骨架——每个新页只是换提示词+换视觉风格（独立主题不重复），半天出 2-3 个。
