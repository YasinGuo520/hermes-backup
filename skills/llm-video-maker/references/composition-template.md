# HyperFrames Composition Template (TikTok portrait)

Minimal working structure for a portrait TikTok/Reels/Shorts video at 1080×1920, 30fps.

## Root structure

```html
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <!-- Chinese font + GSAP as only dependencies -->
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;700;900&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { margin: 0; width: 1080px; height: 1920px; overflow: hidden; }
      .clip { position: absolute; }
      #root { width: 1080px; height: 1920px; position: relative; }

      /* Photo background — for Ken Burns effect (still photos as bg) */
      .photo-bg {
        width: 1100px; height: 1960px; object-fit: cover;
        position: absolute; top: -20px; left: -10px;
      }

      /* Video background — for Pexels stock footage integration */
      video.bg { width: 1080px; height: 1920px; object-fit: cover; }

      /* Dark overlay for text readability on photo/video bg */
      .vb-overlay {
        position: absolute; top: 0; left: 0; width: 1080px; height: 1920px;
        background: linear-gradient(180deg,
          rgba(0,0,0,0.15) 0%, rgba(0,0,0,0.05) 30%,
          rgba(0,0,0,0.05) 60%, rgba(0,0,0,0.4) 85%, rgba(0,0,0,0.7) 100%);
      }

      /* Location tag — pill shape, top left */
      .location-tag {
        position: absolute; top: 60px; left: 60px;
        background: rgba(255,255,255,0.15);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 50px; padding: 14px 30px;
        border: 1px solid rgba(255,255,255,0.2);
        font-family: 'Noto Sans SC', sans-serif;
      }
      .location-tag span { color: #fff; font-size: 28px; font-weight: 400; letter-spacing: 4px; }

      /* Poetic caption — center screen */
      .poem-line {
        font-family: 'Noto Sans SC', sans-serif; color: #fff;
        text-shadow: 0 4px 30px rgba(0,0,0,0.6);
        text-align: center; position: absolute; width: 100%; padding: 0 60px;
      }
      .poem-line .line1 { font-size: 56px; font-weight: 700; display: block; line-height: 1.5; }
      .poem-line .line2 { font-size: 32px; font-weight: 300; opacity: 0.8; display: block; margin-top: 20px; line-height: 1.5; }

      /* White flash overlay for scene transitions */
      .flash-overlay {
        position: absolute; top: 0; left: 0; width: 1080px; height: 1920px;
        background: #fff; opacity: 0;
      }

      /* CTA pill button */
      .cta-pill {
        position: absolute; bottom: 200px; width: 100%; text-align: center;
        font-family: 'Noto Sans SC', sans-serif; font-size: 32px;
        color: rgba(255,255,255,0.7); letter-spacing: 6px;
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px); padding: 16px 40px;
        border-radius: 50px; border: 1px solid rgba(255,255,255,0.2);
      }

      /* Glass card (NOT recommended — backdrop-filter triggers slow capture) */
      .g-card {
        width: 800px; padding: 30px 40px; border-radius: 25px;
        background: rgba(0,0,0,0.45);
        border: 2px solid rgba(255,255,255,0.15);
      }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main"
         data-start="0" data-duration="30"
         data-width="1080" data-height="1920">

      <!-- ===== PROVEN PATTERN: photo bg + overlay + location tag + poem + flash ===== -->
      <!-- Example: single scene from 30s travel vlog (6s per scene) -->

      <!-- SCENE frame: covers full screen -->
      <div id="scene1" class="clip" data-start="0" data-duration="6" data-track-index="0">
        <!-- Photo bg: no inline scale (GSAP handles it) -->
        <img id="bg1" class="photo-bg" src="assets/scene1.jpg" />
        <!-- Gradient overlay -->
        <div class="clip vb-overlay" data-start="0" data-duration="6" data-track-index="1"></div>
        <!-- Location tag: slides in from left -->
        <div id="loc1" class="clip location-tag" data-start="0.5" data-duration="5" data-track-index="2">
          <span>📍 云南 · 大理</span>
        </div>
        <!-- Poetic caption: bounces in -->
        <div id="poem1" class="clip poem-line" style="top:600px;" data-start="1" data-duration="4" data-track-index="3">
          <span class="line1">在大理，时间很慢</span>
          <span class="line2">洱海很蓝</span>
        </div>
      </div>

      <!-- White flash transition between scenes -->
      <div id="flash1" class="clip flash-overlay" data-start="5.8" data-duration="0.4" data-track-index="10"></div>

      <!-- ===== PROVEN PATTERN: video bg (Pexels) + overlay + text ===== -->
      <video id="v-scene2" class="clip bg" data-start="6" data-duration="6"
             data-track-index="0" src="assets/scene_bg.mp4" muted playsinline preload="auto"></video>
      <div class="clip vb-overlay" data-start="6" data-duration="6" data-track-index="1"></div>
      <div id="s2-title" class="clip" data-start="6.5" data-duration="5"
           data-track-index="2" style="top:600px;width:100%;text-align:center;">
        <span class="poem-line" style="font-size:56px;">视频背景场景</span>
      </div>

      <!-- ... more scenes ... -->

      <!-- ===== PROVEN PATTERN: ending CTA ===== -->
      <div id="cta" class="clip" style="position:absolute;bottom:200px;width:100%;text-align:center;opacity:0;"
           data-start="27" data-duration="3" data-track-index="4">
        <span class="cta-pill">✦ 关注我，看更多 ✦</span>
      </div>

      <!-- ===== PROVEN PATTERN: background music ===== -->
      <audio id="bg-audio" class="clip" data-start="0" data-duration="30" data-track-index="20"
             src="assets/bg_music.mp3" loop></audio>
    </div>

    <script>
      window.__timelines = window.__timelines || {};
      const tl = gsap.timeline({ paused: true });

      // SCENE 1 (0-6s): Ken Burns zoom + fade in + fade out
      tl.fromTo("#bg1", { scale: 1.15 }, { scale: 1.25, duration: 6, ease: "power1.out" }, 0);
      tl.from("#loc1", { opacity: 0, x: -40, duration: 0.6, ease: "power2.out" }, 0.5);
      tl.from("#poem1 .line1", { opacity: 0, y: 40, duration: 0.7, ease: "back.out(1.7)" }, 1);
      tl.from("#poem1 .line2", { opacity: 0, y: 30, duration: 0.6, ease: "power2.out" }, 1.6);
      tl.to("#poem1", { opacity: 0, y: -20, duration: 0.5, ease: "power2.in" }, 5);

      // White flash transition
      tl.to("#flash1", { opacity: 0.6, duration: 0.15, ease: "power1.out" }, 5.8);
      tl.to("#flash1", { opacity: 0, duration: 0.25, ease: "power1.in" }, 5.95);

      // SCENE 2 (6-12s): ...
      // (Ken Burns + fade in/out pattern repeats for each scene)

      // SCENE 5 ENDING: CTA fade in
      tl.to("#cta", { opacity: 1, y: -10, duration: 0.8, ease: "power2.out" }, 27.5);

      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
```

