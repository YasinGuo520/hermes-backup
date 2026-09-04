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
| 智能体/Agent bot 对话 API | **Coze 扣子** api.coze.cn | PAT 认证、`POST /v3/chat`（实测有效），1个月过期、bot 免费额度烧完会哑火；详见 `references/coze-api.md` |
| 自托管 AI 应用平台（知识库/工作流/私有化） | **Dify 社区版（Docker 完整版）** | 3.6G 内存完整版可跑通，端口 8850（nginx 统一入口）。**禁止精简**（砍 plugin-daemon 必连环 500）；启动必须 `--profile postgresql`（profile 名不是 db_postgres）；详见 `references/dify-deployment.md` |

## 各平台完整文档

- `references/siliconflow-image.md` — 硅基流动生图：模型表、curl 调用、prompt 技巧、立绘抠图、角色贴纸工作流
- `references/volcengine-ark.md` — 火山方舟：Key 类型、模型开通、视频/图像任务 API、价格表、常见错误
- `references/bailian-cli.md` — 阿里百炼 bl CLI：TTS/播客/儿童故事/有声绘本/商品详情图全工作流
- `references/coze-api.md` — 扣子 Coze API：PAT 认证（1个月过期）、`POST /v3/chat` 实测端点、错误码、bot_id 获取、字节风控登录坑
- `references/dify-deployment.md` — Dify 社区版国内服务器（3.6G内存）精简 Docker 部署实录：镜像源选型、精简 compose、端口/验证/防火墙坑

## 跨平台关键坑（易踩）

- **火山方舟必须用「方舟大模型专用 API Key」**（`ark-` 前缀），普通 API Key 调方舟接口必 401
- Seedance 视频模型开通前需**先充值**（免费额度开不了视频）；API 路径是 `generations`（复数）不是 `generators`——拼错返回 404 空 body
- 百炼**系统音色** `cosyvoice-v3-flash` 加 `--instruction` 会报 428，禁止用；**克隆音色**是 `cosyvoice-v3.5-flash`，两个模型不能混用，克隆音色创建必须去百炼控制台手动操作
- 百炼 TTS 输出的 `.mp3` 实为 WAV(PCM)，ffmpeg 拼接必须 `-c:a libmp3lame` 转码
- 硅基流动必须用 curl 不要用 python urllib（本环境 urllib 会 Connection reset）；图片 URL 有效期 24h，必须下载后再发送
- **硅基 key 验证（2026-09-01 实测）**：`/v1/user/info` 端点已弃用——返回 410 code 20092「endpoint is deprecated」，别拿它测 key 误判。正确验证：`curl -s https://api.siliconflow.cn/v1/models -H "Authorization: Bearer $KEY"` 返回 HTTP 200（模型列表）即 key 有效；或直接 curl `/v1/chat/completions` 发一句 "hi"。返回 401 + `{"code":30014,"message":"Token is invalid."}` = 这把 key 无效（复制不全/旧 key）——去测 `.env` 里那把，别在报错现场猜
- 硅基 Qwen-Image 每次生成背景色值略有不同：抠图时逐图采样四角像素均值，不能写死色值
- 生图用途决定背景色：贴纸抠图用深蓝/纯色底；**图生3D用纯黑底**（见 `ai-image-to-3d` 技能）
- 百炼 `bl video generate` 是同步阻塞调用，并行多条会中断（exit 130）——逐条串行
- **Dify web 容器 SSR 回环超时**（腾讯云）：CONSOLE_API_URL 配公网 IP 会让 web 容器内 SSR fetch 被防火墙拦回环 → 页面报「渲染此组件时发生意外错误」；**最终修复（2026-09-01 完整版实测）**：CONSOLE_API_URL/APP_API_URL **留空**（走 nginx 同源，SSR+浏览器全走 8850 一个口），不写公网 IP 也不写 host.docker.internal。⚠️ `host.docker.internal` 方案容器内通但**浏览器白屏转圈**——已证伪弃用。启动必须 `--profile postgresql`；api↔plugin_daemon 401 **根因（2026-09-01 已查明，非猜测）**：api 源码 `core/plugin/impl/base.py:156` 用 `X-Api-Key: PLUGIN_DAEMON_KEY` 调 daemon，该值必须等于 daemon 容器的 `SERVER_KEY`——不是 PLUGIN_DIFY_INNER_API_KEY（两容器该值本就一致）；修法：根 .env 写 `PLUGIN_DAEMON_KEY=<daemon的SERVER_KEY实测值>` + `--force-recreate api`。**Dify 1.17 模型供应商是插件**：`model-providers` 返回 `{"data":[]}` 是正常（未装插件）；装 SiliconFlow 走 UI Marketplace 搜索安装，别猜市场 API——市场搜索端点 404，UI 点 3 下完事。登录 API curl 明文 401（RSA 加密，用 Playwright 真实登录拿 cookie+CSRF）。详见 `references/dify-deployment.md`
- **Coze 免费额度耗尽 bot 哑火**：豆包免费 token 用完 bot 不回复，不是配置问题；Coze 自动化登录被字节风控（滑块验证码+webdriver 检测）拦，反检测 JS 不够用——别死磕，用 PAT 直调 API。详见 `references/coze-api.md`
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

