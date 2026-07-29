# 插件扩展：自动件域（Auto Parts）

## 概述

当 AI 客服 SaaS 从服装类目扩展到汽车配件类目（如雨刮器），需要创建新的插件域。自动件域的核心需求是**车型匹配**——客户报车型+年份，系统返回配件规格（尺寸+卡扣类型+SKU）。

## 真实案例：雨刮器车型匹配插件（2502条Excel数据导入）

本参考记录了一次完整的插件域扩展实践：从用户发来的Excel表格，到可运行的车型匹配插件。

### 数据源特征

- 格式：Excel（每个品牌一个Sheet，90+品牌）
- 记录数：2502条
- 每条记录：品牌 | 【车型】年份范围 | SKU编码
- SKU编码格式：`{卡扣码}-{主驾尺寸}{副驾尺寸}` 或 `{卡扣码}-{主驾尺寸}{副驾尺寸}{后窗尺寸}`
  - 例：`U-2620` = U型卡扣，主驾26寸，副驾20寸
  - 例：`2-2828` = 2号卡扣，主驾28寸，副驾28寸
  - 例：`U-161414` = U型，主驾16寸，副驾14寸，后窗14寸

### 卡扣类型映射

```python
CONNECTOR_MAP = {
    'U': 'U型',        # 传统挂钩式，最通用
    '1': '1号卡扣',    # 常见燕尾/直插
    '2': '2号卡扣',    # 侧插/按扣式
    '3': '3号卡扣',    # 燕尾式
    'D': 'D型卡扣',    # 特定品牌专用
    'G': 'G型卡扣',    # 新型低风阻接口
    # ... (字母+数字组合的代码也保留原始代码显示)
}
```

## 数据库构建流程

### Step 1: 解析Excel生成JSON数据库

从Excel提取数据并构建搜索索引的核心流程：

```python
# 1. 解析SKU编码
def parse_sku(s):
    parts = s.split('-')
    conn_code = parts[0]                       # 卡扣类型代码
    conn = CONNECTOR_MAP.get(conn_code, f'{conn_code}型卡扣')
    sizes = parts[1]                            # 尺寸字符串
    driver = int(sizes[:2])                     # 主驾（前2位）
    passenger = int(sizes[2:4])                 # 副驾（3-4位）
    rear = int(sizes[4:6]) if len(sizes) >= 6 else None

# 2. 解析车型行: 【8代凯美瑞/凯美瑞双擎】2018-2023款
def parse_model(text):
    m = re.match(r'【(.+?)】\s*(.+?)?(?:款)?$', text)
    model_name = m.group(1)                     # "8代凯美瑞/凯美瑞双擎"
    year_text = m.group(2) or ''                # "2018-2023"

# 3. 提取年份范围
years = []
for mm in re.finditer(r'(\d{2,4})\s*(?:[-/]\s*(\d{2,4}))', year_text):
    y1, y2 = int(mm.group(1)), int(mm.group(2))
    # 处理两位缩写年份: 04 → 2004, 99 → 1999
    if y1 < 100: y1 += 2000 if y1 < 90 else 1900
    if y2 < 100: y2 += 2000 if y2 < 90 else 1900
    years.append((y1, y2))
```

### Step 2: 构建搜索关键词索引

**关键：** 添加各种车型名变体，确保用户模糊搜索能命中。

```python
def extract_keywords(model, brand):
    kws = [brand, model]

    # 按/分割子车型
    for sub in re.split(r'[/]', model):
        kws.append(sub.strip())

    # ⭐ 去掉代系前缀（核心技巧）
    # 处理 "第八代雅阁" → "雅阁"
    # 处理 "8代凯美瑞" → "凯美瑞"
    clean = re.sub(
        r'^((?:第)?[\d一二三四五六七八九十百]+)(?:代(?:半)?|代半)\s*', 
        '', model
    )
    kws.append(clean)

    # 去掉括号内容: "3系（旅行版）" → "3系"
    clean2 = re.sub(r'[（(][^)）]*[)）]', '', clean).strip()
    kws.append(clean2)

    # ⭐ 去连字符别名: "CR-V" → "CRV"（用户常省略连字符）
    for kw in list(kws):
        nw = kw.replace('-', '').replace(' ', '')
        if nw and nw not in kws: kws.append(nw)

    return kws
```

### Step 3: 持久化搜索索引

**关键：** 预构建搜索索引随JSON一起持久化，避免每次启动时重建（2500条目 × 每条3-5关键词 = 7500+次字符串操作）。

```python
_SEARCH_INDEX = {}
for idx, entry in enumerate(entries):
    for kw in entry['search_keywords']:
        kw_l = kw.lower().strip()
        if len(kw_l) >= 2:
            if kw_l not in _SEARCH_INDEX:
                _SEARCH_INDEX[kw_l] = []
            _SEARCH_INDEX[kw_l].append(idx)

# 存到JSON数据库文件中
json.dump({'entries': entries, 'search_index': _SEARCH_INDEX, ...}, f)

# 插件加载时直接读取
_SEARCH_INDEX = WIPER_DATA["search_index"]  # 不用重建
```

