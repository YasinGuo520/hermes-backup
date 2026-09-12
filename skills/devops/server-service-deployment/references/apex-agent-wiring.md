# Mac 端 APEX 页面「光点」↔ 服务器 Agent 矩阵：对照与接线（2026-09-12 定）

用户发截图问「页面上的英文光点对应我哪个项目」时的标准作业。本次结论已落盘 `~/Desktop/hermes/apex-agent-map.md`。

## 一、光点是模板自带的 18 节点名单，不是你的服务

源码（Mac 实例 `~/apex-src/APEX-UI`，服务器镜像 `~/Desktop/hermes/mac-apex-src/APEX-UI`）：

| 文件 | 内容 |
|---|---|
| `components/ReasoningWeb.jsx` | `ROSTER`（18 行：key / 英文名 / 层 / x / y / `live` 布尔 / bend / 半径）；第 6 位 `live=false` = 模板作者自己标的「未建成」 |
| `components/ApexWorld.tsx` | `ROSTER`（18）+ `INFO`（职责/示例请求/status online\|standby\|integration）+ `AgentOverview` 弹窗（**现在点光点只弹介绍窗，不跳真实服务**） |

三层配色 `COL = { consultant:#00e5ff 青/参谋 , doer:#f5a623 橙/执行 , tool:#7f9bb3 灰/工具 }`。
名单来自模板原作者的业务（国外 3D 打印小公司），所以 Engineering（3D 打印参数）之类与 Yasin 无关。

## 二、18 光点 → 项目对照（服务器 8924–8940，全 200 实测）

| 光点 | 中文 | 对应 | 状态 |
|---|---|---|---|
| Chief of staff | 幕僚长/总管 | ①统筹运营 8924 | ✅ |
| Researcher | 调研员 | ③趋势监控 8929（+中国市场调研 8922） | ✅ |
| Finance | 财务 | ⑯财务 8940 | ✅ |
| Editor | 编辑/质检 | ⑨合规审查 8933 | ✅ |
| Sales | 销售 | ②销售分析 8928 | ✅ |
| Marketing | 营销 | ⑧内容生产 8932 + ⑪选品 8935 | ✅ |
| Ops | 运营 | ⑥流程自动化 8930 | ✅ |
| Social | 社媒 | ⑩舆情监控 8934 | ✅ |
| Analytics | 分析 | ⑫数据分析 8936 | ✅ |
| Memory | 长期记忆 | 无独立服务（Hermes 记忆 + Obsidian；部分吃在④培训导师知识库） | ⚠️ |
| Strategist | 战略官 | 无（最像六分身 8921 / 红蓝 8920） | ⚠️ |
| Design | 设计 | 无（有 ai-ecommerce-visual-design 技能可包装） | ⚠️ |
| CRM | 客户管理 | 无（可接服小助客户库） | ⚠️ |
| Calendar / Email / Drive | 日历/邮箱/云盘 | 无（技能里有 google-workspace / email-inbox-triage / box） | ⚠️ |
| Developer | 开发者 | 就是 Hermes 本身；模板 `live=false` | — |
| Engineering | 工程 | 模板作者的 3D 打印业务，无关（用户已说先放着不管） | — |

**反向缺口**（有 Agent、图上没光点）：⑤招聘 8925 / ⑦绩效 8926 / ④培训 8927 / ⑬供应链 8937 / ⑭库存 8938 / ⑮物流 8939 = 6 个。

## 三、接线铁律：门脸留本地，业务接服务器

用户问「接你那边（服务器）还是接本地比较好」时的答案：

| 层 | 放哪 | 为什么 |
|---|---|---|
| 耳朵（麦克风/拍手） | 本地 Mac | TCC 授权在 Hermes venv Python 手上，Chrome 那把恒静音 |
| 嘴（TTS/扬声器） | 本地 Mac | 服务器无声卡 |
| 门脸（这张图 :3000） | 本地 Mac | 屏幕在用户面前 |
| 16 个业务 Agent | 服务器 | 已在那边、7×24、**¥2-3/天**；Mac 是烧费端 **¥12-27/天**且会睡眠 |

- 用户的直觉「先对接本地 Hermes」对的是**语音通道**（拍手→桥 :3210→本地 Hermes→朗读），不是**项目入口**。
- 光点点击 = `href` 直开服务器 Agent 页（**优先 Tailscale 内网 `100.105.38.39:89xx`**，不暴露公网端口防白嫖 LLM 按钮）；纯前端一行，不经本地 Hermes 转发。
- 以后若要「点光点 = 跟这个 Agent 对话」，才由**本地 Hermes 当总机**去调服务器 Agent，答案再交给桥朗读（语音链不用改）。
- **业务逻辑别往 Mac 搬**：贵 5–10 倍且会睡。

## 四、改这张图的路径与验收

1. 服务器侧改 → `rsync` 到 Mac → Mac 上 `bash -lc "cd ~/apex-src/APEX-UI && npm run build"`（node_modules 只在 Mac；macOS 无 `timeout`）。
2. 动代码前先 `git commit` as-found 基线（`mac-apex-src/APEX-UI` 有 git，基线 c465c08 附近）。
3. A 方案（接线）：18 光点 href → 服务器对应页 + 补 6 个缺失光点；用户已说 Engineering 先不管。B 方案（补 Calendar/Email/Drive/CRM/Design/Memory 六个真服务）**未获表态，别擅自开建**——那是「为了好看而建服务」。
4. 验收：先在服务器侧按「端口身份盘点」确认各端口 200，再从 Mac 点一个光点看是否跳对页。