## Timing rules

- Each clip has `data-start`, `data-duration`, `data-track-index`
- GSAP tween's position parameter (last arg) = absolute seconds, corresponding to `data-start`
- Scene divs cover the full frame and use `data-track-index="0"` (background layer)
- Text/emoji elements use `data-track-index="1"` and up (foreground layers)
- Scene transitions are handled by GSAP opacity/position tweens, not by video cuts
- Video backgrounds: MUST have `muted playsinline preload="auto"`

## 5-scene travel vlog pattern (verified 30s)

| Offset | Duration | Content |
|--------|----------|---------|
| 0s | 6s | Scene 1: intro location, main caption |
| 5.8s | 0.4s | White flash transition |
| 6s | 6s | Scene 2: secondary location |
| 11.8s | 0.4s | White flash transition |
| 12s | 6s | Scene 3: reflective / solo moment |
| 17.8s | 0.4s | White flash transition |
| 18s | 6s | Scene 4: cultural / architectural |
| 23.8s | 0.4s | White flash transition |
| 24s | 6s | Scene 5: final scene + CTA |
| 27.5s | 2.5s | CTA fades in |
| 30s | — | End |

Voiceover lasts ~21s for a 30s video (leaves 9s for opening/closing silence + CTA).

## Scene structure (per scene)

```html
<div id="sceneN" class="clip" data-start="{offset}" data-duration="6" data-track-index="0">
  <img id="bgN" class="photo-bg" src="assets/sceneN.jpg" />
  <div class="clip vb-overlay" data-start="{offset}" data-duration="6" data-track-index="1"></div>
  <div id="locN" class="clip location-tag" style="opacity:0;" data-start="{offset+0.5}" data-duration="5" data-track-index="2">
    <span>📍 地点名称</span>
  </div>
  <div id="poemN" class="clip poem-line" style="top:640px;opacity:0;" data-start="{offset+1}" data-duration="4.5" data-track-index="3">
    <span class="line1">主文案</span>
    <span class="line2">副文案</span>
  </div>
</div>
```

GSAP for each scene:
```js
tl.fromTo("#bgN", { scale: 1.15 }, { scale: 1.25, duration: 6, ease: "power1.out" }, offset);
tl.fromTo("#locN", { opacity: 0, x: -40 }, { opacity: 1, x: 0, duration: 0.6, ease: "power2.out" }, offset+0.5);
tl.fromTo("#poemN", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.7, ease: "power2.out" }, offset+1);
tl.to("#poemN", { opacity: 0, y: -20, duration: 0.5, ease: "power2.in" }, offset+5);
```

White flash transition:
```js
tl.to("#flashN", { opacity: 0.6, duration: 0.15, ease: "power1.out" }, offset+5.8);
tl.to("#flashN", { opacity: 0, duration: 0.25, ease: "power1.in" }, offset+5.95);
```

## GSAP animation tips

| Intent | GSAP pattern |
|--------|-------------|
| Bounce in | `{ opacity: 0, y: 60, scale: 0.5, duration: 0.6, ease: "back.out(1.7)" }` |
| Elastic pop | `{ scale: 0.3, duration: 0.5, ease: "elastic.out(1, 0.5)" }` |
| Slide in from left | `{ opacity: 0, x: -40, duration: 0.6, ease: "power2.out" }` |
| Ken Burns zoom | `fromTo(el, { scale: 1.15 }, { scale: 1.25, duration: 6, ease: "power1.out" })` |
| Stagger cards | Run `tl.from()` for each with 1-1.5s gap between position params |
| Shake | `{ x: 10, duration: 0.1, repeat: 3, yoyo: true }` |
| Pulse glow | `to()` with `{ scale: 1.08, duration: 1.5, repeat: 0, yoyo: true }` |

## Performance notes

- 30s at 30fps = 900 frames. Draft quality renders ~1-3 min on i7/16GB
- `backdrop-filter` triggers slow screenshot capture (~3 min for 30s) — avoid or use for final renders only
- Google Fonts resolve during capture but produce lint warnings — acceptable for draft
- Video backgrounds increase file size ~4-5x (2.8MB → 12MB for 30s)
- Avoid `background-image: url(...)` from network — inline gradients or base64 only
