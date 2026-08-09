# 图片一致性限制与解决方案

> 适用场景：需要在多张生成图/视频中保持同一人物、同一产品外观时。
> 核心问题：Qwen-Image（百炼 text-to-image）**无状态**，每张图独立掷骰子，无法保持跨图一致性。

---

## 为什么生成图无法保持一致性

| 原因 | 说明 |
|------|------|
| **无参考图机制** | Qwen-Image 不支持 Character/IP Adapter，不给参考图光靠 prompt 描述"保持一样"——模型每次重新想象 |
| **Prompt 语意损耗** | "蓝色卫衣的30岁男人" → 模型理解的是"一个穿蓝衣服的男人大概30岁"，脸型五官每次不同 |
| **产品细节丢失** | 包装上的文字、logo、渐变、材质反光——text-to-image 不擅长精确还原 |
| **无记忆** | API 无状态调用，上张图的内容不影响下一张 |

## 一致性分级需求

| 需求等级 | 示例 | 适用方案 |
|----------|------|----------|
| **L1 - 风格一致** | 多张图都是"日系简约风"，人物长相不同无所谓 | Qwen-Image 纯 prompt 即可 |
| **L2 - 产品一致** | 多角度展示同一款内衣/手机壳，不涉及人脸 | 去背景 + image-to-image 编辑（当前管线能做到的最好水平） |
| **L3 - 人物一致** | 同一个人穿不同衣服/在不同场景 | 必须用 IP-Adapter / InstantID / FaceID |
| **L4 - 人物+产品一致** | 同一个人穿同一款产品在不同场景 | IP-Adapter + 产品抠图叠加 |

## 四套解决方案（按成本从低到高）

### 方案1：图生图编辑（当前管线）
**适用：** L2（产品一致），已有当前管线的去背景+image-to-image
**局限：** 只保产品形状，不保人物脸部、不保跨图一致性
```bash
# 当前能做到的最好程度
bl image edit \
  --image product_no_bg.png \
  --prompt "Place this product in {scene}..." \
  --model qwen-image-2.0-pro
```

### 方案2：局部重绘（Inpainting）
**适用：** 换背景/换衣服，主体不动
**依赖：** 需要支持 inpainting 的模型（SD 系列）或 ComfyUI
```python
# Stable Diffusion Inpainting 伪代码
pipe = StableDiffusionInpaintPipeline.from_pretrained("runwayml/stable-diffusion-inpainting")
image = pipe(prompt=prompt, image=base_image, mask_image=mask).images[0]
```

### 方案3：ComfyUI + ControlNet / IP-Adapter（推荐专业方案）
**适用：** L3-L4，真正需要批量一致生图时
**组件：**
- **IP-Adapter**：给一张参考图，后续生图以这张为风格/人物标准
- **InstantID/FaceID**：专门保人脸一致性
- **ControlNet (Canny/Depth)**：保产品轮廓一致性
- **流程**：参考图 → IP-Adapter 提取特征 → ControlNet 约束结构 → 多张生成

### 方案4：视频管线兜底一致性
**适用：** 最终形态是短视频（抖音带货素材）
**原理：** 视频帧天然有连续性，人物/产品在不同帧里保持一致
**管线：** Wan2.2 动态背景 + edge-tts + moviepy
**注意：** 静态图场景下如果最终要做视频，直接走视频管线比生图再拼更省事

---

## 决策树

用户需求 → 
  要单张图？→ Qwen-Image 直接出
  要多张同一产品的不同场景图？→ 去背景 + image-to-image 编辑
  要同一人物在多张图出现？→ ComfyUI + IP-Adapter/InstantID
  要做短视频？→ 直接走视频管线（Wan2.2/llm-video-maker）

---

## 与本 skill（aliang-bailian 商品详情图章节）的关系

- 当前 skill 的「去背景 + 入场景」流程**只能做到 L2（产品一致）**
- 遇到 L3/L4 需求时，主动告知限制和替代方案，不要硬生成多张导致用户反复试
- 用户表现出"每次生成都不一样"的挫败感时，直接贴这个文档的决策树
