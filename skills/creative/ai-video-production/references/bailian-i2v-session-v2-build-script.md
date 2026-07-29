# 百炼 I2V 图生视频 + ffmpeg 合成完整脚本 v2

实拍产品图 → 百炼 I2V (HappyHorse-1.1-I2V, ¥0.06/条) → 3条动态 → 
ffmpeg 两段合成（交叉淡化+字幕图+BGM+配音）→ 成品 MP4

## 产品图

来自 CHAOKE 潮客摄影的内衣模特实拍图。

## 配音文案（LLM 生成）

```
CHAOKE潮客摄影，专注内衣视觉定制。
专业级光影质感，每一帧都是大片。
让您的品牌，在镜头前惊艳绽放。
```

## 流程

1. 上传产品图 → `bl file upload --file product.jpg --model happyhorse-1.1-i2v`
2. 并发生成3条I2V（推进/上移/转身）→ 每条~30s
3. edge-tts 生成配音 → 测时长 9.94s
4. 计算截取长度：`(9.94 + 0.5*2) / 3 = 3.65s/段`
5. Pass 1: ffmpeg xfade 交叉淡化（3段→1条视频）
6. Pass 2: PIL 字幕图 + ffmpeg overlay + BGM lavfi + 配音混音

## 出片参数

| 参数 | 值 |
|------|-----|
| 分辨率 | 832×1108 |
| 时长 | 9.9s |
| 编码 | H.264 CRF18 preset slow |
| 比特率 | ~5800kbps |
| 总成本 | ¥0.18 |
