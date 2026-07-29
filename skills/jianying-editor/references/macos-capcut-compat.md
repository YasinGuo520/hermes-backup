# 剪映 Skill + macOS 兼容性测试记录

## 剪映专业版 5.9.0（中文版）

| 项目 | 内容 |
|------|------|
| App 路径 | `/Applications/VideoFusion-macOS.app` |
| Bundle ID | `com.lemon.lvpro` |
| 版本号 | 5.9.0（draft_info.json version: 360000） |
| 频道 | `jianyingpro_0` |
| 草稿目录 | `~/Movies/JianyingPro/User Data/Projects/com.lveditor.draft/` |
| 安装方式 | dmg 安装（非 App Store） |
| 升级框架 | 自研 HTTP 检查（无 Sparkle） |

### 升级阻止

通过 `/etc/hosts` 屏蔽以下域名（需要 sudo）：

```
127.0.0.1 lv-pc-api.bytedance.net
127.0.0.1 lv-pc-api-boe.bytedance.net
127.0.0.1 starling.bytedance.net
127.0.0.1 logvcapi.capcut.com
127.0.0.1 update-api.capcut.com
```

⚠️ 不要屏蔽 `bytedanceapi.com` 或 `ibytedtos.com`，否则会影响云端素材/模板加载。

### JyWrapper 兼容性（v5.9）

| 功能 | 状态 | 备注 |
|------|------|------|
| 新建草稿 | ✅ | 自动修复 corrupted draft |
| `add_media_safe` 导入视频 | ✅ | MP4/图片均正常 |
| `add_transition_simple("crossfade", ...)` | ✅ | 0.5s 交叉淡化 |
| `add_text_simple` 添加文字 | ✅ | |
| `add_narrated_subtitles` 配音+字幕 | ✅ | |
| `draft_inspector.py list` | ✅ | |
| `api_validator.py` | ✅ | |
| 自动导出（auto_exporter） | ❌ | 仅支持 Windows |
| 剪映中手动导出 | ✅ | 打开草稿手动导出即可 |

### 竖屏项目注意事项

初始化 JyProject 时必须指定分辨率和 overwrite=True：

```python
project = JyProject("项目名", width=832, height=1108, overwrite=True)
```

视频 track 不允许重叠，交叉淡化必须用 `add_transition_simple()`，不能靠时间轴叠放。

文字 track 同样不允许重叠，两条文字同时出现需合并到同一段（用换行符 `\n`）。

## CapCut 国际版 7.4.0 快速参考

| 项目 | 内容 |
|------|------|
| App 路径 | `/Applications/CapCut.app` |
| Bundle ID | `com.lemon.lvoverseas` |
| 草稿目录 | `~/Movies/CapCut/User Data/Projects/com.lveditor.draft/` |
| 升级框架 | Sparkle |
| 阻止升级 | `defaults write com.lemon.lvoverseas SUEnableAutomaticChecks -bool false` |

> ℹ 此 Skill 主要为剪映专业版中文版设计。CapCut 国际版草稿格式可能有差异，核心 API 通常可用，但自动导出不支持。
