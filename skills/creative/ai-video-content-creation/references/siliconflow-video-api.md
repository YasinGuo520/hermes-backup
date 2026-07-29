# SiliconFlow 视频生成 API（Wan2.2 T2V）

## 端点

| 操作 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 提交 | POST | `https://api.siliconflow.cn/v1/video/submit` | 返回 requestId |
| 状态 | POST | `https://api.siliconflow.cn/v1/video/status` | 轮询结果 |

## 提交参数

```json
{
  "model": "Wan-AI/Wan2.2-T2V-A14B",
  "prompt": "描述视频画面",
  "image_size": "720x1280",
  "negative_prompt": "可选，排除的内容",
  "seed": 12345
}
```

## 状态响应

```json
{
  "status": "InQueue|InProgress|Succeed|Failed",
  "reason": "失败原因（仅Failed时）",
  "results": {
    "videos": [{"url": "https://...oss-cn-shanghai.aliyuncs.com/..."}],
    "timings": {"inference": 123},
    "seed": 123
  }
}
```

## 实测数据

| 模型 | 分辨率 | 生成耗时 | 文件大小 | 画质 |
|------|--------|---------|---------|------|
| Wan2.2-T2V-A14B | 720x1280 | ~8-9分钟 | 1.8MB | 氛围感画面，非叙事内容 |

## 注意

- 提交用 `.cn`，不是 `.com`
- 状态查询用 POST + JSON body，不是 GET + query params
- 视频URL为阿里云OSS临时链接，生成成功后需立即下载
- 不支持生成有叙事逻辑/角色/字幕的内容视频——只能做氛围背景
- 可以配合 edge-tts 配音 + moviepy 合成，做成完整的"氛围视频+配音"内容
