# 14步管线工程实现模式

> 关联 skill: `ai-ecommerce-visual-design`
> 本文件记录从 2026-07-13 技术实现方案中提炼的可复用工程模式。
> 适用于：需要实际编码实现14步管线的后端工程师。

## 模式1：CLIP差异化检测

**位置**：S3 竞品差异化检测

```python
import torch
from transformers import CLIPProcessor, CLIPModel

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def compute_differentiation(generated_image, top100_images):
    """计算生成图与TOP100的差异度"""
    gen_inputs = processor(images=generated_image, return_tensors="pt")
    gen_features = model.get_image_features(**gen_inputs)
    gen_features = gen_features / gen_features.norm(dim=-1, keepdim=True)
    
    similarities = []
    for comp_image in top100_images:
        comp_inputs = processor(images=comp_image, return_tensors="pt")
        comp_features = model.get_image_features(**comp_inputs)
        comp_features = comp_features / comp_features.norm(dim=-1, keepdim=True)
        sim = (gen_features @ comp_features.T).item()
        similarities.append(sim)
    
    avg_similarity = sum(similarities) / len(similarities)
    differentiation = 1 - avg_similarity
    
    return {
        "similarity_score": avg_similarity,
        "differentiation_index": differentiation,
        "is_too_similar": differentiation < 0.3,  # 阈值可调
        "suggestions": generate_suggestions(differentiation, gen_features)
    }
```

**降级方案**：用 qwen3.6-flash vision 做 LLM 版差异化评分，每次~¥0.005。

## 模式2：异步S2爬虫（并控）

**位置**：S2 TOP100范式拆解

```python
import asyncio

async def analyze_top100(platform, category, force_refresh=False):
    # 1. 查缓存（同天同类目去重）
    cache = await db.query(
        "SELECT * FROM top100_cache WHERE platform=:p AND category=:c AND analysis_date=CURRENT_DATE",
        {"p": platform, "c": category}
    )
    if cache and not force_refresh:
        return cache
    
    # 2. 爬取（Playwright + 反检测）
    products = await crawl_top100(platform, category)
    
    # 3. 并控分析（max 5 concurrent）
    semaphore = asyncio.Semaphore(5)
    async def analyze_one(product):
        async with semaphore:
            prompt = "分析这张电商主图，输出：1)主色调HSL 2)构图方式 3)卖点文案 4)风格标签"
            result = await llm_vision(prompt, product.image_url)
            return {**product, **result}
    
    results = await asyncio.gather(*[analyze_one(p) for p in products])
    
    # 4. 聚合入库
    analysis = {
        "color_scheme": aggregate_colors([r["dominant_color"] for r in results]),
        "composition": count_frequencies([r["composition"] for r in results]),
        "keywords": extract_keywords([r["text_elements"] for r in results]),
        "review_insights": await analyze_reviews(top10_product_ids)
    }
    await db.execute("INSERT INTO top100_cache ...", analysis)
    return analysis
```

## 模式3：差评攻击文案生成

**位置**：S5隐舍S10

```python
async def generate_copy_with_review_attack(product_name, category, platform):
    # 1. 获取TOP10竞品的差评
    top10 = await get_top10_products(platform, category)
    all_reviews = []
    for product in top10:
        negative_reviews = await crawl_reviews(
            product["id"], platform=platform, rating_filter="1-3", limit=50
        )
        all_reviews.extend(negative_reviews)
    
    # 2. NLP高频差评词提取
    pain_points = extract_frequent_pain_points(all_reviews)
    # 输出: {"起球": 32, "褪色": 28, "勒": 25, ...}
    
    # 3. LLM生成针对性文案
    prompt = f"""
    商品名：{product_name}
    类目：{category}
    以下是同类目商品用户的差评痛点统计：{json.dumps(pain_points)}
    请根据这些差评，生成3组主图卖点文案，每组4个关键词。
    要求：每个文案直接对应一个差评痛点。
    如：差评说"起球"→ 文案写"不起球"
    输出JSON：{{"versions": [{{"text": "不起球｜不褪色｜不勒", "target_pain": "起球/褪色/勒"}}]}}
    """
    return await llm(prompt)
```

