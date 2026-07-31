---
name: manim-creative-scenes
description: "Manim 创意/展示类动画场景：像素画逐格点亮、画廊巡游、作品集展示。含画幅裁剪/黑帧预览/中文字体等实战踩坑。"
version: 1.0.0
platforms: [linux, macos, windows]
---

# Manim 创意/展示类动画场景

用 Manim Community Edition 做**非数学**的创意展示动画：像素画展厅、游戏角色画廊、作品集逐格点亮、海报/封面动态化。与 `manim-video`（数学/算法解释视频）互补——本技能管展示类、装饰类、逐格类场景。

## 何时用

- 用户有一批「作品/图案」（像素画、图标、角色、卡片）要做成动画展示页
- 需要「逐像素/逐格点亮」「画框浮现」「画廊巡游」这类效果
- 静态 HTML 画廊升级为动画版（点击卡片 → 弹窗播放 Manim 视频）

## 核心模式

### 1. 像素矩阵 → 逐格点亮（最常见需求）

```python
def build_pixel_group(pixels, palette, cell=0.42):
    """NxN 像素矩阵 → (Group, cells)。. = 透明，字母 = 调色板 key"""
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
```

点亮动画——随机顺序逐格 GrowFromCenter，**一次 LaggedStart 搞定，不要逐格 play**：
```python
random.seed(42); order = cells[:]; random.shuffle(order)
self.play(LaggedStart(*[GrowFromCenter(sq) for sq in order],
                       lag_ratio=0.012), run_time=4.5)
```

### 2. 多个作品共用一个 Scene 基类

10 个作品 = 10 个 Scene 类，用 `type()` 动态生成，避免重复代码：
```python
class PixelArtScene(Scene):
    ART = None  # dict(name, sub, desc, palette, pixels)
    def construct(self): ...  # 读 self.ART
for i, art in enumerate(ARTS, 1):
    cls = type(f"Art{i:02d}_{art['name']}", (PixelArtScene,), {"ART": art})
    globals()[cls.__name__] = cls
```

### 3. 画廊场景标准节奏

金框+画布 Create → 标题 Write（画框**下方**，博物馆标签式）→ 逐格点亮 → 轻微浮动上下 → 淡出。完整可跑脚本模板见 `references/pixel-art-scenes.md`。

## ⚠️ 踩过的坑（全部实战验证）

1. **画幅裁剪（最坑）**：Manim 默认画幅 14.22 x 8。mobject 尺寸超过这个范围（如画框 19.2 宽）会**直接在画面外被裁掉**，金框标题全不可见只剩中间残片。修复：
   ```python
   self.camera.frame_width = 16.0
   self.camera.frame_height = 9.0   # 必须保持 16:9，否则输出变形
   ```
   或缩小元素（canvas 7.6 / frame 8.4 / cell 0.42 是验证过的安全组合）。

2. **`-s` 预览黑帧**：`manim -s` 保存**最后一帧**。场景结尾若是 `FadeOut(Group(*self.mobjects))`，预览图纯黑，视觉模型会误判「画面为空」甚至以为渲染失败。正确预览：
   ```bash
   manim -ql --format mp4 script.py Art01_勇者
   ffmpeg -y -loglevel error -ss 6 -i media/videos/script/480p15/Art01_勇者.mp4 -frames:v 1 /tmp/preview.png
   ```

3. **中文字体**：Manim Text 渲染中文必须有 CJK 字体。先 `fc-list :lang=zh` 确认，再显式指定 `font=MONO`（服务器上是 `WenQuanYi Zen Hei`）。

4. **系统依赖**：pip 装 manim 因 pycairo 编译失败（`pkg-config not found`）。先：
   ```bash
   sudo apt-get install -y pkg-config libcairo2-dev libpango1.0-dev libffi-dev
   python3 -m venv manim-venv && ./manim-venv/bin/pip install manim
   ```

5. **中文文件名 mp4**：Scene 类名带中文（`Art01_勇者.mp4`），页面 URL 引用麻烦。拷贝成英文名再给前端：
   ```bash
   cp "media/videos/script/720p30/Art01_勇者.mp4" videos/art01_hero.mp4
   ```

## 页面集成（HTML 画廊）

- 每作品 11s 左右 720p/30fps mp4 实际只有 180-300KB，网页直接可播。
- 卡片缩略图用 ffmpeg 抽动画中间帧（`-ss 7`，像素全点亮后的帧）——比静态 CSS 像素画更有「这是动画」的暗示。
- 交互：点击卡片 → 深色遮罩弹窗 + `<video controls autoplay loop playsinline>`，Esc/点遮罩关闭。
- 海报帧 + 播放按钮覆盖层（半透明遮罩+金色圆形播放钮）提升点击率。

## 渲染命令

```bash
# 低清验证 1 个场景
manim -ql --format mp4 manim_gallery.py Art01_勇者
# 全部场景高清（2 核机 10 个场景约 5-10 分钟；后台跑 + notify_on_complete）
manim -qm --format mp4 manim_gallery.py Art01_... Art10_...
```

## 参考文件

| 文件 | 内容 |
|------|------|
| `references/pixel-art-scenes.md` | 完整可跑脚本模板 + 10作品动态类生成 + 踩坑详录 |
