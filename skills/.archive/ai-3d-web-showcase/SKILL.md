---
name: ai-3d-web-showcase
description: 用AI把2D立绘转真3D模型(GLB)并部署Three.js网页展示。墙内全流程+混元3D API坑。
---

# AI 图生3D 网页展示

把 2D 立绘/产品图/角色图变成**真 3D 模型**（GLB），并部署到 Three.js 3D 网页（360° 拖拽旋转、滚轮缩放、自动巡航、太空/展厅场景）。墙内全流程已跑通，成本 ≈ ¥0.2/角色。

## 何时使用

- 用户要「人物/角色/产品做成 3D 立体」「3D 网页展示」「能 360° 转的真模型」
- **先讨论方案再动手**（用户明确要求：真3D vs 伪3D差异要讲清、给方案让他拍板，不要上来就干）
- 区分：**真3D**（本文：真模型可转背面）vs 伪3D 视差（CSS perspective，见 visual-component-patterns）——用户说「真3D才行」时走本文

## 全链路（4步）

```
① Qwen-Image 生成立绘（纯黑背景、全身完整）
② 腾讯混元3D API 图生3D（SubmitHunyuanTo3DRapidJob）
③ OBJ zip → obj2gltf 转 GLB
④ Three.js 展示页 + http.server 部署
```

### ① 生成立绘
- 工具：硅基流动 Qwen-Image（`SILICONFLOW_API_KEY`，curl 调用，见 siliconflow-image-gen 技能）
- Prompt 要点：`全身立绘、正面站立、纯黑色背景、完整可见、无文字无水印`
- **纯黑背景是图生3D关键**——混元直接从图提几何，背景干净出模好
- ⚠️ 版权：不要生成知名 IP 角色（擎天柱=孩之宝版权，商用必撞枪口）。改为「原创机甲指挥官、红蓝配色致敬」同款气质，既保留气势又无雷

### ② 腾讯混元3D API（墙内唯一可达通道）
- Tripo/Meshy 全部连不上（api.tripo3d.ai / api.meshy.ai 测过 000），**只有腾讯混元3D 通**
- 唯一认证：**SecretId + SecretKey**（TC3-HMAC-SHA256 签名）。sk- 开头的 key 一律无效，别浪费时间
- **开通服务 ≠ 有额度**！开通后必须去控制台手动领取免费积分包（https://console.cloud.tencent.com/ai3d），否则报 `ResourceInsufficient 资源不足`
- 接口：`ai3d.tencentcloudapi.com`，SDK 模块 `ai3d.v20250513`（不是 v20241218）
- 提交：`SubmitHunyuanTo3DRapidJob`，参数 `ImageUrl`（必须公网可访问——用已验证开放端口服务图片）
- 轮询：`QueryHunyuanTo3DRapidJob`，Status: WAIT/RUN/DONE/FAIL
- 结果：`ResultFile3Ds`，Type=OBJ 返回 zip（极速版给 OBJ 不是 GLB，要转）
- 完整脚本：`scripts/hunyuan3d.py`（自动读 .env、提交、轮询、下载一条龙）

### ③ OBJ → GLB
- 解压 zip：.obj + .mtl + texture_4096.png
- 用 node 工具：`npm i obj2gltf`（npmmirror 源）→ `npx obj2gltf -i model.obj -o model.glb --binary`
- 验证：文件头 magic = `glTF`、version = 2

### ④ Three.js 展示页
- 可改模板：`templates/space-showcase.html`（深空星空粒子 + 星云背景 + 机甲悬浮 + 拖拽旋转 + 滚轮缩放 + 触屏）
- 部署：`python3 -m http.server 8931 --bind 0.0.0.0`（background=true 起服务）
- 验证：本地 curl 200 → 公网 curl 200 → browser_vision 截图确认模型完整无破面

## Pitfalls（踩过的坑）

1. **Three.js ES module 结构**（墙内环境最大坑）：
   - GLTFLoader 是 ES module，必须配 `three.module.js`（不能和 three.min.js 混用）
   - 下载源用 jsdelivr：`https://cdn.jsdelivr.net/npm/three@0.160.0/...`（unpkg/npmmirror 也能用）
   - 目录必须按官方结构放：`js/loaders/GLTFLoader.js`、`js/loaders/DRACOLoader.js`、`js/utils/BufferGeometryUtils.js`、`js/libs/draco/`（decoder 4 件套：draco_decoder.js/wasm + wasm_wrapper）
   - importmap 映射**精确路径**，不要用 `three/addons/` 通配前缀（GLTFLoader 内部相对 import 会 404）
   - `draco.setDecoderPath` 用本地相对路径 `./js/libs/draco/`，不要 CDN
   - 下载失败特征：文件只有几百字节 = 404 错误页，`stat -c%s` 检查

2. **轮询 Connection reset**：腾讯云 API 偶发 `Connection reset by peer`，重试即可（脚本里 try/except + sleep 15s 继续，别当失败）

3. **腾讯云机器 pip 源**：pypi.org 超时。用阿里镜像 `--index-url https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com`（清华/腾讯源 301 也能通）

4. **端口开放**：新端口不一定公网通（8930 公网 000）。图生3D 的 ImageUrl 用已验证开放端口（如 8915 展厅）服务图片；页面交付前必须验证公网可达

5. **模型体积**：混元极速版 OBJ 转 GLB 约 15MB，加载要几秒，loader 进度显示做上（`xhr.loaded/total`）

## 关联

- siliconflow-image-gen（立绘生成）
- visual-component-patterns（伪3D视差/CSS 3D环形展厅——非真模型）
- volcengine-ark-api（火山方舟，视频/图像，非3D）
