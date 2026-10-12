# TikHub 数据 API（抖音/小红书/快手等 25 平台公开数据）— 唯一权威版

> **本文件是全库唯一权威版。** 原 `china-ai-platforms` 的 `tikhub-endpoints.md`、`tikhub-api-facts.md` 与 `web-scraping` 的 `tikhub-api-douyin-intelligence.md` 已并入此处。
>
> 结论先行：**要结构化抖音数据（对标账号画像、视频列表、直播、热榜），TikHub 是当前验证可用的开发 API 主通道。** 别再去爬抖音站内（搜索页/视频页全验证码）或指望蝉妈妈/飞瓜（无公开 API）。

## 接入

- **Base**: `https://api.tikhub.io`；认证头 `Authorization: Bearer <TIKHUB_API_KEY>`（**不是** X-Api-Key，实测 Bearer 正确）
- **Key**: `~/Desktop/hermes/tikhub/.env`
- **端点真相源**: `curl https://api.tikhub.io/openapi.json`（~2.5MB schema，含 method/参数/description）——**查端点和 method 先看这个，别猜**；平台端点数与端点路径随版本漂移，下表只是快照
- **定价**: 注册送 ~50 次试用；之后 $0.001/次起，量大递减至 $0.0005（≈¥0.004/次）
- **封装**: `~/Desktop/hermes/company-agents/common/tikhub.py`（`call()` / `search_accounts()` / `hot_billboard()` / `user_profile()`，已处理两层解析与 GET/POST·body/params 歧义）；现成脚本 `~/Desktop/hermes/tikhub/douyin_creator.py "账号名"` → `output/creators.json`

## 平台覆盖与免费边界

| 平台 | 端点数 | 电商相关 | 免费？ |
|------|:------:|---------|:------:|
| douyin 抖音 | 332-335 | 直播商品/星图（付费） | 仅 billboard 账号搜索免费 |
| tiktok 国际 | 166-168 | 内容数据 | 付费为主 |
| xiaohongshu 小红书 | 45 | search_products / get_product_detail / reviews | **全付费** |
| kuaishou 快手 | 38-39 | `app/fetch_shopping_top_list` 购物榜 | **全付费** |
| wechat_channels 视频号 | 12 | 无电商端点，仅内容 | **全付费** |
| wechat_mp 公众号 / weibo / bilibili / zhihu | 9-67 | 内容数据 | 付费为主 |

铁律：
- **免费只有抖音 billboard 系（`fetch_hot_account_search_list`）**
- **付费端点欠额度返回 HTTP 402**——不是网络/参数错误，别反复重试；调用付费端点前先确认余额
- **TikHub 拿不到任何平台自己店铺后台的数据**（订单/GMV）——店铺数据一律走 Excel 或官方 API 对接
- **淘宝/拼多多/京东 = 0 端点**（行业事实：生意参谋/商智/多多情报通都是付费订阅 + 商家账号绑定）；同花顺 `openapi.10jqka.com.cn` 是 A 股行情、**不是**抖音数据（曾误判）

## 响应结构（解析前先打印原始返回）

```python
# 抖音热榜（付费计费）
GET /api/v1/douyin/app/v3/fetch_hot_search_list?page=0&page_size=30
#   （另一版本实测路径为 /api/v1/douyin/web/fetch_hot_search_result）
→ data["data"]["word_list"][].{rank, word, hot_value}

# 抖音账号搜索（免费 ⭐）
GET /api/v1/douyin/billboard/fetch_hot_account_search_list?keyword=xxx&cursor=0&count=8
→ data["data"]["user_list"][].{nick_name, fans_cnt, user_id}   # user_id 实际是 sec_uid
```

- ⚠️ **`data` 是两层嵌套**：先 `d = r.get("data", {}); d = d.get("data", {})` 再取值；用 `data.user_list` / `u["nickname"]` 解析会拿到 0 条
- ⚠️ **字段是 snake_case**（`nick_name` / `fans_cnt`），不是驼峰
- 付费端点响应带 `"message": "Request successful. This request will incur a charge."`；响应里的 `cache_url` 24 小时内可复查且**不计费**

## 端点速查（已实测）

