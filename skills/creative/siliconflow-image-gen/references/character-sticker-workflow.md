# AI 角色立绘 → 抠图 → HTML 贴纸集成 完整工作流

> 2026-07 从「红蓝分析法页面贴纸升级」会话沉淀。用 AI 生成赛博机甲机器人角色，替换 CSS 手绘贴纸，全程零额外依赖（不装 rembg）。

## 适用场景

- 页面需要「有质感的角色/吉祥物/贴纸」，CSS 手绘不够
- 深色科技风页面要炫酷角色（3D渲染贴纸风、赛博机甲风最搭）

## 三步流程

### Step 1 — 生成（SiliconFlow，务必用 curl）

⚠️ **用 curl 调 API，不要用 python urllib**（本环境 urllib 会 `Connection reset by peer`，curl 稳定成功）。

风格统一关键：**固定 STYLE_TAIL 后缀**，多角色只改前面的角色描述：

```
STYLE_TAIL = "3D render, sticker design, cyberpunk mecha style, glowing neon accents, dark navy blue solid background, clean white outline, cute mascot, centered, high quality, octane render"
```

角色描述示例（逐张生成，每张间隔 1-2s）：
- thinking: "Cute curious robot mascot in thinking pose with hand on chin, big glowing cyan eyes, blue and silver armor, small question mark hologram floating above head"
- attack: "Confident battle robot mascot in fighting stance, red glowing visor eyes, crimson and dark metal armor, energy shield on arm"
- happy: "Joyful robot mascot jumping happily, bright golden yellow accents, happy glowing smile, sparkle effects around"
- surprised: "Surprised shocked robot mascot with wide glowing purple eyes, mouth open in awe, exclamation mark hologram above head"

**批量生成失败模式**：一次性 bash 循环/多张并发常失败（瞬时网络重置）；单张前台 curl 稳定。→ 逐张生成 + 每张重试最多 4 次 + 失败 sleep 4s。

### Step 2 — 抠图（色键法，零依赖）

**不要装 rembg**（本环境 pip 代理被腾讯云镜像卡死）。生成图背景是纯色（如深蓝），用 **ffmpeg 编解码 + numpy RGB 距离阈值** 抠图，秒级完成。

⚠️ **关键坑：Qwen-Image 每次生成背景色值略有不同**（不是统一色），必须逐图采样角落像素（四角均值）再抠，不能写死一个背景色。

```bash
# 采样背景色（四角）
ffmpeg -y -v error -i in.png -vf "crop=20:20:0:0" -frames:v 1 -f rawvideo -pix_fmt rgb24 - | od -A n -t u1 | head -1
# 或 python: 读四个角像素取均值
```

运行 `scripts/chroma_cut.py` 完成抠图（见 scripts 目录，支持逐图传背景色）。

**为什么不用 ffmpeg chromakey 滤镜**：chromakey 按色度匹配，会把角色上的相近颜色（如蓝色发光部件）也误扣掉（实测 94%+ 全透），numpy RGB 距离更可控。

### Step 3 — HTML 集成（AI 立绘 + CSS 动效外壳）

替换 CSS 手绘贴纸结构：

```html
<div class="sticker s-hero-r" data-lines='["先红后蓝？","查一下数据…"]'>
  <div class="think-bubble"><span class="think-dots"><span></span><span></span><span></span></span></div>
  <img class="robot-img" src="images/robot_thinking_cut.png" alt="思考机器人">
</div>
```

动效外壳（保留原贴纸互动，去掉 .face 表情切换逻辑）：
- `.sticker`：absolute + floaty 浮动 + hover 放大旋转 + jump 点击跳跃 + drop-shadow
- `.robot-img`：120px（小的用 .sm 96px）+ `botGlow` 霓虹呼吸光晕动画
- 点击互动：气泡文案轮换（data-lines）+ WebAudio 叮声；无 .face 元素的贴纸用 showToast 临时气泡

完整 CSS 见 visual-component-patterns 的「动态表情贴纸角色」章节（AI 立绘版差异：.robot-img/.botGlow，无 .face/.head 表情变体）。

## 踩坑清单

1. python urllib 调 SiliconFlow → Connection reset，curl 稳 → 统一 curl
2. 批量循环生成 → 部分失败；单张+重试稳
3. chromakey 滤镜误扣角色主体 → numpy RGB 距离
4. 背景色逐图不同 → 逐图采样，不写死
5. opacity 0→1 周期动画元素（气泡/星星）截图自检时可能正好隐藏 → 常显微动（opacity .7~1）
6. 抠图保留白色描边（贴纸感）：阈值取在背景色与描边色之间，feather 15 渐变
