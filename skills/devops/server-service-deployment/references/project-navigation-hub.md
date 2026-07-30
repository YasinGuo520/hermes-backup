# 项目导航中心（Hub）模式

**触发场景：** 服务器上多个Web项目，需要统一入口方便查看和跳转。用户说"集合到一个网页"、"重新设计"、"全部项目展示上去"。

## 架构模式

```
hermes-hub/
├── build_hub.py     ← 生成脚本（编辑 PROJECTS 列表即可扩展）
└── index.html       ← 生成的静态导航页面（http.server 托管）
```

## 核心实现

### 1. 项目列表配置

`PROJECTS` 列表每行一个项目，含端口、名称、图标、描述、颜色、类型和可选URL覆盖：

```python
PROJECTS = [
    {"cat":"🌐 页面","port":8900,"name":"方法论工具箱","icon":"🧰","desc":"130工具·7大类","color":"#6c5ce7"},
    # 使用 url 字段覆盖默认的 IP:PORT 跳转（如域名）
    {"cat":"⚙️ 服务","port":8001,"name":"中年人生诊断","icon":"🩺","desc":"midage.icu",
     "color":"#f59e0b","url":"http://midage.icu"},
]
```

按 `cat` 字段分组展示（🌐 页面 / 🆕 新项目 / ⚙️ 服务），每类独立section。

### 2. 实时状态检测

```python
PORT_KEYS = [8000, 8001, 8894, ...]  # 所有端口统一管理

def port_alive(port, timeout=2):
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{port}/")
        urllib.request.urlopen(req, timeout=timeout)
        return True
    except urllib.error.HTTPError as e:
        # 307 重定向也算在线（FastAPI RedirectResponse）
        return e.code in (301, 302, 303, 307, 308)
    except:
        return False

def check_ports():
    return {p: port_alive(p) for p in PORT_KEYS}
```

**关键坑：** FastAPI `RedirectResponse` 返回 307，`urlopen` 默认不跟随跳转会抛 HTTPError。
**坑2：** 用列表 `PORT_KEYS` 统一管理，不要在 `check_ports()` 里硬编码。

### 3. 设计要点（基础版 → 炫酷版）

| 要素 | 基础版 | 炫酷版 |
|:----|:-------|:-------|
| 背景 | 纯暗色 + 径向渐变 | **极光(Aurora)** 三层流动渐变 + 80粒子连线系统 |
| 标题 | 静态渐变文字 | **渐变动画** 4s 无限循环 `background-position` 偏移 |
| 卡片 | 左侧光条 | 左侧霓虹辉光 + 背景色渲染 |
| 状态灯 | 纯色圆点 | **脉冲呼吸灯** `@keyframes pulse` |
| 入场 | 无 | 卡片依次错开40ms，`fadeIn` 动画 |
| 悬停 | 右移 + 光条亮 | 上移2px + shadow扩散32px |
| 统计 | 文字数字 | 各状态不同渐变色数字 |

**关键CSS技巧：**
- 渐变动画：`background-size: 200% 200%` + `animation: gradientShift 4s ease infinite`
- 极光：`createRadialGradient` 多层Canvas绘制，`requestAnimationFrame` 驱动漂移
- 卡片入场：`animation: fadeIn 0.5s ease backwards` + `nth-child` 错开延迟
- 呼吸灯：`@keyframes pulse { 50% { opacity: 0.5 } }`
- `color-mix(in srgb, var(--accent) X%, ...)` 动态生成半透明色。⚠️ 老浏览器不支持，备选用硬编码

### 4. 部署方式

```bash
python3 build_hub.py
# HTTP服务（background=true）
cd ~/Desktop/hermes/hermes-hub && python3 -m http.server 8895 --bind 0.0.0.0
```

### 5. 日常维护

```python
# 加新项目 → build_hub.py 的 PROJECTS 列表加一行
# 删项目 → 从 PROJECTS 移除对应行
# 更新页面 → python3 build_hub.py（http.server 自动刷新文件）
# 端口变更 → 改 port 值 + 同步 PORT_KEYS + 重启 http.server
```

### 6. 并行创建多个HTML项目（delegate_task 批量构建）

**场景：** 用户说"上面提到的全部搞出来" — 一次性创建8个HTML项目。

```python
# 每批最多3个任务并行
delegate_task(tasks=[
    {"goal": "创建A项目HTML...",
     "context": "端口8913, 存 ~/Desktop/hermes/project-a/, 启动服务器"},
    {"goal": "创建B项目HTML...",
     "context": "端口8914, 存 ~/Desktop/hermes/project-b/, 启动服务器"},
    {"goal": "创建C项目HTML...",
     "context": "端口8915, 存 ~/Desktop/hermes/project-c/, 启动服务器"},
])
```