## 模式4：IP-Adapter风格一致性

**位置**：详情页生成（跨多段图片风格一致性）

| 策略 | 做法 | 成本 |
|------|------|------|
| 主色调锁定 | Pillow 提取首图主色调，后续prompt注入统一配色 | ¥0 |
| 统一Prompt后缀 | 每段详情prompt末尾追加 `"保持与前图一致的风格：暖色调、简约白底"` | ¥0 |
| IP-Adapter（推荐） | ComfyUI工作流，加载首图为风格参考图 | 免费(本地) |
| 色调统一后处理 | 生成后将所有图片转为一致的色温曲线 | ¥0 |

## 模式5：Celery任务编排

**位置**：后端任务编排

```
14步管线在Celery中注册为独立Task。
编排策略（标准模式）：
  S1_task → S2_task → S3_task
    → chord([S4_task, S5_tasks]) → S6_task → chord([S7_task, S14_task])
```

## 模式6：手机预览模板

**位置**：S7

```python
from PIL import Image, ImageDraw, ImageFont

def generate_mobile_preview(main_image, platform="douyin"):
    """模拟抖音商品卡信息流预览"""
    canvas = Image.new("RGB", (750, 1334), "#F5F5F5")
    draw = ImageDraw.Draw(canvas)
    
    # 顶部状态栏
    draw.rectangle([0, 0, 750, 60], fill="#FFFFFF")
    
    # 主图区域（等比缩放居中）
    img_resized = resize_to_fit(main_image, 700, 700)
    x_offset = (750 - img_resized.width) // 2
    canvas.paste(img_resized, (x_offset, 170))
    
    # 底部信息
    draw.text((30, 900), "商品标题", font=text_font, fill="#333333")
    draw.text((30, 950), "¥89 已售2.3万", font=price_font, fill="#FF4444")
    return canvas
```

## 模式7：季节/人群适配规则引擎

**位置**：S11 + S12

```python
from datetime import datetime

SEASON_MAP = {
    (3, 4, 5):  {"season": "spring", "colors": ["#C8E6C9","#FFF9C4","#BBDEFB"], "prompt": "清新春日色调"},
    (6, 7, 8):  {"season": "summer", "colors": ["#E3F2FD","#B3E5FC","#FFFFFF"], "prompt": "清凉夏日色调"},
    (9, 10, 11): {"season": "autumn", "colors": ["#FFE0B2","#FFCC80","#FFAB91"], "prompt": "温暖秋日色调"},
    (12, 1, 2): {"season": "winter", "colors": ["#E8EAF6","#FFFFFF","#C5CAE9"], "prompt": "冬日暖色系"},
}

CROWD_STYLE_MAP = {
    "18-25_female": {"style": "ins风/小红书风", "colors": ["#FFC0CB","#FFB6C1"], "composition": "氛围感"},
    "25-35_female": {"style": "简约高端",        "colors": ["#333333","#F5F5F5"], "composition": "留白特写"},
    "18-25_male":   {"style": "科技感/潮牌",    "colors": ["#FF0000","#0000FF"], "composition": "冲击力"},
    "35-45_male":   {"style": "实用主义",        "colors": ["#666666","#444444"], "composition": "功能展示"},
}

def get_prompt_extras(target_age, target_gender):
    month = datetime.now().month
    for months, season_data in SEASON_MAP.items():
        if month in months:
            season = season_data
    crowd_key = f"{target_age}_{target_gender}"
    crowd = CROWD_STYLE_MAP.get(crowd_key, CROWD_STYLE_MAP["25-35_female"])
    return f"{season['prompt']}，{crowd['style']}风格"
```

## 常见陷阱

| 陷阱 | 解决方案 |
|------|---------|
| 爬虫被封 | 动态住宅IP池 + Playwright stealth + 2req/s限速 + 多账号轮换 |
| 差评爬取合规 | 仅爬公开页面、不爬用户个人信息、内部分析不展示原文 |
| CLIP差异度不敏感（白底数码等类目） | 叠加构图/配色规则评分 + 文案关键词差异度 |
| S2缓存击穿（同一类目多用户同时触发） | Redis分布式锁，仅第一个请求执行S2，其余等待缓存 |
