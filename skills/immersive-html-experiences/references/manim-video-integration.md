# Manim 视频管线（像素画/展示类素材）

当页面需要 Manim 渲染的动画素材时用的完整管线。本文件是从像素画展厅项目（pixel-gallery，8915端口）实测沉淀。

## 环境准备（Linux 腾讯云）

```bash
# pycairo 需要系统头文件，否则 pip install manim 报
# "Dependency lookup for cairo with method 'pkg-config' failed"
sudo apt-get install -y pkg-config libcairo2-dev libpango1.0-dev libffi-dev
python3 -m venv manim-venv && ./manim-venv/bin/pip install manim
```

中文字体：`fc-list :lang=zh` 查可用字体（此机有 WenQuanYi Zen Hei）。
```python
MONO = "WenQuanYi Zen Hei"
Text("勇者", font_size=48, font=MONO, weight=BOLD)
```

## 核心坑

### 1. 默认画幅 14.22x8，元素超尺寸会被静默裁掉
不报错、Create() 播放了但画面全空——元素在视野外。必须显式放宽画幅：
```python
self.camera.background_color = BG
self.camera.frame_width = 16.0   # 保持 16:9 比例，否则输出变形
self.camera.frame_height = 9.0
```
或把 mobject 缩小到默认画幅内。**别只靠代码逻辑判断布局，必须渲染后抽帧目检。**

### 2. `manim -ql -s` 存最后一帧 = 全黑
场景结尾 `FadeOut(Group(*self.mobjects))` 后最后一帧是空场，看起来像渲染失败。
正确预览：渲染完整 mp4 后抽中间帧：
```bash
manim -ql --format mp4 --progress_bar none script.py Scene1
ffmpeg -y -loglevel error -ss 5 -i media/videos/script/480p15/Scene1.mp4 -frames:v 1 /tmp/preview.png
```

## 像素画 → 动画模式

16x16 字符矩阵定义像素画，逐像素点亮动画：

```python
def build_pixel_group(pixels, palette):
    n = len(pixels); cell = 0.42
    group = VGroup(); cells = []
    for r in range(n):
        for c, ch in enumerate(pixels[r]):
            if ch == "." or ch not in palette: continue
            sq = Square(side_length=cell, fill_color=palette[ch],
                        fill_opacity=1.0, stroke_width=0)
            sq.move_to([(c - n/2 + 0.5)*cell, (n/2 - 0.5 - r)*cell, 0])
            group.add(sq); cells.append(sq)
    return group, cells

# 场景内：随机顺序 LaggedStart 逐像素点亮
random.seed(42); order = cells[:]; random.shuffle(order)
self.play(LaggedStart(*[GrowFromCenter(sq) for sq in order],
                       lag_ratio=0.012), run_time=4.5)
```

要点：
- cell 值 = 像素画整体宽度 ÷ 16。画幅16宽、画布7.6宽时 cell≈0.42
- 多个场景用动态生成类：`type(f"Art{i:02d}_{name}", (BaseScene,), {"ART": art})`
- 统一视觉常量（背景/金框/标题色/MONO字体）放文件顶部

## 渲染与搬运

```bash
# 批量渲染所有场景（720p30 生产，2核机10场景约5-8分钟）
manim -qm --format mp4 --progress_bar none script.py Scene1 Scene2 ...
# 后台跑：terminal(background=true, notify_on_complete=true)

# 抽海报帧（动画中间帧，不是最后一帧）
ffmpeg -y -loglevel error -ss 7 -i videos/art01.mp4 -frames:v 1 posters/art01.jpg
```

- 视频/海报文件用**英文文件名**（中文名在 URL/浏览器有编码问题）
- 目录结构：`videos/` + `posters/` + `index.html` + 渲染脚本，纯静态 http.server 即可
- 页面嵌入修复（16:9 溢出坑）见主 SKILL.md「嵌入渲染视频」章节
