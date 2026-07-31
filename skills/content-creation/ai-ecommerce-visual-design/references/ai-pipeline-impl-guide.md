# AI爆款主图生成器 — 14步管线实现参考

> 本文件记录 `ai_pipeline/` 代码库的实际实现架构，供需要接管/扩展/复现该项目的后续会话使用。
> 代码位置：`~/Desktop/hermes/AI爆款主图生成器/ai_pipeline/`

## 目录结构

```
ai_pipeline/
├── __init__.py              # 包声明
├── config.py                # Settings dataclass（API Key/模型/尺寸/风格参数/违禁词库）
├── client.py                # BaiLianClient — 统一百炼API封装（真实+模拟双模式）
├── requirements.txt         # 依赖清单
├── run_pipeline.py          # 14步管线编排器 + CLI入口 argparse
│
├── analyzer/                # 分析模块
│   ├── product.py           # S1 产品分析（色彩/品类/价位带 → 视觉策略推荐）
│   ├── top100.py            # S2 TOP100范式拆解（LLM样本分析 / 真实图片批量分析）
│   ├── differentiation.py   # S3 差异化检测（CLIP向量距离 → LLM回退）
│   └── season.py            # S11 季节/节日检测（日历+规则引擎）
│
├── generator/               # 生成模块
│   ├── main_image.py        # S4 范式驱动主图生成（Prompt构建+生图）
│   ├── copywriting.py       # S5+S10 文案优化+差评攻击检测（3版文案+违禁词过滤）
│   ├── variant.py           # S8 变体生成（7种类型：颜色/背景/构图/光线/文字/简化/丰富）
│   └── detail_page.py       # 详情页分镜规划 → 逐段出图
│
├── scorer/                  # 评分模块
│   ├── ctr.py               # S6 CTR评分（6维度LLM评审 + 排序）
│   └── heatmap.py           # S13 热力图预测（TranSalNet → 简化版 → 4x4网格分析）
│
├── adapter/                 # 适配模块
│   ├── mobile_preview.py    # S7 手机预览裁剪 + OpenCV文字可读性检测
│   ├── platform_resize.py   # 多平台尺寸（淘宝/京东/拼多多/抖音/小红书/微信/Amazon）
│   ├── crowd_styles.py      # S12 人群审美映射（6类人群 × 风格/色调/文字）
│   └── ab_test.py           # S14 A/B测试方案（pairwise/multi/champion三种策略）
│
├── tracker/
│   └── ctr_tracker.py       # S9 CTR跟踪（本地JSON存贮 + 趋势分析 + 最佳方案推荐）
│
├── preprocess/              # 预处理模块
│   ├── classifier.py        # 输入分类（URL / 本地路径 / 文本描述）
│   ├── background.py        # 去背景（RMBG → API → PIL 三级降级）
│   ├── lighting.py          # 调光（亮度/对比/饱和/色温/锐度 + 自动增强）
│   └── upscale.py           # 超分（Real-ESRGAN → PIL LANCZOS）
│
├── prompts/                 # Prompt模板（JSON格式）
│   ├── product_analysis.json
│   ├── top100_analysis.json
│   ├── copywriting.json
│   ├── ctr_score.json
│   ├── review_attack.json
│   └── detail_plan.json
│
└── comfyui/                 # ComfyUI工作流（JSON格式）
    ├── remove_bg.json       # RMBG 1.4 去背景
    ├── upscale.json         # Real-ESRGAN 超分（2x/4x可调）
    └── ip_adapter.json      # IP-Adapter 风格参考生图
```

## 核心架构模式

### 1. 双模式 Client（client.py）

BaiLianClient 自动检测 dashscope SDK 是否安装。安装则走真实API调用；未安装则静默回退到 MockBaiLianClient 返回模拟数据。

```python
class BaiLianClient:
    def __init__(self):
        if _HAS_DASHSCOPE:
            self._impl = _RealBaiLianClient()
        else:
            self._impl = _MockBaiLianClient()  # 返回 mock 数据，测试用
```

Mock模式效果：无需API Key即可测试整条管线的逻辑流、错误处理、编排顺序。

### 2. 三级降级链

每个外部依赖模块实现至少2级降级：

