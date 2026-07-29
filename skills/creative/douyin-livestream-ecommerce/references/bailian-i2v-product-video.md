# 百炼图生视频(I2V)带货素材生产管线

> 2026-07-11 实测验证。用CHAOKE潮客摄影内衣模特实拍图 → 百炼 HappyHorse-1.1-I2V → 5秒竖屏动态视频，产品100%一致，成本 ¥0.06/条。

## 核心洞察

带货视频用AI生图的**最大坑**：AI画出来的产品细节不可控（标签乱码、包装颜色不对、logo变形）。正确做法是**用手机实拍的产品照做I2V源图**，让AI只负责"让画面动起来"的部分。

## 完整命令链

### 1. 上传实拍产品图到百炼临时存储

```bash
bl file upload \
  --file /path/to/product_photo.jpg \
  --model "happyhorse-1.1-i2v" \
  --output json
```

返回示例（48h有效期）：
```json
{
  "url": "oss://dashscope-instant/xxx/2026-07-11/yyy/img_xxx.jpg",
  "model": "happyhorse-1.1-i2v",
  "expires_in": "48 hours"
}
```

### 2. 用实拍图生成动态视频

```bash
bl video generate \
  --model "happyhorse-1.1-i2v" \
  --image "oss://dashscope-instant/xxx/yyy.jpg" \
  --prompt "Slow push-in camera movement, model stands confidently, her long dark hair gently swaying, the white lace bra fabric subtly shimmering under soft studio lighting, elegant commercial fashion video, smooth cinematic motion, professional product showcase" \
  --negative-prompt "Disfigured, deformed, blurry, low quality, distorted face, bad anatomy, extra limbs, ugly" \
  --resolution "720P" \
  --ratio "9:16" \
  --duration 5 \
  --watermark false \
  --download ~/Desktop/hermes/output_video.mp4 \
  --output json
```

## 参数详解

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| `--model` | `happyhorse-1.1-i2v` | 百炼默认I2V模型，质量好，速度快 |
| `--image` | OSS URL | 从 `bl file upload` 获取的临时OSS链接 |
| `--prompt` | 描述镜头运动 | I2V的prompt描述"画面怎么动"而非"画面有什么" |
| `--negative-prompt` | 标准反义提示词 | 保持画面质量稳定 |
| `--resolution` | `720P` | 实测输出832x1108，竖屏够用 |
| `--ratio` | `9:16` | 抖音竖屏比例 |
| `--duration` | `5` | 单段5秒，方便后期拼接 |
| `--watermark` | `false` | 带货视频去水印 |
| 成本 | **¥0.06/次** | 做100条才6元 |

## 实测数据

| 指标 | 值 |
|------|-----|
| 源图 | CHAOKE潮客摄影内衣模特图（实拍） |
| 模型 | HappyHorse-1.1-I2V |
| 输出分辨率 | 832x1108（接近9:16竖屏） |
| 输出时长 | 5.2秒 |
| 文件大小 | 4.4MB |
| 渲染耗时 | ~60秒（含排队） |
| 费用 | **¥0.06** |

## I2V Prompt模板（带货场景）

I2V的prompt不是描述画面内容（画面由输入图决定），而是描述**镜头运动和动态效果**。

### 产品特写类
```
Slow push-in camera, product texture subtly revealed under soft studio lighting, elegant commercial showcase, smooth cinematic motion, premium feel
```

### 模特展示类（内衣/服装）
```
Model stands confidently, her hair gently swaying in soft breeze, fabric subtly shimmering under studio lighting, elegant commercial fashion video, slow cinematic camera movement
```

### 开箱/桌面演示类
```
Camera slowly panning from left to right, product on clean table, natural daylight, premium unboxing feel, smooth motion
```

### 对比展示类
建议分两段I2V（每个产品一段），后期剪辑做对比转场，不要在一个prompt里做复杂动作。

## 完整的带货视频生产工作流

```
① 手机实拍产品图/模特图（确保光线好、清晰）
       ↓
② 百炼 I2V 生成 5秒动态视频 × N个角度
       ↓
③ VC (viral_copywriter) 出带货文案
       ↓
④ edge-tts 配音（zh-CN-XiaoxiaoNeural rate+15%）
       ↓
⑤ ffmpeg 合成：I2V视频 + 配音 + 底部字幕
       ↓
⑥ 成品 ~/Desktop/hermes/产品名_日期.mp4
```

## 成本对比（单条5秒带货视频）

| 环节 | 费用 | 备注 |
|------|:----:|------|
| 拍照 | ¥0 | 用已有实拍图 |
| 百炼I2V | ¥0.06 | 核心成本 |
| VC文案 | ¥0.00xxx | DeepSeek token费，可忽略 |
| edge-tts配音 | ¥0 | 本地免费 |
| ffmpeg合成 | ¥0 | 本地免费 |
| **总计** | **≈¥0.06** | 100条才6元 |

## 注意与坑

- 上传文件有48h有效期，过期后需重新 `bl file upload`
- I2V输入图建议至少1080x1080，太小放大后画面糊
- I2V会对原图做微调（光线/角度轻微变化），但不影响产品识别
- 不要用复杂动态prompt（"模特转身走两步"），大概率崩
- 首选镜头运动：推近(push-in)、拉远(pull-out)、平移(pan)、微风吹动头发/衣服
- 本管线用百炼（阿里云）API，需要 `bl auth login` 已登录且有余额
