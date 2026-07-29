# 外部短剧AI工具/Agent对比（2026年7月）

## 概览

| 工具 | 本质 | 能否集成到Hermes | 费用结构 | 核心依赖 |
|:----:|:----:|:---------------:|:--------:|:--------:|
| **aliang-skills** | 开源Agent Skill合集(6个) | ✅ cp到~/.hermes/skills/ | MIT免费，按阿里百炼API用量付费 | 阿里云百炼CLI + ffmpeg |
| **Micro-Drama-Skills** | 开源Claude Skill(纯短剧) | ✅ 可转Hermes skill | MIT免费，按Google Gemini+Seedance付费 | Gemini API + Seedance本地 |
| **橙星漫工厂** | 商业SaaS平台 | ❌ 独立平台 | "0成本启动"，免费剧本库 | 风行在线云端 |
| **小云雀短剧Agent** | 字节跳动SaaS (Seedance 2.0) | ❌ App/网页 | 注册1200积分+每天120积分 | 即梦/小云雀App |
| **welopc-opc-drama-agent** | npm方法论包+提示词骨架 | ⚠️ 仅借鉴规范 | npm免费，需WelOPC CLI | WelOPC CLI |

---

## 逐个详解

### 1. aliang-skills

- **GitHub**: `aliang2052/aliang-skills` (14 stars, MIT)
- **6个Skill**:
  | Skill | 功能 | 一句话触发 |
  |:-----|:-----|:----------|
  | aliang-shortvideo | 短剧成片 | "做个短剧" |
  | aliang-product-detail-photos | 电商详情图 | "做商品详情图" |
  | aliang-kids-story-maker | 儿童故事+配音+配图 | "制作儿童故事" |
  | aliang-picturebook-audiobook | 有声绘本 | "做有声绘本" |
  | aliang-podcast-maker | 多人播客 | "把这段做成播客" |
  | aliang-bailian-voice-clone | 语音合成(TTS) | "声音合成" |
- **依赖**: 阿里云百炼CLI (`npm install -g bailian-cli`) + ffmpeg
- **费用**: skill免费，百炼API按量计费（见下方阿里云百炼价格表）
- **特点**: "一句话触发"全流程，视频阶段默认只输出命令不自动付费
- **价值点**: 短剧部分与本地管线重叠，**最有价值的是电商详情图skill和儿童故事skill**

### 2. Micro-Drama-Skills (zhaihao118)

- **GitHub**: `zhaihao118/Micro-Drama-Skills` (223 stars, 65 forks)
- **核心能力**:
  - produce-anime: 生成完整短剧（剧本+角色+分镜+故事板）
  - generate-media: 调用Gemini生成角色图/分镜图/视频
  - submit-anime-project: 批量提交到Seedance
- **10种内置视觉风格**: 电影质感、经典动漫、赛博朋克、水墨国风、韩剧氛围、暗黑悬疑、港风复古、武侠大片、甜蜜恋爱、纪实写实
- **依赖**: Google Gemini API (生图) + Seedance本地服务 (生视频)
- **费用**: 开源免费，API用量付费
- **坑**: Google API在国内访问需代理; Seedance需本地起服务
- **最值得借鉴**: 6宫格分镜模板、10种视觉风格预设prompt

### 3. 橙星漫工厂

- **网址**: mgc.funshion.com (风行在线)
- **定位**: 商业SaaS平台，"漫剧制作领域的Cursor"
- **核心能力**:
  - 八智能体协同、端到端闭环生产
  - 内置100+题材商用剧本库（免费）
  - 剧本→角色→分镜→视频→分发全链路
- **费用**: "0成本启动"，每月省200-500元会员费
- **劣势**: 不能与Hermes集成，所有操作在网页上

### 4. welopc-opc-drama-agent

- **npm**: `welopc-opc-drama-agent`
- **不是工具，是生产规范方法论包**，包含:
  - 主方法论+Agent接入说明
  - 提示词骨架（小说拆解、角色系统、生图、视频节点、声音分层）
  - 模板（项目简报、角色卡、视频节点、音频混音、token账本）
  - 检查表（预检、全模态review、脱敏发布）
  - 脱敏仙侠短剧样例
- **核心原则**:
  - 人物不是一句提示词，而是资产系统（下集还能认出）
  - 4K母版与4K安全代理图分开（避免近脸审核）
  - 1-3秒短镜头打包成4-5秒视频节点再剪辑
  - 视频模型原声不进最终混音（TTS、BGM、SFX分层合成）
- **价值**: 工业化大批量生产时参考，日更10集以上再读

### 5. 小云雀短剧Agent（Seedance 2.0）

