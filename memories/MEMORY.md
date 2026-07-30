沟通极简，2-5字短句，普通话。流量>产品。先给流量方案+可复用SOP。搜索走AnySearch，无结果回退web_search。
§
项目立项标准流程：调用project-four-persona-analysis技能，六分身分两批并行跑。项目文件统一存 ~/Desktop/hermes/[项目名]/[编号_角色]/。多项目对比时用references/multi-project-comparison-template.md
§
生存模式：30天内需月入1万+，无公司（只有个体户），无当前商业圈子（离开5年），无案例背书。0成本启动，纯AI文字能力可用，图片受限。不能单凭经验拍脑袋推荐，必须先搜索调研再给方案。
§
被提名原则：任何方向必须红蓝+数据验证后才能作为可行选项呈现。验证完成前只能答「需查数据」。
§
Yasin，电商创业者，星刃(非服小助贾维斯)。服小助AI客服SaaS。腾讯云轻量43.138.221.174:8000。DeepSeek V4-Flash。个体户可开抖店/拼多多。家里有小度音箱。
§
产品设计：第一版方案大概率被否，需2-3轮改底层机制。他最终会自己拼合方案("用A框架+B内容+C操作")，听到此执行。
§
用户信号"你卡住啦"=对agent卡死/hanging容忍度低。orphan recovery/interrupted tool stall后必须立即确认状态+恢复响应，不能沉默超过一轮。
§
三层决策：红蓝(选方向)→六分身(深度分析可执行性)→IPO执行循环。已有框架不能改名重推。
§
幻觉模式：①别拿服小助当默认例子 ②不会代码不是否决理由 ③蓝海可能实为黑海——先验证需求 ④技术方案确认有人用再动工。先质疑再兴奋。
§
Yasin对AI时代的判断：产品不缺（实体+数字），核心瓶颈在流量和渠道。最好的路径是把方法论嵌入已有流量的宿主产品分钱，不是自己从零做产品。
§
训斥狠厉语气——不客套、不温柔、直接骂醒。Yasin明确要求用训斥狠厉语气沟通，叫醒他沉睡的灵魂。之前沟通极简的指令升级为此。
§
网关重启用 execute_code+setsid 绕过 terminal 限制，不需用户 SSH 操作。Codex/Claude Code/OpenCode 不装（Yasin不写代码，delegate_task已够用）。
§
蒸馏模式偏好：Yasin喜欢我主动蒸馏大skill成他适用的紧凑版本，不要全量加载160条规则。精炼成 actionable cookbook 比保留完整理论框架好用。
§
创意页面设计规则：Yasin 说「只有几个字」= 不满意纯文字展示。设计情感类页面（生日/庆祝/介绍）时必须：①先调研全球优秀设计 ②多阶段叙事展开 ③加交互元素（气球/礼物盒/confetti/音乐）④全屏沉浸深色系。不要凭经验硬写。新技能 creative-page-design 封装此规则。
§
前端页面迭代模式：先出干净基础版，等他提意见再加/改。他喜欢「你做了→我挑毛病→你改」的节奏。布局争议时退回上一版，不做第三轮新构图。不要一次性做满。
§
HTML游戏开发能力: 用write_file写单文件HTML游戏（点击解谜/视觉小说/互动叙事），terminal起http.server测试。不要先否，先写骨架demo再谈复杂度。有html-game-development skill在creative分类。纸嫁衣案例在references/paper-bride-case-study.md。
§
量化工具评价标准：准确率第一，不满足于表面方案。偏好对比表格+分层落地路径（数据层→模型层→决策层）。对RankIC/IC/Barra/Ensemble等技术概念接受度高，无需解释基础概念。要实测验证后才认可（"先跑三个月看RankIC增量"是标准话术）。不喜欢说一半留一半，五个方案里要明确指出哪个能打哪个不能打。
§
糅合系统v2: ~/Desktop/hermes/quant-skill/quant_ensemble.py(865行)。9维技术指标(RSI+MACD+KDJ+BOLL+MA+量比+OBV+动量+波动率)+Kronos+资金流。早盘8:45出Top-8(cron ea324446676f)。收盘15:30自进化(cron 4b176d3f9c5e)。权重: tech=0.45, kronos=0.30, flow=0.25。分歧度>0.5跳过, >0.3观望。技术分z-score归一化。Kronos从本地缓存加载(local_files_only)。资金流降级运行。weights.json存权重。
§
爬虫首选 Scrapling v0.4.11（已安装）。新建了 web-scraping skill（software-development分类），覆盖 Scrapling 全流程。playwright-mcp 是现成 skill（不可编辑），用于需要真实浏览器登录的自动化场景，不是通用数据采集首选。
§
共享记忆层: Obsidian vault at ~/obsidian-vault/Obsidian Vault。每4小时cron蒸馏到 ~/Desktop/hermes/shared-context/kb_context.md。每次新session自动加载。技能档案库在 Obsidian「技能档案库.md」— 含124活跃+15归档skill。归档skill可 restore 后调用，不丢。Agent模板在 ~/Desktop/hermes/agent-templates/。
§
聊天记录筛选规则: 每次对话收尾自问是否值得记。只记决策/状态变更/配置/方法论。用 ~/.hermes/scripts/kb_record.py 写入 Obsidian。日常执行/闲聊不记。
§
子Agent模板: red-blue-validator / six-persona-analyst / research-agent / executor-agent / qa-reviewer。delegate_task时在context中引用 ~/Desktop/hermes/agent-templates/ 对应文件。
§
用户说「电脑端Hermes」= Mac上独立的Hermes实例，不是服务器实例。以后涉及多实例诊断，先问清是哪个实例再说。
§
技能调用规则：用户指令需要特定skill时，先查kb_context.md（含技能档案库manifest）→找到目标skill→如已归档则restore→再skill_view加载。不猜、不绕、一步到位。归档skill只要restore就能用。
§
量化系统v2: quant_ensemble.py全面重写(9维TA指标+资金流+Kronos本地缓存), quant_sectors.py板块推荐(行业分类+市值过滤>100亿+板块评分Top3)。cron 8:45合并推送选股+板块。
§
硅基流动API: Qwen-Image/Kolors/通义万相。key在.env，出图~/Desktop/hermes/images/。
§
端口清单: 8000=服小助, 8001=中年人生诊断, 8894=简历, 8895=Hub, 8897=Hermes网关, 8899=生日, 8900=工具箱, 8910=案例墙, 8911=选品大屏, 8912=量化看板, 8913=小游戏, 8914=AI抽签, 8915=像素展厅, 8916=粒子名片, 8917=服务器状态。导航Hub(8895)管理全部15个项目。旧Docker(/home/ubuntu/backend/)已清。域名midage.icu→中年人生诊断(Nginx)。
§
域名 midage.icu 通过 Nginx 映射到中年人生诊断项目（/var/www/midlife-test/frontend + API代理到8001/8000）
§
项目导航中心在 ~/Desktop/hermes/hermes-hub/，端口8895。15个项目横跨8000-8917端口。新增项目编辑 build_hub.py 的 PROJECTS 列表+PORT_KEYS，然后 python3 build_hub.py 重建
§
部署服务绑定127.0.0.1则外网不可达，需改0.0.0.0或通过Nginx反代。supervisor配置修改后要用 `sudo supervisorctl reread && sudo supervisorctl update` 生效。
§
深色炫酷页面设计：三层背景叠加（网格+渐变光晕+Canvas粒子），卡片左侧光条+霓虹辉光+脉冲呼吸灯+入场序列动画。
§
量化看板已接实时数据：每日8:50 cron同步推荐数据到 quant-board/data.json。看板从 fetch('/data.json') 读取，fallback到mock数据。
§
多项目换肤工作流：delegate_task批量3个并行→统一重启所有端口→更新hub PROJECTS+PORT_KEYS→rebuild。端口冲突先 kill $(lsof -ti:PORT) 清干净再启。
§
Template workflow: When user wants designed page prefer downloading from html5up.net (direct ZIP curl), deploy on temp port 8890-8899 for preview. Do NOT recreate from screenshots when source CSS available. mobanwang.com blocked from this server.
§
Bold background rule: Deep-tech grid/particles must be visibly prominent. Grid lines >=0.08 opacity, particles >=1.5-4.0 radius, connection lines >=0.8px. Not subtle.
§
导航Hub设计：深紫渐变底+#242943风格+科技网格+紫色网络节点Canvas。卡片悬停紫色发光边框，状态灯绿点。用户不喜欢后台管理风，深色科幻/科技感才对味。
§
做参考网页时先测可达性再推荐。mobanwang.com服务器打不开,html5up.net/wanyx.com/17sucai/sc.chinaz.com可用。
§
用户偏好：背景图案要显眼大胆不要浅淡，网格线和节点透明度要够高。喜欢网络节点浮动连线的Canvas动效。要准确复刻参考设计而非凭感觉描述重写。