## 匹配算法

### 核心逻辑

```python
def find_wiper(message):
    # 1. 遍历搜索索引，找到所有匹配的entry
    for keyword, indices in _SEARCH_INDEX.items():
        if len(keyword) >= 2 and keyword in msg_lower:
            for idx in indices:
                matched_indices.add(idx)

    # 2. 对每个匹配entry打分
    for idx in matched_indices:
        score = 0

        # 年份匹配（权重最高！）
        year_matched = year_in_range(years_in_msg, entry["years"])
        if year_matched:    score += 500
        elif years_in_msg:  score -= 50  # 有年份但没匹配，降权

        # 模型名精确匹配
        if entry["model"].lower() in msg_lower: score += 100

        # 品牌匹配
        if entry["brand"] in matched_brands: score += 50

        # 关键词命中数
        score += kw_count * 10

    # 3. 排序去重，取Top5
    scored.sort(key=lambda x: -x[0])
    return scored[:5]
```

### 年份提取（客户输入容错）

```python
def _extract_year(text):
    years = []
    # 完整年份: 2018, 2022
    for m in re.finditer(r'(?:19|20)\d{2}', text):
        years.append(int(m.group()))
    # 两位年份+款/年: "12款"→2012, "10年"→2010
    for m in re.finditer(r'(\d{2})\s*(?:款|年)', text):
        y = int(m.group(1))
        years.append(2000 + y if y < 90 else 1900 + y)
    return years
```

### 单字车型守卫（关键坑）

单字车型名如"V"（哪吒V）、"S"（哪吒S）、"Z"（林肯Z）极易被误匹配：

| 用户输入 | 含字符 | 容易误配 | 原因 |
|---------|-------|---------|------|
| "CRV" | v | 哪吒V | "v"是"crv"的子串 |
| "CR-V" → "CR V" | v独立词 | 哪吒V | normalize后空格分词 |

**解决方案：** 单字车型必须同时匹配品牌前缀：

```python
if len(keyword) <= 1:
    brand_name = entry['brand'][:2].lower()  # 取品牌名前2字
    if keyword not in words or brand_name not in msg_lower:
        continue  # 品牌没提，不匹配单字
```

### 排序策略：年份优先

```python
# 权重分配（经验值）
year_match:     +500    # 年份匹配是最高优先级
model_exact:    +100    # 完整车型名匹配
brand_match:    +50     # 品牌匹配
keyword_per:    +10     # 每个关键词命中
year_mismatch:  -50     # 有年份但没对上(降权)
```

**为什么这么配：** 同款车不同年份可能用完全不同尺寸和卡扣。如凯美瑞2018款(8代，U-2620) vs 凯美瑞2024款(9代，1-2620)。年份权重必须压倒纯关键词匹配。

## 自动打包备注（wiper_pick）——关键工作流

当雨刮匹配成功后，系统需要自动写入一条**打包备注**，让仓库人员知道该拿什么货。

### 在聊天中实时写入

在 `chat.py` 中，插件处理完消息后、返回回复前，插入打包备注：

```python
# 雨刮器匹配结果自动写备注
for pr in plugin_results:
    if pr.get("type") == "wiper_match" and pr.get("matches"):
        for m in pr["matches"]:
            content = f"【雨刮打包】{m['brand']} {m['model']}"
            if m.get("year"):
                content += f" ({m['year']})"
            content += f" | 主驾{m['driver_size']}寸"
            if m.get("passenger_size"):
                content += f" 副驾{m['passenger_size']}寸"
            if m.get("rear_size"):
                content += f" 后窗{m['rear_size']}寸"
            content += f" | {m['connector']} | SKU: {m['sku']}"
            db.add(CustomerNote(
                tenant_id=tenant_id, platform=req.platform,
                note_type="wiper_pick",  # 专门类型，看板可筛选
                note_content=content, status="pending",
            ))
        db.commit()
        break
```

### 通过Webhook异步触发（零LLM成本）

当电商平台（抖店/拼多多）推送订单备注时，webhook 直接匹配并写备注：

```python
@router.post("/webhook/order-remark")
def order_remark_webhook(req: OrderRemark, db: Session):
    # 1. 写客户备注
    note = CustomerNote(tenant_id=1, note_content=req.remark, ...)
    db.add(note)
    db.flush()

    # 2. 跑雨刮匹配（纯本地，零API调用）
    wipered = _create_wiper_pick_notes(tenant_id, note, db)
    # → 这步完全不需要LLM
```

**优势：** SDK匹配走本地JSON数据库（2500条内存加载），比调LLM快100倍、零费用。

### 批量处理历史积压备注

```python
@router.post("/api/notes/process-wiper")
def process_wiper_notes(payload, db):
    notes = db.query(CustomerNote).filter(
        status="pending", note_type != "wiper_pick"
    ).all()
    for note in notes:
        result = plugin.process_message(note.note_content, context)
        if result and result.get("matches"):
            # 创建 wiper_pick 备注
            ...
        note.status = "done"  # 标记已处理
```

