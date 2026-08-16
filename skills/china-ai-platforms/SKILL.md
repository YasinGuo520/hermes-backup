---
name: china-ai-platforms
description: 中国AI云平台API调用与选型：硅基流动生图/火山方舟豆包Seedance/百炼bl CLI配音绘本。
triggers:
  - 生图
  - 生成图片
  - 硅基
  - 火山
  - 豆包
  - 即梦
  - Seedance
  - 百炼
  - bl命令
  - TTS
  - 配音
  - 克隆声音
  - 播客
  - 绘本
  - 儿童故事
  - 商品详情图
  - 开源模型
  - API调用
related:
  - ai-video-production
  - ai-image-to-3d
---

# 中国AI云平台调用总纲

> 统一入口：选哪个中国云AI平台、怎么调。三家平台各有专长，先按矩阵选型，再进对应 reference 拿命令。

## 平台选型矩阵（先选平台，再看细节）

| 需求 | 平台 | 为什么 |
|------|------|--------|
| 开源模型（K3/Qwen/FLUX/DeepSeek 镜像） | **硅基流动** SiliconFlow | 便宜、key 已有（`~/.hermes/.env` 的 `SILICONFLOW_API_KEY`），无需 GPU |
| 图片生成（商品图/封面/绘本插图/小红书配图） | **硅基流动** Qwen-Image / Z-Image / Kolors | 现成 key、curl 直调；百炼 `qwen-image-2.0-pro` 也可 |
| 豆包/即梦/Seedance（字节闭源模型） | **火山方舟** Ark | 硅基流动没有闭源模型；视频生成是主场景 |
| TTS 配音 / 克隆音色 / 多人播客 | **阿里百炼** bl CLI | cosyvoice 系列，逐句生成+ffmpeg拼接 |
| 儿童故事 / 有声绘本 / 商品详情图 | **阿里百炼** bl CLI | 完整流水线（story.json + 脚本 + 网页模板） |
| 图生视频 I2V（实拍产品→动效） | **阿里百炼** happyhorse-1.1-i2v | ¥0.06/条最便宜；完整管线见 `ai-video-production` |
| 视频生成（氛围/T2V） | 硅基流动 Wan2.2 / 火山 Seedance | 硅基便宜但只能氛围画面；Seedance 质量高需充值 |

## 各平台完整文档

- `references/siliconflow-image.md` — 硅基流动生图：模型表、curl 调用、prompt 技巧、立绘抠图、角色贴纸工作流
- `references/volcengine-ark.md` — 火山方舟：Key 类型、模型开通、视频/图像任务 API、价格表、常见错误
- `references/bailian-cli.md` — 阿里百炼 bl CLI：TTS/播客/儿童故事/有声绘本/商品详情图全工作流

## 跨平台关键坑（易踩）

- **火山方舟必须用「方舟大模型专用 API Key」**（`ark-` 前缀），普通 API Key 调方舟接口必 401
- Seedance 视频模型开通前需**先充值**（免费额度开不了视频）；API 路径是 `generations`（复数）不是 `generators`——拼错返回 404 空 body
- 百炼**系统音色** `cosyvoice-v3-flash` 加 `--instruction` 会报 428，禁止用；**克隆音色**是 `cosyvoice-v3.5-flash`，两个模型不能混用，克隆音色创建必须去百炼控制台手动操作
- 百炼 TTS 输出的 `.mp3` 实为 WAV(PCM)，ffmpeg 拼接必须 `-c:a libmp3lame` 转码
- **硅基流动必须用 curl 不要用 python urllib**（本环境 urllib 会 Connection reset）；图片 URL 有效期 24h，必须下载后再发送
- 硅基 Qwen-Image 每次生成背景色值略有不同：抠图时逐图采样四角像素均值，不能写死色值
- 生图用途决定背景色：贴纸抠图用深蓝/纯色底；**图生3D用纯黑底**（见 `ai-image-to-3d` 技能）
- 百炼 `bl video generate` 是同步阻塞调用，并行多条会中断（exit 130）——逐条串行
- 账单查询：百炼去控制台 bailian.console.aliyun.com（`bl usage stats` 需 console login）；火山按产品线分开开通分开计费

## 支持文件

| 文件 | 用途 |
|------|------|
| `scripts/build_audiobook.py` | 百炼有声绘本一键构建（story.json → 分段TTS+配图+网页/mp4/音频） |
| `scripts/chroma_cut.py` | 色键抠图脚本（角色立绘→透明贴纸，ffmpeg+numpy 零依赖） |
| `assets/player_template.html` | 绘本翻页播放器模板 |

## 关联技能

- `ai-video-production` — I2V 视频管线、Wan2.2、视频合成（本技能是平台调用层）
- `ai-image-to-3d` — 2D立绘转 GLB 3D（混元3D API）
- `volcengine-ark-api` / `siliconflow-image-gen` / `aliang-bailian` 已并入本技能（原内容在 references/ 对应文件）
