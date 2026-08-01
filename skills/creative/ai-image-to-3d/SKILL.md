---
name: ai-image-to-3d
description: 2D立绘转GLB真3D模型（腾讯混元3D API）→ Three.js 3D展示网页。墙内可用，成本≈0。
---

# AI图生3D（立绘 → GLB → 3D网页）

把一张2D图片变成可360°旋转的真3D模型（GLB），并放进 Three.js 3D展示页。
适用：机甲/角色/产品/吉祥物 3D展示页（个人主页、品牌IP、作品展厅）。

## 何时使用
- 用户要求「把XX做成3D立体的」「3D展示页」「转3D模型」
- ⚠️ 动手前先问清楚：**真3D**（可旋转看背面，本技能）还是**伪3D**（CSS视差倾斜，见 visual-component-patterns「AI立绘动态升级」）。用户说「真3D的才行」就是本技能。

## 通道选择（腾讯云服务器实测）
| 通道 | 状态 | 说明 |
|------|------|------|
| 腾讯混元3D API | ✅ 可用 | 唯一实测通，endpoint ai3d.tencentcloudapi.com |
| Tripo (tripo3d.ai) | ❌ 000 | 服务器 curl 全不通 |
| Meshy (meshy.ai) | ❌ 000 | 同上 |

前提：腾讯云账号（用户已有）+ API密钥。密钥页面：https://console.cloud.tencent.com/cam/capi
（SecretId + SecretKey，让用户去生成后发来）

### 密钥与开通的坑（实测踩过）
- ⚠️ **只认 SecretId + SecretKey**（TC3-HMAC-SHA256 签名）。sk- 开头的 key 无效——那是混元大模型LLM的key，不是3D API的。用户可能给 sk- key，直接拒。
- ⚠️ **开通服务 ≠ 有额度**。刚开通时提交任务报 `ResourceInsufficient 资源不足`，是因为**免费积分要手动去控制台领取**：https://console.cloud.tencent.com/ai3d → 免费额度/资源包管理 领取；或 设置→后付费 开通。让用户领完再重试。
- ⚠️ 错误码诊断：
  - `ResourceUnavailable.NotExist 计费状态未知` = 服务没开通 → 去 product/ai3d 开通
  - `ResourceInsufficient 资源不足` = 已开通但没领免费额度/没开后付费
  - `AuthFailure.InvalidAuthorization` = 用了非签名认证方式（如 Bearer sk-）
- 子账户密钥可以用，但需要主账户在 CAM 授权 `QcloudAIA3DFullAccess`
- 主账户密钥自2023-11-30起 SecretKey 只显示一次，丢了只能删了重建

### 工作流偏好（用户明确要求）
- **先讨论方案、用户拍板，再动手执行**（用户原话：「我们先讨论的，你不用马上干」）
- 讨论阶段给方案对比表（真3D vs 伪3D、成本、工具、版权风险），等用户明确选型后再开工
- 用户说「能搞就行」= 确认技术方向，但仍要等他说「搞」才执行

## 立绘准备（Qwen-Image 生成，见 siliconflow-image-gen）
图生3D输入图必须：
- **纯黑色背景**（建模友好，不要花背景）
- 全身完整、正面站姿、无遮挡
- 无文字无水印
- prompt 模板（写实机甲例）：
  `原创机甲指挥官，写实风格，全身立绘，正面站立姿态，红蓝双色涂装，金属材质高光反射，胸前六边形能量核心发光，宽大肩甲，机械关节细节，电影级CG渲染，8K细节，纯黑色背景，全身完整可见，无文字无水印`

## SDK 安装（腾讯云机器，pip 必须用阿里云镜像）
```bash
cd <项目目录> && python3 -m venv venv
./venv/bin/pip install --index-url https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com tencentcloud-sdk-python
```
⚠️ 坑：pypi.org 在腾讯云上直接超时；腾讯云自带镜像 mirrors.tencentyun.com 会 ProxyError。
⚠️ 坑：ai3d 模块路径是 **v20250513**（网上文档常写 v20241218，会 ModuleNotFoundError）：
`from tencentcloud.ai3d.v20250513 import ai3d_client, models`

## API 调用流程
1. `SubmitHunyuanTo3DRapidJob`（极速图生3D）：参数 `ImageUrl`（图片必须**公网可访问URL**）
2. `QueryHunyuanTo3DRapidJob`：轮询（每10s），状态 `SUCCEED` 后响应里取模型URL
3. ⚠️ **极速版返回 OBJ zip，不是 GLB**（实测）：zip 内含 `.obj + .mtl + 4096纹理.png`，响应 `ResultFile3Ds[].Type` 为 `OBJ`。别写死找 .glb。
4. **OBJ → GLB 转换（obj2gltf，node 环境）**：
```bash
npm install --registry=https://registry.npmmirror.com obj2gltf
npx obj2gltf -i model.obj -o model.glb --binary --unlit
# 验证 GLB 头：magic == b'glTF'，version == 2
```
5. 完整可运行脚本：`scripts/hunyuan3d.py`（复制到项目改 TENCENT_SECRET_ID/KEY 环境变量）
6. ⚠️ 轮询偶发 `Connection reset by peer`：提交成功但查询被断属正常抖动，重试即可（10s 间隔继续查）

