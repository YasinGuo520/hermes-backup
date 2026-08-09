---
name: ai-video-content-creation
description: AI视频内容创作全流程——使用国内AI视频平台（小云雀/即梦AI/可灵AI）生成短视频素材，配合Hermes完成分镜规划、提示词编写、视频合成与配乐。适用于抖音带货素材、创意短片、一人公司内容生产。
triggers:
  - AI视频生成
  - 视频创作
  - 小云雀
  - 即梦AI
  - 可灵AI
  - Seedance
  - Kling
  - AI video generation
  - 短视频素材制作
  - 火星基地
  - video prompt
---

# AI Video Content Creation（AI视频内容创作）

使用国内AI视频平台生成短视频素材的工作流。覆盖从分镜规划→提示词编写→分段生成→合成出片的完整链路。

## 适用平台（国内可访问）

| 平台 | 出品方 | 网址 | 免费额度 | 适合场景 |
|:---:|:-----:|:----:|:-------:|---------|
| 🥇 **小云雀** | 字节跳动剪映团队 | xyq.jianying.com | 注册1200积分+每天120 | 一句话出片，零门槛，最佳搭配 |
| 🥈 **即梦AI** | 字节跳动Seedance | jimeng.jianying.com | 有免费试用 | 质量顶级，科幻场景最佳 |
| 🥉 **可灵AI** | 快手Kling | klingai.com | 少量免费 | 物理理解强，广告级质量 |

## 硬件前提

**此工作流专为无GPU环境设计**（如Intel Mac、无独显电脑）。不需本地算力，全走云端。

## 核心工作流

### 1. 分镜规划（Split & Script）

将一条完整视频拆成3-5秒的独立片段，逐段生成。

**规则**：每个片段聚焦**一个视觉元素+一个运动**，不要一个镜头塞太多信息。

```
15秒视频 → 5个3秒片段
```

### 2. 提示词编写原则

| 原则 | 说明 |
|------|------|
| 一个镜头一个焦点 | 别在一条提示词里既写基地又写飞船又写机器人 |
| 指定运动方向 | "从左向右飞入"优于"飞船飞过" |
| 加氛围词 | "电影级布光""暖橙蓝对比色""史诗感" |
| 加平台名 | 某些平台对"火星""科幻"理解有偏差 → 加参考风格 |

### 3. 分段生成

| 镜头 | 时长 | 焦点 | 提示词要点 |
|:---:|:---:|:----:|-----------|
| 1 | 0-3s | 全景定场 | Wide shot Mars surface, dome base, establish setting |
| 2 | 3-6s | 机器人挖矿 | Yellow robot digging, mechanical arm, red soil |
| 3 | 6-9s | 飞船1穿梭 | Spaceship flying left to right, white contrail |
| 4 | 9-12s | 飞船2交错 | Second ship crossing opposite direction, interweave |
| 5 | 12-15s | 拉伸收尾 | Pull back to wide shot, entire base visible |

### 4. 合成出片

```bash
# 下载各段视频（命名规范：clip_01.mp4 到 clip_05.mp4）
# 合并（无需重编码）
ffmpeg -f concat -safe 0 \
  -i <(for f in clip_0*.mp4; do echo "file '$PWD/$f'"; done) \
  -c copy output_merged.mp4

# 加BGM + 淡入淡出
ffmpeg -i output_merged.mp4 -i bgm.mp3 \
  -filter_complex "[0:a]afade=t=in:d=1,afade=t=out:st=13:d=2[a];[1:a]volume=0.3[a2];[a][a2]amix=inputs=2" \
  -c:v copy output_final.mp4
```

## 与Hermes配合模式

| 模式 | 你的操作 | Hermes操作 | 适合场景 |
|:---:|---------|-----------|---------|
| 🅰 全托管 | 登录好平台 | 浏览器操作生成+下载+合成 | 完整流程，最省心 |
| 🅱 用户生成+代理合成 | 复制提示词逐段生成 | 接收片段合成+配乐+调色 | 不想授权浏览器操作 |
| 🅲 纯脚本输出 | 无 | 输出分镜脚本+提示词+合成分步指令 | 用户自己全程操作 |

## 常用提示词模板

### 科幻场景
```
Cinematic shot of [火星基地/穹顶建筑/机器人在作业] on red planet surface, 
[详细描述场景], warm orange and blue lighting, epic sci-fi atmosphere, 
wide angle, ultra realistic, 8K quality
```

### 产品展示
```
[Product] being used, [demonstrate key feature], 
clean background, soft lighting, product photography style, 
slow motion, 4K detail shot
```

