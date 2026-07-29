# 电商AI客服SaaS — 技术架构与启动说明

> 项目：服小助（暂定） | 2026-07-12 搭建完成

## 核心架构

- **模式：** 通用底座（全类目）+ 垂直插件（服装优先）
- **后端：** Python FastAPI + SQLite → MySQL
- **LLM：** DeepSeek V4-Flash（API调用，无需本地模型）
- **前端：** 纯HTML+Tailwind CDN+Chart.js+原生JS（无构建步骤）
- **计费：** 按量计费+封顶（¥49-699/月）
- **多租户：** 所有表带 tenant_id，LLM调用注入对应知识库

## 项目位置

```
~/projects/ai_cs_saas/
├── app/
│   ├── main.py              # FastAPI入口
│   ├── config.py            # 配置（含定价方案）
│   ├── database.py          # SQLAlchemy + SQLite
│   ├── models/              # 6个数据模型
│   ├── api/                 # 7组API路由
│   ├── core/                # 5个核心模块
│   ├── plugins/             # 插件引擎+2个插件
│   └── static/              # 4个前端页面
├── requirements.txt
├── deploy.sh
└── test_api.py
```

## API路由总表

| 前缀 | 功能 |
|:----|:-----|
| `/api/auth` | 注册/登录/JWT |
| `/api/knowledge/items` | 知识库CRUD |
| `/api/chat/send` | AI回复核心 |
| `/api/billing` | 用量/账单/看板 |
| `/api/plugins` | 插件安装/卸载/列表 |
| `/api/notes` | 智能备注（提取/列表/标记已处理） |
| `/webhook` | 抖店回调/支付回调 |
| `/static` | 前端页面 |

## 启动方式

```bash
cd ~/projects/ai_cs_saas
source venv/bin/activate
# 必须从 .env 加载 DeepSeek API Key
export $(grep -v '^#' /home/ubuntu/.hermes/.env | xargs)
python -m app.main
# 服务跑在 http://0.0.0.0:8000
```

## 配置要点

- **config.py** 中的 `DEEPSEEK_API_KEY` 从系统环境变量 `DEEPSEEK_API_KEY` 读取
- **定价方案** 硬编码在 config.py 的 `PRICING_PLANS` 和 `PLUGIN_PRICING` 中
- **插件定价：** 尺码引擎 ¥29/月, 面料库 ¥19/月
- **模型名：** `deepseek-v4-flash`

## 已知问题和注意事项

1. **JWT token 被Hermes脱敏** — 测试时不要用 `terminal` 命令取 token，用 `httpx` 写独立测试脚本
2. **模型名易错** — config.py 里的 `DEEPSEEK_CHAT_MODEL` 子Agent可能写成 `deepseek-chat`，要改为 `deepseek-v4-flash`
3. **API路径与Spec不一致** — 子Agent按自己的方式命名了路由（如 `/api/knowledge/items` 而非 `/api/knowledge/add`），建好后要 grep 确认实际路径
4. **Tencent云安全组** — 端口8000需要在腾讯云轻量应用服务器→防火墙中开放

## 已实现功能

- [x] 用户注册/登录/JWT鉴权
- [x] 通用RAG知识库（商家上传资料→向量检索→LLM回复）
- [x] DeepSeek V4-Flash集成（含降级策略）
- [x] 服装尺码推荐插件（BMI+版型算法）
- [x] 面料知识库插件（10种面料预设）
- [x] 按量计费系统（额度检查+超额预警+月度账单）
- [x] 智能备注（客户需求提取→记录→看板展示）
- [x] 4个前端管理页面（登录/看板/知识库/账单）
- [x] Web管理后台（Chart.js趋势图）
- [ ] 抖店真实Webhook回调（需用户申请开放平台）
- [ ] 拼多多API接入（需用户申请开放平台）
- [ ] 微信/支付宝支付接入（需用户申请商户号）