## 图片公网服务（关键坑）
API 要 ImageUrl，但**新端口（如8930）腾讯云安全组未开放 → 公网 curl 000**。
✅ 复用已验证开放的端口：如 8915（像素画展厅）直接 cp 图片进去：
```bash
cp mecha_front.png ~/Desktop/hermes/pixel-gallery/
curl -s -o /dev/null -w "%{http_code}" http://43.138.221.174:8915/mecha_front.png  # 验证 200
```
（先用 curl 验证公网可达再提交任务，别提交了才发现 URL 打不开）

## Three.js 展示页（拿到 GLB 后）
- Three.js CDN + GLTFLoader 加载 `.glb`
- 太空/深空风：星空粒子背景 + 模型自动慢转 + 鼠标拖拽旋转 + 环境光/方向光/点光三灯
- 风格基调参考 visual-component-patterns（深色科技风），页面独立端口 + http.server 部署
- 部署参考 immersive-html-experiences

### ⚠️ r160 起是 ES module，importmap 必须精确到文件（实测踩坑，白屏排查 30 分钟）
墙内不能用 Google CDN，three.js 用 jsdelivr 下载到本地 `js/` 目录：
```
js/
├── three.module.js                # ✅ 不是 three.min.js（旧版非 module 不配 jsm loader）
├── loaders/GLTFLoader.js          # ✅ 路径 examples/jsm/loaders/
├── loaders/DRACOLoader.js
├── utils/BufferGeometryUtils.js   # GLTFLoader 内部 import '../utils/...'
└── libs/draco/                    # draco_decoder.js/.wasm/wrapper（本地化）
```
❌ **坑1：GLTFLoader.js 下载回来 77 字节** = jsdelivr 404 页。r160 起 loader 移到 `examples/jsm/loaders/`，`examples/js/loaders/` 已移除。
❌ **坑2：importmap 用通配 `"three/addons/": "./js/"` 会静默失败**——GLTFLoader 内部相对 import（`../utils/BufferGeometryUtils.js`）解析错，模型不加载、canvas 不创建、**控制台无报错**。必须精确映射：
```html
<script type="importmap">
{"imports": {
  "three": "./js/three.module.js",
  "three/addons/loaders/GLTFLoader.js": "./js/loaders/GLTFLoader.js",
  "three/addons/loaders/DRACOLoader.js": "./js/loaders/DRACOLoader.js",
  "three/addons/libs/draco/": "./js/libs/draco/"
}}
</script>
```
❌ **坑3：BufferGeometryUtils.js 缺失**（GLTFLoader 依赖），浏览器静默 404，同坑2症状。补上 `utils/BufferGeometryUtils.js`。
❌ **坑4：DRACO decoder 必须本地**：`draco.setDecoderPath('./js/libs/draco/')`，别留 jsdelivr 远程。
✅ **排查法**：`performance.getEntriesByType('resource')` 里 `.glb` 根本没被请求 → 模块早挂了，查 importmap/依赖文件；loader 隐藏但 canvas 没出现 = 脚本报错。

## 流程总结
1. 确认要真3D（问：360°旋转还是视觉炫就行）
2. 生成/准备纯黑背景立绘（siliconflow-image-gen，¥0.14/张）
3. 让用户提供腾讯云 SecretId/SecretKey
4. 立绘放已开放公网端口（curl 验证）
5. `hunyuan3d.py` 提交+轮询+下载 OBJ zip
6. obj2gltf 转 GLB → Three.js 太空页展示，浏览器验证

## 参考文件
- `scripts/hunyuan3d.py` — 可复用图生3D脚本（提交+轮询+下载，环境变量读密钥）
- `references/threejs-space-showcase.md` — Three.js 太空展示舱完整要点（本地js结构/importmap/场景/相机控制，实例 mecha3d/web/index.html）

## 版权与精细度决策（讨论阶段就讲清）
- ⚠️ **版权角色不能做**：用户想要擎天柱/变形金刚类角色时，直接告知孩之宝版权风险（公开传播会被举报/索赔），推荐「原创机甲指挥官+红蓝配色致敬」路线，延续用户红蓝分析法 IP。
- ⚠️ **AI图生3D的精细上限**：电影级写实细节（密密麻麻机械件）转3D会糊成泥。Q版/半写实效果最好。「视觉效果精致」AI能做；「建模细节真多」得上 Blender 手动建模（成本翻几十倍）。用户要区分这俩。
- 图生3D质量排序：Q版卡通 > 半写实 > 电影写实（几何越简单越稳）
