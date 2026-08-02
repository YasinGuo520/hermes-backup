---
name: cloud-image-gen
description: 通过云API（硅基流动 SiliconFlow）生成高质量图片——支持Qwen-Image、Kolors、通义万相等模型。不需要本地GPU，API秒级出图。
category: content-creation
---

# Cloud Image Generation (硅基流动 API)

通过 SiliconFlow API 生成图片，不需要本地 GPU。Yasin 有 API key，写死在 `~/.hermes/.env` 的 `SILICONFLOW_API_KEY`。

## 可用模型

| 模型 | 质量 | 速度 | 分辨率 | 用途 |
|------|------|------|--------|------|
| **Qwen/Qwen-Image** | ⭐⭐⭐⭐⭐ | 中等 | 1328×1328 | 写实/插画/商品图，首选 |
| **Tongyi-MAI/Z-Image** | ⭐⭐⭐⭐ | 中等 | 自动 | 通义万相，质量稳定 |
| **Tongyi-MAI/Z-Image-Turbo** | ⭐⭐⭐ | 最快 | 自动 | 快速出图/批量 |
| **Kwai-Kolors/Kolors** | ⭐⭐⭐⭐ | 中等 | 自动 | 快手可图，图文融合 |
| **baidu/ERNIE-Image-Turbo** | ⭐⭐⭐ | 快 | 自动 | 百度文心 |

**注意：** 没有 Flux / SD3 / Midjourney 级别的模型，但做短视频封面、商品图、小红书配图完全够用。

## 调用方式

### 文生图

```bash
curl -s -X POST "https://api.siliconflow.cn/v1/images/generations" \
  -H "Authorization: Bearer $SILICONFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen-Image",
    "prompt": "你的提示词，中文即可",
    "n": 1,
    "size": "1328x1328"
  }'
```

### 输出处理

API 返回 JSON，图片 URL 在 `data.images[0].url` 字段。URL 是临时 S3 链接，有效期24小时，需要立刻下载保存到本地。

```python
# 下载图片
import requests, json
res = requests.post(url, headers=headers, json=payload)
url = res.json()['images'][0]['url']
img_data = requests.get(url).content
with open('/home/ubuntu/Desktop/hermes/images/output.png', 'wb') as f:
    f.write(img_data)
```

## 提示词技巧

- 中文提示词即可，不需要翻译成英文
- 加质量修饰语：`写实风格` `高质感` `柔光` `8K细节`
- 加构图描述：`中心构图` `浅景深` `产品居中`
- 写实 vs 插画：Qwen-Image 两种都支持，在 prompt 里指定风格

## Yasin 常用场景

- 商品主图/详情图
- 短视频封面
- 小红书配图/种草图
- 产品场景图（白底图、ins风、电商风）

## 存储约定

所有生成的图片保存到 `~/Desktop/hermes/images/`，文件名格式 `{用途}_{时间戳}.png`。

## 相关 reference

- `references/siliconflow-models.md` — 完整模型列表和参数对比
- `references/prompt-examples.md` — 各场景提示词模板

## Pitfalls

1. **URL 有时效** — 24小时后失效，出图后立刻下载
2. **模型不可用** — 偶尔某模型 overload，Fallback 顺序：Qwen-Image → Z-Image → Kolors
3. **不要问权不权限** — Yasin 已经有 key，直接调
4. **质量和价格平衡** — 没限制用量但不要无脑批量刷
