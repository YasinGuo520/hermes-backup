# TikHub API 实测事实（2026-09-02 验证）

> 数据平台API（非AI模型）：抖音/小红书/快手等公开数据。key 在 ~/Desktop/hermes/tikhub/.env（TIKHUB_API_KEY，Bearer认证）。
> 客户端封装：~/Desktop/hermes/company-agents/common/tikhub.py（call()/search_accounts()/hot_billboard() 可直接复用）。

## 平台覆盖（openapi.json 1066端点/25平台）

| 平台 | 端点数 | 电商相关 | 免费？ |
|------|:------:|---------|:------:|
| douyin 抖音 | 332 | 直播商品/星图（付费） | 仅 billboard 账号搜索免费 |
| xiaohongshu 小红书 | 45 | search_products/get_product_detail/reviews | **全付费** |
| kuaishou 快手 | 38 | app/fetch_shopping_top_list 购物榜 | **全付费** |
| wechat_channels 视频号 | 12 | 无电商端点（仅内容） | **全付费** |
| wechat_mp 公众号 | 9 | 无 | 付费 |
| tiktok/instagram/bilibili/weibo/zhihu/youtube 等 | — | 内容数据 | 付费为主 |

**铁律：付费端点欠额度返回 HTTP 402**。小红书/快手/视频号全部付费；免费只有抖音 billboard 的 `fetch_hot_account_search_list`。调用付费端点前先确认余额，别把402当网络错误反复重试。

## 响应结构坑（两层嵌套，解析前必看原始返回）

```python
# 抖音热搜词（付费计费）：
GET /api/v1/douyin/app/v3/fetch_hot_search_list?page=0&page_size=30
→ data["data"]["word_list"][].{rank, word, hot_value}    # 注意两层 data

# 抖音账号搜索（免费）：
GET /api/v1/douyin/billboard/fetch_hot_account_search_list?keyword=xxx&cursor=0&count=8
→ data["data"]["user_list"][].{nick_name, fans_cnt, user_id}   # 两层 + snake_case 字段！
# 用 data.user_list / u["nickname"] 解析会拿 0 条——先打印原始结构再写解析
```

## 重大坑：热搜词 ≠ 商品榜

`fetch_hot_search_list` 返回**抖音时事热搜词**（新闻/事件，如"比什凯克再聚首"），**不是商品/销量榜**。选品不能拿它当商品数据——只适合"蹭热点选题"（内容生产用途）。

## 商品数据源现状（2026-09 实测：无免费平台商品API）

- 抖音商品榜：蝉妈妈/飞瓜/精选联盟后台（付费墙或人工导出）
- 小红书商品：TikHub search_products（付费）
- 1688-cli（npm 本地工具）：可搜品/供应商/询盘/下单，但要先 `npx playwright install chromium`，且首次被阿里风控滑块拦截（跑一次 `--headed` 人工过验证后数小时可用）
- 免费真商品数据只有公开榜（亿邦动力月榜/电商战报网按类目）——见 douyin-data-intelligence skill 一级渠道

## 选品打分平台差异化（已实现于 company-agents/selection 后端，55分制）

同品不同平台得分不同：

| 目标平台 | 平台适配分/5 | 逻辑 |
|---------|:---:|------|
| 抖音 | 5 | 内容化潜力最强 |
| 快手/小红书 | 4 | 内容/种草次之 |
| 淘宝 | 3 | 评价体系/搜索流量 |
| 拼多多 | 2（客单价>50再降1） | 低价竞争，内容弱 |