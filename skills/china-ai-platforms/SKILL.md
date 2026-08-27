---
name: china-ai-platforms
description: 中国AI云平台API调用与选型：硅基流动生图/火山方舟Seedance/百炼bl CLI/腾讯混元3D图生3D/DeepSeek计费审计与模型锁死。
triggers:
  - 生图
  - 生成图片
  - 硅基
  - 火山
  - 豆包
  - 即梦
  - Seedance
  - 百炼
  - bl命令
  - TTS
  - 配音
  - 克隆声音
  - 播客
  - 绘本
  - 儿童故事
  - 商品详情图
  - 开源模型
  - API调用
related:
  - ai-video-production
  - ai-image-to-3d
---

# 中国AI云平台调用总纲

> 统一入口：选哪个中国云AI平台、怎么调。三家平台各有专长，先按矩阵选型，再进对应 reference 拿命令。

## 平台选型矩阵（先选平台，再看细节）

| 需求 | 平台 | 为什么 |
|------|------|--------|
| 开源模型（K3/Qwen/FLUX/DeepSeek 镜像） | **硅基流动** SiliconFlow | 便宜、key 已有（`~/.hermes/.env` 的 `SILICONFLOW_API_KEY`），无需 GPU |
| 图片生成（商品图/封面/绘本插图/小红书配图） | **硅基流动** Qwen-Image / Z-Image / Kolors | 现成 key、curl 直调；百炼 `qwen-image-2.0-pro` 也可 |
| 豆包/即梦/Seedance（字节闭源模型） | **火山方舟** Ark | 硅基流动没有闭源模型；视频生成是主场景 |
| TTS 配音 / 克隆音色 / 多人播客 | **阿里百炼** bl CLI | cosyvoice 系列，逐句生成+ffmpeg拼接 |
| 儿童故事 / 有声绘本 / 商品详情图 | **阿里百炼** bl CLI | 完整流水线（story.json + 脚本 + 网页模板） |
| 图生视频 I2V（实拍产品→动效） | **阿里百炼** happyhorse-1.1-i2v | ¥0.06/条最便宜；完整管线见 `ai-video-production` |
| 视频生成（氛围/T2V） | 硅基流动 Wan2.2 / 火山 Seedance | 硅基便宜但只能氛围画面；Seedance 质量高需充值 |

## 各平台完整文档

- `references/siliconflow-image.md` — 硅基流动生图：模型表、curl 调用、prompt 技巧、立绘抠图、角色贴纸工作流
- `references/volcengine-ark.md` — 火山方舟：Key 类型、模型开通、视频/图像任务 API、价格表、常见错误
- `references/bailian-cli.md` — 阿里百炼 bl CLI：TTS/播客/儿童故事/有声绘本/商品详情图全工作流

## 跨平台关键坑（易踩）

- **火山方舟必须用「方舟大模型专用 API Key」**（`ark-` 前缀），普通 API Key 调方舟接口必 401
- Seedance 视频模型开通前需**先充值**（免费额度开不了视频）；API 路径是 `generations`（复数）不是 `generators`——拼错返回 404 空 body
- 百炼**系统音色** `cosyvoice-v3-flash` 加 `--instruction` 会报 428，禁止用；**克隆音色**是 `cosyvoice-v3.5-flash`，两个模型不能混用，克隆音色创建必须去百炼控制台手动操作
- 百炼 TTS 输出的 `.mp3` 实为 WAV(PCM)，ffmpeg 拼接必须 `-c:a libmp3lame` 转码
- **硅基流动必须用 curl 不要用 python urllib**（本环境 urllib 会 Connection reset）；图片 URL 有效期 24h，必须下载后再发送
- 硅基 Qwen-Image 每次生成背景色值略有不同：抠图时逐图采样四角像素均值，不能写死色值
- 生图用途决定背景色：贴纸抠图用深蓝/纯色底；**图生3D用纯黑底**（见 `ai-image-to-3d` 技能）
- 百炼 `bl video generate` 是同步阻塞调用，并行多条会中断（exit 130）——逐条串行
- 账单查询：百炼去控制台 bailian.console.aliyun.com（`bl usage stats` 需 console login）；火山按产品线分开开通分开计费

## 支持文件

| 文件 | 用途 |
|------|------|
| `scripts/build_audiobook.py` | 百炼有声绘本一键构建（story.json → 分段TTS+配图+网页/mp4/音频） |
| `scripts/chroma_cut.py` | 色键抠图脚本（角色立绘→透明贴纸，ffmpeg+numpy 零依赖） |
| `assets/player_template.html` | 绘本翻页播放器模板 |

## 关联技能

- `ai-video-production` — I2V 视频管线、Wan2.2、视频合成（本技能是平台调用层）
- `volcengine-ark-api` / `siliconflow-image-gen` / `aliang-bailian` 已并入本技能（原内容在 references/ 对应文件）