## TikHub 数据API速查（2026-09-02 实测）

TikHub（api.tikhub.io）是抖音/小红书/快手等25平台的公开数据API（1066端点）——**免费只有抖音billboard几个，小红书/快手全付费（402=欠额度）**；拿不到任何平台自己的店铺后台数据。抖音端点解析必看：`data.data` 两层嵌套（热榜 word_list / 账号 user_list）。完整端点表+实测结构见 `references/tikhub-endpoints.md`（参考实现：`~/Desktop/hermes/company-agents/common/tikhub.py`）。

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
**2026-09-02 实测：硅基已涨到与官方同价，不再便宜**（原 ¥1/¥2 旧价已作废）。主=**DeepSeek 官方**（2026-09-02 已全切：Hermes 主模型+辅助+3条高耗cron+16公司agents 公共层，硅基弃用；仅 vision 辅助留硅基 Qwen3-VL，官方无等效稳定视觉替代且用量小），见下方锁死清单。

| 平台 | 输入·未命中 | 输出 | 缓存命中 | 时段格局 |
|---|---|---|---|---|
| **硅基流动（当前主）** | ¥1.5 低价 / ¥3.0 高价 | ¥4.5 低价 / ¥9.0 高价 | ¥0.15 / ¥0.30（官方3倍） | 低价=每天凌晨2-8点；高价=0-2 & 8-24（每天18h） |
| DeepSeek 官方（fallback） | ¥1.5 / 高峰¥3.0 | ¥4.5 / 高峰¥9.0 | ¥0.05 / ¥0.10 | 高峰=工作日9-12、14-18（5h/天） |

**高峰时段坑（2026-09-02 实测）**：官方高峰只工作日5小时；硅基高价时段每天18小时（**8点整就涨价**）。「9点前跑完避高峰」策略在对官方**重新生效**（官方9点才起高峰；晨间 cron 已全挪 7:00-7:55 档——三合一7:10/英语7:30/看板同步7:50等，见下；白天9-18两边同价；18点后+周末官方全天空闲价、硅基仍高价）。deepseek-v4-pro 是 flash 的 **3倍**；**输出已含 thinking token**（别被本地 usage.jsonl 的 reasoningTokens 误导）。

### 账单/余额查询实证（2026-09-02 实测）

**查 key 先看 `~/.hermes/.env`**（Hermes 专用 key 文件，用户明确纠正过：别全盘 find/grep 找 key）。里面直接有 `DEEPSEEK_API_KEY`、`DEEPSEEK_BASE_URL=https://api.deepseek.com/v1`、`SILICONFLOW_API_KEY`、`OPENAI_API_KEY` 等。key 前缀 `sk-` 长度 35。

**余额/今日消费：**
- DeepSeek 官方：`curl https://api.deepseek.com/user/balance -H "Authorization: Bearer $KEY"`（实测可用，返回 `balance_infos[]: currency/total_balance/granted_balance(赠)/topped_up_balance(充)`）
- 硅基流动：**没有公开余额端点**（`/v1/user/info` deprecated / `balance`、`usage` 全 404）→ 余额和「今日消费」只能看控制台 console.siliconflow.cn（需登录，拿不到就请用户截图对账，别编）

**本地 cron 精确账本**：`~/.hermes/cron/usage_audit.jsonl` 每行一条 cron 执行记录，含 `ts`（**UTC，+8=北京**）、`prompt_tokens`、`completion_tokens`、`model`、`job_id`——这是 cron 侧最可靠的 token 账。⚠️ `sessions/sessions.json` 的 input/output/cache 字段**实测全为 0 不可靠**（没在记账）；`request_dump_*.json` 只有 cron 会话有。

**渠道切换前先盘点**：改渠道不是全量改。先 `python3` 读 `~/.hermes/cron/jobs.json` 按 `provider` 字段分组，只改目标渠道的 job（2026-09-02 实测：14 个 cron 里 4 个已钉官方 `provider=deepseek`、3 个走硅基 `provider=custom`）。company-agents 的公共层配置在 `~/Desktop/hermes/company-agents/common/llm.py` 的 `BASE=` 一行。

### 成本三大规律
1. **贵不贵看缓存命中率，不看总量**：同样10万token，命中90%≈¥0.5，命中0%≈¥30，差60倍。新会话/cron冷启动/上下文压缩→前缀变→全价未命中
2. **固定行李**：Hermes 系统提示+工具schema+skills列表 ≈ 2.8万token/次——重但不贵（90%命中后每天约¥0.5-1）
3. **烧钱大头排序**：输入未命中缓存 ≫ 输出/thinking > 固定行李

