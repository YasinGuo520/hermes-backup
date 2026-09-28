# Kronos CPU部署避坑指南

验证时间：2026-07-25
模型：Kronos-small (24.7M参数)
环境：腾讯云轻量服务器 (无NVIDIA驱动，PyTorch 2.13)

## 完整安装步骤

```bash
# 1. 安装依赖
pip install kronos-model-arch baostock

# 2. PyPI包代码不完整，需要额外克隆GitHub源码
cd ~/Desktop/hermes
git clone https://gitclone.com/github.com/shiyu-coder/Kronos.git kronos-repo

# 3. 模型加载（Python）
import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'   # 国内镜像，必须在import前设置
import sys
sys.path.insert(0, '/path/to/kronos-repo')
sys.path.insert(0, '/path/to/kronos-repo/model')
from model.kronos import KronosTokenizer, Kronos, KronosPredictor

t = KronosTokenizer.from_pretrained('NeoQuasar/Kronos-Tokenizer-base')
m = Kronos.from_pretrained('NeoQuasar/Kronos-small')
m.eval()
p = KronosPredictor(m, t, device='cpu', max_context=512)  # 关键: device='cpu'要显式传
```

## 已知坑

### 坑1：KronosPredictor CUDA崩溃
**症状：** `RuntimeError: Found no NVIDIA driver on your system`
**原因：** `__init__` 中 `torch.cuda.is_available()` 在部分PyTorch版本(2.13+)直接崩溃（非返回False）
**修复：** 显式传 `device='cpu'`
- ✅ 正确：`KronosPredictor(m, t, device='cpu', max_context=512)`
- ❌ 错误：`KronosPredictor(m, t, 512, device='cpu')` — 512位置参数被当作device

### 坑2：HuggingFace模型下载慢
**修复：** `export HF_ENDPOINT=https://hf-mirror.com`

### 坑3：GitHub克隆慢
**替代源：** `https://gitclone.com/github.com/shiyu-coder/Kronos.git`

### 坑4：PyPI包代码不全
**症状：** `from model.kronos import ...` 提示找不到
**原因：** PyPI包只打包了部分文件
**修复：** 从GitHub克隆，把repo/model加入sys.path

## CPU推理性能

| 模型 | 参数 | 20步预测耗时 | 适用 |
|:----|:---:|:-----------:|:----|
| Kronos-mini | 4.1M | ~0.5s | 批量扫描(300只≈2.5分) |
| Kronos-small | 24.7M | ~2.5s | 精选(30只≈1.5分) |
| Kronos-base | 102.3M | ~10s | 单股深度(CPU略慢) |

## 单股预测示例

```python
pred = p.predict(
    df=df[['open','high','low','close','volume','amount']].iloc[n-lb:n-20],
    x_timestamp=pd.Series(pd.to_datetime(df['date'].iloc[n-lb:n-20])),
    y_timestamp=pd.Series(pd.to_datetime(df['date'].iloc[n-20:n])),
    pred_len=20, T=1.0, top_p=0.9, sample_count=1, verbose=False
)
# 方向判断
pred_dir = 1 if pred['close'].iloc[-1] > df['close'].iloc[n-21] else 0
```

## 验证脚本

`~/Desktop/hermes/validate/` 目录下：
- `test_kronos.py` — 加载测试
- `final_test2.py` — 方向预测测试（5只大盘股，已验证100%准确）
- `validate_quick.py` — 传统因子RankIC基线（含方向反转）

## Kronos在A股上的实测结论（2026-07-25）

| 指标 | 数值 | 含义 |
|:----|:----:|:-----|
| 方向准确率 | 100%(5/5) | 样本太小，需继续验证 |
| CPU耗时/只 | ~2.5s | 70只≈3分钟，可接受 |
| 与传统因子互补性 | 高 | 因子看均值回归，Kronos看形态趋势 |
