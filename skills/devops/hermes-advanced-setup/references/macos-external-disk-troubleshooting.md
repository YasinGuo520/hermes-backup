# macOS 外置盘无法识别排查指南

当用户说"盘插了但电脑识别不了"时，按以下分层排查。

## 分层诊断流程

### 第0层（新增）：跨操作系统验证 — 最重要的第一步

当外置盘**灯亮但系统不认**时，先插到另一台电脑（最好是 Windows）验证：

如果 Windows 能读 → **盘、线、盒子全是好的**，是 macOS 侧问题。
如果 Windows 也不能读 → 硬件故障（线/盒子/盘）。

| Windows 能读？ | 结论 | 下一步 |
|--------------|------|--------|
| ✅ 能读 | 盘和线盒子全好 → **macOS 侧问题** | 查 Disk Arbitration、force-eject 黑名单、USB 总线复位、NVRAM 重置 |
| ❌ 不能读 | 硬件故障 | 换线→换口→换盒子验证 |

**为什么 Windows 能读是强诊断信号：**
- macOS 的 Disk Arbitration 会**记录强制弹出的磁盘**，重新连接后拒绝自动挂载
- Windows 没有"记忆"机制，插上重新识别
- Windows USB 栈对边缘状态硬盘更宽容（不挑剔 USB 握手时序）
- 如果 Windows 能读，不用花冤枉钱买新盒子/跑数据恢复

### 第1层：确认系统能否看到设备

```bash
# 查看所有磁盘（含外置）
diskutil list

# 只看外置磁盘
diskutil list external

# 查看挂载点目录（注意：有目录 ≠ 真的挂载了）
ls -la /Volumes/
```

关键判断：
- `diskutil list` 里没有外置盘 → 硬件级未被检测
- 有 disk 节点但没有 `/Volumes/` 目录 → 格式不兼容或未挂载
- 有 `/Volumes/` 目录但没有 `df -h` 记录 → 挂载点残留（空目录）

### 第2层：检查物理连接

```bash
# USB 设备列表
system_profiler SPUSBDataType

# Thunderbolt / USB4 设备列表
system_profiler SPThunderboltDataType
```

看 USB 设备里是否有大容量存储类设备（Mass Storage, SATA, SSD, HDD 等关键词）。
只有 iPhone、Hub、转接头 → 外置盘硬件级未通电/未识别。

### 第3层：检查挂载状态

```bash
# 看实际挂载了的文件系统
df -h | grep -v "com.apple"

# 看 mount 表（精确匹配卷名）
mount | grep <卷名>
```

`df -h` 不显示、`mount` 不匹配、但 `/Volumes/` 有目录 → **挂载点残留**，盘不在线。

### 第4层：检查系统日志（近15分钟）

```bash
log show --predicate \
  'subsystem == "com.apple.diskmanagement" OR 
   subsystem == "com.apple.iokit.IOStorageFamily" OR 
   message CONTAINS "USBMSC" OR 
   message CONTAINS "disk2" OR 
   message CONTAINS "external"' \
  --last 15m 2>/dev/null | tail -30
```

实时监听（插拔时运行）：
```bash
log stream --predicate \
  'subsystem contains "IOStorage" OR 
   message contains "USBMSC" OR 
   message contains "disk2"' \
  --source --last 10
```

### 第5层：ioreg 深度探测

```bash
# 查看 IOKit 中有无大容量存储设备类
ioreg -p IOUSB -l -b | grep -i "disk\|storage\|mass\|drive\|media\|MSC\|SATA\|SSD\|HDD"

# 或更精准：检查 USB Mass Storage 驱动计数器
ioreg -p IOUSB -l -b | grep -c "IOUSBMassStorage"
```

计数为 0 → 内核的 USB Mass Storage 驱动根本没加载到该设备。

## 分层判断树

```
diskutil list 有外置盘？
├── 有 → mount 了？
│   ├── 有 → 权限问题（走 macos-backup-automation 的 permission quirk 章节）
│   └── 无 → 格式不兼容（NTFS 只读/未挂载）、刚插入需要等几秒
└── 无 → system_profiler 能看到 USB 设备？
    ├── 能看到 USB 大容量存储类设备 → 驱动/格式问题
    │   ├── 检查 Disk Utility → 看灰显/未挂载的卷
    │   └── 尝试手动挂载：diskutil mount /dev/disk2s1
    └── 看不到任何新设备 → 硬件级断连
        ├── ⭐ 先插 Windows 验证（如果 Windows 能读 = macOS 侧问题，走恢复流程）
        ├── 换线（数据线最容易坏，尤其 Type-C）
        ├── 换口（换一个 USB-C 口直插）
        ├── 直插笔记本（跳过 HUB/扩展坞）
        ├── 听声音（机械硬盘有无转动声/咔咔声）
        └── 插另一台电脑验证是盘坏了还是 Mac 口坏了
```

