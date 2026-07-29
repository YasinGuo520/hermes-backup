# Wan2.2 T2V Pipeline（SiliconFlow文生视频）

## API 端点

| 操作 | 方法 | URL | Body |
|------|------|-----|------|
| 提交 | POST | `https://api.siliconflow.cn/v1/video/submit` | `{"model":"Wan-AI/Wan2.2-T2V-A14B","prompt":"...","image_size":"720x1280"}` |
| 状态 | POST | `https://api.siliconflow.cn/v1/video/status` | `{"requestId":"..."}` |

**注意：** 是 `.cn` 不是 `.com`，状态查询是 POST 不是 GET。

## 完整提交+轮询+下载代码

```python
import json, urllib.request, re, os, time

with open(os.path.expanduser("~/.hermes/config.yaml"), "r") as f:
    content = f.read()
key = re.search(r'image_gen:.*?api_key:\s*(\S+)', content, re.DOTALL).group(1)
headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

# 1. 提交
payload = json.dumps({
    "model": "Wan-AI/Wan2.2-T2V-A14B",
    "prompt": "深色科技感动态背景，蓝紫渐变，发光数据流，竖屏9:16",
    "image_size": "720x1280",
}).encode("utf-8")
req = urllib.request.Request(
    "https://api.siliconflow.cn/v1/video/submit", data=payload, headers=headers)
with urllib.request.urlopen(req, timeout=30) as resp:
    request_id = json.loads(resp.read())["requestId"]

# 2. 轮询（每10秒，最长10分钟）
for i in range(60):
    time.sleep(10)
    status_req = urllib.request.Request(
        "https://api.siliconflow.cn/v1/video/status",
        data=json.dumps({"requestId": request_id}).encode(),
        headers=headers)
    with urllib.request.urlopen(status_req, timeout=15) as resp:
        status = json.loads(resp.read())
    
    state = status.get("status", "")
    print(f"[{i+1}] {state}")
    
    if state == "Succeed":
        url = status["results"]["videos"][0]["url"]
        # 立即下载（URL有时效）
        dl = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(dl, timeout=60) as d:
            data = d.read()
        with open("ai_bg_video.mp4", "wb") as f:
            f.write(data)
        break
    elif state == "Failed":
        print(f"失败: {status.get('reason','')}")
        break
```

## 作为背景集成到视频流水线

### 硬切方式（最稳）

```python
from moviepy import VideoFileClip, concatenate_videoclips

bg = VideoFileClip("ai_bg_video.mp4")  # 通常只有5秒

def make_slide(bg_clip, title_text, subtitle_text, duration):
    # 循环短背景到所需时长
    bg_dur = bg_clip.duration
    loops = max(1, math.ceil(duration / bg_dur))
    parts = [bg_clip] * loops
    bg_looped = concatenate_videoclips(parts, method="chain")
    bg_segment = bg_looped.subclipped(0, duration).resized((720, 1280))
    
    # 半透明遮罩（让文字清晰）
    def darken(t):
        import numpy as np
        f = np.zeros((1280, 720, 3), dtype=np.uint8)
        return f
    overlay = VideoClip(frame_function=darken, duration=duration).with_opacity(0.35)
    
    clips = [bg_segment, overlay]
    # ...叠加文字...
    return CompositeVideoClip(clips, size=(720, 1280))
```

### 交叉溶解方式（平滑过渡，推荐）

```python
from moviepy import VideoFileClip, concatenate_videoclips, CompositeVideoClip
from moviepy.video.fx import CrossFadeIn

bg = VideoFileClip("ai_bg_video.mp4")

# 1. 制作所有分镜（硬切，不做淡入淡出）
slides = []
for dur, title, sub in SCENES:
    slide = make_slide(bg, title, sub, dur)
    slides.append(slide)

# 2. 用 CrossFadeIn + CompositeVideoClip 重叠
OVERLAP = 0.3
composite_clips = []
t = 0.0
for i, s in enumerate(slides):
    if i > 0:
        s = s.with_effects([CrossFadeIn(OVERLAP)])
    composite_clips.append(s.with_start(t))
    t += s.duration - OVERLAP

video = CompositeVideoClip(composite_clips, size=(720, 1280))
video = video.with_duration(t + slides[-1].duration)
```

## ⚠️ 陷阱

1. **不要用 FadeIn/FadeOut** — 与 VideoFileClip 不兼容，会报 `NoneType has no attribute 'get_frame'`
2. **交叉溶解用 CrossFadeIn** — 已验证与 VideoFileClip 兼容，用 `with_effects([CrossFadeIn(0.3)])` 配合 `CompositeVideoClip` + `with_start()` 实现
3. **不要关掉 bg_video** — `bg_video.close()` 会导致所有引用的循环片段丢失 reader
4. **Wan2.2 只能生成氛围画面** — 带具体角色/叙事的视频它做不了
5. **生成耗时 3-9 分钟** — 前端等待时要设足够长的 timeout