- **平台**: 小云雀AI (xyq.jianying.com / App)
- **出品方**: 字节跳动
- **核心**: 全球首个搭载Seedance 2.0的短剧Agent
- **能力**: 一句话生成完整短剧（剧本理解+角色管理+多剧集生成）
- **费用**: 注册1200积分+每天120积分
- **适用**: 快速原型验证、免费出片测试

---

## 阿里云百炼API价格（2026年7月）

当使用依赖阿里百炼的工具（如aliang-skills）时，以下为按量计费价格：

| 服务 | 模型 | 价格 |
|:----|:----|:----:|
| 文生视频 720P | wan2.7-t2v | **0.6元/秒** |
| 文生视频 1080P | wan2.7-t2v | **1元/秒** |
| 图生视频 | wan2.7-i2v | 类似幅度 |
| 文生图 | 通义万相/千问图像 | 几分~几毛/张 |
| TTS语音合成 | CosyVoice v3.5 | 约0.02元/次 |

**Token Plan订阅**（阿里云统一套餐，可抵扣所有模型）:
| 档位 | 价格 | Credits量 |
|:----|:----:|:--------:|
| 标准坐席 | 198元/月 | 25,000 |
| 高级坐席 | 698元/月 | 100,000 |
| 尊享坐席 | 1,398元/月 | 250,000 |

**算账举例** — 一部25集短剧，每集30秒:
- 720P: 25 × 30 × 0.6 = **450元**
- 1080P: 25 × 30 × 1.0 = **750元**
- 剧本/分镜阶段几乎免费（文本+预览图而已）

---

## 三管线对比：本地 vs llm-video-maker vs aliang-skills

| 项目 | 本地Wan2.2管线 | llm-video-maker(HyperFrames) | aliang-shortvideo(百炼) |
|:----|:----------:|:--------------------------:|:--------------------:|
| **视频风格** | AI实拍(短剧/氛围) | 图文动画(带货/知识/干货) | AI实拍(短剧剧情) |
| **本质** | Python+moviepy合成 | HTML/GSAP引擎本地渲染 | 阿里云通义万相API |
| **渲染方式** | 本地+SiliconFlow API | 本地Chrome headless | 云端API调用 |
| **TTS** | edge-tts **免费** | Kokoro/edge-tts **免费** | 百炼付费TTS |
| **是否需网络** | API需要，渲染本地 | 渲染时可断网 | 必须联网 |
| **电商图** | ❌ 无 | ✅ 场景插画可内嵌 | ✅ aliang-product-detail-photos |
| **一句话触发** | ❌ 需手动拼 | ✅ Brief→全自动 | ✅ 百炼CLI |
| **运营成本** | 低(仅API费) | **几乎0成本** | 中(0.6元/秒) |
| **最适合** | 氛围短片/背景视频 | 带货/知识/干货/种草 | AI实拍剧情短剧 |

### 选择决策树

```
要做带货/知识/干货? → llm-video-maker (免费, 本地渲染)
要做剧情短剧且有钱? → aliang-shortvideo (0.6元/秒)
要做剧情短剧且没钱? → 本地Wan2.2+edge-tts
要做电商详情图?     → aliang-product-detail-photos
要做儿童故事/绘本?  → aliang-kids-story-maker / aliang-picturebook-audiobook
```

**核心判断**: 三条管线互补不冲突。llm-video-maker做带货低成本出量；aliang-shortvideo做短剧剧情但费钱；本地管线做氛围短片兜底。

---

## 安装记录（2026-07-10）

### aliang-skills 安装

```bash
git clone https://github.com/aliang2052/aliang-skills.git /tmp/aliang-skills
cp -R /tmp/aliang-skills/skills/* ~/.hermes/skills/
# 验证6个skill已安装:
# aliang-shortvideo, aliang-product-detail-photos,
# aliang-kids-story-maker, aliang-picturebook-audiobook,
# aliang-podcast-maker, aliang-bailian-voice-clone
```

### bailian-cli 安装

```bash
npm install -g bailian-cli
# 输出: added 25 packages in 3s
bl auth status
# → authenticated: false
# → 需配key: bl auth login --api-key sk-你的key
# → Key获取: https://bailian.console.aliyun.com/
```

### llm-video-maker 已就绪

| 组件 | 状态 | 版本 |
|-----|------|------|
| HyperFrames | ✅ | 0.7.45 |
| Kokoro TTS | ✅ | kokoro-onnx 0.5.0 |
| Chrome | ✅ | 143 |
| edge-tts | ✅ | Hermes venv中 |
| Pexels直链下载 | ✅ | 中国可直连 |
