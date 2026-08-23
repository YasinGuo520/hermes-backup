# DeepSeek 扣费案例实录

## 案例1：8/19-8/22 扣费调查（首次完整排查）

**背景**：用户发现 DeepSeek 控制台 8/19 当日 token 24.7M（命中15.9M + 未命中8.56M + 输出0.26M），感觉"没怎么用却扣费严重"。总消费 ¥126.45（7/21-8/19）。

**结论**：
- 烧钱大头 = **输入未命中缓存 8.56M**（×高峰价¥3/M ≈ ¥25.7，占80%）
- 输出仅0.26M，即使全是 thinking 最多 ¥2.3——所以"thinking占87%"的说法（Mac上Hermes自测）**不成立**，是本地 usage.jsonl 的 reasoningTokens 统计口径与 DeepSeek 计费对不上
- 服务器侧 8/19 全天 104 次调用、输入5.2M、命中率89%，费用约 ¥2-3；Mac 侧贡献了 ~19M 输入（新会话多、命中率低）

**教训**：排查扣费必须先看控制台 tooltip 的三项分解，用官方价算账，再查日志归因。不要信本地 usage 统计。

## 案例2：8/22 晚 pro 扣费 ¥0.62 之谜（未查明）

**现象**：控制台显示 21:00-22:00 有 deepseek-v4-pro 扣费 ¥0.62。

**排查过程（全部排除）**：
- 服务器 8/22 19-23点：0 次 API 调用（当天70次全在白天，是 cron）
- Mac 8/22 19-23点：7 次调用（19:14-19:43 cron"每日自检+记忆清洗"），全 v4-flash
- Mac Hermes.app（桌面版 GUI，`hermes serve` 进程 PID 720）：gui.log 17:04 后无记录；leveldb 里 `desktop-active-pro` 键其实是 profile 名不是模型；app.asar 里 0 处 pro 引用
- 全盘 grep `deepseek-v4-pro`：服务器 /home/ubuntu、/var/www、Mac 全目录——**0 处业务代码引用**（只有 hermes-agent 源码/tests/缓存元数据）
- 服小助(8002) 当天 0 连接；Docker 无容器

**意外发现**：`agent.log.1`（8/14前的轮转旧档）显示 **8/11 16:06-8/12 12:23 该 Feishu 会话曾切到 deepseek-v4-pro 跑过 19 次调用、输入75.9万token**——这是历史上真实发生过的 pro 扣费（可能是 8/11 某次误切模型），但日期与用户看到的 8/22 21-22点对不上。

**结论**：8/22 当晚 pro 来源未查明（疑第三方/控制台显示问题）。处理：锁死所有服务 + balance API 基线（¥4.91）+ 2天观察 cron。**若观察期仍出现 pro → key 泄露，必须换 key**（`sk-ce1a8ba...` 硬编码在多处：落地页 red-blue server.py 曾写死、服小助、Hermes）。

**教训**：
- 排查跨机时，Mac 桌面版 GUI 走 `hermes serve`（写 gui.log）而不是 gateway（写 agent.log）——两个日志都要看
- 历史扣费查 `agent.log.1` 旧档，别只查当天
- key 复用面广（Hermes+服小助+落地页三处共用），锁死要覆盖全部调用方

## 案例3：keepalive 端口顶替（2026-08-19 简历↔中年人生互换）

nginx 把 8894 从 portfolio http.server 换成反代中年人生(8001) 后，keepalive.sh 每3分钟发现 8894 "没起 http.server" 就重新拉起 portfolio，跟 nginx 抢端口，导致 nginx reload 静默失败、新配置不生效。

**修复**：从 keepalive.sh 的 STATIC_PROJECTS 删除 `portfolio|8894` 条目，再 reload nginx。
**铁律**：任何端口从 http.server/socat 换成 nginx 反代后，立刻从 keepalive.sh 对应数组删除该条目。

## 案例4：落地页改模型必须手动重启进程

改完 `red-blue-method/server.py` 的 MODEL 后，keepalive 检查端口活着（200）不会重启——旧进程（8/4启动）还在用旧代码。必须 `kill PID` 再启动（keepalive 会补拉新代码），用 `ps -o lstart -p PID` 验证启动时间确实是改完之后的。

## DeepSeek 官方定价速查（2026-08 核实）

| 模型 | 输入命中(空闲/高峰) | 输入未命中(空闲/高峰) | 输出(空闲/高峰) |
|---|---|---|---|
| deepseek-v4-flash | 0.05/0.10 | 1.5/3.0 | 4.5/9.0 |
| deepseek-v4-pro | 0.15/0.30 | 4.5/9.0 | 13.5/27.0 |
| deepseek-v4-flash-vision-exp | 0.05/0.10 | 1.5/3.0 | 4.5/9.0 |

- 高峰时段：北京时间 9:00-12:00、14:00-18:00
- 2026-08-23 起：周末全天按低谷价
- 模型版本：V4-Flash-0731 / V4-Pro-0813
- balance API：`GET https://api.deepseek.com/user/balance`，返回 `balance_infos[0].total_balance`（¥）
- 无公开 usage 明细 API（只有 balance），用量只能看控制台
