立项流程：红蓝+数据验证→六分身→IPO；新方案默认关联Obsidian(_kb/entities/按SCHEMA建页+更新index/log.md)
§
量化糅合v2：~/Desktop/hermes/quant-skill/quant_ensemble.py(tech0.45/kronos0.30/flow0.25，flow<60%降权)；verify_v2_daily.py当日口径T+1
§
内容/设计偏好：大skill蒸馏成紧凑版(cookbook>理论)，数据表格保留、cron日报不压缩；Obsidian ~/obsidian-vault/每4h蒸馏kb_context.md；网格bg≥0.08/粒子≥1.5px、html5up优先(curl ZIP)、角色立绘Qwen-Image→色键抠图→帧动画(不CSS手绘)
§
媒体工具：Manim ~/Desktop/hermes/manim-venv；图生3D只有混元3D可用(Tripo/Meshy被墙)，key ~/Desktop/hermes/mecha3d/.env
§
Mac TS100.80.117.5(yasin) SSH mac@；TCC挡~/Desktop但~/.hermes/skills可读；approvals=off；抓数据只走playwright+channel=chrome+headless=False(禁camofox)；Mac烧费端(¥12-27/天vs服务器¥2-3)，查扣费先查Mac端cron
§
cron铁律：钉model/provider+完整12位ID(8位报Job not found)；disabled任务edit报Cannot activate须先resume；LLM cron全挪7:00-7:55(DeepSeek空闲价)；cron禁web_search；curl直连GitHub Trending/HN限15次。
§
翻墙/美区ID详见overseas-account-setup技能。机场：飞鸟FlyingBird(¥15/100G)+山海(¥6)月付；TikTok须美国节点+English(US)，拔SIM或网页版。
§
小红书红线：个人店禁教育类目，卖课须企业店+定向邀约+ICP；AI虚假种草=封号，纯AI量产限流须勾选AI辅助+真人化改写；话术禁收益承诺/虚假人设/私域导流
§
财务紧急(救急优先)。已验证真：U客直谈/快马日结(勿买会员)、牛片网/圆领/淘宝代剪300-800/条、AI视频300-500/条；骗局：微赚/短剧出海一次性费用/游戏搬砖；避一品威客
§
TikHub key(~/Desktop/hermes/tikhub/.env)09-17实测401失效勿再试(需重注册)；端点结构见china-ai-platforms技能references/tikhub-endpoints.md；淘宝/拼多多/京东无API，抖音/百度/搜狗反爬→TikHub或Mac侧采集。
§
Yasin方向：公域→私域，抖音带货→个微起步(真人IP)>3000人再企微+SCRM。机器狗=国潮爆品方向。私域SOP见traffic-acquisition-sop技能(落地~/Desktop/hermes/gongyu-siyu-sop/)
§
Coze：PAT 2026-10-01重生成；POST api.coze.cn/v3/chat，4200=缺bot_id。Dify：8850=nginx/8851=API/8852=web，UI-gated走UI别DB hack。用户偏好：招聘截图只分析岗位不查公司；'别查了'=停调研直接分析手头材料
§
公司Agent矩阵(16个)：~/Desktop/hermes/company-agents/(venv fastapi/uvicorn/pandas，db开WAL)。保活=keepalive.sh的AGENT_SERVICES数组；备份backup_company_db.sh(03:20留14份)。⚠️实测空转→别提议补文档
§
环境坑：①国内服务器禁外网CDN→静态资源本地化；②Hub=python3 http.server 8895 serve ~/Desktop/hermes/hermes-hub/(子页同目录免开端口)；③npm prefix=~/.npm-global/bin
§
DeepSeek key sk-ce1a8ba2疑泄漏(09-06)勿复用；硅基流动key 09-28已轮换(两机36文件含备份/快照/state.db-wal，旧key实测401失效)；扣费查不到来源时先测旧key是否仍有效=是否被外部盗用(审计+轮换配方见agent-performance技能)
§
玄学工具站：~/Desktop/hermes/{tarot 8901,bazi 8902,face 8903,fortune-wheel 8914}，FastAPI单服务(static+/api→v4-flash)，八字用6tail lunar-python。导航铁律：hub index.html由build_hub.py生成，只改PROJECTS/PORT_KEYS
§
Hermes检索降级：web_search超时/web_extract无backend→anysearch MCP(mcp__anysearch__search/extract)免配置，中文长文稳定
§
腾讯云暴露面靠控制台防火墙(iptables全ACCEPT+ufw未启)，服务监听0.0.0.0裸奔；curl公网端口不通先ss -tlnp区分服务挂vs防火墙拦
§
跨机采集铁律：持续采集跑Mac(真IP+真人profile)，机房IP+headless=封号；服务器8920-8940被Agent矩阵占、8941=luopan-monitor，内存紧→采集器别放服务器。抖音罗盘+达人广场共用底座=Mac采集器(Tailscale+SSH)+上报8941+飞书(~/luopan-collector)。细节见web-scraping技能第八章
§
Mac上Hermes=launchd服务ai.hermes.gateway(PPID1，供8642+微信端)不需开桌面端；合盖睡眠会停gateway+apex+微信渠道，唤醒后RunAtLoad=false的不自己回。APEX语音UI自研~/apex-src：2026-10-06起不随开机自启(plist已挪到~/apex-src/launchagents/+launchctl disable两道保险)，只双击「APEX 开.app」手动起、关.app停。
§
语音输入(09-12)：手机飞书按住说话(电脑端不支持)→STT硅基Qwen3-ASR(stt.language显式zh)。TTS=edge zh-CN-XiaoyiNeural。改stt/tts免重启网关。/voice on=回语音。
§
维修纪律：证据先行+改代码前立基线、两轮未定位根因即停汇报、长任务离主会话+超60条/new、验收量化。服务器侧改他人代码先立基线；分析中发现的故障只报告别顺手修。⚠️用户账号/外部服务(Antigravity等)写操作——建会话/调用模型/读凭证/消耗配额——必须先获明确授权，只读侦察≠授权，查完先报告再问。细节在Mac端SOUL.md。
§
用户问「选哪个方案/怎么解决」（已给A/B/C）=只在给定选项内给推荐+理由+代价对比，禁发明第四条路、禁顺手执行未批改动（09-15"别绕"）
§
服务器浏览器：browser_exec卡死=直连pypi不通(uvx冷启动卡下载)。修：uv.toml指腾讯云镜像+uv tool install browser-use；常驻Chrome=systemd --user hermes-browser.service(--headless, 9333)，cdp_url须用hermes config set配
§
Yasin的Mac=Intel i7-1068NG7/16G/macOS15.0.1(非M系→Gemini官方Mac App装不了)，未装node/npm。AI分工：DeepSeek主力(便宜/中文)，Gemini只补多模态(图/PDF/超长文)，生视频走火山Seedance。免费额度走AI Studio API(1500次/天,1M)>App(32K)。详见overseas-account-setup技能
§
红线：腾讯云服务器禁装梯子/代理(实据:翻墙直接封禁不警告，当客户端连代理也被封；服务器跑Hermes+16Agent+量化+工具站，封机代价≫收益)。海外模型(Gemini/GPT/Claude)只在Mac侧用(美国节点)，服务器IP调用403→服务器只走国内DeepSeek/硅基流动。OpenRouter在Mac全通，免费50次/天；用户发key要求实测→要跑真实调用给结论
§
升级服务器Hermes：agent跑不了 hermes update/gateway restart(硬黑名单，chmod/heredoc/execute_code/systemd-run包裹全被拒)→唯一正解=用户在飞书发 /update(网关detach跑 hermes update --gateway)。清单见hermes-advanced-setup技能references/update-hermes.md
§
出海与 Upwork 业务基线：Upwork 账号已上线（Yasin G. - E-commerce Consultant | Competitor Audit & Market Research，/hr），已绑定 Payoneer 外币卡（尾号21da，72小时安全锁 10月9日解禁），密保 lucky，首个标杆作品集已发布。所有推送强制双语上下对照（英文在上中文在下），且代码级拦截 interview/call/meeting 实时沟通。
§
AI 高自动化盈利矩阵与被动管道实战操典沉淀于 Obsidian 016 篇：涵盖无脸 YouTube 商业长视频美金 RPM、编程型 SEO 对比站、冷门利基 POD 印刷、Chrome 垂直 Micro-SaaS 插件、高客单合规工作流资产包五大自动化管道，主打 90% 机器执行 + 10% 操盘手终审收款。
§
已蒸馏书籍与知识资产清单：① 墨多《自渡》（2026-10-03，Obsidian 011篇，心力自渡与底层防御系统重构手册，五阶心力飞轮与课题分离商业脱水版）；② 钱婧《新收入》（2026-08-13，副业与一人公司收入结构蒸馏手册）；③ 丹尼尔·卡尼曼《思考，快与慢》（2026-08-10，心智模型与决策认知偏差）；④ 《毛泽东选集》（2026-08-10，战略与一人公司方法论蒸馏手册）。
§
全域唯一 Obsidian 记忆网络已固化：Mac 主库 ~/Documents/Obsidian Vault 与云端服务器 ~/obsidian-vault/Obsidian Vault 100% 双向同构对齐，Antigravity 的 17 篇操典已通过物理软链接挂载进主库并全量同步云端。本地 Hermes、云端 Hermes、Antigravity 与 Yasin 客户端四方完全共享唯一 Obsidian 知识网络。
§