### 氛围镜头
```
[Scene description], cinematic lighting, shallow depth of field, 
film grain, atmospheric, moody, golden hour light
```

## 🆕 全自动AI图文视频流水线（无GPU版）

完全在本地运行的文字幻灯片视频生成方案，不需要GPU，不需要手动操作任何平台。

### 适用场景

| 场景 | 说明 |
|------|------|
| AI工具测评短视频 | 配图+配音+文字，不上镜也能出片 |
| 知识科普/干货分享 | 信息图风格，配合AI配音 |
| 带货选品/数据分析 | 结构化表格截图+语音讲解 |
| 人设故事/观点输出 | 文字画面+背景音乐+配音 |

### 流水线架构

```
┌─ 文案 ─→ 分镜规划 ─→ ┐
├─ 配图 ─→ SiliconFlow  ─→ ┤
├─ 配音 ─→ edge-tts     ─→ ┤ → moviepy合成 → MP4
├─ 转场 ─→ FadeIn/Out   ─→ ┘
└─ BGM  ─→ 音频叠加     ─→ ┘
```

### 核心技术栈

| 工具 | 用途 | 安装 |
|------|------|------|
| **moviepy** 2.x | 视频合成（帧、音频、文字） | `pip3 install moviepy` |
| **edge-tts** | 中文配音（微软TTS引擎） | `pip3 install edge-tts` |
| **numpy** | 图像帧处理 | `pip3 install numpy` |
| **SiliconFlow API** | AI配图生成 | 配置在 `~/.hermes/config.yaml` |
| **STHeiti Medium.ttc** | 中文字体 | macOS内置 `/System/Library/Fonts/` |

### moviepy 2.x API陷阱（与1.x不兼容）

| 功能 | 1.x写法 | 2.x正确写法 |
|------|---------|-------------|
| 帧函数参数 | `make_frame` | `frame_function=func` |
| 交叉淡入淡出 | `.crossfadein()` / `.crossfadeout()` | `from moviepy.video.fx import FadeIn, FadeOut` → `.with_effects([FadeIn(d), FadeOut(d)])` |
| 中文字体 | − | 用 `STHeiti Medium.ttc` 而非 `PingFang.ttc`（PIL不支持.ttc集合文件） |
| 设置时长 | `.set_duration(d)` | `.with_duration(d)` |
| 设置位置 | `.set_position(...)` | `.with_position(...)` |

**⚠️ 性能陷阱**：禁止在帧函数中用 `for y in range(H): for x in range(W):` 逐像素运算。用numpy向量化或直接省略暗角遮罩。

**⚠️ 背景进程路径**：`terminal(background=True)` 跑Python脚本时，在脚本顶部加：
```python
import sys, site
sys.path.insert(0, site.getusersitepackages())
```

### 配图生成（SiliconFlow API）

不要用Hermes内置的 `image_generate` 工具（格式不匹配）。直接Python调用：

```python
import json, urllib.request, re, os
with open(os.path.expanduser("~/.hermes/config.yaml")) as f:
    content = f.read()
key = re.search(r'image_gen:.*?api_key:\s*(\S+)', content, re.DOTALL).group(1)

url = "https://api.siliconflow.cn/v1/images/generations"
req = urllib.request.Request(url,
    data=json.dumps({"model":"Qwen/Qwen-Image","prompt":"文字","n":1,"size":"720x1280"}).encode(),
    headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"})
with urllib.request.urlopen(req, timeout=60) as resp:
    img_url = json.loads(resp.read())["data"][0]["url"]
# 立刻下载（presigned URL会过期）
urllib.request.urlretrieve(img_url, "slide.png")
```

### 文字排版位置规则

| 元素 | 位置 | 说明 |
|------|------|------|
| **主标题** | `(center, H//2 - 120)` | 居中偏上 |
| **副标题/说明文字** | `(center, H - 180)` | **底部**，不要放在中间 |
| **字幕** | 底部180px | 用户偏好：解说文字放最下面 |

### AI配图质量陷阱

当用户反馈"图太low了"、"没有科技感"时，说明Qwen/Qwen-Image生成的图无法满足要求。此时**立即切换到程序化渐变背景方案**，不要再优化提示词重试。

**程序化渐变背景方案**（比AI生图更可控）：
```python
def gradient_bg(color_top, color_bot):
    def make_frame(t):
        frame = np.zeros((H, W, 3), dtype=np.uint8)
        for y in range(H):
            ratio = y / H
            frame[y, :] = [
                int(color_top[0]*(1-ratio) + color_bot[0]*ratio),
                int(color_top[1]*(1-ratio) + color_bot[1]*ratio),
                int(color_top[2]*(1-ratio) + color_bot[2]*ratio),
            ]
        return frame
    return make_frame
```