### 扣费排查五步
0. **先 `date` 确认当前日期，再查日志** — 跨天会话极易用错日期（实测：会话开始8/19、实际执行8/22，用8/19过滤日志全空白查一轮）。日志文件名 `agent.log`/`agent.log.1` 轮转，旧档也保留。
1. 控制台 → 用量 → 模型维度，看「输入未命中缓存」×高峰价 = 最大扣费项
2. `grep "API call" ~/.hermes/logs/agent.log | grep 日期 | grep -oP 'model=\S+ provider=\S+' | sort | uniq -c`（cron 会话 ID 格式 `[cron_xxx_时间戳]`；交互会话 `[YYYYMMDD_HHMMSS_hash]`；`agent.log.1` 轮转旧档也要查 pro 调用）
3. cron 审计：`cat ~/.hermes/cron/jobs.json`（`{"jobs":[...]}` 结构）遍历 model/provider 字段
4. 全站模型扫描（**不只 Hermes——导航Hub全生态都要查**，2026-09-04 实测在中年人生backend抓出漏网的 `deepseek-chat`）：按服务类型定位 config 位置（落地页 server.py MODEL 行 / 服小助 app/config.py / 中年人生 `/var/www/midlife-test/backend/config.py` / company-agents 公共层 / 静态页 JS 直连 / n8n sqlite / Dify postgres），完整配方见 `references/full-fleet-model-audit.md`
5. 跨机：Mac 查 `~/.hermes/logs/agent.log` + `gui.log`（桌面 GUI 走 `hermes serve` 写 gui.log 不写 agent.log）

### 模型锁死清单（只允许 deepseek-v4-flash；2026-09-02 已全切 DeepSeek 官方）
| 位置 | 做法（官方版） |
|---|---|
| config.yaml 主模型 | `provider: deepseek` + `default: deepseek-v4-flash` + `base_url: https://api.deepseek.com/v1` + `api_key: ${DEEPSEEK_API_KEY}`（官方模型名**不带前缀**；带 `deepseek-ai/` 前缀的是硅基命名，两边不通用） |
| config.yaml fallback | 已清空（官方即主渠道，无需兜底） |
| 辅助模型 | `auxiliary.compression` + `auxiliary.session_search` 同切官方；⚠️ `config set` 对 `auxiliary.session_search.*` 打印 "not a recognized config key" 警告，但**值照样写入 yaml 且生效**（运行时读 yaml，不查 registry） |
| delegation + 全部 auxiliary auto 段 | **2026-09-04 全钉死**：`delegation.*` + `auxiliary.{skills_hub,approval,review,mcp,title_generation,memory_query_rewrite,tts_audio_tags,triage_specifier,kanban_decomposer,profile_describer,goal_judge,curator,monitor,background_review,moa_reference,moa_aggregator}`（16 段）逐个 `hermes config set <段>.{model,provider,base_url,api_key}` → model=`deepseek-v4-flash`/provider=`deepseek`/官方 base_url/api_key=`${DEEPSEEK_API_KEY}`。**`provider: auto` 或空配置 = 静默漏跑 pro 的路径**（主模型一改 auto 全跟着跑偏），锁死必须显式钉不能靠继承 |
| 辅助 vision | **留硅基** `Qwen/Qwen3-VL-8B-Instruct`（用量小；官方视觉模型仅 vision-exp 不稳定） |
| cron jobs | 显式 pin：`hermes cron edit <完整12位ID> --model deepseek-v4-flash --provider deepseek`；⚠️ **8位短 ID 报 "Job not found"**，必须完整 12 位 hex（从 `hermes cron list` 或 jobs.json 复制） |
| 16 公司 agents | `common/llm.py`：`BASE = "https://api.deepseek.com/v1"` + `MODEL = "deepseek-v4-flash"` + 读 `DEEPSEEK_API_KEY`（切完跑 `python3 common/llm.py` 验证连通） |
| 落地页 server.py | **硬编码** `MODEL = "deepseek-v4-flash"`，不要 os.environ.get（可被覆盖成 pro） |
| 中年人生 backend（8001/midage.icu） | `/var/www/midlife-test/backend/config.py` 的 `DEEPSEEK_MODEL`——**2026-09-04 抓出写的是 `deepseek-chat`（V3 非 flash）**，已改 flash；supervisord 管理（program `midlife-test`），改完 `sudo -n supervisorctl restart midlife-test`（非 root 直接 supervisorctl 报 PermissionError） |
| 服小助 | `app/config.py` 硬编码 `DEEPSEEK_CHAT_MODEL`（本来就是官方 key，无需动） |

