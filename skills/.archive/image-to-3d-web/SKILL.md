---
name: image-to-3d-web
description: 用户要"把XX做成3D立体放网页展示"时用，2D立绘→腾讯混元3D→GLB→Three.js展示。
---

# AI图生3D → 3D网页展示（墙内全链路）

把2D人物/角色/产品图变成真3D模型（GLB），再放上 Three.js 3D 交互展示网页。已实测跑通（机甲指挥官 8931）。

## 触发

用户说「把人物/形象做成3D立体」「放3D网页展示」「图生3D」→ 此技能。
注意区分：用户可能只要伪3D（CSS视差）——先确认「真3D（360°旋转看背面）还是视觉够炫」。真3D才走本流程。

## 全流程

```
1. 生成立绘（SiliconFlow Qwen-Image，纯黑背景！）
   → 图生3D对背景敏感：纯色干净背景转3D效果最好，深色背景也可
2. 立绘放公网可访问URL（用已验证开放的端口，如8915展厅）
3. 腾讯混元3D API 提交图生3D任务 → 轮询 → 下载OBJ+纹理zip
4. obj2gltf 转 GLB
5. Three.js 展示页（深空/太空主题+拖拽旋转+自动巡航）
6. 挂导航Hub（见 html-project-hub skill）
```

## 腾讯混元3D API 关键点

| 项 | 值 |
|---|---|
| 端点 | `ai3d.tencentcloudapi.com`（ap-guangzhou） |
| SDK | `tencentcloud-sdk-python`，模块 `tencentcloud.ai3d.v20250513`（**不是 v20241218**） |
| 提交 | `SubmitHunyuanTo3DRapidJob`（参数 ImageUrl，返回 JobId） |
| 查询 | `QueryHunyuanTo3DRapidJob`（Status: WAIT/RUN/DONE/FAIL，DONE 后 ResultFile3Ds[] 含 OBJ/GLB 下载URL） |
| 认证 | 腾讯云标准 TC3 签名：SecretId+SecretKey（AKID开头）。**不是 sk- 开头的 API Key** |
| 子账户 | 需要授权 `QcloudAIA3DFullAccess`（或 QcloudAI3DFullAccess），否则报权限错 |
| 免费额度 | 开通服务后**必须手动去控制台领取免费积分**（console.cloud.tencent.com/ai3d → 免费额度/资源包管理），不领则报 `ResourceInsufficient 资源不足` |
| 结果 | 极速版返回 OBJ+MTL+4096纹理 的 zip；下载URL 有签名参数（& 等），**必须用 Python requests/curl 传完整URL，不要 shell 截断** |

### 报错排查
- `ResourceUnavailable.NotExist 计费状态未知` → 服务未开通，去 console.cloud.tencent.com/ai3d 开通
- `ResourceInsufficient 资源不足` → 开通了但免费额度没领 / 子账户无权限
- 查询偶发 `Connection reset` → 重试即可（提交成功≠查询一定通）

### 安装坑
- pip 腾讯云源/pypi 都超时 → 用阿里云镜像：`pip install --index-url https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com`
- 用 venv（PEP 668 挡系统 pip）

## OBJ → GLB 转换

```bash
# node v22 可用
npm install --registry=https://registry.npmmirror.com obj2gltf
npx obj2gltf -i model.obj -o model.glb --binary --unlit
```

## Three.js 展示页坑（r160+ ES module）

1. **GLTFLoader 已移入 ES module**：`examples/jsm/loaders/GLTFLoader.js`，不是旧的 `examples/js/loaders/`（那路径 404，文件只有77字节错误页）
2. **importmap 必须精确映射**（不能用 `three/addons/` 通配，会解析错）：
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
3. **目录结构必须按官方相对路径**：GLTFLoader 内部 `import '../utils/BufferGeometryUtils.js'` → 放 `js/utils/BufferGeometryUtils.js`。BufferGeometryUtils 404 时模块静默失败，canvas 都不创建，且 console 无报错（难查！）
4. **draco decoder 要本地化**：`draco.setDecoderPath('./js/libs/draco/')`，下载 draco_decoder.js/wasm/wrapper 三个文件，别用 CDN（墙内不稳）
5. **模型加载后缩放居中**：Box3 算包围盒 → scale 适配 → 平移居中
6. 15MB 模型加载要等，loader 进度条用 xhr 回调更新

## 展示页设计（用户偏好）

- 深空背景：程序化星云 CanvasTexture + 数千星空粒子（Points）
- 多灯光：主光+轮廓光(蓝色)+点缀点光(红/蓝)，ACESFilmic tone mapping
- 交互：拖拽旋转（yaw/pitch 平滑插值）、滚轮缩放（球坐标）、自动巡航（松手自转）
- 触屏支持：单指旋转+双指缩放
- 全流程成本 ≈ ¥0.14（立绘）+ 混元免费额度

## 参考文件

- `scripts/hunyuan3d.py` — 提交+轮询+下载GLB的完整脚本（改 env 和 job_id 即可）
- `scripts/threejs_showcase_index.html` — 可复用的深空3D展示页模板（importmap 已配好）