推荐配色方案（科技感深色主题）：

| 场景 | 顶色(RGB) | 底色(RGB) | 强调 |
|------|-----------|-----------|------|
| 标题/开场 | (10,10,50) | (40,10,80) | 蓝紫科技 |
| 痛/警告 | (50,10,10) | (80,20,20) | 红强调 |
| 工具/产品 | (10,20,60) | (20,40,100) | 蓝光 |
| 步骤/教程 | (10,10,40) | (30,20,70) | 紫蓝 |
| 对比 | (40,10,10) | (10,40,10) | 红→绿 |
| 结果/肯定 | (10,30,20) | (20,60,40) | 绿科技 |
| CTA/关注 | (20,10,50) | (50,20,90) | 紫发光 |

### SiliconFlow 文生视频（Wan2.2 T2V）

通过SiliconFlow的Wan2.2模型，支持文字直接生成视频。

**API地址**：`https://api.siliconflow.cn/v1/video/submit`（注意是.cn不是.com）

**参数**：
```python
payload = {
    "model": "Wan-AI/Wan2.2-T2V-A14B",
    "prompt": "深色科技感动态背景，蓝紫渐变，发光数据流...",
    "image_size": "720x1280",  # 参数名是image_size，不是size
}
```

**状态查询**：`POST https://api.siliconflow.cn/v1/video/status`
- Body: `{"requestId": "<id>"}` (POST, 不是GET)
- 状态值: `InQueue` → `InProgress` → `Succeed` / `Failed`
- 轮询间隔：10秒，最长等待10分钟
- 返回结果中的视频URL为阿里云OSS presigned URL，需立即下载

**已知限制**：
- 目前只能生成氛围画面（科技感动态背景），无法生成带具体角色/叙事逻辑的内容视频
- 生成耗时较长（约5-9分钟）
- 同一账户建议不要并发过多请求

### 配音（edge-tts）

```python
import asyncio, edge_tts
c = edge_tts.Communicate("中文", voice="zh-CN-XiaoxiaoNeural", rate="+15%")
asyncio.run(c.save("voice.mp3"))
```

## 常见问题

| 问题 | 解决 |
|------|------|
| 生成画面不符合预期 | 加更多具体描述词（颜色、材质、灯光方向） |
| 人物/物体形态不稳定 | 缩短单段时长（3s→2s），减少动作复杂性 |
| 多段合成颜色不统一 | 所有片段提示词统一加同一组调色关键词 |
| 平台限免额度不够 | 多个平台切换使用（小云雀→即梦→可灵轮流） |

## 🆕 火山引擎/即梦 API 程序化调用（Seedance/豆包系）

除了网页版手搓，Seedance/即梦视频生成可走火山引擎 API 接入流水线（产品图→I2V→带货视频）。

**⚠️ Key 类型是最大坑（2026-07 实测踩坑）：**
- 火山引擎 = 字节云全家桶；**火山方舟** = 其中的大模型服务平台；即梦/Seedance = 独立产品线（同一账号分开开通）
- 三种凭证别搞混：Access Key（云API签名）/ 普通 API Key（数据面 Bearer）/ **方舟大模型专用 API Key**
- ⚠️ **普通 API Key 调方舟接口必 401**（`ark.cn-beijing.volces.com/api/v3/models` 和 `contents/generators/tasks` 都拒绝）——视频生成/豆包大模型要走「方舟大模型专用 API Key」，控制台页面提示链接里创建
- 配置位置：`/home/ubuntu/backend/.env` 的 `ARK_API_KEY`（字段已建，待正确 key 填入）
- 价格：Seedance 1.0 Pro-fast 720P 最便宜（0.08元/秒，15秒≈1.2元）；1.5 Pro 720P 无声 0.17元/秒；2.0 约1元/秒；新手先买 100元/月 基础体验版（1000算点）测试
- 详细 API 端点、计费表、验证命令见 `volcengine-ark-api.md`

## 模型平台生态速查（2026-07）

| 平台 | 能调什么 | 不能调什么 |
|------|---------|-----------|
| 硅基流动 SiliconFlow | 开源模型全家桶（Kimi K3 已上线、DeepSeek、Qwen、GLM、FLUX、Wan2.2） | 闭源商用模型（GPT/Claude/Gemini 一律没有） |
| 火山引擎/方舟 | 豆包系、Seedance/即梦视频、K3（官方） | − |
| OpenRouter | 开源+闭源全都要 | 国内网络不稳定 |
