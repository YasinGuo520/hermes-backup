---
name: ai-3d-showcase
description: 2D立绘/产品图转真3D模型并做Three.js 3D展示网页。墙内用腾讯混元3D API。
category: creative
---

# AI 图生3D + Three.js 3D展示

把人物/产品立绘做成真3D模型，放3D网页（太空舱/展厅风格）360°展示。

## 何时使用

- 用户要求「把XX做成3D立体的」「3D网页展示」「图生3D」
- 已有2D立绘（AI生成的或用户提供的）想转真3D模型
- 注意区分：**真3D**（GLB模型可360°旋转看背面）vs **伪3D**（CSS视差倾斜，只能小角度）。用户说"真3D才行"时走本流程；说"视觉够炫"可以只做视差。

## 全流程

```
1. 生成立绘（硅基流动 Qwen-Image，见 siliconflow-image-gen skill）
   → 提示词要求：纯黑/纯色背景 + 全身完整 + 正面站立，方便图生3D识别
2. 腾讯混元3D API 图生3D（本文档核心）
   → 提交任务 → 轮询(10-20分钟) → 下载 OBJ zip
3. OBJ → GLB 转换（node obj2gltf）
4. Three.js 太空展示页（本地化依赖，importmap 精确映射）
5. 启动 http.server → 浏览器验证 → 挂导航Hub
```

## 工具选型（墙内实测）

| 工具 | 可用性 | 说明 |
|------|--------|------|
| 腾讯混元3D API | ✅ | ai3d.tencentcloudapi.com，需腾讯云密钥 |
| Tripo (tripo3d.ai) | ❌ 被墙 | 服务器连不上 (000) |
| Meshy | ❌ 被墙 | 同上 |
| 混元3D在线版 | ⚠️ 需登录 | 浏览器自动化可到登录页，但需扫码 |

**所以：墙内图生3D = 腾讯混元3D API，唯一通道。**

## 腾讯混元3D API 细节（踩坑实录）

### 开通与额度（最大坑）
- 密钥：腾讯云 API 密钥管理 https://console.cloud.tencent.com/cam/capi （SecretId AKID开头 + SecretKey）
- **开通服务 ≠ 有额度**：必须去 https://console.cloud.tencent.com/ai3d 控制台**手动领取免费积分**，否则报 `ResourceInsufficient 资源不足`
- sk- 开头的 key 不是腾讯云密钥格式（那是混元大模型LLM的key），图生3D只认 SecretId+SecretKey 签名认证
- 子账户 key 可用，需授权 `QcloudAIA3DFullAccess` 策略

### SDK
```bash
python3 -m venv venv
./venv/bin/pip install --index-url https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com tencentcloud-sdk-python
# pypi.org 直连会超时，必须用阿里云镜像
```
- **模块路径是 `tencentcloud.ai3d.v20250513`**（不是网上文档写的 v20241218，旧版本不存在）
- endpoint: `ai3d.tencentcloudapi.com`，region: `ap-guangzhou`

### 接口
| 接口 | 用途 |
|------|------|
| SubmitHunyuanTo3DRapidJob | 图生3D极速版，参数 ImageUrl |
| QueryHunyuanTo3DRapidJob | 轮询状态，Status: WAIT/RUN/DONE/FAIL |

- ImageUrl 必须是**公网可访问的URL**（用已有开放端口服务图片，如 8915）
- 查询接口偶发 `Connection reset by peer`——重试即可，任务没丢
- 极速版返回 `ResultFile3Ds`：**Type=OBJ 的 zip 包**（不是GLB）+ PreviewImageUrl

### 完整脚本
见 `scripts/hunyuan3d.py`（提交+轮询+下载一体），用法：
```bash
set -a && source .env && set +a   # .env: TENCENT_SECRET_ID / TENCENT_SECRET_KEY
./venv/bin/python hunyuan3d.py --image_url "http://IP:PORT/img.png" --out model_raw.zip
```

## OBJ → GLB 转换

极速版返回 OBJ 压缩包（obj + mtl + 4096纹理png），需转 GLB 给 Three.js：

