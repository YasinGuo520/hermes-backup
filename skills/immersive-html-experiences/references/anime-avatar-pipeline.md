# 头像动漫化两段式处理

将真实照片转为二次元风格头像。分两步：服务端 PIL 预处理 + 浏览器 SVG CSS 滤镜。

## 为什么两段？

- **仅 PIL 处理**：能平滑皮肤+色块化，但做不出清晰轮廓线
- **仅 SVG 滤镜**：轮廓线识别不够精准，色块不够平
- **两段组合**：PIL 先粗处理，SVG 在浏览器端叠加轮廓线+重色块化

## A. 服务端 PIL 预处理

```python
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
import numpy as np

img = Image.open('input.jpg').resize((400,400), Image.LANCZOS)

# 1. 强平滑（类双边滤波）
for _ in range(2):
    img = img.filter(ImageFilter.MedianFilter(5))

# 2. 边缘检测 + 反转 + 二值化
edges = img.filter(ImageFilter.FIND_EDGES).convert('L')
edges = ImageOps.invert(edges)
edges = edges.point(lambda x: 255 if x > 180 else 0).convert('L')

# 3. 色块化（16色）
img = img.quantize(16).convert('RGB')

# 4. 叠加边缘线
arr = np.array(img)
edge_arr = np.array(edges) / 255.0
for c in range(3):
    arr[:,:,c] = (arr[:,:,c] * (1 - edge_arr*0.5) + edge_arr*30).astype(np.uint8)
result = Image.fromarray(arr)

# 5. 色彩增强
result = ImageEnhance.Color(result).enhance(1.5)
result = ImageEnhance.Contrast(result).enhance(1.2)

result.save('output_anime.jpg', quality=95)
```

### 参数速查

| 参数 | 值 | 效果 |
|------|-----|------|
| MedianFilter | 5 | 平滑面颊，保留边缘 |
| Threshold | 180 | 二值化阈值（调低→更多线条） |
| quantize | 16 | 颜色数（调低→更扁平/cel shading） |
| 边缘叠加权重 | 0.5 | 线稿透明度（调高→更粗黑线） |
| 边缘底色 | 30 | 线稿颜色偏移（调高→浅线） |

## B. 浏览器 SVG CSS 滤镜

```xml
<svg style="position:fixed;width:0;height:0;z-index:-1;" aria-hidden="true">
  <filter id="anime" x="-10%" y="-10%" width="120%" height="120%">
    <!-- 色块离散化（7级） -->
    <feComponentTransfer in="SourceGraphic" result="poster">
      <feFuncR type="discrete" tableValues="0 0.15 0.3 0.5 0.7 0.85 1"/>
      <feFuncG type="discrete" tableValues="0 0.15 0.3 0.5 0.7 0.85 1"/>
      <feFuncB type="discrete" tableValues="0 0.15 0.3 0.5 0.7 0.85 1"/>
    </feComponentTransfer>

    <!-- Laplacian 边缘检测 -->
    <feConvolveMatrix order="3"
      kernelMatrix="-1 -1 -1 -1 8 -1 -1 -1 -1"
      preserveAlpha="true" result="edge"/>

    <!-- 放大边缘对比（alpha×6） -->
    <feColorMatrix in="edge" type="matrix"
      values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 6 0"
      result="edgeGlow"/>

    <!-- 叠加：色块 × 边缘线 -->
    <feBlend in="poster" in2="edgeGlow" mode="multiply"/>
  </filter>
</svg>
```

CSS 引用：`filter: url(#anime);`

### SVG 滤镜参数调优

| 参数 | 值域 | 说明 |
|------|------|------|
| tableValues 级数 | 4-10 | 少→更扁平（cel shading），多→保留渐变 |
| kernelMatrix | 3x3 Laplacian | 标准拉普拉斯算子 |
| alpha 倍数 | 4-8 | 高→更粗更亮的边缘线 |

## 故障排查

| 现象 | 原因 | 修复 |
|------|------|------|
| 轮廓线太粗 | 原图太小 | resize到400+ |
| 色块断层严重 | quantize太少 | 升到24-32色 |
| SVG滤镜不生效 | CORS限制 | 同域名文件 |
| 边缘线消失 | 二值化阈值太高 | 降到150-160 |
| 皮肤像塑料 | 平滑过度 | MedianFilter改3或只用1次 |
