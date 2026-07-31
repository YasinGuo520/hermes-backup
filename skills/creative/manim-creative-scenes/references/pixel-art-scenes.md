# 像素画画廊动画 — 完整模板与踩坑详录

2026-07 从 pixel-gallery 项目（Manim 动画版像素画展厅）沉淀。10 幅 16x16 像素画 → 720p/30fps 动画 → HTML 画廊页面。

## 完整脚本结构（manim_gallery.py）

```python
from manim import *
import random

# ── 统一画展视觉 ──
BG      = "#14110c"   # 深色画展墙
FRAME   = "#c9a84c"   # 金框
WALL_BG = "#2c2418"   # 画布底
TITLE_C = "#f5f0e6"   # 标题米白
SUB_C   = "#8a7e6a"   # 副标题灰金
MONO    = "WenQuanYi Zen Hei"

# ── 16x16 像素矩阵（. = 透明，字母 = 调色板 key） ──
ARTS = [
    dict(
        name="勇者", sub="NES Hero · 红白机经典", desc="蓝衣棕靴的像素英雄",
        palette={"H": "#e8c8a0", "B": "#2868b0"},
        pixels=[
            "................",
            "......HHHH......",
            "...（16 行，每行 16 字符）...",
        ],
    ),
    # ... 更多作品
]

def build_pixel_group(pixels, palette, cell=0.42):
    n = len(pixels)
    group = VGroup(); cells = []
    for r in range(n):
        for c, ch in enumerate(pixels[r]):
            if ch == "." or ch not in palette:
                continue
            sq = Square(side_length=cell, fill_color=palette[ch],
                        fill_opacity=1.0, stroke_width=0)
            sq.move_to([(c - n/2 + 0.5) * cell, (n/2 - 0.5 - r) * cell, 0])
            group.add(sq); cells.append(sq)
    return group, cells

class PixelArtScene(Scene):
    ART = None
    def construct(self):
        a = self.ART
        self.camera.background_color = BG
        # ⚠️ 画幅放宽：默认 14.22x8 会裁掉大画框
        self.camera.frame_width = 16.0
        self.camera.frame_height = 9.0

        canvas = RoundedRectangle(corner_radius=0.06, width=7.6, height=7.6,
                                  fill_color=WALL_BG, fill_opacity=0.9,
                                  stroke_color=FRAME, stroke_width=3)
        frame = RoundedRectangle(corner_radius=0.08, width=8.4, height=8.4,
                                 fill_color=BG, fill_opacity=0,
                                 stroke_color=FRAME, stroke_width=6)
        canvas.shift(UP * 1.2); frame.shift(UP * 1.2)
        self.play(Create(frame), Create(canvas), run_time=1.0)
        self.wait(0.2)

        # 标题放画框下方（博物馆标签式），避免上方超界
        title = Text(a["name"], font_size=44, color=TITLE_C, weight=BOLD, font=MONO)
        title.next_to(frame, DOWN, buff=0.45)
        sub = Text(a["sub"], font_size=20, color=SUB_C, font=MONO)
        sub.next_to(title, DOWN, buff=0.1)
        self.play(Write(title), FadeIn(sub, shift=DOWN * 0.3), run_time=0.9)
        self.wait(0.2)

        # 逐像素点亮：随机顺序 + 一次 LaggedStart
        group, cells = build_pixel_group(a["pixels"], a["palette"])
        group.shift(UP * 1.2)
        random.seed(42); order = cells[:]; random.shuffle(order)
        self.play(LaggedStart(*[GrowFromCenter(sq) for sq in order],
                               lag_ratio=0.012), run_time=4.5)
        self.wait(0.8)

        # 轻微浮动
        stuff = [frame, canvas, group, title, sub]
        self.play(*[m.animate.shift(UP * 0.08) for m in stuff], run_time=1.2)
        self.play(*[m.animate.shift(DOWN * 0.08) for m in stuff], run_time=1.2)
        self.wait(1.0)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)

# 动态生成 10 个 Scene 类
for i, art in enumerate(ARTS, 1):
    cls = type(f"Art{i:02d}_{art['name']}", (PixelArtScene,), {"ART": art})
    globals()[cls.__name__] = cls
```

## 渲染 + 搬运 + 抽海报

```bash
# 1) 后台高清渲染全部（2核机约 5-10 分钟）
manim -qm --format mp4 --progress_bar none manim_gallery.py Art01_勇者 ... Art10_花朵

# 2) 拷贝成英文文件名 + 抽中间帧做海报（-ss 7 = 像素全点亮后）
declare -A MAP=( [Art01_勇者]=art01_hero [Art02_爱心]=art02_heart ... )
for src in "${!MAP[@]}"; do
  dst=${MAP[$src]}
  cp "media/videos/manim_gallery/720p30/$src.mp4" "videos/$dst.mp4"
  ffmpeg -y -loglevel error -ss 7 -i "videos/$dst.mp4" -frames:v 1 "posters/$dst.jpg"
done
```

## HTML 画廊集成要点

- 卡片：`<div class="video-wrap">` 内放海报 `<img>` + 播放按钮覆盖层（半透明遮罩 + 圆形金色播放钮）。
- 弹窗：深色遮罩 `rgba(20,17,12,0.92)` + backdrop-filter blur，`<video controls autoplay loop playsinline>`。
- 交互：点卡片 `openOverlay(i)` → 设 `player.src` → `player.load()` → `player.play()`；Esc/点遮罩/关闭按钮 → `player.pause()` + 移除 active。
- 海报缩略图 `loading="lazy"`，宽高比 `aspect-ratio:16/9` + `object-fit:cover`。

## 视觉验证经验

- 用 vision_analyze 检查**动画中间帧**（ffmpeg 抽帧）而不是 `-s` 最后一帧——结尾 FadeOut 后是黑场，视觉模型会说「画面为空」。
- 像素画本身细节（眼睛、手柄）在 16x16 分辨率下很粗糙，视觉模型会挑剔——小瑕疵可在像素矩阵里补一两格，不必过度打磨。

## 尺寸参考（验证过）

| 项 | 值 |
|----|-----|
| 画幅 | 16.0 x 9.0（16:9，防变形） |
| cell | 0.42 → 16x16 像素组 ≈ 6.7 宽 |
| 画布 | 7.6 x 7.6（RoundedRectangle，corner 0.06） |
| 画框 | 8.4 x 8.4（stroke 6） |
| 整体上移 | UP * 1.2（给下方标题留空间） |
| 输出 | 720p/30fps，11s ≈ 180-300KB |
