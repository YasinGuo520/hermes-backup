# 网关"没回应"诊断记录 — gateway.platforms list/dict 崩溃（2026-08-04）

## 事故时间线

用户消息在飞书发出后没回应，反复追问"你好了没"。网关日志显示：

```
22:50:27 inbound message: platform=feishu user=Yasin chat=oc_... msg='你好了没'
22:50:32 ERROR gateway.run: Agent error in session agent:main:feishu:dm:oc_...
          File ".../gateway/run.py", line 4457, in _handle_message_with_agent
            _plat_gw_cfg = _platforms_gw_cfg.get(platform_key) or {}
          AttributeError: 'list' object has no attribute 'get'
23:05:08 (再次收到同款消息) 23:05:15 同样崩溃
```

关键特征：**每次用户发消息才崩**（消息处理路径触发），网关进程本身活着（ps 能看到 gateway run），端口还监听。

## 根因链

1. 升级 Hermes 到 v0.20 后，`gateway/run.py:4456-4458` 新增了 per-platform `skip_context_files` 读取逻辑：
   ```python
   _platforms_gw_cfg = (ctx.user_config.get("gateway") or {}).get("platforms") or {}
   _plat_gw_cfg = _platforms_gw_cfg.get(platform_key) or {}   # ← list 没有 .get()
   ```
2. 而 config.yaml 里 `gateway.platforms` 还是旧格式 **list**：
   ```yaml
   gateway:
     platforms:
     - feishu
     - qqbot
   ```
3. `.get(platform_key)` 作用在 list 上 → `AttributeError: 'list' object has no attribute 'get'`

## 修复（当时实际做的）

23:06 用 python yaml 把 `gateway.platforms` 改写为 dict 格式（改前备份 `config.yaml.bak-20260804230607`，diff 确认只改了这一段）：

```python
import yaml, shutil
shutil.copy('/home/ubuntu/.hermes/config.yaml', '/home/ubuntu/.hermes/config.yaml.bak')
cfg = yaml.safe_load(open('/home/ubuntu/.hermes/config.yaml'))
cfg['gateway']['platforms'] = {
    'feishu': {'skip_context_files': False},
    'qqbot': {'skip_context_files': False},
}
yaml.safe_dump(cfg, open('/home/ubuntu/.hermes/config.yaml','w'),
               allow_unicode=True, sort_keys=False, default_flow_style=False)
```

然后重启网关（cron 进程树外重启，见 update-hermes.md）。

## 验证命令

```bash
# 1. 确认新进程 PID 变化
pgrep -af "hermes_cli.main gateway run"
# 2. 当前实例无新错误（0 = 干净）
tail -50 ~/.hermes/logs/gateway.log | grep -cE "ERROR|AttributeError"
# 3. systemd 状态
systemctl --user status hermes-gateway | head -3   # Active: running
# 4. 配置格式
grep -A6 "^gateway:" ~/.hermes/config.yaml
```

## 经验

- **"网关没回应" ≠ 网关挂了**。先看 gateway.log 有没有 `Agent error in session` + 行号，再 ps 确认进程。崩溃可能只在消息处理路径触发。
- v0.20 升级后 config.yaml 结构有变化，升级必查 `gateway.platforms` 格式。
- 修完配置**必须重启网关**，不是新会话就生效。
- 备份对比法（diff 修改前后的 config.yaml）能快速确认改了什么。
