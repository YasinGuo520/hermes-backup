立项流程：三层决策(红蓝→六分身→IPO)，先红蓝+数据验证；调project-four-persona-analysis技能，方案默认关联Obsidian(_kb/entities/按SCHEMA建页+更新index/log.md)，桌面副本~/Desktop/hermes/[项目名]/可选
§
量化糅合v2: ~/Desktop/hermes/quant-skill/quant_ensemble.py，权重tech=0.45/kronos=0.30/flow=0.25，flow<60%降权，命中率50-60%正常；verify_v2_daily.py当日口径,T+1。
§
内容偏好：大skill蒸馏成紧凑版，精炼cookbook>完整理论框架，Obsidian ~/obsidian-vault/每4h蒸馏kb_context.md；caveman skill触发词'caveman mode'/'less tokens'，输出省65%但总账单仅省5-10%；数据表格保留、cron日报不压缩。
§
设计系统：背景网格≥0.08opacity/粒子≥1.5px；模板优先html5up.net(curl ZIP)部署8890-8899，先基础版；角色/贴纸用AI生成立绘(Qwen-Image→色键抠图→帧动画)不用CSS手绘。
§
端口: 8000=AI爆款主图, 8001=中年人生API, 8002=服小助, 8894=中年人生前端, 8895=Hub(用户称"导航仪"), 8900=工具箱, 8913=game-zeying, 8915=像素画展厅, 8920=红蓝, 8921=六分身, 8922=市场调研, 8923=行业调研, 8931=mecha3d, 5678=n8n(待放行)；8924+=电商运营Agent矩阵各Agent工作台页面(方案见OB entities/电商运营Agent矩阵.md)；midage.icu=portfolio走IP:8894
§
媒体工具：Manim ~/Desktop/hermes/manim-venv(CE v0.20.1，展示用manim-creative-scenes，数学用manim-video)；图生3D(8931)混元3D唯一可用(Tripo/Meshy被墙)，key~/Desktop/hermes/mecha3d/.env。
§
Mac Tailscale 100.80.117.5(yasin)，SSH用户mac@；TCC挡读~/Desktop但~/.hermes/skills可读，跨机同步走skills目录；Mac主要烧费端(¥12-27/天vs服务器¥2-3)，查扣费先怀疑Mac端cron。
§
cron铁律：须显式钉model/provider(hermes cron edit --model --provider，用完整12位ID，8位短ID报Job not found)；disabled任务edit报Cannot activate须先改jobs.json或resume。避高峰：DeepSeek官方9点起高峰、8点前全空闲价→LLM cron已全挪7:00-7:55(三合一7:10/英语7:30/看板同步7:50)；注意变现日报cbab278b/AI资讯99bf3a31/GitHub热门580726f6/量化早报ea324446/自进化4b176d3f共5任务已停用(2026-09-02确认,恢复前不跑)。cron搜索禁web_search走ddgs，改curl直连GitHub Trending/HN Algolia/国内媒体+限15次。
§
翻墙：两台iPhone 11共用美区ID Shadowrocket，一台留iOS 15.7专用(只切App Store不切iCloud)；TikTok切节点=换区+风控，FB/TikTok须美国节点+English(US)，TikTok拔SIM卡或网页版；机场飞鸟FlyingBird(¥15/100G全IPLC)+山海(¥6)月付。
§
小红书红线：个人店禁教育类目，卖课须企业店+定向邀约+ICP或第三方；AI虚假种草=封号，纯AI量产限流须勾选AI辅助+真人化改写；话术禁收益承诺/虚假人设/私域导流。
§
Yasin财务紧急：月支1万撑不过1个月，救急优先。已验证真实：U客直谈/快马日结(勿买98/198会员)；骗局：微赚、短剧出海'一次性费用'、游戏搬砖(时薪7-15)；避一品威客。剪辑接单：U客直谈/牛片网(需作品集)/圆领/淘宝代剪300-800/条，AI视频300-500/条。
§
环境坑：国内服务器页面禁用外网CDN(Tailwind等)——已本地化服小助static/tailwind.js(6页改引用)；pip/uv ProxyError先unset http_proxy https_proxy all_proxy
§
TikHub API已打通(key在~/Desktop/hermes/tikhub/.env)：抖音数据主源，api.tikhub.io Bearer认证，免费端点billboard/fetch_hot_account_search_list(搜账号)+热榜+get_user_info，付费handler_user_profile_v4(画像)+fetch_user_post_videos(视频)；402=欠额度。淘宝/拼多多/京东无公开API，蝉妈妈/飞瓜无API；抖音/百度/搜狗全反爬→先走TikHub别爬
§
Yasin方向转向(2026-08-30)：AI项目变现难→直播达人带货+短视频带货。对标：AI智能玩具源头工厂(1.5万粉,小号起量)+AI智能机器狗专场(12.4万粉,腰部)；机器狗=2026国潮爆品，赛道头部89万粉未垄断、新人仍有空间。复制：痛点文案模板(孩子难哄/养狗/送礼6变体)+评论区转化。红蓝博主定位已让位给带货执行。
§
Coze：星刃bot免费额度耗尽会哑火(已发飞书,不在服务器)；PAT pat_开头1个月有效(2026-10-01须重生成)；POST api.coze.cn/v3/chat，4200=缺bot_id(bot页URL取)。Dify已部署：8850=nginx入口、8851=API、8852=web容器；模型未配，配时用DeepSeek官方非硅基(同Hermes key)。用户偏好：发招聘截图=分析岗位工作内容(职责拆解/死法活法/技能对照表)不查公司背景；说'别查了'=停止调研直接分析手头材料。
§
电商运营Agent矩阵项目(2026-09-02立项)：自用版16个agent，全挂Hub「⚙️公司流程化Agent」单入口→agent-hub.html二级页(走8895同目录免开端口)，端口8924-8940(8931已被mecha3d占)；数据=抖音TikHub自动+淘宝Excel手工上传(无API)；无定时任务先做页面(每页手动触发按钮)；分批：第一批①统筹8924/⑪选品8935/⑬库存8938/⑯财务8940，第二批②销售8928/③趋势8929/⑭供应链8937/⑮物流8939，第三批⑤招聘8925/④培训8927/⑦绩效8926/⑨合规8933/⑩舆情8934/⑧内容8932/⑥流程8930；费用：开发¥3-5一次性+运行¥1-2/月(无定时)
§
环境坑：Hub=python3 http.server 8895，serve ~/Desktop/hermes/hermes-hub/，同目录放子页免开防火墙；npm全局前缀已改~/.npm-global/bin(装全局包报EACCES先改prefix)；1688-cli v0.1.47已装此前缀下；nexscope eCommerce-Skills(nexscope-ai)的SKILL.md frontmatter是nexscope:命名空间，装Hermes必须补顶层name/description字段否则不识别；GitHub直连TLS不稳→jsDelivr/raw.githubusercontent拉文件，GitHub search API无认证60次/时限流
§
公司流程化Agent部署状态(2026-09-02)：16个全上线，~/Desktop/hermes/company-agents/（common共享层+每agent目录+公共venv），批量启动start_all.sh（脚本内&循环，terminal background=true；禁止前台&/nohup），日志/tmp/agent-*.log，静态页改动免重启。端口：8924统筹/8925招聘/8926绩效/8927培训/8928销售/8929趋势/8930流程/8932内容/8933合规/8934舆情/8935选品/8936数据/8937供应链/8938库存/8939物流/8940财务。Hub二级页=8895/agent-hub.html(16卡全在线)。设计：design-system.md v2（深蓝科技风统一视觉+每页布局各异+页头居中放大；极简炭黑被Yasin否决；批量页面禁止统一模板），详见server-service-deployment技能references/deep-blue-tech-design-system.md。TikHub端点实测详见china-ai-platforms技能references/tikhub-endpoints.md。
§
模型锁死铁律(2026-09-02更新)：只允许deepseek-v4-flash禁v4-pro/chat/reasoner；渠道已全切DeepSeek官方(api.deepseek.com/v1, provider=deepseek, key=${DEEPSEEK_API_KEY})：Hermes主模型+compression+session_search+cron 73d214f4英语/791dff1e记忆瘦身/e88a6c79三合一+16agents公共层llm.py；硅基仅剩auxiliary.vision(Qwen3-VL)。切因：硅基V4-Flash涨价=官方同价(高峰in3/out9、空闲in1.5/out4.5)但缓存0.15-0.30贵3倍、高峰18h/天(0-2/8-24)远宽于官方5h(工作日9-12/14-18)→官方省35-50%。官方余额2026-09-02=¥9.47需充值(platform.deepseek.com/user/balance查)。Qwen-Image $0.02/张 python直连报错须curl；火山方舟key在~/backend/.env。Dify待配模型用DeepSeek官方非硅基。