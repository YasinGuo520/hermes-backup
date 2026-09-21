# 思维导图输出格式（FreeMind .mm / XMind）

用于把知识库内容转成可视化层级结构（路径、等级、分类、排行榜），XMind 与 FreeMind 都能直接打开 `.mm`。

## 何时生成

- 用户要「思维导图 / XMind 文件 / 知识结构图」
- 摄取的内容本身带层级（难度等级、优先度、分类树、路径选项）
- 层级结构比平铺文字更好导航

## 基础模板

```xml
<?xml version="1.0" encoding="UTF-8"?>
<map version="1.1">
    <node TEXT="Root Title" FOLDED="false" COLOR="#ffffff" BACKGROUND_COLOR="#1a1a2e">
        <font NAME="PingFang SC" SIZE="16" BOLD="true"/>
        <node TEXT="Branch One" FOLDED="true" COLOR="#ffffff" BACKGROUND_COLOR="#0f3460">
            <font NAME="PingFang SC" SIZE="14" BOLD="true"/>
            <node TEXT="Leaf item" COLOR="#333333" BACKGROUND_COLOR="#e8f4f8"/>
            <node TEXT="Nested items" FOLDED="true" COLOR="#333333" BACKGROUND_COLOR="#e8f4f8">
                <node TEXT="Detail A" COLOR="#333333" BACKGROUND_COLOR="#f0f0f0"/>
            </node>
        </node>
    </node>
</map>
```

## 配色（深色根 → 浅色分支）

| 角色 | 背景 | 文字 | 用途 |
|------|------|------|------|
| 根节点 | `#1a1a2e` | `#ffffff` | 中心 |
| 一级分支 | `#16213e` / `#0f3460` / `#1a5276` / `#2471a3` | `#ffffff` | 顶层类目 |
| 二级分支 | `#e8f4f8` / `#fff3e0` / `#e8f5e9` / `#fce4ec` | `#333333` | 子类目 |
| 叶子 | `#f0f0f0` | `#333333` | 明细 |
| 高价值/重点 | `#ffcdd2` | `#d32f2f` | 收入、关键指标 |

## 节点属性

- `TEXT` — 显示文本（必填）
- `FOLDED="true"` — 默认折叠（首屏干净）；`"false"` — 展开
- `COLOR` / `BACKGROUND_COLOR` — 文字色 / 背景色（hex）
- `<font NAME="…" SIZE="…" BOLD="…"/>` — 字体样式

## 流程

1. 提取源材料的天然树（类目 → 子类 → 明细）
2. 深度封顶 3-4 层；二级分支 `FOLDED="true"`
3. 用 `write_file` 写 `.mm`
4. 存放：知识库资产 `_kb/raw/assets/`；需要桌面直取时再复制一份到 `~/Desktop/hermes/`
5. 校验：文件首行是 `<?xml ...?>`，标签闭合正确

## 坑

- `TEXT` 里的 XML 特殊字符必须转义：`&amp;` `&lt;` `&gt;` `&quot;`
- macOS 上 XMind 不会自动刷新文件图标 → 让用户 `File → Open` 或拖入 XMind
- `.mm` 没有标准 linter，用 `xmllint --noout file.mm` 验良构性
- **不要 `pip install XMind`** —— 与现代 XMind 2024+ 不兼容，生成的文件打不开；纯 XML 才可靠
- 中文字体：`<font>` 里写 `NAME="PingFang SC"`（macOS）
