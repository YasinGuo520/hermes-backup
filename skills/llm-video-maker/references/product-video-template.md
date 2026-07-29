# Product Video Scene Template (30s · 6-Shot · 9:16 Portrait)

For fashion/lingerie/accessory product videos using AI keyframes + Ken Burns animation.

## Shot Plan

| Shot | Time | Size | Subject | Narration | Animation |
|------|------|------|---------|-----------|-----------|
| 1 | 0-5s | 全景 | Establish scene (bedroom/dressing room) with model + product | Opening hook: emotional/value statement | Ken Burns zoom 1.15→1.25 |
| 2 | 5-10s | 中景 | Model adjusting/wearing product, side view | Feature benefit: fit, comfort, design | Ken Burns zoom 1.1→1.2 |
| 3 | 10-15s | 特写 | Fabric texture close-up, hand touching material | Sensory detail: touch, feel, quality | Ken Burns zoom 1.15→1.3 |
| 4 | 15-20s | 中景 | Different angle (back/side), showing unique design | Design detail: craftsmanship detail | Ken Burns zoom 1.1→1.2 |
| 5 | 20-25s | 特写 | Light playing on fabric, artistic detail shot | Emotional: confidence, elegance | Ken Burns zoom 1.15→1.3 |
| 6 | 25-30s | 全景 | Full shot, model smiling, product name | CTA/closing: brand + call to action | Ken Burns zoom 1.1→1.2 + CTA button |

## Narration Pacing

- Total narration: ~22-25s (video is 30s, leave 5-8s for final CTA silence)
- Each shot's narration: ~3-4 seconds
- Tone: warm, poetic, confident — NOT aggressive sales
- edge-tts rate: +5% (moderate, not pushy)

## HTML Composition Pattern

```html
<!-- Each scene: img + gradient overlay + caption -->
<div class="clip" data-start="N" data-duration="5" data-track-index="0">
  <img id="bg{N}" class="scene-bg" src="assets/shot_0{N}.png" />
  <div class="clip warm-overlay" data-start="N" data-duration="5" data-track-index="1"></div>
  <div id="txt{N}" class="clip poem-line" style="top:640px;" data-start="N+0.8" data-duration="3.5" data-track-index="3">
    <span class="line1">文案第一行</span>
    <span class="line2">文案第二行</span>
  </div>
</div>

<!-- Transition: white flash at scene boundaries -->
<div id="flash{N}" class="clip flash-overlay" data-start="N+4.8" data-duration="0.4" data-track-index="10"></div>
```

## Color Palette (Warm Feminine)

| Role | Color | Usage |
|------|-------|-------|
| Overlay top | `rgba(255,200,150,0.08)` | Warm skin tone tint |
| Text | `#fff` with `text-shadow` | Readability on bright images |
| CTA button | `linear-gradient(135deg, #d4a0b0, #c08090)` | Rose gold, feminine |
| Tag background | `rgba(255,200,180,0.15)` + backdrop-filter | Glassmorphism product tag |
| Flash | `#fff` opacity 0.5 | Clean scene transition |
