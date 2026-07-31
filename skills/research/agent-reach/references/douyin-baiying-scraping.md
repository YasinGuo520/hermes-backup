# 抖音百应工作台 — 精选联盟商品数据采集

## 场景
用户是抖音达人（精选联盟分销），需要从百应工作台获取**爆款榜**实时商品数据（销量、价格、佣金率）用于选品。

## 方法对比

| 方式 | 可行性 | 说明 |
|------|--------|------|
| web_search + web_extract | ❌ | 抖音反爬极强，直接访问跳验证码 |
| Playwright 独立浏览器 | ⚠️ | 需用户手动扫码登录（不继承 Safari/Chrome 会话） |
| computer_use (cua-driver) | ✅ | 操作用户已登录的 Safari，可读取完整数据 |

## computer_use 工作流程

### 1. 前提
- 用户已登录百应工作台（Safari 浏览器）
- cua-driver 正常运行（若截图为空 → `killall cua-driver` 重启）

### 2. 核心步骤

```
1. focus_app(name='Safari') + raise_window=true  // 将 Safari 带到前台
2. capture(app='Safari', mode='som')              // 获取页面元素索引
3. 点击导航到 选品中心 → 联盟榜单 → 爆款榜
   - 侧边栏"联盟榜单"通常是 AXMenuItem，可通过 label 搜索索引
   - 爆款榜 tab 是 AXRadioButton
4. 可交互元素类型限制：
   - ✅ AXButton / AXMenuItem / AXRadioButton / AXLink — 可直接 AXPress
   - ❌ AXImage (自定义下拉箭头) — 不支持 AXPress，需用 coordinate 点击
   - ❌ AXStaticText (筛选标签) — 不支持 AXPress
```

### 3. 数据提取方式

**方式 A — SOM 树提取（推荐）**
```
1. capture(app='Safari', mode='som', max_elements=300)
2. 从返回的 elements 数组中解析：
   - AXStaticText 标签含商品标题（长度 > 10，含中文）
   - 附近的 AXStaticText 标签含店铺名（含"店"、"旗舰"）
   - AXStaticText 含 "%" 为佣金率
   - 价格和销量数据在 AXCells 内
3. 用 bounds 判断元素的 Y 坐标来关联同一行的商品
```

**方式 B — vision 视觉读取**
```
1. capture(app='Safari', mode='vision')
2. 从 vision_analysis 描述中读取可见商品数据
3. 滚动后重复
```

**方式 C — 控制台 JavaScript（最直接）**
```
// 理论上可在 Safari Web Inspector 控制台运行：
// Cmd+Option+I 打开检查器 → Console → 运行 JS 提取表格数据
// 但 computer_use 操作 JS 控制台不稳定，不推荐作为主要手段
```

### 4. 筛选条件设置（坑点记录）

百应工作台的筛选控件（售价区间、佣金率、体验分）是 **自定义 UI 控件**：
- 下拉箭头是 AXImage（不支持 AXPress）
- 标签文本是 AXStaticText（不支持 AXPress）
- **解决方案**：获取 AXImage 的 bounds，用 coordinate=[center_x, center_y] 点击

示例：
```python
# 售价区间标签 bounds=[368, 405, 56, 20]
# 下拉箭头 image bounds=[492, 407, 16, 16]
# 点击箭头中心：
computer_use(action='click', coordinate=[500, 415])
```

### 5. 通用数据字段映射

| 页面字段 | 描述 | 提取方式 |
|----------|------|----------|
| 排名 | 数字 1, 2, 3... | AXStaticText 纯数字 |
| 商品信息 | 标题（较长中文文本） | AXStaticText 含中文 >10字 |
| 店铺名称 | 店铺名 | AXStaticText 含"店"/"旗舰" |
| 近2小时热销 | 销量数字 + "万" | AXStaticText 含数字+万 |
| 佣金/% | 如 "34% 赚¥13.57" | AXStaticText 含 % |
| 加选品车 | 操作按钮 | AXButton 含"加选品车" |

### 6. Excel 输出规范

```python
OUTPUT_DIR = Path.home() / "Desktop" / "hermes"  # 统一输出目录
OUTPUT_FILE = OUTPUT_DIR / f"抖音爆款榜选品表_{date}.xlsx"
```

Excel 须包含：
- Sheet 1: 选品清单（排序：综合推荐指数降序）
  - 列：序号、商品名、售价、佣金率、佣金/单、近2h热销、店铺、品类、桌播适配、推荐指数、3秒钩子、备注
- Sheet 2: 选品策略（标准 + 收益测算 + 话术框架）
- 条件格式：高佣金(≥25%)绿色、中佣金(≥20%)黄色

### 7. Cron 自动化

```yaml
# 每日 7:00 自动生成选品表（无需登录，使用已有数据模板）
schedule: "0 7 * * *"
script: "daily_xuanyuan.py"  # 放在 ~/.hermes/scripts/
workdir: "/Users/<user>/Desktop/hermes"
no_agent: true  # 纯脚本模式，直接输出 stdout
```

⚠️ **关键**：cron 运行的脚本须在内部设置 PYTHONPATH（cron 不继承 shell 环境）：
```python
SITE_PACKAGES = '/usr/local/lib/python3.11/site-packages'
if SITE_PACKAGES not in sys.path:
    sys.path.insert(0, SITE_PACKAGES)
```

### 8. 已知问题

| 问题 | 表现 | 解决 |
|------|------|------|
| cua-driver 截图为空 | 0x0 capture | `killall cua-driver` 后重试 |
| Safari 无窗口但进程中 | focus_app 失败 | `open -a Safari` 打开新窗口 |
| Playwright 不继承登录态 | 百应显示登录页 | 需用户手动扫码，或改用 computer_use 操作已登录 Safari |
| 自定义 UI 控件不可点击 | AXPress 是 no-op | 改用 coordinate 坐标点击 |
