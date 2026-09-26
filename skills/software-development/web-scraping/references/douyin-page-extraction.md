# 抖音视频页内容提取（无需登录）

场景：用户发抖音分享短链（v.douyin.com/xxx），要分析视频内容/数据/评论区。

> **先读本文件再动手。** 下面是本项目已验证的路径 + 一份死路清单。不先读就会把 curl 老接口、第三方解析、无头渲染、移动 UA 分享页挨个试一遍——那些全是死路，实测每条都白烧调用。

## 执行环境：先选载体，再动手（2026-09-17 实测修订）

| 载体 | 结果 |
|---|---|
| 服务器（无头/机房IP） | 抖音分享页/详情接口全被风控拦 → 拿不到内容 |
| **真实桌面机（Mac，系统 Chrome，headless=False）** | ✅ 稳定，无需登录即可读全文 |

**一步到位的正确路径**（别再逐个试错）：

```bash
# ① 服务器侧就能做：解析短链拿 aweme_id（纯 HTTP，200，无风控）
curl -sL -o /tmp/dy.html -w '%{url_effective}\n' "https://v.douyin.com/E5yLsA5zhBs/"
# → https://www.iesdouyin.com/share/video/7657446598594616390/?...  ← 中间那段数字就是 aweme_id
```

```bash
# ② 把渲染这一步丢给桌面机（Mac 已装 playwright + 系统 Chrome；脚本见本技能 scripts/douyin-video-content.py）
scp scripts/douyin-video-content.py mac@<mac-ts-ip>:/tmp/
ssh mac@<mac-ts-ip> "cd ~/luopan-collector && ./venv/bin/python /tmp/douyin-video-content.py 7657446598594616390"
```

③ 读 `document.body.innerText`（长页面取前 6000 字符就够）→ 章节要点/标题/互动数据/推荐视频全在里面。

> 若 Hermes 自身所在机器有可用的浏览器 harness，也可直接 `browser_navigate` 打开 `https://www.douyin.com/video/{aweme_id}`，取数方式完全相同。

## 判定：这个视频「能不能在网页看」（先判，再费劲）

有的视频**根本不开放网页播放**（平台侧限制：刚发布、作者设置、互动类作品等）。**先认信号，再决定要不要渲染**：

| 信号 | 含义 |
|---|---|
| `www.douyin.com/video/<id>` 最终跳 `jingxuan?previous_page=web_video_404_link` | 该视频没有网页版 |
| 分享页正文只有 `抱歉出错了` + `请尝试在抖音内观看` | 只许 App 内播放 |
| 分享页 meta description 仍写「于<日期>发布在抖音，已经收获了N个喜欢」 | **不代表可访问**——ID 有效，只是不给你看内容 |
| 短链 302 的 `location` 里 `share_track_info.social_author_id` | 作者 ID 仍可解析出来，可用于其它渠道查证 |

**终审 = 真实桌面机的有头系统 Chrome**（见上）。若这条链路仍跳 404：换 UA、换代理、换 headless/headed、换机器或换 IP **都不会变**——不要再试，直接向用户要**截图或字幕文案**，并明说这是平台限制而不是抓取失败。

判定已内置在脚本里：`scripts/douyin-video-content.py` 命中会打印 `[STOP]` 并给出 `verdict: APP_ONLY`。

## 死路清单（实测，别再浪费时间）

| 路径 | 实测结果 |
|---|---|
| 分享页/iesdouyin HTML | 35KB SPA 空壳，`_ROUTER_DATA` 里只有 query 参数，**没有 desc/play_addr** |
| `m.douyin.com/share/video/<id>` | 200 + 32KB，但正文只有 argus SDK 脚本，无内容 |
| `www.douyin.com/aweme/v1/web/aweme/detail/` | `Blocked by ArgusSecurityPlugin Uifid Not Found`（缺 uifid/签名，别去逆向） |
| `iesdouyin.com/web/api/v2/aweme/iteminfo/` | 空响应（老接口已死） |
| `web_extract` / 第三方 extract 服务 | 抖音页 JS 渲染 + 风控，直接报 extract_failed |
| TikHub `douyin/*/fetch_one_video` | 本次 401 Invalid API token（key 失效需重新生成）；`fetch_video_by_share_url` 返回 404（此路径不存在，别猜端点名） |

**判定信号**：页面 HTML 里出现 `argus-csp-token` = 字节 Argus 风控，curl/SSR 这条路到此为止，直接换真机浏览器渲染。

## 无需登录即可拿到的数据

| 数据 | 说明 |
|---|---|
| 标题 + 话题标签 | heading 元素，含全部 #tag |
| **官方章节要点** | 「章节要点」区域：AI 生成的分段总结+时间戳，**快速还原视频叙事的捷径**（本次靠它拿到完整论点） |
| 互动数据 | 顺序出现：点赞 → 评论 → 收藏 → 分享 |
| 作者信息 | 昵称、粉丝数、获赞数 |
| 发布时间 | 「发布时间：YYYY-MM-DD HH:MM」 |
| 评论区 | 含作者回复；「请先登录后发表评论」不遮挡已有评论 |
| 推荐视频 | 同领域视频标题+点赞数（能看出博主内容矩阵 + 同题材竞品） |
| 作者声明 | 「内容由 AI 生成」标记 |

## 要点

- **不要用截图/视觉分析内容**——登录弹窗+静音提示遮挡画面；用 innerText
- 视频本体（画面/语音）拿不到，**章节要点就是内容摘要**，足够做观点拆解
- 评论区作者回复是金矿：博主真实意图、工具分工、对争议的回应都在里面
- 收藏/点赞比 >1 是实用型教程内容信号（用户存起来以后用）；评论少=内容没争议性
- 章节要点带时间戳，直接还原视频结构（引言→介绍→实操→结语）
- 数据顺序固定：点赞/评论/收藏/分享（173=分享是最后一个）
- 章节要点会标注「内容由 AI 生成」——引用时说明这是平台 AI 摘要，不是逐字转写

## 从「别人的工具视频」到「我能不能干」（回答骨架）

用户发一条 AI 工具/自动化视频后问「分析下，你能干吗」，按这个骨架回，别写散文：

1. **视频讲了啥**（表格：核心 / 能干啥 / 流程 / 前提 / 定位）——末尾加一句「概念科普还是实操细节」，避免用户高估视频
2. **能力对照表**：`视频里的能力 | 我能不能 | 用什么工具 | 实测状态`——「实测状态」列必须有真实状态（在跑/未做/挂了），不写「可以支持」这种空话
3. **一句话结论**：能干/不能干 + 手里已有的活证据（例：本机采集器就是这套东西的落地版）
4. **真门槛**（视频常不说的）：通常是登录态+风控环境、业务标准化，而不是视频演示的那个技术点
5. **下一步二选一**，让用户挑，别自己启动
