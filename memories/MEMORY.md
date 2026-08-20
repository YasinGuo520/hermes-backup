流量>产品先给方案+SOP。三层决策(红蓝→六分身→IPO)先红蓝+数据验证。项目立项调project-four-persona-analysis技能，存~/Desktop/hermes/[项目名]/。
§
量化糅合v2: ~/Desktop/hermes/quant-skill/quant_ensemble.py，权重tech=0.45/kronos=0.30/flow=0.25，flow覆盖<60%降权，命中率50-60%正常；旧~projects/quant_self_evolve.py不相通；--help误触发调权须--report-only；当日口径verify_v2_daily.py，backtest是T+1。
§
蒸馏偏好：主动蒸馏大skill成紧凑版，不加载160条规则。精炼cookbook比完整理论框架好。
§
设计系统：背景网格≥0.08opacity粒子≥1.5px，模板优先html5up.net(curl ZIP)部署8890-8899，前端先基础版不做第三轮新构图；页面角色/贴纸用AI生成立绘(Qwen-Image→色键抠图→帧动画+3D视差)不用CSS手绘，见visual-component-patterns。
§
Delegation子Agent模板: red-blue-validator/six-persona-analyst/research-agent/executor-agent/qa-reviewer，见~/Desktop/hermes/agent-templates/。
§
Obsidian vault ~/obsidian-vault/，每4h蒸馏到kb_context.md，新session自动加载。
§
端口清单: 8000=AI爆款主图(Docker), 8001=中年人生, 8002=服小助客服, 8894=个人主页, 8895=Hub, 8900=工具箱, 8913=game-zeying, 8915=像素画展厅, 8920=红蓝, 8921=六分身, 8922=市场调研, 8923=行业调研, 8931=mecha3d。
§
红蓝分析法IP：蓝=提案/理性(#3b82f6)、红=攻击/质疑(#ef4444)，深黑蓝底+红蓝粒子，品牌页指纹见ux-pro-max/references/yasin-personal-homepage.md；落地页(8920红蓝/8921六分身)=FastAPI静态页+POST /api/analyze→DeepSeek，server.py自己读.env，提示词铁律(收入打折/区分推断/黑海/最小行动单元)。
§
媒体工具：Remotion ~/Desktop/hermes/remotion-lab；Manim ~/Desktop/hermes/manim-venv(CE v0.20.1,中文字体，像素/展示用manim-creative-scenes，数学用manim-video)；图生3D(8931)腾讯混元3D唯一可用通道(Tripo/Meshy被墙)，密钥~/Desktop/hermes/mecha3d/.env。
§
API：①DeepSeek真key在Hermes配置.env，config.yaml的sk-gaw是SiliconFlow非DeepSeek；高峰10-11点503→fallback SiliconFlow(deepseek-ai/DeepSeek-V4-Flash, base_url=api.siliconflow.cn/v1, key_env=SILICONFLOW_API_KEY)；config set存数组变字符串无效须python yaml写列表。②硅基流动key在.env，Qwen-Image $0.02/张≈¥0.14，出图~/Desktop/hermes/images/，python直连Connection reset须curl。③火山方舟key在~/backend/.env，接口见volcengine-ark-api。
§
Mac Tailscale IP 100.80.117.5(yasin)，SSH用户mac@；TCC挡SSH读~/Desktop但~/.hermes/skills可读，跨机同步走skills目录。见hermes-multi-machine。
§
接码用hero-sms.com/5sim（sms-activate已停）。
§
远程装Hermes：Mac实例实际配了DeepSeek key且是主要烧费端(¥12-27/天 vs 服务器¥2-3)，查扣费差额先怀疑Mac端cron/新会话；Windows机SSH连不上用向日葵兜底。
§
Hermes v0.20坑：config.yaml gateway.platforms必须是dict(feishu:{skip_context_files:false})，list格式导致网关崩溃。
§
Cron drift：模型变更后旧cron被跳过，编辑~/.hermes/cron/jobs.json改provider/model/provider_snapshot/model_snapshot四字段（cronjob update不支持；config.yaml须hermes config set）。默认deepseek/deepseek-v4-flash，模型变更须用户确认。web_search(DDG)中国服务器持续超时，用curl浏览器UA直抓+AnySearch MCP替代。
§
服务运维：保活~/Desktop/hermes/scripts/keepalive.sh+crontab每3分钟+@reboot；网关重启杀background http.server(html-project-hub坑6)；8002=服小助独立venv；8897=网关须nginx反代改写Host；改Hub(8895)先备份build_hub.py+index.html只动导航页，工具箱(8900)card-link禁丢，改完跑linkcheck.sh。
§
翻墙/机场：联通主用GPT+视频；两台iPhone 11共用美区Apple ID下Shadowrocket，一台留iOS 15.7翻墙专用(只切App Store不切iCloud)；FB/TikTok须美国节点+English(US)，TikTok拔SIM卡或网页版；TikTok唯一高度敏感(切节点=换区+风控)，X/FB/IG/TG/WhatsApp/YouTube/Discord切英国等节点无影响(FB偶弹验证)，频繁横跳才触发风控。已选飞鸟FlyingBird(¥15/100G全IPLC)+山海(¥6)月付，价格上官网确认。TG接入Hermes：国内腾讯云连不上api.telegram.org，须代理或Mac跑，见china-im-channels技能references/telegram.md。
§
小红书2026红线：个人店禁教育类目(2026.4起)，卖课须个体户/企业店+定向邀约+ICP或走第三方(千聊/小鹅通/知识星球)；AI虚假种草=封号+法律风险，AI托管封号13万+，纯AI量产限流，须勾选AI辅助+真人化改写；话术禁收益承诺/虚假人设/私域导流。平台操作类变现必须先查规则再给结论。GPT充值用Pockyt礼品卡最稳(GamsGo拼车不可靠)。
§
拼多多2026运营：赛马制核心(低价爆款+高转化)，流量四来源(搜索/场景/活动/付费)，售后是最大亏点，APP百亿补贴C位。雨刮器(标品)适合百亿补贴/秒杀，服装(非标)适合9块9+场景推荐。
§
Yasin财务紧急(2026-08)：月支1万撑不过1个月，救急赚钱优先，先推执行不谈长期计划。已验证：U客直谈真实(免费版接剪辑单，勿买98联系卡/198会员)、快马日结真实(蓝领150-300/天需出门)、微赚=骗局、短剧出海'一次性费用'=割韭菜、游戏搬砖时薪7-15元不适合；避开一品威客会员费(4.8万)和'免费教学+日350'招聘。剪辑接单渠道：U客直谈/牛片网(需作品集)/圆领/淘宝代剪(300-800/条)，AI视频技能可差异化定价300-500/条。TikTok短剧出海有兴趣：Seedance国内生成+TikTok Drama Center免费翻译，3-6个月项目非救急。
§
DeepSeek key sk-ce1a8ba... 多端共用：服务器Hermes+服小助(ai_cs_package/.env)+红蓝/六分身落地页(server.py硬编码)+Mac实例(主要消耗源)，对账控制台总量>>agent.log=差额在其他端。官方价(2026-08)：v4-flash缓存命中¥0.05-0.1/M、未命中¥1.5-3/M、输出¥4.5-9/M，高峰(北京9-12/14-18)=2倍；每次调用固定5-6万token行李，cron首调用缓存命中仅19-26%。