| 端点 | Method | 用途 | 状态 |
|------|--------|------|------|
| `/api/v1/douyin/billboard/fetch_hot_account_search_list` | GET | 按关键词搜账号（keyword/cursor/count） | ✅ 免费 |
| `/api/v1/douyin/app/v3/fetch_hot_search_list` | GET | 抖音热榜（时事热搜，**非商品榜**） | ⚠️ 付费 |
| `/api/v1/douyin/web/handler_user_profile_v4` | GET | 用户画像（sec_user_id） | ⚠️ 付费 |
| `/api/v1/douyin/web/fetch_user_post_videos` | GET | 视频列表（sec_user_id/max_cursor/count） | ⚠️ 付费 |
| `/api/v1/douyin/web/fetch_live_room_product_result` | GET | 直播商品（room_id/author_id） | ⚠️ 付费 |
| `/api/v1/tikhub/user/get_user_info` | GET | 查账号额度/权限范围 | ✅ 200 |
| `/api/v1/douyin/search/fetch_user_search(_v2)` | **POST** | App 关键词搜用户（body: keyword/cursor/douyin_user_fans/search_id） | ⚠️ 402 |
| `/api/v1/douyin/web/fetch_query_user` | **POST** | body 是 **ttwid cookie 字符串**，不是 keyword（summary 误导） | ⚠️ 有坑 |

## HTTP 错误码速查（坑最多的地方）

| 状态 | 含义 | 处理 |
|------|------|------|
| 402 Payment Required | 该端点需付费额度（免费试用不含） | 换 billboard 免费搜索或充值 |
| 405 Method Not Allowed | Method 错了——很多搜索端点是 **POST + JSON body** | 查 openapi.json 该端点的 method |
| 422 Unprocessable | body/query 字段名错（把 offset 当 cursor、拿 keyword 喂 ttwid 端点） | 看 openapi.json 的 requestBody schema/description |

## 标准流程：账号搜索 → 画像 → 视频

1. `GET billboard/fetch_hot_account_search_list?keyword=<名称>&cursor=0&count=10` → `data.data.user_list[]`
2. 按名称精确匹配选目标（候选常含同名小号，选粉丝数与名字都像的）
3. `GET handler_user_profile_v4?sec_user_id=<user_id>` → 完整画像
4. `GET fetch_user_post_videos?sec_user_id=<sec_uid>&max_cursor=0&count=30` → 视频列表（desc + statistics）→ 直接做对标账号爆款拆解

## 重大语义坑：热搜词 ≠ 商品榜

`fetch_hot_search_list` 返回**抖音时事热搜词**（新闻/事件），**不是商品/销量榜**。选品不能拿它当商品数据——只适合「蹭热点选题」（内容生产用途）。

## 商品数据源现状（2026-09 实测：无免费的平台商品 API）

- 抖音商品榜：蝉妈妈 / 飞瓜 / 精选联盟后台（付费墙或人工导出）
- 小红书商品：TikHub `search_products`（付费）
- 1688-cli（npm 本地工具）：可搜品/供应商/询盘/下单，需 `npx playwright install chromium`，且首次被阿里风控滑块拦截（跑一次 `--headed` 人工过验证后数小时可用）；TikHub 没有 1688 通道
- 免费真商品数据只有公开榜（亿邦动力月榜 / 电商战报网按类目）

### 选品打分的平台差异化（已实现于 company-agents/selection 后端，55 分制）

| 目标平台 | 平台适配分/5 | 逻辑 |
|---------|:---:|------|
| 抖音 | 5 | 内容化潜力最强 |
| 快手/小红书 | 4 | 内容/种草次之 |
| 淘宝 | 3 | 评价体系/搜索流量 |
| 拼多多 | 2（客单价>50 再降 1） | 低价竞争，内容弱 |

## 替代通道（无 key / 端点不可用时）

- 抖音视频页内容：见 `references/douyin-page-extraction.md`——**短链解析 aweme_id → 真实桌面机有头浏览器读 `document.body.innerText`**；curl 抓 HTML 是混淆 JS 没用；TikHub 的 `douyin/*/fetch_one_video` 曾返回 401/404（key 失效或路径不存在）
- 抖音站内搜索页 / 百度 / 搜狗：全反爬拦截，服务器无桌面浏览器 → 先走 TikHub，别硬爬

## 踩坑记录

- 以为 `fetch_query_user` 传 keyword 能搜用户 → 422；实际 body 是 ttwid cookie 字符串（description 有写，summary 误导）
- `douyin/search/fetch_user_search` 第一次 POST 用 offset/count → 402（付费墙，不是字段错）；免费替代 = billboard 搜索
- 结论：**先翻 openapi.json 的 description/example 再动手；免费端点先试 billboard 系列**
