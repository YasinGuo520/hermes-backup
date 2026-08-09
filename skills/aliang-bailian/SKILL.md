---
name: aliang-bailian
description: 阿里云百炼 bl CLI 内容制作：语音合成/多人播客/儿童故事/有声绘本/商品详情图。
---

# 阿里云百炼（Bailian bl CLI）内容制作

> 统一入口：所有走阿里云百炼 `bl` CLI 的内容制作工作流（语音合成 / 多人播客 / 儿童故事 / 有声绘本 / 商品详情图）。
> 触发词：TTS、配音、克隆声音、播客、儿童故事、绘本、有声书、商品详情图、百炼、bl 命令。
> 前置：`bl` 已安装并登录（`bl auth status` 可查），需要 `DASHSCOPE_API_KEY`；导出 mp4 / 合并音频需要 `ffmpeg`。

## 模型速查（最关键的区别）

| 模型 | 用途 | 说明 |
|------|------|------|
| `cosyvoice-v3-flash` | 系统音色 TTS | 内置音色（龙小淳/龙安温等），**加 `--instruction` 会报 428**，禁止用 instruction |
| `cosyvoice-v3.5-flash` | **克隆音色** TTS | 完整 voice ID 含前缀 `cosyvoice-v3.5-flash-`；**两个模型不能混用** |
| `qwen-image-2.0` / `qwen-image-2.0-pro` | 文生图 / 图生图 | 商品图、绘本插图、关键帧 |
| `happyhorse-1.1-i2v` | 图生视频 | ¥0.06/条，详细管线见 `ai-video-production` skill |

**克隆音色创建必须在百炼控制台手动操作**：DashScope `/compatible-mode/v1/audio/voices` 端点返回 404，CLI 无法直接创建克隆音色。已有音色表（阿亮：日常 `cosyvoice-v3.5-flash-YOUR_WARM_VOICE_ID` / 科技 `cosyvoice-v3.5-flash-YOUR_TECH_VOICE_ID`）。

## 一、语音合成（含克隆音色）

### 基本命令

```bash
bl speech synthesize \
  --text "{要合成的文本}" \
  --model cosyvoice-v3.5-flash \   # 克隆音色；系统音色用 cosyvoice-v3-flash
  --voice {音色ID} \
  --out {输出路径.mp3} \
  --language zh
```

### 参数

| 参数 | 说明 |
|------|------|
| `--model` | `cosyvoice-v3-flash`（系统）或 `cosyvoice-v3.5-flash`（克隆） |
| `--voice` | 音色 ID；克隆音色必须完整含前缀 |
| `--language` | `zh` / `en` |
| `--rate` | 语速 0.5-2.0（默认 1.0） |
| `--pitch` | 音调 0.5-2.0（默认 1.0） |
| `--volume` | 音量 0-100（默认 50） |
| `--out` | mp3/wav/pcm/opus |

### 常用系统音色

| 声音ID | 名称 | 风格 |
|--------|------|------|
| longanwen_v3 | 龙安温 | 温柔妈妈（默认） |
| longanyun_v3 | 龙安昀 | 知性女声 |
| longxiaochun_v3 | 龙小淳 | 可爱童声 |
| longhuhu_v3 | 龙呼呼 | 亲切叔叔 |
| longpaopao_v3 | 龙泡泡 | 活泼哥哥 |
| longfeifei_v3 | 龙菲菲 | 甜美姐姐 |
| longanhuan | 阿欢 | 欢脱元气女 |
| longxiaoxia_v3 | 龙小夏 | 沉稳权威女 |
| longtian_v3 | 龙天 | 磁性理智男 |
| longze_v3 | 龙泽 | 温暖元气男 |
| longcheng_v3 | 龙成 | 智慧青年男 |

完整列表可用 `bl speech synthesize --list-voices --model cosyvoice-v3-flash` 查。

## 二、多人对话播客（脚本 → 语音）

多角色对话脚本逐句 TTS + ffmpeg 拼接：

1. **分析对话角色**，为每个角色分配音色（见上表），向用户确认音色方案。
2. **逐句生成**：`mkdir -p {输出目录}/{标题}_语音`，每句一条 `bl speech synthesize`，命名 `{角色名}_{序号}.mp3`（Bailian TTS 不支持同命令切换音色，必须逐句；>20 句可并行）。
3. **拼接列表**：语音目录下建 `concat_list.txt`，按对话顺序 `file '角色_序号.mp3'`。
4. **拼接**（关键坑：Bailian TTS 输出扩展名 .mp3 实际是 WAV/PCM，必须转码）：

```bash
ffmpeg -y -f concat -safe 0 -i {输出目录}/{标题}_语音/concat_list.txt \
  -c:a libmp3lame -b:a 192k {输出目录}/{标题}_完整版.mp3
```

5. 清理 concat_list.txt，报告成品路径/时长/音色方案。
6. 进阶：片头/片尾用同法在列表里加 intro/outro。

## 三、儿童故事（故事 + 音频 + 插图）

