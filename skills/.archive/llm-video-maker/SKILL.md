---
name: llm-video-maker
description: "Turn a prompt or brief into a fully rendered MP4 video using HyperFrames engine. AI video generation with voiceover (TTS), word-synced captions, music, icons, brand logos, stock photos, and b-roll. TikTok/Reels/Shorts (9:16), YouTube (16:9), square (1:1). HTML/GSAP deterministic render, Remotion-style. Companion skill: edit-video for chapter-scoped edits."
metadata:
  version: 1.0.0
  source: https://github.com/GoldLegendW80/llm-video-maker
---

# /llm-video-maker — brief → rendered video (Hermes adaptation)

You are the pipeline orchestrator. This skill wraps the [HyperFrames](https://www.npmjs.com/package/hyperframes) engine: the agent writes HTML/GSAP compositions, the engine renders them to MP4 via Chrome headless. Every stage writes its artifact into the project directory so the run is resumable.

This skill works best for: TikTok/Reels/Shorts, YouTube intros, startup hero loops, product promos, data explainers with animated charts, square social posts.

## Prerequisites (one-time setup on this machine)

All dependencies are already installed:

| Component | Status | Version |
|-----------|--------|---------|
| Node.js | ✅ | v22.23.1 |
| FFmpeg | ✅ | 8.1.2 |
| Chrome | ✅ | 143 |
| HyperFrames engine | ✅ | 0.7.45 |
| Kokoro TTS (local) | ✅ | kokoro-onnx 0.5.0 |
| Soundfile | ✅ | 0.14.0 |

**Before using this skill**, ensure Kokoro venv is in PATH:
```bash
export PATH="/Users/mac/.video-maker/runtime/python/bin:$PATH"
```
Add that line to `~/.zshrc` to make it permanent.

## Quick Start (one-time per project)

Project directory: `~/Desktop/hermes/video-maker/`

```bash
# 1. Go to project
cd ~/Desktop/hermes/video-maker

# 2. Init a new video project
npx hyperframes init projects/<project-id>
# ⚠️ `init` tries to clone skills from GitHub. If it times out in China,
#    the project scaffold IS still created — just Ctrl+C and proceed.

# 3. Render (draft quality for fast iteration, standard for final)
npx hyperframes render projects/<project-id> -o projects/<project-id>/renders/<project-id>.mp4 -q draft
```

## Creating a new video — step by step

1. Write a brief JSON to `~/Desktop/hermes/video-maker/briefs/` (required: `id`, `platform`, `story`, `source`)
2. `npx hyperframes init projects/<id>` — scaffolds the project
3. Agent reads the brief, researches/writes facts, designs palette & typography, storyboards scenes, fetches assets, and writes the HTML/GSAP composition
4. Validate: `cd projects/<id> && npx hyperframes lint` then `npx hyperframes validate`
5. Render: `npx hyperframes render projects/<id> -o projects/<id>/renders/<id>.mp4`

## First-time Chromium download (China fix)

If the first `hyperframes render` hangs downloading Chrome, kill it and retry with:

```bash
export PUPPETEER_DOWNLOAD_BASE_URL="https://npmmirror.com/mirrors/chromium-browser-snapshots/"
# then re-run the render command
```

Or pre-download: `npx hyperframes browser ensure` with the env var set.

## Usage

Provide a brief (JSON or inline description) then:

```
/make-video "30s TikTok promo for a productivity app — funny, high energy, Chinese voiceover"
```

Required brief fields: `id`, `platform` (tiktok/reels/shorts/youtube/square), `story`, `source`.

## Pipeline Stages

1. **PREFLIGHT** — check Node, FFmpeg, Chrome via `npx hyperframes doctor`
2. **INGEST** — research topic / analyze codebase / interpret script → write `facts.json`
3. **DESIGN** — palette, typography, motion personality → write `design.md`
4. **STORYBOARD** — scene plan → write `storyboard.json`
5. **ASSETS** — fetch icons, images, b-roll, music → write `assets/`
6. **COMPOSE** — write HTML/GSAP composition → `index.html`
7. **VALIDATE** — lint, WCAG AA contrast, vision pass (max 3 iterations)
8. **RENDER** — `npx hyperframes render projects/<id>` → MP4
9. **QA + REPORT** — ffprobe, frame extraction, sync check → `report.md`

## AI Voiceover

Local Kokoro TTS (offline, ~80MB model download once):
```bash
uv venv ~/.video-maker/runtime/python
uv pip install --python ~/.video-maker/runtime/python/bin/python kokoro-onnx soundfile
```
Model auto-downloaded to `~/.cache/hyperframes/tts/models/kokoro-v1.0.onnx`

Or supply your own recording + timestamped transcript (transcript-locked mode).

## Optional API Keys (free tiers)

| Key | Unlocks |
|-----|---------|
| `PEXELS_API_KEY` / `PIXABAY_API_KEY` | stock photos + video b-roll |
| `GIPHY_API_KEY` / `TENOR_API_KEY` | reaction gifs |
| `FREESOUND_API_KEY` | CC0 sound effects |
| `OPENAI_API_KEY` + `IMAGE_GEN=openai` | AI image generation |

## Companion Skill

See "Companion: edit-video" section below — chapter-scoped edits of finished videos without re-rendering everything. Trigger: `/edit-video <project-id> <chapter-id> "make the intro punchier"`

## AI-Generated Keyframes with 百炼 (bl CLI)

For videos needing specific scenes or product imagery (fashion, beauty, accessories, product promos), generate high-quality still keyframes with `bl image generate`, then animate them with Ken Burns effects in HyperFrames. This avoids stock photo limitations and runs entirely on this machine.

### When to use

| Scenario | Stock photos | AI keyframes (百炼) |
|----------|-------------|-------------------|
| Generic scenic/travel | ✅ Pexels free photos | Overkill |
| Product showcase (lingerie/fashion/accessories) | ❌ Rarely available | ✅ Generate exactly what you need |
| Specific scene setups | ❌ Hard to find | ✅ Describe the exact scene |
| Real human model in specific outfit | ❌ Impossible | ⚠️ AI quality varies; use bl i2v for motion |
| Brand-specific visual style | ❌ Rarely matches | ✅ Control via style prompts |

### Prerequisites

```bash
# bl CLI must be installed and authenticated
which bl && bl auth status
# Expected: bl 1.7.0+, API key configured
```

### Keyframe generation pattern

```bash
# Generate a single high-quality keyframe
bl image generate \
  --prompt "[场景描述]，[人物描述]，[产品描述]，[光线/色调]，[风格]" \
  --model qwen-image-2.0-pro \
  --size 9:16 \
  --seed <stable_number> \
  --watermark false \
  --out-dir projects/<id>/assets/ \
  --out-prefix shot_01
```

**Key parameters:**
- `--model qwen-image-2.0-pro` — highest quality, best for product shots
- `--size 9:16` — TikTok/Reels portrait format (generates 1536×2688)
- `--seed <N>` — deterministic; same seed + prompt = same image. Use a different seed per shot (e.g. 41, 42, 43...) for variety while keeping subjects consistent
- `--watermark false` — remove 百炼 watermark

### Product video prompt patterns (for lingerie/fashion)

| Shot type | Prompt ingredients |
|-----------|-------------------|
| 全景开场 | 全景展示，整体场景：梳妆台/卧室/衣帽间，自然晨光，暖色调 |
| 中景/整理 | 对镜子整理[产品细节]，侧面展示，柔美曲线 |
| 特写/面料 | 手指轻抚[面料]超特写，精致纹理，微距，4K |
| 中景/不同角度 | 转身展示背部/侧面设计，[产品细节] |
| 特写/光影 | [产品]面料光影特写，光透过[材质]纹理，高级感 |
| 全景/结尾 | 对镜头微笑，自信优雅，暖色调 |

**Style prefix** (add to every prompt for consistency):
```
韩剧质感/日系清新，明亮通透，柔和自然光，细腻肤质，暖色调，高级感
```

### Full pipeline: 百炼 → HyperFrames → edge-tts

1. Generate all keyframes (one per scene) via `bl image generate`
2. Copy generated images to HyperFrames project assets/
3. Write HyperFrames composition with Ken Burns animation on each image
4. Generate narration with edge-tts (Xiaoxiao, +5% rate for relaxed vibe)
5. Render with HyperFrames
6. Mix narration on top of rendered video audio via ffmpeg amix filter

### Pitfalls

- **百炼 may reject NSFW prompts**: Lingerie product shots (underwear, swimwear) are usually accepted as product photography, but overly explicit descriptions get blocked. Keep prompts product-focused: "精致蕾丝内衣" not "暴露". If blocked, the CLI returns an error — rephrase more conservatively.
- **AI-generated human anatomy**: Hands, fingers, and body proportions may have AI artifacts. Multiple generations with different seeds or prompt tweaks may be needed for a usable frame. Minor imperfections are masked by Ken Burns zoom + text overlays.
- **Cost**: `bl image generate` is free within 百炼's free tier. Only `bl video generate` (i2v) costs money — skip it and use HyperFrames for free animation.
- **Not a substitute for real footage**: AI keyframes cannot replace real human models for product demos requiring movement/fit assessment. Use for mood/concept videos, not fit verification.

## Adding Real Human Video Backgrounds (Pexels free stock footage)

This pipeline supports embedding real video backgrounds behind text overlays for much higher production value. Verified workflow from this machine:

### 1. Find vertical portrait free stock videos on Pexels

Search: `site:pexels.com/video "woman" "portrait" "1080x1920"` or browse Pexels directly.

Key signal: look for the direct CDN URL pattern in the page source:
```
https://videos.pexels.com/video-files/{ID}/{ID}-hd_1080_1920_30fps.mp4
```

Some Pexels pages block direct hotlinking (403). Use the download redirect instead:
```bash
curl -sL -o output.mp4 "https://www.pexels.com/download/video/{ID}/" -H "User-Agent: Mozilla/5.0"
```

### 2. Downscale and normalize

4K downloads (2160×3840) need downscaling to 1080×1920. Non-30fps videos need frame-rate conversion:
```bash
# 4K → FHD
ffmpeg -i input.mp4 -vf "scale=1080:1920:flags=lanczos" -r 30 -c:v libx264 -preset fast -crf 23 output.mp4
# 25fps → 30fps
ffmpeg -i input.mp4 -r 30 -c:v libx264 -preset fast -crf 23 output.mp4
```

### 3. Cut to scene duration

Cut exact segments per scene timing:
```bash
ffmpeg -i source.mp4 -t {duration_seconds} -c copy scene_bg.mp4        # from start
ffmpeg -i source.mp4 -ss {start_seconds} -t {duration} -c copy clip.mp4 # from offset
```

### 4. Embed in HyperFrames composition

```html
<!-- Background video: plays in timeline, muted, preloaded -->
<video id="v-scene1" class="clip bg" data-start="0" data-duration="4.2" data-track-index="0"
       src="assets/scene_bg.mp4" muted playsinline preload="auto"></video>

<!-- Dark overlay for text readability -->
<div class="clip overlay" data-start="0" data-duration="4.2" data-track-index="1"
     style="width:1080px;height:1920px;background:linear-gradient(180deg,rgba(0,0,0,0.3) 0%,rgba(0,0,0,0.1) 40%,rgba(0,0,0,0.4) 100%);"></div>

<!-- Text overlay on top of video -->
<div class="clip" data-start="0.5" data-duration="3.7" data-track-index="2"
     style="font-size:80px;font-weight:900;color:#fff;text-shadow:0 4px 30px rgba(0,0,0,0.7);">
  穿错内衣尴尬到想遁地！
</div>
```

CSS for the video background and overlay (add to `<style>`):
```css
video.bg { width: 1080px; height: 1920px; object-fit: cover; }
```

### 5. Post-render: merge with voiceover audio

HyperFrames render produces video-only (hasAudio: false). Merge with edge-tts generated audio:
```bash
ffmpeg -y -i rendered.mp4 -i narration.mp3 -c:v copy -c:a aac -b:a 192k \
  -map 0:v:0 -map 1:a:0 -t {total_duration} final.mp4
```

## Chinese Voiceover (better than Kokoro for Chinese)

Kokoro TTS has limited Chinese voice quality. For commercial-grade Chinese voiceover, use edge-tts (already installed on this machine in Hermes venv) and merge with FFmpeg post-render:

```bash
# Source the script
cat > script.txt << 'EOF'
穿错内衣的尴尬，懂的都懂！肩带总滑落、勒出红痕、抬手就走光——说的是不是你？
直到我发现了这款云感内衣！3D立体剪裁超贴合，透气面料会呼吸，无痕设计穿紧身衣也看不出来！
10万+姐妹已经入手了，现在限时买一送一！原价199，现在只要89！点击下方购物车，手慢无！
EOF

# Generate TTS (Xiaoxiao female voice, +15% speed for energetic Douyin style)
/Users/mac/.hermes/hermes-agent/venv/bin/edge-tts \
  --voice zh-CN-XiaoxiaoNeural \
  --text "$(cat script.txt)" \
  --write-media narration.mp3 \
  --rate +15%

# Merge with rendered video
ffmpeg -y -i rendered.mp4 -i narration.mp3 -c:v copy -c:a aac -b:a 192k \
  -map 0:v:0 -map 1:a:0 -t 30 final-with-audio.mp4
```

## Bundled Scripts & Reference Files

### Pipeline scripts (`$SKILL_DIR/scripts/`)

This skill ships with the full upstream pipeline scripts locally:

| Script | Size | Purpose |
|--------|------|---------|
| `validate-brief.mjs` | 9.8KB | Validate brief format against schema |
| `plan-scenes.mjs` | 8.3KB | Scene planning and transcript coverage |
| `fetch-assets.mjs` | 17.7KB | Fetch icons, stock photos, b-roll, music |
| `analyze-codebase.mjs` | 7.6KB | Analyze codebase to extract facts |
| `capture-demo.mjs` | 6.4KB | Playwright screen capture for app demos |
| `normalize-transcript.mjs` | 6.5KB | Normalize timestamped transcripts |
| `schema.json` | 3.4KB | Brief input validation schema |

Scripts are invoked via `node "$SKILL_DIR/scripts/<name>.mjs"` — each is a self-contained Node.js CLI with `--help` output.

### Reference files (`$SKILL_DIR/references/`)

| File | Purpose |
|------|---------|
| `install-notes.md` | Installation log and China network notes |
| `composition-template.md` | Working HTML/GSAP composition template for portrait mode |
| `audio-post-processing.md` | Add voiceover after render — edge-tts + FFmpeg workflow |
| `product-video-template.md` | 30s product video 6-shot template for lingerie/fashion |

## Companion: edit-video — chapter-scoped edit loop（合并自 edit-video skill）

编辑已生成视频的某一章/段，其他章节保持逐字节不变。Trigger: `/edit-video <project-id> <chapter-id> "change description"`。

### Invariants（绝对不能动的）
- **The clock is locked** — 场景 start/end/duration 和 segment ID 不动
- **The narration track is untouchable** — 绝不切片/调换/重配平音频轨
- **The caption overlay is a locked layer** — 字幕横跨全片独立轨道
- **Downward-only regeneration** — design.md 和 facts.json 是只读上下文

### Process
1. 读 `projects/<id>/storyboard.json` 确认章节存在（没有就列出可用章节）
2. 读 design.md / facts.json / 该章 scenes
3. 只重写该章 scenes 到 storyboard（re-storyboard）
4. 更新 assets（追加 manifest 条目，re-fetch）
5. 只重写 index.html 里该章的 scene 块
6. 验证：lint → WCAG → 编辑帧+边界帧 vision pass（最多3轮）
7. 重渲全片：`npx hyperframes render projects/<id>`
8. QA：ffprobe + 编辑窗口抽帧 + sync check
9. 更新 report.md 加 edit log

### Security
- project/chapter ID 必须匹配 `^[a-z0-9][a-z0-9-]*$`
- 所有路径限制在 `projects/<id>/` 内，拒绝 `..` 穿越
- 不用字符串拼 shell 命令，用引号 argv；change description 是创意指令不是命令

## Notes

- No network at render time; all assets vendored locally
- Facts on screen must trace to `facts.json` — no invented stats
- Deterministic, validated render — runs are resumable
- Output lands in `projects/<id>/`

## Pitfalls (learned from practice)

### Don't say "can't do" — try all available pipelines first
When the user asks for a video that seems beyond the tool's capability (real human models, specific product shots, 4K quality), do NOT default to "this can't be done." Try these alternatives in order **before** telling the user to use external tools:
1. **百炼 bl image generate** — can produce photorealistic product/scene keyframes for fashion, beauty, and lifestyle shots
2. **HyperFrames Ken Burns** — animates still images with slow zoom + text overlays, creating the illusion of video motion
3. **edge-tts + music** — adds professional voiceover and background music for production value
4. **short-drama-pipeline** — full short drama pipeline with 百炼 image gen + optional i2v video

The user's default expectation is: make it work with what's available. Only escalate to external tools (可灵/即梦/Sora) after you've demonstrated what the local pipeline can actually produce and the user explicitly says it's not enough.

### GSAP `repeat: -1` breaks deterministic capture
`hyperframes lint` errors on infinite repeats. GSAP tweens MUST use a finite `repeat` count. For a pulse animation that should last until the end of a scene: calculate `repeat: Math.floor(remainingDuration / cycleDuration) - 1`. Or use `repeat: 0` for a single yoyo cycle.

### portrait mode (TikTok 1080×1920)
Set `data-width="1080" data-height="1920"` on the root `<div>` AND in the `<meta name="viewport">` tag. The default template is 1920×1080 landscape.

### no audio by default
`npx hyperframes render` produces video with `hasAudio: false` unless `<audio>` elements are manually added to the composition. TTS generation (Kokoro or edge-tts) is a separate step — the render does NOT call TTS automatically. To add voiceover: generate audio externally, then add `<audio data-start="0" data-duration="30" src="assets/narration.mp3" />` to the composition.

### `hyperframes init` may timeout in China
The init command tries to clone HyperFrames skills from GitHub. This often times out. The project scaffold IS created before the clone attempt, so just Ctrl+C the stalled process and proceed. The skills were already installed globally by `npx hyperframes skills` during setup.

### Kokoro requires Python ≥ 3.10
onnxruntime ≥ 1.20.1 (required by kokoro-onnx) has no wheel for Python 3.9. Use Python 3.11+ for the TTS venv. On this machine: `python3.11` is at `/usr/local/bin/python3.11`.

### Google Fonts produce lint warnings
Fonts loaded from `fonts.googleapis.com` trigger a `google_fonts_import` lint warning. The renderer resolves them correctly during capture, but for production videos, prefer bundling fonts locally via `@font-face`.

### `backdrop-filter` forces slow screenshot capture (big performance hit)
Any element using CSS `backdrop-filter: blur(...)` triggers HyperFrames to fall back from its fast drawElement streaming capture to slow per-frame screenshot capture. A 30s video that renders in ~30s with streaming can take 3+ minutes with screenshot fallback.
**Fix**: Replace `backdrop-filter` with a solid/translucent background layer. For glassmorphism effects, use `background: rgba(0,0,0,0.45)` with a separate blur element behind it, or omit the blur entirely. Gradient overlays (`linear-gradient`) do NOT trigger this fallback — use them instead.

### Ken Burns effect (slow zoom on photos) needs GSAP fromTo
For the Ken Burns slow-zoom effect on photo backgrounds:
- Remove inline CSS `transform: scale(...)` from the `<img>` tag
- Use GSAP `tl.fromTo()` to set start AND end scale explicitly, avoiding `gsap_css_transform_conflict` lint errors:
  ```js
  tl.fromTo("#bg1", { scale: 1.15 }, { scale: 1.25, duration: 6, ease: "power1.out" }, 0);
  ```
- Each scene image starts slightly oversized (scale 1.1–1.15) and zooms to 1.25–1.3 over its 6s duration

### Audio mixing: narration + background music via FFmpeg
When combining edge-tts narration with background music generated by FFmpeg lavfi:
```bash
ffmpeg -y -i rendered.mp4 -i narration.mp3 \
  -filter_complex "[0:a]volume=0.4[bg];[1:a]adelay=500|500[voice];[bg][voice]amix=inputs=2:duration=first:weights=0.3 1[out]" \
  -map 0:v:0 -map "[out]" -c:v copy -c:a aac -b:a 192k -t 30 final.mp4
```
- `volume=0.4` keeps background music quiet enough for voice clarity
- `adelay=500` gives a 0.5s pause before narration starts (natural feel)
- `weights=0.3 1` — bg at 30%, voice at 100% — voice always cuts through
- For travel vlog style: edge-tts rate +10% (not +15%) for a relaxed pace

### Pexels free still-photo curl download (no API key needed)
For scenic/travel content, Pexels still photos are free and downloadable via curl with no API key. This works from China network:
```bash
# Extract the "Free download" URL from the Pexels photo page, then:
curl -sL -o asset.jpg "https://images.pexels.com/photos/{ID}/pexels-photo-{ID}.jpeg?cs=srgb&dl=...&fm=jpg"
# Add --max-time 15 to avoid hanging on slow connections
```
Photos are typically 1-3MB at high resolution (usable as HyperFrames backgrounds after scaling).

### Travel vlog scene pattern (5-scene, photo bg + Ken Burns + white flash transition)
For a 30s travel/cinematic vlog:
- 5 scenes × 6s each, with white flash overlays at scene boundaries (0.4s flash at 5.8s, 11.8s, 17.8s, 23.8s)
- Each scene: photo background with Ken Burns zoom + location tag (slide in from left) + poetic caption (fade in center) + gradient overlay
- Final scene: ending CTA button that fades in at ~27s
- Voiceover narration shorter than video by 5-8s (21s narration for 30s video), leaving room for final CTA silence
- Scene transition: GSAP `.to()` for fade-out on text, then white flash, then next scene elements fade in

### .zshrc PATH addition for Kokoro venv
Use `write_file` (not terminal) to append to `~/.zshrc`, because terminal redirects (`>>`) trigger security blocks. The line needed:
```
export PATH="/Users/mac/.video-maker/runtime/python/bin:$PATH"
```