## macOS Force-Eject 恢复流程（分级尝试）

当外置盘**插 Windows 能读**但**插回 Mac 不认**时（常见于 I/O 中断导致的强制弹出），按顺序尝试：

### 第1级：软件复位（无副作用）

```bash
# ① USB 总线复位（无需重启，不影响其他 USB 设备）
sudo killall -STOP -c usbd 2>/dev/null
sleep 3
sudo killall -CONT -c usbd 2>/dev/null

# ② 拔掉重插后检查
diskutil list external

# ③ 如果能看到盘但没挂载 → 手动挂载
diskutil mount /dev/disk2s1   # 盘符按实际改
```

### 第2级：重启（重置 Disk Arbitration）

```bash
sudo reboot
```

### 第3级：更彻底的 Disk Arbitration 重置

```bash
sudo launchctl unload /System/Library/LaunchDaemons/com.apple.diskarbitrationd.plist 2>/dev/null
sudo launchctl load /System/Library/LaunchDaemons/com.apple.diskarbitrationd.plist
```

### 第4级：NVRAM 重置（终极手段，修复 USB 控制器初始化问题）

当 `diskutil list` 完全看不到外置盘、`system_profiler SPUSBDataType` 也不显示任何新设备，但 Windows 能正常读写时，说明 USB 控制器/NVRAM 配置损坏。

**操作步骤：**
1. 关机
2. 按一下电源键开机
3. **立刻**同时按住 **Option + Command + P + R** 四个键
4. 持续按住约 **20 秒**（屏幕会闪一次或听到两次启动声）
5. 松手，让电脑正常启动
6. 进系统后插上外置盘测试

**注意：** NVRAM 重置会恢复启动磁盘选择、音量、屏幕分辨率等硬件参数到默认值，但**不会丢失任何个人数据**。这个操作对 Intel Mac（含 T2 芯片机型）有效。

### 第5级：重新安装 USB 驱动（最后手段）

```bash
# 重建内核扩展缓存
sudo kextcache -i /
# 然后重启
sudo reboot
```

## 常见场景与结论

| 现象 | 结论 | 行动 |
|------|------|------|
| `diskutil list` 无、USB 列表无、/Volumes/ 有空目录 | 盘未通电/物理断连 | 换线→换口→直插→换机验证 |
| `diskutil list` 无但 **Windows 能读** | ⭐ macOS USB 控制器初始化失败 / NVRAM 损坏 | USB 总线复位→重启→**NVRAM 重置**→重装驱动 |
| `diskutil list` 无但 USB 列表有未知设备 | 握手失败/供电不足 | 换供电充足的线/USB口/外置供电 |
| `diskutil list` 有 disk2 但 `df -h` 无 | 格式不识别 | Disk Utility 看有没有灰显卷 |
| `diskutil list` 有、mount 表有但 `/Volumes/` 无 | 挂载点被删除 | `diskutil mount /dev/disk2s1` |
| `/Volumes/` 有、`df -h` 无、`mount` 无 | 挂载点残留（空壳目录） | 盘不在线，走硬件排查 |
| I/O 操作（tar/cp）后盘被弹出 | USB 桥接板不稳定 / macOS 强制卸载 | 插 Windows 验证→USB 总线复位→换盒子 |
| `diskutil resetFusion` 提示"At least one internal disk must be solid-state" | 非 Fusion Drive 机型，命令无效 | 走其他恢复路径 |

## 关键陷阱

- **`/Volumes/` 有目录 ≠ 盘真的在线** — 上次挂载留下的空壳目录，无 `df -h` 匹配即残留
- **`diskutil list external` 返回空** 但用户坚持插了盘 → 说服用户先做物理排查
- **系统日志**里的 `external trust evaluation` 跟外置盘无关（那是 SSL 证书验证），别被干扰
- **USB Hub/扩展坞** 经常供电不足导致外置盘握手失败，直插笔记本 USB-C 口是最高优先级的测试
- **Boot Camp 分区** (BOOTCAMP) 会显示在 /Volumes/ 里，但那是内部盘的一部分，不是外置盘
- **一插就发烫 ≠ 桥接板一定烧了** — 可能只是 macOS USB 控制器初始化失败导致设备进入异常状态，插回 Windows 重新初始化后即可恢复正常
- **NVRAM 重置是 macOS 特定硬件问题的最后防线** — 在重启、USB 复位都无效时再尝试，对 Intel Mac（含 T2）有效，对 Apple Silicon 无效
