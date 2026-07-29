---
name: domestic-video-distribution
description: 将视频自动分发到国内主流平台（抖音/小红书/快手/视频号/B站）。使用 Spreado CLI 通过浏览器自动化实现一键多平台发布。
---

# 国内视频多平台分发

VC 出文案 → LLM-video-maker 做视频 → **Spreado 分发**。最后这个环节。

## 工具

**Spreado** — 开源 Python CLI，浏览器自动化发布视频。
- 路径：`~/Desktop/hermes/Spreado/`
- 运行：`uv run spreado <command>`
- 平台：抖音 / 小红书 / 快手 / 视频号 / B站

## 工作流程

### 0. 首次使用 — 登录各平台（仅一次）

每个平台首次使用需扫码登录，Cookie 会持久化保存。

```bash
cd ~/Desktop/hermes/Spreado

# 逐一登录
uv run spreado login douyin
uv run spreado login xiaohongshu
uv run spreado login kuaishou
uv run spreado login shipinhao
uv run spreado login bilibili
```

每个命令会弹出浏览器窗口，扫码即可。登录一次后不用再登，除非 Cookie 过期。

### 1. 验证 Cookie

```bash
# 验证全部平台
uv run spreado verify all --parallel

# 或指定某个平台
uv run spreado verify douyin
```

### 2. 发布视频

```bash
# 发布到所有平台（并行）
uv run spreado upload all --video output.mp4 --title "标题" --parallel

# 指定单个平台
uv run spreado upload douyin --video output.mp4 --title "标题" --desc "描述" --tags "tag1,tag2"
```

### 3. 排期发布

```bash
uv run spreado upload douyin --video output.mp4 --title "标题" --schedule "2026-07-12 10:00"
```

## 集成到现有管线

视频生产工作流（`video-production-workflow`）完成后，追加一步分发：

```
VC (viral_copywriter) 出文案
  → LLM-video-maker 生成视频（输出到 ~/Desktop/hermes/）
  → Spreado 多平台分发
  → 完成
```

## 平台支持明细

| 平台 | 命令名 | 发布类型 | 备注 |
|------|--------|----------|------|
| 抖音 | `douyin` | 视频 | 主流带货平台 |
| 小红书 | `xiaohongshu` | 视频 | 种草流量 |
| 快手 | `kuaishou` | 视频 | 下沉市场 |
| 视频号 | `shipinhao` | 视频 | 微信生态 |
| B站 | `bilibili` | 视频 | 长尾流量 |

## 调试

```bash
# 加 --debug 看详细日志
uv run spreado upload douyin --video test.mp4 --title "test" --debug

# 查看已安装的平台插件
uv run spreado list
```

## 注意事项

- **Cookie 有效期**：各平台 Cookie 会过期，建议发布前先 `verify`。发现失效就重新 `login`。
- **浏览器依赖**：首次运行 Playwright 会自动下载 Chromium（已装好），也可用系统 Chrome。
- **防盗刷**：发布到 B 站/小红书等对搬运敏感的平台，建议修改标题和描述避免被判重复。
- **一次发多平台**：`upload all --parallel` 并行发，但各平台审核速度不同，最终发布时间会有偏差。
