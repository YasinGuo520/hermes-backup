# Petdex 吉祥物（hermes pets）

> 吸收自 bundled-hub `petdex`（curator 合并）。它只是驱动 `hermes pets` CLI 与 `display.pet` 配置，不生成精灵图。

## When to Use

- 用户想要一个桌面/终端吉祥物，或问到 “pets”
- 用户想换/预览/关闭当前宠物
- 排查宠物为什么不显示（终端图形能力、配置）

## 前置

- 能访问 `petdex.dev`（只读，无鉴权）拉取画廊/manifest
- Pillow（Hermes 核心依赖）负责精灵解码——已装
- 全保真终端渲染需要图形能力终端（kitty / Ghostty / WezTerm / iTerm2 / sixel）；否则自动回退 truecolor Unicode 半块渲染

## 速查

| 目标 | 命令 |
|---|---|
| 浏览画廊 | `hermes pets list`（可跟子串过滤：`hermes pets list cat`）|
| 已安装列表 | `hermes pets list --installed` |
| 安装 | `hermes pets install <slug>`（加 `--select` 同时激活）|
| 设为当前 | `hermes pets select <slug>`（省略 slug 出选择器）|
| 全局改大小 | `hermes pets scale <factor>`（如 `0.5`，范围 0.1-3.0）|
| 终端预览/动画 | `hermes pets show [slug] [--cycle] [--state run]` |
| 关闭 | `hermes pets off` |
| 删除 | `hermes pets remove <slug>` |
| 诊断 | `hermes pets doctor` |

## 流程

1. 找：`hermes pets list <query>`，记下 `slug`
2. 装+激活：`hermes pets install <slug> --select`
3. 预览：`hermes pets show`（Ctrl+C 停）
4. 确认：`hermes pets doctor`——它打印解析到的宠物、渲染模式、终端图形协议与生效模式

宠物装在 `<HERMES_HOME>/pets/<slug>/`（按 profile 隔离）。选中会把 `display.pet.slug` + `display.pet.enabled` 写入 `config.yaml`。

## 配置（`display.pet`）

- `enabled`（bool）— 总开关
- `slug`（str）— 当前宠物；空 = 第一个已安装的
- `render_mode` — `auto`(检测) | `kitty` | `iterm` | `sixel` | `unicode` | `off`
- `scale`（float）— 192×208 原生帧的屏幕尺寸（默认 0.33，0.1-3.0）。一个旋钮改所有界面；用 `hermes pets scale <factor>`、`/pet scale` 或桌面 Appearance 滑块设置
- `unicode_cols`（int）— Unicode 回退时的宽度（列）

## 坑

- 只有**装了且选中了**（`enabled: true`）才会显示
- 管道/重定向（无 TTY）下终端渲染按设计关闭
- petdex 的 npm CLI 装到 `~/.codex/pets`；Hermes 用自己的 profile 级 `<HERMES_HOME>/pets/`——要用 `hermes pets` 安装

## 验证

`hermes pets doctor` 报 `✓ ready` = 已装+已选+已启用+Pillow 可导入。
