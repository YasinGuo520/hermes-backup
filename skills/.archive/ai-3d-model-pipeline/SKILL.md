---
name: ai-3d-model-pipeline
description: 2D立绘→腾讯混元3D图生3D→GLB→Three.js 3D展示页。墙内真3D模型生成全流程。
---

# AI 图生3D → 网页展示流水线

把人物/角色/产品图做成**真3D模型**（GLB）并在网页上 360° 展示。不是伪3D视差，是可旋转看背面的真模型。

## 何时使用

- 用户要求「人物形象做成3D立体的」「真3D才行」「放到3D网页展示」
- 需要吉祥物/角色/产品的可交互 3D 展示页

## 核心路径（已跑通，成本≈¥0.14）

```
① Qwen-Image 生成立绘（纯色背景，方便转3D）   → 硅基流动 ¥0.14/张
② 腾讯混元3D API 图生3D（免费额度）            → 返回 OBJ+MTL+4096纹理 zip
③ obj2gltf 转 GLB                              → node/npm，15MB级
④ Three.js 太空展示页（本地库，不依赖CDN）     → http.server 部署
```

## 关键前置：腾讯混元3D（墙内唯一可用通道）

**Tripo/Meshy 服务器全被墙**（curl 000），只有腾讯混元3D API 可通。

三步开通（少一步就报错）：
1. 开通服务：https://cloud.tencent.com/product/ai3d
2. **手动领取免费积分**（控制台 ai3d → 免费额度/资源包管理）——不领就报 `ResourceInsufficient 资源不足`
3. 密钥：SecretId + SecretKey（**腾讯云API只认签名认证，sk-开头key无效**）

开通后从报错判断卡在哪：
- `ResourceUnavailable.NotExist` → 服务没开通
- `ResourceInsufficient` → 开通了但免费额度没领（最常见）

## API 调用细节

- SDK 模块：`tencentcloud.ai3d.v20250513`（**不是**文档里的 v20241218）
- 端点：`ai3d.tencentcloudapi.com`，Region `ap-guangzhou`
- 提交：`SubmitHunyuanTo3DRapidJob`，参数 `ImageUrl`（**必须公网可访问**）
- 轮询：`QueryHunyuanTo3DRapidJob`，Status `RUN` → `DONE`，成功返回 `ResultFile3Ds`（Type=OBJ，下载URL带签名）
- 图片公网URL：用已开放端口起 http.server 服务（如 8915），新端口可能没开安全组

脚本：`scripts/hunyuan3d.py`（提交+轮询+下载全流程，环境变量 TENCENT_SECRET_ID/TENCENT_SECRET_KEY）

## OBJ → GLB 转换

```bash
npm install --registry=https://registry.npmmirror.com obj2gltf
npx --yes obj2gltf -i model.obj -o model.glb --binary --unlit
```
验证 GLB 头：`magic == b'glTF'`。

## Three.js 本地部署（墙内不依赖CDN）

r160 起 GLTFLoader 是 ES module。**必须按官方目录结构放**，importmap 逐个映射：

```
web/
├── index.html
├── model.glb
└── js/
    ├── three.module.js          # build/three.module.js
    ├── loaders/GLTFLoader.js    # examples/jsm/loaders/GLTFLoader.js
    ├── loaders/DRACOLoader.js   # examples/jsm/loaders/DRACOLoader.js
    ├── utils/BufferGeometryUtils.js  # GLTFLoader内部import ../utils/，缺失=静默失败
    └── libs/draco/              # draco_decoder.js/.wasm + draco_wasm_wrapper.js（本地，勿用CDN）
```

importmap:
```html
<script type="importmap">
{
  "imports": {
    "three": "./js/three.module.js",
    "three/addons/loaders/GLTFLoader.js": "./js/loaders/GLTFLoader.js",
    "three/addons/loaders/DRACOLoader.js": "./js/loaders/DRACOLoader.js",
    "three/addons/libs/draco/": "./js/libs/draco/"
  }
}
</script>
```
`draco.setDecoderPath('./js/libs/draco/')` 用相对路径。

下载源：`https://cdn.jsdelivr.net/npm/three@0.160.0/...`（服务器可通 jsdelivr）。

## 页面要素（用户偏好）

- 深空背景：Canvas 程序化星云 + 星空粒子（4500颗，三种颜色）
- 灯光：主光(暖) + 轮廓光(蓝) + 点光(红/蓝)
- 交互：拖拽旋转 + 滚轮缩放 + 自动巡航（拖拽暂停）+ 触屏双指
- 机甲悬浮微动：`y = 0.2 + sin(t*1.2)*0.12`，自动慢转
- 加载页：进度百分比显示

## Pitfalls

1. **别做版权角色本尊**（擎天柱=孩之宝）。做「原创机甲指挥官」红蓝配色致敬。2D立绘 prompt 明确「原创」，写实风格、纯黑背景、全身完整
2. **pip 走阿里云镜像**：腾讯云机器 pypi.org 也超时，用 `--index-url https://mirrors.aliyun.com/pypi/simple/`
3. **GLTFLoader.js 缺失 BufferGeometryUtils 时页面静默失败**：canvas 不创建、模型不请求、无报错。查 `performance.getEntriesByType('resource')` 看哪个文件 300字节（404页）
4. **Importmap 用 `three/addons/` 通配映射会解析错**（相对路径依赖失效），要逐文件映射
5. **混元3D 极速版返回的是 OBJ 不是 GLB**，必须转换；`--unlit` 保留纹理
6. **查询接口偶发 Connection reset**：重试即可，任务本身在后台继续跑
7. **后台轮询脚本设长超时**（900s+），提交后立即返回 JobId，生成要几分钟
8. 背景粒子用户偏好「明显不能太淡」：70粒子、alpha 0.15-0.35、连线距离140px

## 验证

- `browser_navigate` + `browser_console` 检查 canvas 存在、loader 隐藏、model.glb 资源加载
- `browser_vision` 确认模型完整无破面、交互正常
- 公网 curl 200 才算上线

## 关联

- 立绘生成：siliconflow-image-gen（Qwen-Image，curl 调用）
- 页面贴纸/伪3D视差（不转真模型时）：visual-component-patterns
- 3D环形展厅（CSS伪3D画廊）：visual-component-patterns references/3d-ring-gallery.md