**切换 provider 的坑（2026-08-27 实测）**：
- 标量用 `hermes config set model.provider/default/base_url/api_key`（安全）；数组（fallback_providers）只能 python yaml——`config set` 会把数组存成字符串被静默忽略
- ⚠️ 改全局 provider 后，**有 provider_snapshot 的 cron job 下次运行会 fail closed**——config set 会打印警告，必须 `hermes cron edit <job_id> --model <model> --provider <provider>` 把 job pin 到新值
- ⚠️ **当前会话保留启动时的 provider 快照**——改配置只对新会话/cron 生效，当前会话继续按旧 provider 计费；要全切就重启 gateway 或让用户新开会话
- ⚠️ **`hermes cron list` 只列 active 任务**——jobs.json 里 `enabled=false` 的 job 是停用的（可能早就不跑了，用前先核对 usage_audit 有没有它的记录）；对停用 job 跑 `cron edit --schedule` 报 **"Cannot activate terminal cron job … through update_job"**——只想改其 schedule 保持停用时，`cp jobs.json jobs.json.bak` 后 python 直接改 `schedule.expr`，实测 scheduler 重读生效（`hermes cron status` 的 Next run 即更新）
- 验证：`hermes chat -q "只回复两个字：正常"` 跑通即新 provider 生效；`python3 -c "import yaml; yaml.safe_load(open('~/.hermes/config.yaml'))"` 确认无语法错
- config.yaml 受安全保护，patch/write_file 会被拒，只能 `hermes config set` 或 python yaml；改完落地页要 kill 旧进程重启（keepalive 只在端口挂了才拉起，不会因代码变更自动重启——`ps -o lstart -p PID` 验证）

**渠道全切一次性清单（2026-09-02 官方全切实测；用户明确要求「别绕，一次搞定」）**：
1. 查 key：直接读 `~/.hermes/.env`（Hermes 专用 key 文件），别 find/grep 全盘搜（用户纠正过）
2. 官方余额：`curl https://api.deepseek.com/user/balance -H "Authorization: Bearer $KEY"` → `balance_infos[].total_balance`（⚠️ 切之前查，余额不足先充值——实测切时只剩 ¥9.47，不充值 cron 明早就饿死）
3. `hermes config set` × 4 键（model.provider/default/base_url/api_key）+ auxiliary.compression × 4 + auxiliary.session_search × 4；`config show` 确认展开后 api_key 前缀正确
4. 读 `~/.hermes/cron/jobs.json` 按 provider 分组 → 只改旧渠道的 job：`hermes cron edit <完整12位ID> --model deepseek-v4-flash --provider deepseek`
5. company-agents 公共层：patch `common/llm.py`（BASE/MODEL/key 名三处），跑 `python3 common/llm.py` 验连通
6. 验证收尾：`config show | grep -A8 Model` + jobs.json grep model/provider + 直调 `https://api.deepseek.com/v1/chat/completions` 看 usage 返回

**官方 API 实测坑（2026-09-02）**：
- 官方**默认开思考模式**：completion 返回 `completion_tokens_details.reasoning_tokens` 单独计费；`max_tokens` 设太小会被 thinking 全吃掉（实测 max_tokens=10 → 返回 10 个 reasoning token、`content` 为空）——测连通时 `max_tokens` ≥64，且 content 非空才算真通
- 官方响应带 `prompt_cache_hit_tokens` 字段（缓存命中可观测，能用来对账）
- **官方无 embedding 端点**：`POST /v1/embeddings` 返回 404，`deepseek-embedding` 模型不存在（2026-09-04 实测）。想挂官方 embedding 做 RAG 的（如服小助 knowledge.py `get_embedding`）会静默降级成关键词检索——要语义检索需换硅基 BGE 等 embedding 渠道
- 切换后**当前会话仍走旧 provider 快照**——验证要新开会话或等 cron 跑（见上）

### 优化动作（按 ROI）
少开新会话（缓存命中）> **cron 合并成单会话**（同类 LLM job 并成一个，实测省 40-50% 输入费，完整流程见 `references/cron-merge-token-savings.md`）> cron 挪空闲时段（单价减半）> cron 之间错开 > 压缩阈值调高/降频（历史重写=缓存全废）> 删不用 skills（只提速省钱微小）。

**支持文件**：`scripts/deepseek_watch.sh`（balance API 基线观察，0 token，可 cron no_agent 部署）、`references/deepseek-billing-incidents.md`（8/11 pro 调用历史、8/22 ¥0.62 未查明、keepalive 端口顶替案例）、`references/full-fleet-model-audit.md`（导航Hub全生态模型锁死审计配方：端口→代码目录定位 / 逐服务 grep 位置表 / n8n+Dify 库内查 / 误报过滤——2026-09-04 实测抓出中年人生 deepseek-chat 漏网）。

