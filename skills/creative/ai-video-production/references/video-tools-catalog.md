# 视频工具全景目录

## 快速选型

| 你做哪种视频？ | 用哪个skill | 一句话特点 |
|--------------|------------|-----------|
| 带货短视频（产品实拍→AI动效） | `chaoke-i2v-product-video` | 实拍照→百炼I2V动态→合成，¥0.18，10分钟 |
| 带货短视频（纯AI生成） | `llm-video-maker` | HyperFrames引擎，文案→TTS→字幕→BGM→竖屏出片 |
| 带货短视频（本地Python，零GPU） | `ai-video-production` | moviepy+edge-tts+ffmpeg，文案→语音→字幕→音乐→出片 |
| 短剧（故事→剧本→分镜→成片） | `aliang-shortvideo` | 一句话灵感→剧本→分镜→AI出图→图生视频→合成 |
| 短剧（阿里LumenX本地版） | 开源项目 `alibaba/lumenx` | 全链路漫剧/短剧生产平台，GitHub 791 stars |
| 剪映自动化剪辑 | `jianying-editor` | JyWrapper API，录屏/素材导入/字幕/BGM/导出 |
| 剪映批量剪辑（模板克隆） | `jianying-batch-editor` | TEMPLATE草稿克隆→自动拼接视频/转场/BGM/字幕 |
| 小红书图文笔记 | `xhs-images` | 11种风格×8种排版，自动适配竖屏3:4 |
| 封面图 | `cover-image` | 五维控制，77种预设，多尺寸适配 |
| 敏感词检测 | `content-risk-detector` | 文案/话术审核，防限流封号 |
| 文案去AI痕迹 | `humanizer-zh` | 去除AI味，更像真人写 |
| 一键多平台分发 | `domestic-video-distribution` | 抖音/小红书/快手/视频号/B站，Spreado浏览器自动化 |

## 平台对应关系

| 平台 | 最佳内容形态 | 推荐工具链 |
|------|------------|-----------|
| 抖音 | 9:16竖屏，15-60秒 | llm-video-maker / ai-video-production + 剪映后期 |
| 小红书 | 图文轮播+短视频 | xhs-images + humanizer-zh + content-risk-detector |
| 视频号 | 1-3分钟横竖屏 | 同上，distribution用domestic-video-distribution |
| B站 | 3-10分钟中长视频 | aliang-shortvideo（短剧类）/ llm-video-maker |

## 生产流水线标准流程

1. **文案** → VC出文案 / humanizer-zh去AI味
2. **视觉** → 按形态选：llm-video-maker（全自动）/ chaoke-i2v（产品动效）/ 剪映（人工精修）
3. **安全** → content-risk-detector过一遍
4. **分发** → domestic-video-distribution多平台发

## 国内AI视频平台（skill外）

| 平台 | 特点 | 接入方式 |
|------|------|---------|
| 即梦AI（Seedance） | 字节系，图生视频/文生视频 | API/Web |
| 可灵AI（Kling） | 快手系，图生视频强 | API/Web |
| 小云雀 | 阿里系，CosyVoice配音 | 阿里云百炼 |
| Vidu | 生数科技，文本/图片/参考视频 | Web |