**最佳实践：**
- 每批3个项目并行，分多批执行
- 每个子Agent上下文必须注明：**目录路径、端口号、启动命令（background=true）**
- 子Agent自动完成HTML创建 + HTTP server启动
- 主流程只需最后更新hub的PROJECTS列表
- 最后统一 `for p in PORTS; do lsof -ti:$p; done` 检查所有端口
- 子Agent可能卡住或失败，主流程准备好兜底直接写

### 7. Python f-string + JavaScript 模板字面量冲突

**错误：** 在 Python f-string 中嵌入 JS `${...}` 模板字面量会冲突。

```python
# ❌ Python 会试图解析 ${[108,92,231][i]}
grad.addColorStop(0,`rgba(${[108,92,231][i]},0.04)`);

# ✅ 用字符串拼接代替模板字面量
const c=['108,92,231','92,167,130','167,139,250'][i];
grad.addColorStop(0,'rgba('+c+',0.04)');
```

**修复方法：**
1. 字符串拼接代替模板字面量
2. 或将复杂JS逻辑从f-string中提取出来，f-string只生成数据

### 8. 有域名时覆盖默认URL

```python
{"port": 8001, "url": "http://midage.icu", ...}
```

卡片生成：`href = p.get("url", f"http://43.138.221.174:{p['port']}")`

### 9. 为不同项目分配独特视觉风格（多皮肤系统）

**场景：** 用户说"全部升级一轮"、"每个项目不同风格" — 给N个HTML项目换不同的皮肤。

**方法：** 每次 delegate_task 时在 context 里注明视觉风格要求。见下表：

| 风格名称 | 背景动效 | 主色调 | 适合场景 |
|----------|---------|--------|---------|
| 赛博朋克HUD | 动态网格+扫描线+霓虹光柱 | 暗紫#0a0015 + 青#00f0ff + 粉#ff00aa | 数据大屏、选品看板 |
| 华尔街暗金 | 金色数字流雨 | 深黑#050505 + 金#d4a84b + 绿#00c853 | K线、交易面板 |
| 黑客帝国 | 矩阵代码雨(片假名+数字) | 黑#000000 + 绿#00ff41 | 终端、服务器状态 |
| 神秘玄学 | 烟雾粒子+烛光闪烁 | 暗红#0a0005 + 古金#c9a84c | 抽签、占卜 |
| 复古CRT | CRT雪花噪点+扫描线 | 深蓝#0a0a1a + 像素绿#33ff33 | 像素展厅、游戏 |
| 彩虹卡通 | 彩色泡泡升起破裂 | 彩虹HSL梯度 + 白 | 儿童游戏 |
| 北欧杂志 | 淡色粒子缓慢漂移 | 白底#f5f5f0 + 紫#6c5ce7 | 案例墙、文章 |
| 科技工具 | PCB电路板路径网格 | 深蓝#0a0e1a + 青#00d4ff | 工具箱、后台 |
| 极简名片 | 香槟气泡上升 | 白底#f8f8f8 + 金#c9a84c | 简历、个人页 |

**批量执行流程：**
1. 分3批 delegate_task，每批3个，每批设不同端口和风格
2. 子Agent创建HTML + 启动HTTP server（background=true）
3. 全部完成后：kill所有旧端口 → 重新start所有端口
4. 更新 build_hub.py 的 PROJECTS + PORT_KEYS
5. 重建hub页面

## 常见坑

### 端口冲突（重启服务时 Address already in use）

**现象：** `python3 -m http.server PORT --bind 0.0.0.0` 报 `OSError: [Errno 98]`

**原因：** 旧进程没杀干净。

**根治：**
```bash
kill $(lsof -ti:PORT) 2>/dev/null; sleep 1
# 确认空了再启
cd /path && python3 -m http.server PORT --bind 0.0.0.0
```

**批量重启所有项目（换皮后）：**
停干净再逐个起，不要停一个启一个。用 `for p in PORTS; do kill $(lsof -ti:$p) 2>/dev/null; done` 一次清完。

### 子Agent写大HTML可能卡住

**现象：** delegate_task 派出的子Agent在写 >20KB 的HTML文件（含Canvas动画/图表）时可能超时不返回。

**处理：** 主流程等2分钟没回就手动接管，直接 write_file 创建 + 启动 server。

### 硬件 Canvas 动画性能

移动端或低配VPS：粒子数控制在40以下，不用100。Canvas动画至少设一个 `requestAnimationFrame` 循环，不要用 `setInterval` 做动画帧。

### 用户缓存问题

改完HTML后用户说"没变化" → 浏览器缓存了旧文件。加 `?t=timestamp` 参数或 `?v=N` 强制刷新。
