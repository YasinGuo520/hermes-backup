# 抖音视频分析（Camoufox 浏览器模式）

> 2026-07-23 实测验证。Camoufox 成功打开 `v.douyin.com` 短链，从 DOM 读取视频标题、统计数据、章节要点、评论区。

## 前置条件

- Camoufox 服务在 `localhost:9377` 运行
- 环境变量 `CAMOFOX_DISABLE_DEFAULT_ADDONS=1`（绕过 GFW 对 uBlock Origin 下载的封锁）
- `better-sqlite3` 原生模块已编译（`npm rebuild better-sqlite3`）

## 工作流

### 步骤 1：检查/启动 Camoufox

```bash
# 检查运行状态
curl -s -o /dev/null -w '%{http_code}' http://localhost:9377/health

# 如未运行，启动（Ubuntu 腾讯云/server 环境）
CAMOFOX_DISABLE_DEFAULT_ADDONS=1 ~/.local/bin/camofox-browser &

# 如未运行，启动（macOS 本地环境）
CAMOFOX_DISABLE_DEFAULT_ADDONS=1 camofox-browser &
```

等待日志输出 `browser pre-warmed`（约 2-30s，首次需下载二进制 ~320MB）。

### 步骤 2：导航到视频链接

```javascript
browser_navigate(url="https://v.douyin.com/xxx/")
```

**注意：** 用 `v.douyin.com` 短链，不要用编码后的分享文本格式。

### 步骤 3：读取内容

首次 `browser_navigate` 返回的 snapshot 可能只显示"视频数据加载中"——**等几秒后调用 `browser_snapshot(full=true)` 获取完整内容**。

### 步骤 4：提取数据

从完整 snapshot 可提取：

| 数据 | DOM 位置 | 示例 |
|:----|:--------|:----|
| 标题 | heading level=1 | "当你对一切都失去兴趣时..." |
| 时长 | text 含 "00:00 / mm:ss" | "00:05 / 03:48" |
| 作者名 | link 在评论区上方 | "灯下黑" |
| 粉丝数 | paragraph 含"粉丝X万" | "粉丝19.6万获赞1324.5万" |
| 点赞/评论/转发/收藏 | 四个相邻 text 节点 | "41.0万" / "8315" / "10.6万" / "9.7万" |
| 章节要点 | text + paragraph 交替序列 | "00:00 引言" → "00:19 认知顿悟期 → 长期处于..." |
| 发布时间 | text 含"发布时间" | "2026-07-04 05:11" |
| 评论区 | 可见的 text 序列 | 用户 + 评论内容 + 时间 |
| hashtags | link 含 `//www.douyin.com/search/` | #空心病 #心理学 |
| AI 标注 | text "内容由 AI 生成" | 作者声明 |

### 步骤 5：章节要点读取技巧

章节要点在 DOM 中以交替模式出现：
```
- text: 00:00 引言
- text: 00:19 认知顿悟期
- paragraph: 长期处于高压、高刺激、高消耗后...
- text: 00:35 表达欲消退
- paragraph: 表达欲消退，言语减少...
```

时间标记格式：`MM:SS 章节名`，跟随的 paragraph 是对该章节的描述。

### 步骤 6：分析输出

输出格式（结构化表格）：
```
| 维度 | 内容 |
| 数据表现 | 赞/评/转/藏 |
| 章节 | 时间表+内容 |
| 可复制性 | 钩子/结构/门槛/传播性/变现路径 |
```

## 已知坑点

| 问题 | 原因 | 解决 |
|:----|:-----|:-----|
| 首次 navigate 看到"视频数据加载中" | 页面 JS 未渲染完 | 等几秒再 `browser_snapshot` |
| 抖音弹出 CAPTCHA/验证码 | IP 被标记 | 诚实告知用户，要截图 |
| 500 错误 / 浏览器未就绪 | Camoufox 未完成预热 | 等 `browser pre-warmed` 日志出现后再试 |
| 看不到章节要点 | PC 网页版可能没有此功能 | 只在有"第X章"文字的页面才会出现 |
| `browser_navigate` 报 Connection refused | Camoufox 进程已退出 | 重启 `camofox-browser` |

## 不 work 时（兜底方案）

如果 Camoufox 打不开抖音链接（CAPTCHA/错误），直接问用户要 **截图** 或 **文字描述**，不要试图修 Camoufox，不要换代理，不要 SSH 到远程服务器。

详见 `douyin-inaccessible-video-reconstruction.md`（无访问时的多源三角验证重建方案）。