## 腾讯混元3D：2D立绘 → GLB 真3D（合并自 ai-image-to-3d）

把一张2D图片变成可360°旋转的真3D模型（GLB）并放进 Three.js 展示页。墙内可用，成本≈0（免费额度）。**动手前先确认：真3D（可旋转看背面，走本流程）还是伪3D（CSS视差倾斜，见 `ux-pro-max` 的 references/visual-component-patterns.md「AI立绘动态升级」）。**

### 通道选择（腾讯云实测）
| 通道 | 状态 |
|------|------|
| 腾讯混元3D API | ✅ 唯一实测通，endpoint ai3d.tencentcloudapi.com |
| Tripo / Meshy | ❌ 服务器 curl 全不通 |

**密钥与开通坑**：只认 SecretId+SecretKey（TC3-HMAC-SHA256 签名），`sk-` 开头的混元 LLM key 无效直接拒；**开通服务 ≠ 有额度**——`ResourceInsufficient 资源不足` 要手动去 https://console.cloud.tencent.com/ai3d 领免费额度或开后付费；`ResourceUnavailable.NotExist` = 服务没开通；子账户需主账户 CAM 授权 `QcloudAIA3DFullAccess`；主账户 SecretKey 只显示一次，丢了只能重建。

### 流程
1. 输入图：**纯黑色背景** + 全身完整正面站姿 + 无文字水印（Qwen-Image 生成，prompt 模板见硅基 references）
2. SDK：`pip install --index-url https://mirrors.aliyun.com/pypi/simple/ tencentcloud-sdk-python`（pypi.org 在腾讯云超时）；**ai3d 模块路径是 v20250513**（网上文档常写 v20241218 → ModuleNotFoundError）
3. `SubmitHunyuanTo3DRapidJob`（ImageUrl 必须公网可访问，先 curl 验证 200）→ 每10s轮询 `QueryHunyuanTo3DRapidJob`（900s+ 超时）
4. ⚠️ **极速版返回 OBJ zip 不是 GLB**：zip 内 `.obj+.mtl+4096纹理.png`，按 `ResultFile3Ds[].Type == 'OBJ'` 取
5. OBJ→GLB：`npm install --registry=https://registry.npmmirror.com obj2gltf && npx obj2gltf -i model.obj -o model.glb --binary --unlit`（验证头 magic==b'glTF'）
6. Three.js r160 展示：importmap **必须精确到文件**（`"three/addons/"` 通配静默失败：GLTFLoader 内部相对 import 解析错，canvas 不创建且控制台无报错）；GLTFLoader/DRACOLoader/BufferGeometryUtils 全部本地化（jsdelivr 404 页只有 77 字节，用 `stat -c%s` 检查）；`draco.setDecoderPath('./js/libs/draco/')` 指本地

**轮询/下载坑**：长轮询循环会 Connection reset（104）→ 改单次查询+间隔重试（sleep 5-15s×3）；COS 签名 URL 含 `&` 会被 shell 截断（下载到几百字节假 zip）→ 用 `subprocess.run(['curl','-sL','-o',out,url])` 传列表参数；模型约 15MB 加载 8-10s，进度条用 xhr 回调。

**版权与质量决策（讨论阶段就讲）**：版权角色（擎天柱等）直接告知索赔风险，推荐「原创机甲+红蓝配色致敬」；电影级写实细节转3D会糊成泥，Q版/半写实最好（质量排序：Q版卡通 > 半写实 > 电影写实）。

**支持文件**：`scripts/hunyuan3d.py`（提交+轮询+下载，环境变量读密钥）、`templates/threejs-space-showcase.html` / `templates/threejs-showcase-index.html`（r160 深空展示页模板，importmap 已配好）、`references/threejs-space-showcase.md`（完整要点：本地js结构/importmap/场景/相机控制）。

## DeepSeek API 计费审计与模型锁死（合并自 deepseek-api-cost-control）

**触发**：「为什么DeepSeek扣费严重」「感觉没用多少token却扣钱」「只能调v4-flash锁死」。核心：**先归因（钱烧在哪），再锁死（防止再烧）**。

### 定价要点（deepseek-v4-flash，百万token）
**2026-08-27 主模型已切硅基流动**（官方→硅基反转）：主=SiliconFlow custom、fallback=DeepSeek 官方，见下方锁死清单。

| 平台 | 输入·未命中 | 输出 | 缓存命中 | 高峰加成 |
|---|---|---|---|---|
| **硅基流动（当前主）** | ¥1.0 | ¥2.0 | ¥0.02 | 无 |
| DeepSeek 官方（fallback） | ¥1.5 / 高峰¥3.0 | ¥4.5 / 高峰¥9.0 | ¥0.05 / ¥0.10 | 2倍 |

硅基比官方便宜 55-78% 且无高峰 2 倍价。deepseek-v4-pro 是 flash 的 **3倍**；2026-08-23 起官方周末全天低谷价；**输出已含 thinking token**（别被本地 usage.jsonl 的 reasoningTokens 误导）。