## 品牌别名与错别字处理

用户在输入车型时经常出现错别字/简称，需要品牌别名映射：

```python
_BRAND_ALIAS = {
    # 常见品牌简称
    "bmw": "宝马", "benz": "奔驰", "vw": "大众",
    "byd": "比亚迪", "haval": "哈弗",
    # ⭐ 常见错别字（必须处理）
    "哈佛": "哈弗",  # 用户常把"哈弗"写成"哈佛"
    "volkswagen": "大众",
}
```

### 跨品牌过滤（防误配）

当用户明确说了品牌（如"哈弗H6"），必须过滤掉其他品牌的同名车型（如"红旗H6"）：

```python
for score, key, entry in scored:
    # 如果有明确品牌，只返回该品牌的匹配
    if matched_brands and entry["brand"] not in matched_brands:
        continue
    results.append(entry)
```

## 编译时易错点：write_file中的正则转义

**关键坑：** 在 `write_file` 中写入包含 `r'\u3010'` 的原始字符串时，工具会额外转义反斜杠：

| 意图 | 写入文件的结果 | 实际效果 |
|------|--------------|---------|
| `r'\u3010'` 匹配 `【` | `\\u3010` | 匹配字面量 `\u3010`，失败！ |
| `r'【'` 中文符号 | `【` | 正确匹配 `【` |

**修复：** 正则中直接使用中文符号，不用Unicode转义。

同样问题也影响 `\d`、`\s` 等转义序列：

| 意图 | 错误写法 | 正确写法 |
|------|---------|---------|
| 匹配数字 `\d` | `r'\\d'` | `r'\d'` |
| 匹配空白 `\s` | `r'\\s'` | `r'\s'` |

**检查方法：** 用 `cat -A` 查看文件中的实际字符。如果看到 `\\d` 说明多了一个反斜杠。

## 插件注册流程

```python
# app/plugins/wiper_finder.py — 插件类
class WiperFinderPlugin(BasePlugin):
    name = "wiper_finder"
    category = "auto_parts"  # 新域命名：语义化，不用品牌名

    def get_system_prompt(self) -> str:
        return f"【雨刮器车型匹配工具】数据库覆盖{N}条记录..."

    def process_message(self, message, context) -> dict | None:
        results = find_wiper(message)
        if not results: return None
        return {
            "plugin": "wiper_finder",
            "type": "wiper_match",     # 新类型
            "content": formatted_text,
            "matches": results,         # 结构化数据
        }

# app/main.py — 注册
from app.plugins.wiper_finder import WiperFinderPlugin
plugin_engine.register(WiperFinderPlugin())

# app/config.py — 定价
PLUGIN_PRICING["wiper_finder"] = {"name": "雨刮器车型匹配插件", "price": 29}

# app/api/chat.py — 路由插件结果类型
if pr.get("type") in ("size_recommendation", "fabric_info", "wiper_match"):
    # 插件结果优先于LLM回复
```

## 与服装插件的关键区别

| 维度 | 服装尺码引擎 | 雨刮器匹配 |
|------|------------|-----------|
| 数据源 | 内置算法(BMI+尺寸表) | 外部Excel数据库(2500条) |
| 匹配逻辑 | 输入参数→计算公式 | 车型名→模糊匹配→排序 |
| 精确度要求 | 中(推荐±1码) | 高(差1寸装不上) |
| 年份因素 | 无 | 关键(同车型不同年份可能不同) |
| 多实体 | 不常见(一次一般只问一件) | 常见("一台轩逸一台CRV") |

## 常用覆盖范围

| 品牌族 | 覆盖车型 | 数据量 |
|--------|---------|-------|
| 德系 | 大众/奥迪/宝马/奔驰/保时捷 | 300+ |
| 日系 | 丰田/本田/日产/马自达/雷克萨斯 | 250+ |
| 美系 | 别克/福特/雪佛兰/凯迪拉克/林肯/特斯拉 | 200+ |
| 国产 | 比亚迪/吉利/哈弗/长安/奇瑞/传祺 | 400+ |
| 新势力 | 理想/蔚来/小鹏/问界/零跑/哪吒 | 100+ |
| 韩系 | 现代/起亚 | 80+ |

## 常见坑

| 坑 | 现象 | 解决 |
|:--|:-----|:-----|
| 正则`\u3010`在write_file中变成字面量 | 车型行解析全失败 | 直接用中文符号`【` `】`，不用Unicode转义 |
| 双反斜杠`\d`在raw string中被转义 | `r'\\d'` → 匹配字面`\d` | 用 `r'\d'`，检查文件确认只有1个反斜杠 |
| 中文数字代系："第八代"没被识别 | 雅阁车型搜不到"雅阁"关键词 | regex加 `(?:第)?[\d一二三四五六七八九十百]+` |
| SKU字符串中混入车型名 | "U-2620" vs "【大U-2814】" | parse_sku前先过滤纯字母+数字+连字符格式 |
| 超大JSON文件启动慢 | 2500条JSON加载变慢 | 预构建搜索索引存到JSON，不每次重建 |
