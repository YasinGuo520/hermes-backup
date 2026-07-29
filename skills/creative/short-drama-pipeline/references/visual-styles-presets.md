# 影视视觉风格预设（整理自 Micro-Drama-Skills / zhaihao118）

10种电影级视觉风格，适用于AI视频生成提示词（Wan2.2、Seedance、通义万相、可灵等）。使用风格时，将 `prompt_suffix` 追加到AI视频/图像提示词的末尾。

## 风格速览

| ID | 英文名 | 中文名 | 场景建议 |
|:--:|:------|:------|:--------|
| 1 | Cinematic Film | 电影质感 | **默认**，通用短剧/商品展示 |
| 2 | Anime Classic | 经典动漫 | 动画风漫剧、儿童故事 |
| 3 | Cyberpunk Neon | 赛博朋克 | 科幻、科技感 |
| 4 | Chinese Ink Painting | 水墨国风 | 古风、仙侠 |
| 5 | Korean Drama | 韩剧氛围 | 情感剧、浪漫 |
| 6 | Dark Thriller | 暗黑悬疑 | 悬疑、犯罪 |
| 7 | Vintage Hong Kong | 港风复古 | 怀旧、老香港 |
| 8 | Wuxia Epic | 武侠大片 | 武侠、历史 |
| 9 | Soft Romance | 甜蜜恋爱 | 恋爱、甜宠 |
| 10 | Documentary Real | 纪实写实 | 纪实、探店、生活 |

---

## 1. 电影质感（默认）

```json
{
  "id": 1,
  "name": "Cinematic Film",
  "name_cn": "电影质感",
  "camera": "Panavision Sphero 65 and Hasselblad Lenses",
  "film_stock": "Vision3 500T 5219",
  "filter": "ND0.6, Diffusion Filter 1/4",
  "focal_length": "65mm",
  "aperture": "f/2.0",
  "prompt_suffix": "shot on Panavision Sphero 65 and Hasselblad Lenses, Vision3 500T 5219, ND0.6, Diffusion Filter 1/4, cinematic film grain, shallow depth of field"
}
```

## 2. 经典动漫

```json
{
  "id": 2,
  "name": "Anime Classic",
  "name_cn": "经典动漫",
  "camera": "Virtual Camera",
  "film_stock": "Digital",
  "filter": "Soft Glow",
  "focal_length": "50mm",
  "aperture": "f/2.8",
  "prompt_suffix": "anime style, cel shading, vibrant colors, soft glow, Studio Ghibli inspired, hand-drawn aesthetic"
}
```

## 3. 赛博朋克

```json
{
  "id": 3,
  "name": "Cyberpunk Neon",
  "name_cn": "赛博朋克",
  "camera": "RED Monstro 8K VV",
  "film_stock": "Digital S-Log3",
  "filter": "Pro Mist 1/4, Cyan Gel",
  "focal_length": "35mm",
  "aperture": "f/1.4",
  "prompt_suffix": "shot on RED Monstro 8K VV, cyberpunk neon lighting, Pro Mist 1/4 filter, high contrast, teal and orange color grading, rain-soaked reflections"
}
```

## 4. 水墨国风

```json
{
  "id": 4,
  "name": "Chinese Ink Painting",
  "name_cn": "水墨国风",
  "camera": "ARRI ALEXA Mini LF",
  "film_stock": "ARRI LogC",
  "filter": "Classic Soft 1/2",
  "focal_length": "40mm",
  "aperture": "f/2.8",
  "prompt_suffix": "Chinese ink painting style, shuimo, traditional watercolor wash, flowing brushstrokes, muted earth tones with splashes of vermillion, misty atmosphere"
}
```

## 5. 韩剧氛围

```json
{
  "id": 5,
  "name": "Korean Drama",
  "name_cn": "韩剧氛围",
  "camera": "Sony VENICE 2",
  "film_stock": "Digital X-OCN",
  "filter": "Soft FX 1/2, Warm 81EF",
  "focal_length": "85mm",
  "aperture": "f/1.8",
  "prompt_suffix": "shot on Sony VENICE 2, Korean drama aesthetic, warm soft lighting, shallow depth of field, golden hour glow, dreamy bokeh, pastel color palette"
}
```

## 6. 暗黑悬疑

```json
{
  "id": 6,
  "name": "Dark Thriller",
  "name_cn": "暗黑悬疑",
  "camera": "ARRI ALEXA 65",
  "film_stock": "Kodak Vision3 500T 5219",
  "filter": "ND1.2, Black Pro Mist 1/8",
  "focal_length": "27mm",
  "aperture": "f/2.0",
  "prompt_suffix": "shot on ARRI ALEXA 65, Kodak Vision3 500T, dark thriller atmosphere, high contrast chiaroscuro lighting, desaturated cold tones, noir shadows, tension"
}
```

## 7. 港风复古

```json
{
  "id": 7,
  "name": "Vintage Hong Kong",
  "name_cn": "港风复古",
  "camera": "Kodak Vision3 500T",
  "lens": "Cooke Anamorphic",
  "film_stock": "Kodak Vision3 500T 5219",
  "filter": "Warm 85, Pro Mist 1/4",
  "focal_length": "50mm",
  "aperture": "f/2.0",
  "prompt_suffix": "shot on Kodak Vision3 500T, Cooke Anamorphic lens, vintage Hong Kong cinema style, warm tungsten lighting, film grain, anamorphic lens flare, nostalgic atmosphere"
}
```

## 8. 武侠大片

```json
{
  "id": 8,
  "name": "Wuxia Epic",
  "name_cn": "武侠大片",
  "camera": "Panavision Millennium DXL2",
  "film_stock": "Kodak Vision3 250D 5207",
  "filter": "ND0.9, Glimmerglass 1/4",
  "focal_length": "75mm",
  "aperture": "f/2.0",
  "prompt_suffix": "shot on Panavision Millennium DXL2, Kodak Vision3 250D, wuxia martial arts epic, sweeping landscapes, dramatic overhead crane shots, flowing fabrics, fog and mist"
}
```

## 9. 甜蜜恋爱

```json
{
  "id": 9,
  "name": "Soft Romance",
  "name_cn": "甜蜜恋爱",
  "camera": "Canon C500 Mark II",
  "film_stock": "Canon Cinema RAW Light",
  "filter": "Soft FX 2, Warm 812",
  "focal_length": "100mm",
  "aperture": "f/1.4",
  "prompt_suffix": "shot on Canon C500 Mark II, romantic soft focus, warm pastel tones, dreamy lens flare, cherry blossom petals, gentle backlight, intimate shallow depth of field"
}
```

## 10. 纪实写实

```json
{
  "id": 10,
  "name": "Documentary Real",
  "name_cn": "纪实写实",
  "camera": "Sony FX6",
  "film_stock": "S-Cinetone",
  "filter": "UV only",
  "focal_length": "24mm",
  "aperture": "f/4.0",
  "prompt_suffix": "shot on Sony FX6, documentary style, handheld camera, natural lighting, S-Cinetone color science, realistic skin tones, deep depth of field, raw and authentic"
}
```

---

## 快速引用（一句话指定风格）

- `"使用电影质感风格"` / `"风格1"` / `"Cinematic Film"`
- `"用赛博朋克风格"` / `"风格3"` / `"Cyberpunk Neon"`
- `"港风复古"` / `"风格7"`
- 不指定 → 默认风格1（电影质感）