### 成本三大规律
1. **贵不贵看缓存命中率，不看总量**：同样10万token，命中90%≈¥0.5，命中0%≈¥30，差60倍。新会话/cron冷启动/上下文压缩→前缀变→全价未命中
2. **固定行李**：Hermes 系统提示+工具schema+skills列表 ≈ 2.8万token/次——重但不贵（90%命中后每天约¥0.5-1）
3. **烧钱大头排序**：输入未命中缓存 ≫ 输出/thinking > 固定行李

### 扣费排查五步
0. **先 `date` 确认当前日期，再查日志** — 跨天会话极易用错日期（实测：会话开始8/19、实际执行8/22，用8/19过滤日志全空白查一轮）。日志文件名 `agent.log`/`agent.log.1` 轮转，旧档也保留。
1. 控制台 → 用量 → 模型维度，看「输入未命中缓存」×高峰价 = 最大扣费项
2. `grep "API call" ~/.hermes/logs/agent.log | grep 日期 | grep -oP 'model=\S+ provider=\S+' | sort | uniq -c`（cron 会话 ID 格式 `[cron_xxx_时间戳]`；交互会话 `[YYYYMMDD_HHMMSS_hash]`；`agent.log.1` 轮转旧档也要查 pro 调用）
3. cron 审计：`cat ~/.hermes/cron/jobs.json`（`{"jobs":[...]}` 结构）遍历 model/provider 字段
4. 全站模型扫描：落地页 server.py 的 MODEL 行、服小助 app/config.py（常共用同一 DeepSeek key——三处都要查）
5. 跨机：Mac 查 `~/.hermes/logs/agent.log` + `gui.log`（桌面 GUI 走 `hermes serve` 写 gui.log 不写 agent.log）

### 模型锁死清单（只允许 deepseek-v4-flash；2026-08-27 主模型已切硅基）
| 位置 | 做法 |
|---|---|
| config.yaml 主模型 | `provider: custom` + `default: deepseek-ai/DeepSeek-V4-Flash` + `base_url: https://api.siliconflow.cn/v1` + `api_key: ${SILICONFLOW_API_KEY}`（custom 支持 env 引用格式 `${VAR}`） |
| config.yaml fallback | fallback_providers = `[{provider: deepseek, model: deepseek-v4-flash, key_env: DEEPSEEK_API_KEY}]`（官方兜底，反转前是硅基） |
| 辅助模型 | `auxiliary.compression` / `auxiliary.session_search` 同切硅基（`hermes config set auxiliary.*.provider/model/base_url/api_key`） |
| cron jobs | 每个 LLM job 显式 pin：`hermes cron edit <id> --model deepseek-ai/DeepSeek-V4-Flash --provider custom` |
| 落地页 server.py | **硬编码** `MODEL = "deepseek-v4-flash"`，不要 os.environ.get（可被覆盖成 pro） |
| 服小助 | `app/config.py` 硬编码 `DEEPSEEK_CHAT_MODEL` |

**切换 provider 的坑（2026-08-27 实测）**：
- 标量用 `hermes config set model.provider/default/base_url/api_key`（安全）；数组（fallback_providers）只能 python yaml——`config set` 会把数组存成字符串被静默忽略
- ⚠️ 改全局 provider 后，**有 provider_snapshot 的 cron job 下次运行会 fail closed**——config set 会打印警告，必须 `hermes cron edit <job_id> --model <model> --provider <provider>` 把 job pin 到新值
- ⚠️ **当前会话保留启动时的 provider 快照**——改配置只对新会话/cron 生效，当前会话继续按旧 provider 计费；要全切就重启 gateway 或让用户新开会话
- 验证：`hermes chat -q "只回复两个字：正常"` 跑通即新 provider 生效；`python3 -c "import yaml; yaml.safe_load(open('~/.hermes/config.yaml'))"` 确认无语法错
- config.yaml 受安全保护，patch/write_file 会被拒，只能 `hermes config set` 或 python yaml；改完落地页要 kill 旧进程重启（keepalive 只在端口挂了才拉起，不会因代码变更自动重启——`ps -o lstart -p PID` 验证）

### 优化动作（按 ROI）
少开新会话（缓存命中）> **cron 合并成单会话**（同类 LLM job 并成一个，实测省 40-50% 输入费，完整流程见 `references/cron-merge-token-savings.md`）> cron 挪空闲时段（单价减半）> cron 之间错开 > 压缩阈值调高/降频（历史重写=缓存全废）> 删不用 skills（只提速省钱微小）。

**支持文件**：`scripts/deepseek_watch.sh`（balance API 基线观察，0 token，可 cron no_agent 部署）、`references/deepseek-billing-incidents.md`（8/11 pro 调用历史、8/22 ¥0.62 未查明、keepalive 端口顶替案例）。

