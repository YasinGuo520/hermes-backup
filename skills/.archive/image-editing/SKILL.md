---
name: image-editing
description: 图片编辑与修改——用Python Pillow库或Photoshop修改图片文字、调整内容、覆盖元素。涵盖字体匹配、像素定位、字符提取拼接等技巧。
---

# Image Editing（图片编辑）

当用户要求修改图片中的文字或内容时使用。

## 工具选择

| 方案 | 适用场景 | 效果 |
|------|----------|------|
| **Photoshop（computer_use）** | 需要精准字体匹配、专业效果 | ⭐⭐⭐⭐⭐ |
| **Python Pillow + 系统字体** | 简单文字替换，字体要求不高 | ⭐⭐⭐ |
| **Python Pillow + 原图字符提取** | 需要匹配原图字体但PS不可用 | ⭐⭐⭐⭐ |

## 流程

### 方案A：Photoshop（推荐）
1. `open -a "Adobe Photoshop"` 启动PS
2. 用 `computer_use` 打开图片
3. 用文字工具直接编辑
4. 保存覆盖原文件

### 方案B：Pillow + 系统字体
1. `vision_analyze` 定位文字区域（坐标从视觉分析获取）
2. `getpixel()` 像素扫描验证实际位置
3. 用 `ImageDraw.rectangle()` 覆盖旧文字
4. 用 `ImageFont.truetype()` 加载系统字体（STHeiti Light/Medium for macOS中文）
5. `ImageDraw.text()` 写入新文字
6. 保存并验证

### 方案C：原图字符提取（最佳备选）
1. 定位文字区域
2. 像素扫描找出每个字符的边界框
3. 用 `Image.crop()` 提取每个字符
4. 重新排列字符拼出新文字
5. 用 `Image.paste()` 粘贴回去
6. 保存

## 注意事项（Pitfalls）

- ❌ 不要用多次draw叠加来模拟加粗——会导致负号变成双负号 `--100.00`
- ❌ `vision_analyze` 给的坐标经常不准，必须用 `getpixel()` 验证
- ❌ 系统字体路径因平台而异，macOS中文字体在 `/System/Library/Fonts/`
- ✅ 文字颜色用 `(40,40,40)` 而非纯黑 `(0,0,0)`，与原图更接近
- ✅ `.ttc` 字体文件需要用 `ImageFont.truetype(fp, size)` 加载
- ✅ 擦除旧文字时用 `fill=(255,255,255)`，注意padding不要擦到旁边元素

## 参考

- macOS系统字体：STHeiti Light.ttc / STHeiti Medium.ttc / PingFang.ttc
- 标准数字高度：50-56px 适合移动端截图金额
- 文字颜色：纯黑 `(0,0,0)` 或近黑 `(40,40,40)`