1. **确认参数**：年龄（3-12，决定词汇/情节复杂度）、时长（1/2/3/5 分钟 ≈ 200-250/400-500/600-750/1000-1200 字）、播音风格（cosyvoice-v3-flash 音色表）。
2. **生成 3 个故事选项**：`bl text chat` 生成 3 个不同主题的标题+一句话简介，用户选 A/B/C。
3. **写正文**：`bl text chat` 按选定主题生成完整故事（口语化、适合讲述、结尾晚安祝福）。
4. **生成音频**：`bl speech synthesize --text "{story_text}" --model cosyvoice-v3-flash --voice {voice_id} --output /tmp/story_audio.mp3 --non-interactive`（CLI 默认输出到 `~/bailian-output/speech/`）。
5. **生成插图**：先 `bl text chat` 从故事提取英文视觉描述（100 词内，水彩儿童绘本风格），再 `bl image generate --prompt "A warm and dreamy children's book illustration for a {age}-year-old: {visual_desc}, soft watercolor style, warm golden and pastel color palette, magical bedtime atmosphere, no text" --out-dir /tmp/ --non-interactive`。
6. **整理输出**：`声音/儿童故事/{故事标题}/` 下放 `story.txt` + `audio.mp3` + `cover.png`，报告文件路径。

## 四、儿童有声绘本（多音色配音 + 统一画风配图 → 网页/视频/音频）

完整流水线（AI 写故事 → 分段 → 多音色配音 → 统一画风配图 → 合成网页版翻页有声书，可选 mp4/纯音频）：

1. **确认**：故事主题（必问）+ 要哪些产物（网页版默认必出；是否加 mp4 / 纯音频 mp3）。段数默认 6、年龄默认 4-8、画风默认水彩绘本。
2. **生成 story.json**：读 `references/story_prompt.md` 填主题/段数，`bl text chat --message "<prompt>" --output json` 生成。`json.loads` 报错多为对白英文引号，强调 prompt 第 7 条重新生成，不要手工修补。
3. **选画风**：读 `references/styles.md` 按题材匹配推荐画风（7 种预设，如中国神话 → 国潮插画），AskUserQuestion 让用户挑。
4. **一把梭构建**：

```bash
python3 scripts/build_audiobook.py --story story.json --outdir <项目目录> --style <画风名> [--web] [--video] [--merge-audio] [--all]
```

   - 逐段 TTS + 文生图并组装；`--style` 传预设名或自定义描述；不带产物标志默认只出网页版。
   - **动手前必读 `references/voices.md`**：音色自动分配（旁白固定+角色轮流）、情绪用 rate/pitch 表达；**系统音色加 `--instruction` 会报 428，禁止用**；多音色生效前提是 segments 的 speaker 分给不同角色。
   - 改文字/画风后重跑：换 `--style` 重跑即可；只重建网页加 `--skip-media`。
5. **交付**：`index.html`（翻页播放器，模板 `assets/player_template.html`）、`audio/seg_NN.wav`、`images/seg_NN.png`，可选 `<标题>.mp4`、`<标题>_audio.mp3`。最后 `open index.html` 预览。

story.json 结构：`{title, characters:[{name,role,trait}], segments:[{id,speaker,text,emotion,image_prompt,voice?}]}`，对白用中文全角引号。

## 五、商品详情图（去背景 + 多角度多场景）

1. **确认需求**：图片数量（必问）、产品图路径、比例（1:1/3:4/16:9，默认 3:4）、风格（默认简约）、输出目录（默认 `输出/`）。
2. **规划**：`bl text chat` 分析产品 → 输出「角度+场景」拍摄规划表，用户确认。
3. **去背景**：`bl image edit --image {产品图} --prompt "Remove the background completely, keep only the product itself with clean edges, output on solid white background" --model qwen-image-2.0-pro --out-dir {dir} --out-prefix "product_no_bg"`。
4. **逐张入场景**：`bl image edit --image {去背景图} --prompt "Place this product naturally in {场景}, {构图}, {光线}, professional product photography, sharp focus, no text, no watermark, no logo" --model qwen-image-2.0-pro --size "{比例}" --out-dir {dir} --out-prefix "product_{i}"`。场景建议：食品→餐桌厨房、服装→模特穿搭、数码→简约办公桌、儿童→温馨家居、户外→自然风光。
5. **一致性限制（必知）**：Qwen-Image 无参考图/记忆机制，跨图人物/产品一致性无法保证（logo 位置、材质、长相每张独立）。用户问「为什么不一致」直接答：没有 Character/IP Adapter，每次独立生成。决策表见 `references/consistency-zh.md`：单张 ✅；多角度 ⚠️ 去背景+img2img 效果有限；同一人物多张 ❌ → ComfyUI+IP-Adapter/InstantID；人物+产品都保一致 ❌ → 视频管线（Wan2.2）或 ComfyUI 全套。

## 通用坑

- 系统音色 `cosyvoice-v3-flash` 与克隆音色 `cosyvoice-v3.5-flash` 是不同模型，命令里 `--model` 必须匹配音色类型；克隆音色场景 `--model` 必须显式指定。
- Bailian TTS 输出 .mp3 实为 WAV(PCM)，ffmpeg 拼接必须 `-c:a libmp3lame` 转码。
- `bl video generate`（i2v）是同步阻塞调用，并行多条会中断（exit 130）——逐条串行，单条约 60-90 秒。详细 I2V 管线见 `ai-video-production` skill。
- 账单/欠费查询去百炼控制台（`bl usage stats` 需 console login）。
