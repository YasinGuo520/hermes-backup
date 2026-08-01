---
name: hunyuan-3d-image-to-model
description: 腾讯混元3D图生3D全流程——AI立绘→GLB模型→Three.js网页展示。
---

# 腾讯混元3D 图生3D流水线

把2D立绘变成真3D模型（GLB）并放到网页展示。墙内可用（Tripo/Meshy全被墙，只有腾讯混元3D API通）。

## 全流程

```
AI立绘（Qwen-Image ¥0.14/张）→ 混元3D图生3D（免费额度）→ OBJ zip → obj2gltf转GLB → Three.js网页
```

## 前置条件

- 腾讯云 SecretId/SecretKey（**AKID开头那套签名认证**，sk-开头的key无效！）
- 开通服务：https://cloud.tencent.com/product/ai3d
- **必须手动领取免费额度**：控制台 https://console.cloud.tencent.com/ai3d → 免费额度/资源包管理。不领就报 `ResourceInsufficient 资源不足`
- 子账户需授权 `QcloudAIA3DFullAccess`

## 环境

- venv: `~/Desktop/hermes/mecha3d/venv`（tencentcloud-sdk-python）
- 密钥: `~/Desktop/hermes/mecha3d/.env`（TENCENT_SECRET_ID / TENCENT_SECRET_KEY，chmod 600）
- pip 用阿里源：`--index-url https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com`（pypi.org 和腾讯云镜像都超时）
- npm 用淘宝源：`--registry=https://registry.npmmirror.com`

## 调用（SDK v20250513）

**坑：模块是 `ai3d.v20250513`，不是 v20241218！** 方法列表见 venv 里 `Ai3dClient` 的 dir。

```python
from tencentcloud.ai3d.v20250513 import ai3d_client, models
# 提交：SubmitHunyuanTo3DRapidJob（参数 ImageUrl，需公网可访问URL）
# 轮询：QueryHunyuanTo3DRapidJob（参数 JobId）→ Status: WAIT/RUN/DONE/FAIL
```

- 提交成功返回 JobId
- DONE 后 `ResultFile3Ds[].Url` 是 **OBJ zip 压缩包**（Type=OBJ），不是直接GLB
- 立绘上传：图片放已开放端口目录（如 pixel-gallery 8915），`http://43.138.221.174:8915/xxx.png` 公网可达
- 完整脚本：`~/Desktop/hermes/mecha3d/hunyuan3d.py`（提交+轮询+下载）

### 轮询与下载的坑（2026-08实测）

- ⚠️ **长轮询循环会 Connection reset**：后台脚本连续 `QueryHunyuanTo3DRapidJob`（每15s）实测报 `ClientNetworkError ConnectionResetError(104)` 反复挂。**改成单次查询+间隔重试**（每次新建请求、sleep 5-15s、重试3次）反而稳定成功。轮询代码要 catch ConnectionReset 后继续，别让循环中断。
- ⚠️ **签名下载URL含 `&` 会被 shell 截断**：COS 签名 URL 长串带 `&q-sign-*`，用 `curl -sL "$URL"`（shell 展开）会截断 → 下载到几百字节的假 zip（`unzip` 报 End-of-central-directory not found）。**必须用 Python `subprocess.run(['curl','-sL','-o',out,url], check=True)` 传列表参数**（不经 shell），或在 Python 里直接拿响应 dict 的 `Url` 字段再下载。
- DONE 响应 `ResultFile3Ds` 可能含多条（OBJ zip + 预览图），按 `Type == 'OBJ'` 取。

## OBJ → GLB

```bash
unzip -o model_raw.zip -d model_raw/
npx --yes obj2gltf -i model_raw/xxx.obj -o web/model.glb --binary --unlit
```

## Three.js 墙内加载（关键坑）

**不能依赖 CDN**（Google被墙，jsdelivr部分可用但别赌）。全部本地化：

1. 下载到 `web/js/`：
   - `three.module.js`（r160，1.27MB，jsdelivr: `three@0.160.0/build/three.module.js`）
   - `loaders/GLTFLoader.js`（`examples/jsm/loaders/`，不是examples/js/！）
   - `loaders/DRACOLoader.js`
   - `utils/BufferGeometryUtils.js`（GLTFLoader内部import，缺了报404静默失败）
   - `libs/draco/` 三个文件（decoder）
2. **importmap 必须精确到文件**，不能用 `three/addons/` 通配：
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
3. `draco.setDecoderPath('./js/libs/draco/')` 用相对路径
4. 15MB GLB 加载约 8-10 秒，loader 要有进度显示

## 网页模板

`~/Desktop/hermes/mecha3d/web/index.html`：
- 深空背景：CanvasTexture程序化星云 + 4500粒子星空
- 灯光：环境光 + 主光(暖) + 轮廓光(蓝) + 红色点缀光
- 交互：拖拽旋转(球坐标平滑插值) + 滚轮缩放 + 自动巡航 + 触屏双指
- 模型：GLTFLoader加载，Box3算缩放居中，悬浮微动动画
- 部署：`cd web && python3 -m http.server 8931 --bind 0.0.0.0`（公网直通）

## 验证

```bash
curl -s http://127.0.0.1:8931/model.glb -o /dev/null -w "%{http_code}"  # 200
# GLB头检查
python3 -c "print(open('model.glb','rb').read(4))"  # b'glTF'
# 浏览器实测：browser_console 查 canvas 存在 + loader 隐藏 + 模型100%
```

## 成本

- 立绘 ¥0.14/张（Qwen-Image）
- 混元3D 免费额度（够几十个模型）
- 总计 ≈ ¥0

## 参考

- 工作目录：`~/Desktop/hermes/mecha3d/`（hunyuan3d.py / web/ / images/）
- 上线案例：http://43.138.221.174:8931/（机甲指挥官，已挂导航Hub 8895）