| 模块 | 首选 | 次选 | 末选 |
|------|------|------|------|
| 差异化 | CLIP (torch+transformers) | LLM 分析 | 默认中值 |
| 去背景 | RMBG (rembg) | 百炼API图生图 | PIL颜色阈值 |
| 超分 | Real-ESRGAN | PIL LANCZOS | — |
| 热力图 | TranSalNet (torch) | 4x4网格饱和度分析 | — |

```python
# 降级模式示例 (background.py)
def remove(self, image_url, method="auto"):
    if method == "auto":
        method = self._auto_select_method()  # rembg → api → pil
    if method == "rembg":
        return self._remove_with_rembg(...)
    elif method == "api":
        return self._remove_with_api(...)
    else:
        return self._remove_with_pil(...)  # 保底
```

### 3. Dataclass I/O 契约

每个 public 方法返回一个 typed dataclass，包含 `success: bool` + `error: Optional[str]` 字段，不抛裸异常：

```python
@dataclass
class ProductAnalysisResult:
    dominant_colors: list[str]
    category: str
    price_tier: str
    style_recommendation: dict
    success: bool = True
    error: Optional[str] = None
```

### 4. 成本注释公约

每个模块底部有 `# 成本估算` 注释：

```python
# ── 成本估算 ──────────────────────────────────────────
# 每次 analyze 调用: ~¥0.01 (2K tokens)
```

### 5. 14步管线编排（run_pipeline.py）

PipelineRunner 类管理：
- **串行依赖链**：S0→S1→S2→S3→(S4∥S5)→S6→(S7∥S14)，S2/S11/S12 不阻塞主流程
- **步骤可配置**：`enable_steps` 列表控制运行哪些步骤，支持 `--steps S1 S2 S4 S6`
- **进度回调**：`set_progress_callback(fn)` 接收 `{step_id, step_name, status, total_steps, completed}`
- **错误隔离**：单步失败不阻塞后续步骤，PipelineResult 记录失败信息
- **报告生成**：`save_report()` 输出 JSON 报告到 output_dir

CLI 用法：
```bash
python -m ai_pipeline.run_pipeline \
  --input "保湿面霜" \
  --category "护肤品" \
  --price 128 \
  --platform taobao \
  --steps S1 S2 S4 S5 S6 S14

# 只看指定步骤
python -m ai_pipeline.run_pipeline \
  --input "product.jpg" \
  --steps S1 S2 S4 S6
```

## Prompt 模板系统

JSON 格式模板位于 `prompts/`，包含元数据供程序化加载：

```json
{
  "name": "product_analysis",
  "model": "qwen3.6-flash",
  "system_prompt": "...",
  "user_prompt_template": "产品图片: {product_image_url}",
  "parameters": {"temperature": 0.3, "max_tokens": 1024},
  "output_format": "json"
}
```

加载方式：
```python
from ai_pipeline.prompts import load_prompt, list_prompts
template = load_prompt("product_analysis")
# template["system_prompt"], template["parameters"]["temperature"]
```

## ComfyUI 工作流

JSON 描述格式位于 `comfyui/`，包含节点定义、模型依赖、变体说明：

```json
{
  "name": "remove_bg",
  "models_required": ["briaai/RMBG-1.4"],
  "nodes": [{"id": 1, "type": "LoadImage", ...}],
  "notes": ["输入: 任意产品图片", "前置: 需安装 ComfyUI-RMBG 插件"]
}
```

## 执行验证结果

- **40个 Python 文件**全部通过 `py_compile` 语法校验
- **9个 JSON 文件**全部通过 `json.load` 格式验证
- 依赖 numpy 已预装（macOS venv 中 numpy 2.4.6）

## 已知限制

| 限制 | 说明 | 建议 |
|------|------|------|
| dashscope SDK 未安装 | `pip install dashscope` 安装后可启用真实API | 安装后 client 自动切换真实模式 |
| torch/transformers 未安装 | CLIP 差异化检测走 LLM 回退 | 仅在需要 CLIP 时安装（大依赖 ~2GB） |
| rembg 未安装 | 去背景走 API 或 PIL 降级 | `pip install rembg` 需 onnxruntime |
| OPENCV 可选 | 仅 mobile_preview 和 heatmap 需要 | `pip install opencv-python` |
| mock 模式不生成真实图片 | 返回 `mock://generated/0.png` 占位符 | 设 DASHSCOPE_API_KEY 后自动切换 |
