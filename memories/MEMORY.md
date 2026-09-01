立项流程：三层决策(红蓝→六分身→IPO)先红蓝+数据验证，流量>产品先给方案+SOP；调project-four-persona-analysis技能，存~/Desktop/hermes/[项目名]/；Delegation模板见agent-templates/。红蓝IP：蓝=提案/理性(#3b82f6)、红=攻击/质疑(#ef4444)，深黑蓝底+红蓝粒子，品牌页指纹ux-pro-max/references/yasin-personal-homepage.md；落地页=FastAPI静态页+POST /api/analyze→DeepSeek，server.py自读.env，提示词铁律(收入打折/区分推断/黑海/最小行动单元)。
§
量化糅合v2: ~/Desktop/hermes/quant-skill/quant_ensemble.py，权重tech=0.45/kronos=0.30/flow=0.25，flow覆盖<60%降权，命中率50-60%正常；当日口径verify_v2_daily.py，backtest T+1；--help误触发调权须--report-only。
§
蒸馏偏好：大skill蒸馏成紧凑版，精炼cookbook>完整理论框架；Obsidian vault ~/obsidian-vault/每4h蒸馏到kb_context.md。
§
设计系统：背景网格≥0.08opacity粒子≥1.5px，模板优先html5up.net(curl ZIP)部署8890-8899，前端先基础版不做第三轮新构图；角色/贴纸用AI生成立绘(Qwen-Image→色键抠图→帧动画+3D视差)不用CSS手绘。
§
端口: 8000=AI爆款主图, 8001=中年人生API, 8002=服小助, 8894=中年人生前端(反代8001), 8895=Hub, 8900=工具箱, 8913=game-zeying, 8915=像素画展厅, 8920=红蓝, 8921=六分身, 8922=市场调研, 8923=行业调研, 8931=mecha3d, 5678=n8n(2026-09部署,公网待放行)；midage.icu=portfolio(郭岳兴)，中年人生走IP:8894
§
媒体工具：Remotion ~/Desktop/hermes/remotion-lab；Manim ~/Desktop/hermes/manim-venv(CE v0.20.1,中文字体，像素/展示用manim-creative-scenes，数学用manim-video)；图生3D(8931)混元3D唯一可用(Tripo/Meshy被墙)，密钥~/Desktop/hermes/mecha3d/.env。
§
API：主模型=硅基custom(deepseek-ai/DeepSeek-V4-Flash, api.siliconflow.cn/v1, key=${SILICONFLOW_API_KEY})；fallback=官方deepseek-v4-flash(DEEPSEEK_API_KEY)；compression/session_search同硅基。价(硅基)：入¥1/M出¥2/M缓存¥0.02/M无高峰加成，比官方便宜55-78%。config set写数组变字符串须python yaml。DeepSeek key多端共用(服务器+服小助ai_cs_package/.env+落地页server.py+Mac)，每调用5-6万token行李，cron首调缓存命中19-26%。②硅基key在.env，Qwen-Image $0.02/张≈¥0.14，python直连报错须curl。③火山方舟key在~/backend/.env，见china-ai-platforms技能
§
Mac Tailscale IP 100.80.117.5(yasin)，SSH用户mac@；TCC挡读~/Desktop但~/.hermes/skills可读，跨机同步走skills目录。Mac是主要烧费端(¥12-27/天 vs 服务器¥2-3)，查扣费差额先怀疑Mac端cron/新会话；Windows SSH连不上用向日葵兜底。
§
web_search国内超时→AnySearch MCP；抓URL用mcp__anysearch__extract
§
cron铁律：须显式钉model/provider(hermes cron edit <id> --model <m> --provider <p>)，否则服务商/模型切换后未钉模型的cron被安全阀静默跳过连挂数天(2026-08晨间三合一挂3天实例)；LLM任务9点前跑完避高峰价：8:00英语(单独,早上要用)+8:30晨间三合一(资讯+变现案例+GitHub,多部分单任务省首调全价)；cron搜索禁web_search走ddgs(国内超时+50次保护空转)，改curl直连GitHub Trending/HN Algolia/国内科技媒体兜底+每部分限15次(已注入prompt)
§
翻墙：两台iPhone 11共用美区ID下Shadowrocket，一台留iOS 15.7翻墙专用(只切App Store不切iCloud)；TikTok高度敏感(切节点=换区+风控)，FB/TikTok须美国节点+English(US)，TikTok拔SIM卡或网页版，其余平台切英国等节点无影响(FB偶验证)。机场飞鸟FlyingBird(¥15/100G全IPLC)+山海(¥6)月付。
§
小红书2026红线：个人店禁教育类目，卖课须个体户/企业店+定向邀约+ICP或第三方(千聊/小鹅通/知识星球)；AI虚假种草=封号+法律风险，AI托管封号13万+，纯AI量产限流，须勾选AI辅助+真人化改写；话术禁收益承诺/虚假人设/私域导流。平台变现先查规则再给结论。
§
拼多多2026运营：赛马制核心(低价爆款+高转化)，流量四来源(搜索/场景/活动/付费)，售后是最大亏点，APP百亿补贴C位。雨刮器(标品)适合百亿补贴/秒杀，服装(非标)适合9块9+场景推荐。
§
Yasin财务紧急：月支1万撑不过1个月，救急赚钱优先。已验证：U客直谈真实(勿买98/198会员)、快马日结真实(蓝领150-300/天需出门)、微赚=骗局、短剧出海'一次性费用'=割韭菜、游戏搬砖时薪7-15不适合；避一品威客(4.8万会员费)。剪辑接单：U客直谈/牛片网(需作品集)/圆领/淘宝代剪300-800/条，AI视频差异化300-500/条。TikTok短剧出海：Seedance国内生成+TikTok Drama Center免费翻译，3-6个月非救急。接码：hero-sms.com/5sim(sms-activate已停)
§
模型锁死铁律(Yasin指令)：所有任务只允许deepseek-v4-flash，禁v4-pro/chat/reasoner。已强制：Hermes主模型=硅基deepseek-ai/DeepSeek-V4-Flash；落地页(8920-8923)server.py硬编码；服小助config硬编码。
§
代理坑：pip/uv报ProxyError先unset http_proxy https_proxy all_proxy；pip走腾讯内网源mirrors.tencentyun.com(pip.conf已配)；升级Hermes用gitcode镜像(git ls-remote gitcode HEAD查真实版本，GitHub被墙时git fetch origin可能静默失败exit 0)。
§
caveman skill已装：触发词'caveman mode'/'less tokens'，输出token省65%但总账单仅省5-10%(费用大头在输入·未命中缓存)；Yasin的数据表格保留、cron日报内容不压缩。
§
抖音视频页提取：browser_navigate到www.douyin.com/video/<id>+browser_console取document.title+meta[name=description]+body.innerText，一次拿全标题/作者/点赞/章节要点(AI摘要)；curl抓HTML是混淆JS没用；勿用web_extract抓URL(ddgs仅搜索)
§
TikHub API已打通(key在~/Desktop/hermes/tikhub/.env)：抖音数据主源，base api.tikhub.io Bearer认证，免费端点billboard/fetch_hot_account_search_list(搜账号)+热榜+get_user_info，付费handler_user_profile_v4(画像)+fetch_user_post_videos(视频)；openapi.json查端点方法；402=需付费额度/405=方法错/422=body字段错(如fetch_query_user要ttwid cookie)。淘宝/拼多多/京东无公开数据API(销售数据锁商家后台)；蝉妈妈/飞瓜无API；抖查查/FastMoss有API需账号。抖音/百度/搜狗全反爬→先走TikHub别爬
§
Yasin方向转向(2026-08-30明确)：AI项目变现难→直播达人带货+短视频带货。对标账号：AI智能玩具源头工厂(1.5万粉,小号起量打法)+AI智能机器狗专场(12.4万粉,腰部)，机器狗=2026国潮玩具爆品，赛道头部89万粉未垄断、新人仍有空间。复制打法：痛点场景文案模板(孩子难哄/养狗/送礼6变体)+评论区转化。之前红蓝方法论博主定位已让位给带货执行。
§
性能规则：fallback_providers须清空(DeepSeek官方欠费，硅基失败时fallback白跑10-30秒拖慢全局)；硅基掉线不严重→清空fallback；严重→火山方舟兜底；全局变慢先查fallback
§
运维：保活scripts/keepalive.sh+crontab每3分钟+@reboot；网关重启杀background http.server(hub坑6)；8897=网关须nginx反代改写Host；改Hub/工具箱只动导航页/勿丢card-link，改完跑linkcheck.sh
§
__tmp_usage_check__
§
Coze/扣子：星刃bot=Yasin的Coze bot(已发飞书,不在服务器)，免费额度耗尽会哑火；PAT pat_开头 1个月有效(约2026-10-01到期须重生成，到期前提醒Yasin)；API主端点POST api.coze.cn/v3/chat，认证过=4200缺bot_id，bot_id从bot页面URL取。Dify已部署(2026-09-01)：8850=nginx统一入口(web/install向导)、8851=API、8852=web容器内；Postgres+Redis+Chroma；模型未配，待控制台加SiliconFlow。端口8800/8851/8852已占用。用户偏好：发招聘截图=要分析岗位工作内容本身(职责拆解/死法活法/技能对照表)，不是查公司背景；用户说"别查了"=立即停止外部调研，直接分析手头材料。