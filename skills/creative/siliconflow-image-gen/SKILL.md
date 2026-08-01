---
name: siliconflow-image-gen
description: 通过硅基流动(SiliconFlow) API 生成高质量图片。支持 Qwen-Image、通义万相、快手可图等模型，无需 GPU，API 已有现成 key。
category: creative
---

# SiliconFlow 图像生成

通过 SiliconFlow API 调用 AI 图像生成模型。**服务器已有 API key**（在 `~/.hermes/.env`，`SILICONFLOW_API_KEY`），无需额外配置即可使用。

## 何时使用

- 用户要求「生成一张图」「出图」「做封面」
- 需要商品图、产品展示图、短视频封面、小红书配图
- 用户纠正「你不是有硅基吗」「可以调硅基生图」

## 前提

- `SILICONFLOW_API_KEY` 已配置（在 `~/.hermes/.env` 中）
- curl 可用
- 不需要 GPU，不需要安装任何模型

## API 端点

```
POST https://api.siliconflow.cn/v1/images/generations
Authorization: Bearer $SILICONFLOW_API_KEY
Content-Type: application/json
```

OpenAI 兼容格式，请求体：
```json
{
  "model": "Qwen/Qwen-Image",
  "prompt": "...",
  "n": 1,
  "size": "1024x1024"
}
```

## 可用模型

| 模型 ID | 质量 | 速度 | 适用场景 |
|---------|:----:|:----:|---------|
| `Qwen/Qwen-Image` | ⭐⭐⭐ 高 | 慢 | 写实/插画/商品图，1328×1328 输出 |
| `Tongyi-MAI/Z-Image` | ⭐⭐⭐ 高 | 中 | 通义万相，综合质量好 |
| `Tongyi-MAI/Z-Image-Turbo` | ⭐⭐ 中 | 快 | 快速出图，速度优先 |
| `Kwai-Kolors/Kolors` | ⭐⭐⭐ 高 | 中 | 快手可图，图文融合强 |
| `baidu/ERNIE-Image-Turbo` | ⭐⭐ 中 | 最快 | 快速预览 |

**注意：** 当前可用模型列表可能变化，用以下命令刷新：
```bash
curl -s https://api.siliconflow.cn/v1/models \
  -H "Authorization: Bearer $SILICONFLOW_API_KEY" \
  | python3 -c "import json,sys; data=json.load(sys.stdin); [print(m['id']) for m in data.get('data',[]) if any(x in m['id'].lower() for x in ['image','kolors','flux','sdxl'])]"
```

## 快速出图

### 单张（默认 Qwen-Image 高质量）
```bash
curl -s -X POST "https://api.siliconflow.cn/v1/images/generations" \
  -H "Authorization: Bearer $SILICONFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen-Image",
    "prompt": "一只可爱的橘猫坐在窗台上，阳光洒进来，写实风格，高质感"
  }' | python3 -c "
import json,sys
data=json.load(sys.stdin)
print(data['images'][0]['url'])
"
```

### 下载到本地
```bash
# 先获取 URL，然后用 curl 下载
curl -s -o /path/to/output.png "<image_url>"
```

### 结果展示
下载到 `~/Desktop/hermes/images/` 后用 `MEDIA:/path/to/file` 发送给用户。

## 质量说明

- **Qwen-Image**: 1328×1328 PNG，写实/插画均可，细节丰富
- **不能** 达到 Midjourney / Flux Pro 级别
- 适合：短视频封面、商品图、小红书配图、产品详情图
- 不适合：商业级精修、超写实人物、高精度设计稿
- 图片会生成到临时 S3 链接（`s3.siliconflow.cn/temporary/outputs/`），有效期 24 小时

## 写 Prompt 技巧

| 中英文 | 风格关键词 |
|--------|-----------|
| 写实摄影 | 写实风格, 8K细节, 柔光, 黄金比例, 浅景深 |
| 产品展示 | 白色背景, ins风, 极简, 高级感, 商业摄影 |
| 插画 | 扁平插画, 渐变色, 矢量风格, 柔和色调 |
| 电商 | 干净背景, 质感光影, 细节清晰, 可做素材 |

## 安全注意

- API key 直接暴露在 `.env` 中，不要在对话中粘贴完整 key
- 生成内容注意合规（色情/政治敏感/暴力会被 API 过滤）
- 计费：硅基流动的图片 API 按张计费，非免费

## Pitfalls

1. **字段索引混淆**：`images[0].url` 是临时 URL，不是 base64，必须下载后再发送
2. **中文 prompt 可正常**：不用强制转英文，Qwen-Image 对中文理解好
3. **部分模型（如 Flux/SD3）当前不可用**：如果用户问为什么不用更好模型，解释受限于硅基的模型接入范围
4. **图片有 watermark / 审查限制**：如果被拦截，API 返回 error，需调整 prompt
5. **用 curl 调 API，不要用 python urllib**：本环境 urllib 会 `Connection reset by peer`（curl 稳定成功）。批量生成脚本要逐张 + 每张重试最多 4 次 + 失败 sleep 4s，一次性并发循环常失败
6. **Qwen-Image 每次生成背景色值略有不同**：需要抠图时，必须逐图采样角落像素（四角均值）作背景色，不能写死一个色值

## 立绘用途决定背景色（重要）

| 用途 | 背景要求 | 原因 |
|------|---------|------|
| 贴纸抠图（页面角色） | 深蓝/纯色背景 | 色键抠图，需采样四角 |
| **图生3D（混元3D/Tripo）** | **纯黑背景** | 建模友好，避免主体混入背景；全身完整正面站姿、无文字水印 |

图生3D完整流程见 `ai-image-to-3d` 技能（混元3D API + Three.js展示）。

## 角色立绘 → 抠图 → HTML 贴纸集成

需要「有质感的页面角色/吉祥物」时（CSS 手绘不够），走完整工作流：
1. 生成：固定 STYLE_TAIL 风格后缀，多角色只改前面描述（保持风格统一）
2. 抠图：**色键法零依赖**（ffmpeg 编解码 + numpy RGB 距离阈值），不要装 rembg；ffmpeg 的 chromakey 滤镜按色度匹配会误扣角色主体，不可用
3. 集成：AI 立绘 + CSS 动效外壳（浮动/霓虹呼吸光晕/点击互动气泡）

详见 `references/character-sticker-workflow.md`，抠图脚本 `scripts/chroma_cut.py`。
