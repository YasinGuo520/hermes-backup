# 配音后期合成 (edge-tts + FFmpeg)

HyperFrames 渲染的视频默认不含音频（`hasAudio: false`）。配音需要单独生成后合并。

## 推荐工作流

```bash
# 1. 写配音文案
echo "配音文案内容" > projects/<id>/script.txt

# 2. 用 edge-tts 生成配音
# 中文女声推荐 zh-CN-XiaoxiaoNeural (语速+15%)
edge-tts \
  --voice zh-CN-XiaoxiaoNeural \
  --text "$(cat projects/<id>/script.txt)" \
  --write-media projects/<id>/renders/narration.mp3 \
  --rate +15%

# 3. 用 FFmpeg 合成音视频
ffmpeg -y \
  -i projects/<id>/renders/<id>.mp4 \
  -i projects/<id>/renders/narration.mp3 \
  -c:v copy \
  -c:a aac \
  -b:a 192k \
  -map 0:v:0 -map 1:a:0 \
  -t 30 \
  projects/<id>/renders/<id>-with-audio.mp4
```

## 注意

- `-t 30` 保持视频全长（配音通常比视频短几秒）
- 若配音比视频长，用 `-shortest` 截断视频到配音长度
- edge-tts 路径：`/Users/mac/.hermes/hermes-agent/venv/bin/edge-tts`
- Hermes 环境下执行时用绝对路径避免 PATH 问题

## 文案长度参考

| 时长 | 文案字数 | 语速+15% 实际时长 |
|------|---------|-----------------|
| 15s | ~60字 | ~12s |
| 30s | ~120字 | ~25s |
| 60s | ~240字 | ~50s |

配音一般比视频短 3-5 秒，刚好留出结尾 CTA 的静默氛围。
