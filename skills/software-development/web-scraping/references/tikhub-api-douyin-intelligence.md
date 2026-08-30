# TikHub API — 抖音/小红书数据采集（2026-08 实测打通）

> 结论先行：**要结构化抖音数据（对标账号画像、视频列表、直播、热榜），TikHub 是当前验证可用的开发 API 主通道。** 别再去爬抖音站内（搜索页/视频页全验证码）或指望蝉妈妈/飞瓜（无公开 API）。

## 接入信息

- **Base**: https://api.tikhub.io
- **认证**: `Authorization: Bearer <TIKHUB_API_KEY>`（不是 X-Api-Key 头，实测 Bearer 正确）
- **Key 存放**: `~/Desktop/hermes/tikhub/.env`（`TIKHUB_API_KEY=...`）
- **API 全量文档**: `curl https://api.tikhub.io/openapi.json`（2.5MB schema，含每个端点 method/参数/描述）— **查端点方法先看这个，别猜**
- **定价**: 注册送 ~50 次免费试用；之后按量 $0.001/次起，量大递减至 $0.0005（≈¥0.004/次）。免费额度内某些端点仍要求 402

## 端点速查（已实测）

| 端点 | Method | 用途 | 状态 |
|------|--------|------|------|
| `/api/v1/douyin/billboard/fetch_hot_account_search_list` | GET | **按关键词搜账号**（免费可用 ⭐）参数: keyword, cursor, count | ✅ 200 |
| `/api/v1/douyin/web/fetch_hot_search_result` | GET | 抖音热榜 | ✅ 200 |
| `/api/v1/tikhub/user/get_user_info` | GET | 查账号额度/权限范围 | ✅ 200 |
| `/api/v1/douyin/web/handler_user_profile_v4` | GET | 用户画像（昵称/粉丝/作品/获赞）参数: sec_user_id | ✅ 200 |
| `/api/v1/douyin/web/fetch_user_post_videos` | GET | 用户视频列表（desc+点赞/评论/分享）参数: sec_user_id, max_cursor, count | ✅ 200 |
| `/api/v1/douyin/search/fetch_user_search(_v2)` | POST | App 关键词搜用户（body: keyword, cursor, douyin_user_fans, douyin_user_type, search_id） | ⚠️ 需付费 402 |
| `/api/v1/douyin/web/fetch_query_user` | POST | body 是 **ttwid cookie 字符串** 不是 keyword！文档易误读 | ⚠️ 有坑 |

## HTTP 错误码速查（坑最多的地方）

| 状态 | 含义 | 处理 |
|------|------|------|
| 402 Payment Required | 该端点需付费额度（免费试用不含） | 换 billboard 免费搜索或充值 |
| 405 Method Not Allowed | Method 错了——很多搜索端点是 **POST + JSON body** | 查 openapi.json 该端点 method |
| 422 Unprocessable | body/query 字段名错（如把 offset 当 cursor、拿 keyword 喂 ttwid 端点） | 看 openapi.json 的 requestBody schema/description |

## 账号搜索 → 画像 → 视频 标准流程

1. `GET billboard/fetch_hot_account_search_list?keyword=<名称>&cursor=0&count=10`
   → `data.data.user_list[]` 每项有 `nick_name`、`fans_cnt`、`user_id`（实际是 sec_uid 长串）
2. 按名称精确匹配选目标（候选常含同名小号，选粉丝+名字都像的）
3. `GET handler_user_profile_v4?sec_user_id=<user_id>` → 完整画像（nickname/follower_count/aweme_count/total_favorited）
4. `GET fetch_user_post_videos?sec_user_id=<sec_uid>&max_cursor=0&count=30` → 视频列表（desc + statistics.digg_count/comment_count/share_count）→ 直接做对标账号爆款拆解

**现成脚本**: `~/Desktop/hermes/tikhub/douyin_creator.py "账号名1" "账号名2"` — 跑完输出 `output/creators.json`。改端点前先看脚本里的 call() 助手（已处理 GET/POST/body/params 歧义）。

## 平台覆盖（openapi.json 实测统计）

- 抖音 335 端点、小红书 45、TikTok 168、微博 67、B站 42、快手 39
- **淘宝/拼多多/京东 = 0** —— 国内电商销售数据无公开 API（行业事实：生意参谋/商智/多多情报通都是付费订阅+商家账号绑定）
- 蝉妈妈/飞瓜无公开 API（DNS 不解析）；抖查查有 API 但需账号；同花顺 openapi.10jqka.com.cn 是 **A股行情**不是抖音数据（曾误判）

## 踩坑记录（2026-08-30 实测）

- 以为 `fetch_query_user` 传 keyword 能搜用户 → 422。实际该端点 body 是 ttwid cookie 字符串（description 有写，summary 误导）
- `douyin/search/fetch_user_search` 第一次 POST 用 offset/count → 402（付费墙，不是字段错）；免费替代 = billboard 搜索
- 结论：**先翻 openapi.json 的 description/example 再动手；免费端点先试 billboard 系列**

## 替代通道（当 TikHub 不可用/无 key 时）

- 抖音视频页提取：`browser_navigate` 到 `www.douyin.com/video/<id>` + `browser_console` 读 document.title + meta[name=description] + body.innerText（一次性拿标题/统计/章节要点）；curl 抓 HTML 是混淆 JS 没用
- 抖音站内搜索页/百度/搜狗：全反爬拦截（验证码），服务器无桌面浏览器 → 先走 TikHub 别硬爬