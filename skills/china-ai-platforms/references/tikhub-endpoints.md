# TikHub API 端点速查（2026-09-02 实测）

> api.tikhub.io，Bearer 认证（key 在 ~/Desktop/hermes/tikhub/.env 的 TIKHUB_API_KEY）。
> **402 = 欠额度（Payment Required）**，付费端点余额不足时返回，充值后才能用。

## 平台覆盖（openapi.json 实锤：1066 端点 / 25 平台）

| 平台 | 端点数 | 备注 |
|------|:------:|------|
| douyin 抖音 | 332 | 免费端点只在 billboard 类 |
| tiktok 国际 | 166 | — |
| xiaohongshu 小红书 | 45 | **全付费**；有商品搜索/详情/评价（电商级） |
| kuaishou 快手 | 38 | **全付费**；有 shopping_top_list 购物榜 |
| wechat_channels 视频号 | 12 | **全付费**；无电商端点，内容数据 |
| wechat_mp 公众号 | 9 | 内容数据 |
| weibo/bilibili/zhihu 等 | 195 | 内容数据 |

关键结论：
- **免费只有抖音 billboard 几个端点**（账号搜索/热榜）
- **小红书/快手有真实商品级数据**但全付费，402 挡路
- TikHub 拿不到任何平台的**自己店铺后台数据**（订单/GMV）——店铺数据一律 Excel/API 对接

## 抖音端点实测结构（两层 data 嵌套，解析必看）

热榜（App V3）：
```
GET /api/v1/douyin/app/v3/fetch_hot_search_list?page=0&page_size=N
→ data.data.word_list[] { rank, word, hot_value }
```

账号搜索（billboard，免费）：
```
GET /api/v1/douyin/billboard/fetch_hot_account_search_list?keyword=XXX&cursor=0&count=N
→ data.data.user_list[] { nick_name, fans_cnt, user_id, sec_uid }
```

画像（付费）：`GET /api/v1/douyin/web/handler_user_profile_v4?sec_user_id=...`
视频列表（付费）：`GET /api/v1/douyin/web/fetch_user_post_videos?sec_user_id=...&max_cursor=0&count=N`
直播商品（付费）：`GET /api/v1/douyin/web/fetch_live_room_product_result?room_id=...&author_id=...`

⚠️ **坑：response 的 `data` 字段是 `data.data` 两层**（如热榜 word_list 在 `r["data"]["data"]["word_list"]`），解析时先 `d = r.get("data", {}); d = d.get("data", {})` 再取值。字段名是 snake_case（nick_name/fans_cnt），不是驼峰。

## 响应特征

- 付费端点响应带 `"message": "Request successful. This request will incur a charge."`——每次调用计费
- 缓存：响应里有 cache_url（24小时可复查，不计费）
- 1688 商品搜索走 `1688-cli`（npm，需 Playwright chromium + 首次人工过滑块验证），TikHub 没有 1688 通道

## 参考实现

`~/Desktop/hermes/company-agents/common/tikhub.py` — 已封装 call/search_accounts/hot_billboard/user_profile，含两层解析修正。