```bash
cd ~/Desktop/hermes/<project>
npm install --registry=https://registry.npmmirror.com obj2gltf   # pypi同理，默认源超时
unzip model_raw.zip -d model_raw/
npx --yes obj2gltf -i model_raw/<hash>.obj -o web/model.glb --binary --unlit
# 验证: python3 -c "open('model.glb','rb').read(4)" == b'glTF'
```

## Three.js 网页（本地化依赖 + importmap 踩坑）

three@0.160 起 GLTFLoader 移到 ES module 版（examples/jsm/），且依赖链变复杂。**必须全部本地化下载**（jsdelivr CDN 可达，Google CDN 墙内不可用）：

```
web/
├── index.html
├── model.glb
└── js/
    ├── three.module.js          # build/three.module.js (1.27MB)
    ├── loaders/GLTFLoader.js    # examples/jsm/loaders/GLTFLoader.js
    ├── loaders/DRACOLoader.js   # examples/jsm/loaders/DRACOLoader.js
    ├── utils/BufferGeometryUtils.js  # examples/jsm/utils/BufferGeometryUtils.js (GLTFLoader依赖!)
    └── libs/draco/              # draco_decoder.js/.wasm + draco_wasm_wrapper.js
```

### importmap 必须精确映射（不能只映射目录前缀）
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
<script type="module">
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
```
- GLTFLoader.js 内部 `import { toTrianglesDrawMode } from '../utils/BufferGeometryUtils.js'` → 所以 utils/ 必须和 loaders/ 平级
- **DRACOLoader decoder 路径要指本地**：`draco.setDecoderPath('./js/libs/draco/')`，别指CDN
- 若只映射 `"three/addons/": "./js/"` 会让相对路径解析错误（这是本会话踩过的大坑）

### 排障信号
- canvas 没创建 + 无 JS 报错 → 模块加载失败，查 performance entries 里有没有 300字节的404文件（下载失败页）
- loader 一直 100% → 15MB 模型加载需要时间，等10秒再看
- 页面 200 但模型没请求 → importmap 映射错误

## 网页要点（太空展示舱风格）

- 深空背景：程序化 CanvasTexture 星云（radial gradient 紫色斑块）
- 星空粒子：THREE.Points 4500颗，三色（蓝/暖/白），sizeAttenuation
- 灯光：ambient + keyLight(暖) + rimLight(蓝) + 红蓝点光，ACESFilmicToneMapping
- 模型缩放：`Box3().setFromObject` 算 size，scale = 3.2/max(size)
- 交互：pointerdown/move 拖拽旋转（球坐标 yaw/pitch），wheel 缩放，触屏 pinch
- 自动巡航：未拖拽时 targetYaw 缓慢自增
- 加载动画：环形 loader + 百分比

## 交付检查清单

1. `browser_navigate` 打开本地页 → 等10s → `browser_console` 查 canvas 存在 + loader 隐藏
2. `browser_vision` 确认模型完整（无破面/残缺）、背景/灯光效果
3. 公网 curl 200（新端口可能被防火墙拦，用已验证开放的端口如8915服务图片/模型）
4. 挂导航Hub（build_hub.py PROJECTS 加一行）

## Pitfalls

1. **开通后必须手动领免费额度**，ResourceInsufficient 就是这个原因，不是key问题
2. **sk- key ≠ 腾讯云密钥**，别浪费时间测
3. **pip/npm 默认源超时**（腾讯云机器外网受限），pip用阿里云、npm用npmmirror
4. **极速版返回OBJ不是GLB**，需要 obj2gltf
5. **importmap 要精确到文件路径**，目录前缀映射会炸
6. 图生3D 对复杂机械细节会简化——"精细版"预期管理：视觉效果精致可达，建模细节不保真
7. 版权：擎天柱等角色有版权，做原创机甲/角色（红蓝配色致敬），商用才安全

## 关联技能

- `siliconflow-image-gen` — 生成立绘（本流程第1步）
- `html-project-hub` — 挂导航 + 保活
- `visual-component-patterns` — 前端视觉组件（玻璃卡片/粒子背景复用）
