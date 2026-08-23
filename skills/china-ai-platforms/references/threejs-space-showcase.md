# Three.js 太空展示舱页面要点（r160，实测可用）

完整可用页面实例：`~/Desktop/hermes/mecha3d/web/index.html`（机甲指挥官·太空展示舱，8931端口）。

## 目录结构（本地化，不依赖任何 CDN）

```
web/
├── index.html
├── model.glb              # obj2gltf 转换后的模型
└── js/
    ├── three.module.js
    ├── loaders/GLTFLoader.js
    ├── loaders/DRACOLoader.js
    ├── utils/BufferGeometryUtils.js
    └── libs/draco/ (draco_decoder.js / draco_wasm_wrapper.js / draco_decoder.wasm)
```

下载源（墙内可达）：`https://cdn.jsdelivr.net/npm/three@0.160.0/...`

## importmap（必须精确到文件，通配会静默失败）

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

## 场景构成

| 元素 | 实现 |
|------|------|
| 背景 | CanvasTexture 程序化星云（径向渐变+随机紫/粉斑块） |
| 星空 | Points 4500 粒子，球面分布，三色（蓝/暖白/纯白） |
| 灯光 | Ambient 0.5 + Directional 主光(2.2,带阴影) + Directional 轮廓光(1.6) + 2×PointLight 点缀 |
| 渲染 | ACESFilmicToneMapping, exposure 1.15, shadowMap PCFSoft |
| 模型 | GLTFLoader + DRACOLoader，Box3 计算 scale=3.2/max轴，居中 |

## 相机控制（球坐标，平滑阻尼）

- 拖拽：pointerdown/move/up → targetYaw/targetPitch（pitch 限 ±1.2），`lerp(controls.x, target, 0.08)`
- 滚轮/双指：targetDistance（3~12），同样平滑
- 自动巡航：非拖拽时 `targetYaw += 0.0025 * dt * 60`（约 0.15rad/s 慢转）
- 悬浮微动：模型 y 轴 `sin(t*1.2)*0.12`，rotation.y `sin(t*0.4)*0.06`

## HUD

- 标题：gradient text（红橙→蓝紫）+ drop-shadow 呼吸动画
- 底部提示：拖拽旋转/滚轮缩放/自动巡航
- 加载器：旋转 ring + 进度文字（onProgress 更新百分比），onLoad 后 `.hide`

## 验证清单

1. 所有 js 文件大小正常（three.module ~1.2MB；GLTFLoader ~108KB；BufferGeometryUtils ~31KB；DRACOLoader ~13KB）
2. 浏览器 console 无报错，canvas 出现
3. performance entries 里能看到 model.glb 被请求（没请求 = 模块层挂了）
4. browser_vision 确认模型完整、无破面、背景粒子可见
