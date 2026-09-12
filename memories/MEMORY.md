立项：先红蓝+数据验证→再六分身→IPO；新方案默认关联Obsidian(_kb/entities/按SCHEMA建页+更新index/log.md)
§
量化糅合v2：~/Desktop/hermes/quant-skill/quant_ensemble.py(tech0.45/kronos0.30/flow0.25，flow<60%降权，命中率50-60%正常)；verify_v2_daily.py当日口径T+1
§
内容偏好：大skill蒸馏成紧凑版(cookbook>理论框架)；Obsidian ~/obsidian-vault/每4h蒸馏kb_context.md；数据表格保留、cron日报不压缩
§
设计系统：网格bg≥0.08/粒子≥1.5px；html5up优先(curl ZIP)；角色/贴纸Qwen-Image立绘→色键抠图→帧动画，不CSS手绘
§
媒体工具：Manim ~/Desktop/hermes/manim-venv；图生3D只有混元3D可用(Tripo/Meshy被墙)，key ~/Desktop/hermes/mecha3d/.env
§
Mac TS100.80.117.5(yasin) SSH mac@；TCC挡~/Desktop但~/.hermes/skills可读，同步走skills；Mac端Hermes approvals已改off(cron/single/unattended=approve,timeout300)——原smart+60s连python3 -c都判ask-approval；SOUL.md新增8.9硬规矩=抓数据只走playwright+channel=chrome+headless=False(禁camofox,Mac无xvfb恒headless)；Mac烧费端(¥12-27/天vs服务器¥2-3)，查扣费先查Mac端cron
§
cron铁律：钉model/provider(cron edit --model --provider)+完整12位ID(8位报Job not found)；disabled任务edit报Cannot activate须先resume/改jobs.json；LLM cron全挪7:00-7:55(DeepSeek 8点前空闲价)；cron禁web_search，curl直连GitHub Trending/HN/国内媒体限15次；5资讯/变现任务停用(09-02)
§
翻墙详见overseas-account-setup技能。两台iPhone11共用美区ID Shadowrocket(iOS15.7那台只切AppStore)；TikTok须美国节点+English(US)，拔SIM或网页版(切节点=风控)；机场：飞鸟FlyingBird(¥15/100G)+山海(¥6)月付
§
小红书红线：个人店禁教育类目，卖课须企业店+定向邀约+ICP；AI虚假种草=封号，纯AI量产限流须勾选AI辅助+真人化改写；话术禁收益承诺/虚假人设/私域导流
§
Yasin财务紧急(月支1万撑不过1月)救急优先。已验证真：U客直谈/快马日结(勿买98/198会员)、牛片网(需作品集)/圆领/淘宝代剪300-800/条、AI视频300-500/条；骗局：微赚/短剧出海一次性费用/游戏搬砖；避一品威客
§
TikHub key=~/Desktop/hermes/tikhub/.env，api.tikhub.io Bearer，402=欠额度；端点→china-ai-platforms技能references/tikhub-endpoints.md；淘宝/拼多多/京东无API(蝉妈妈/飞瓜无)，抖音/百度/搜狗反爬→先走TikHub
§
Yasin方向：公域→私域(09-08定)，抖音带货→个微起步(真人IP)>3000人再企微+SCRM。机器狗=国潮爆品方向(头部89万未垄断)；私域SOP=traffic-acquisition-sop技能references/siyu-chengjie-sop.md，落地~/Desktop/hermes/gongyu-siyu-sop/
§
Coze：PAT 1个月有效(2026-10-01重生成)；POST api.coze.cn/v3/chat，4200=缺bot_id(bot页URL取)。Dify：8850=nginx/8851=API/8852=web，UI-gated走UI别DB hack(模型=DeepSeek官方同Hermes key)。用户偏好：招聘截图直接分析岗位不查公司；'别查了'=停调研直接分析手头材料
§
公司Agent矩阵(16个)：~/Desktop/hermes/company-agents/(venv fastapi/uvicorn/pandas，db开WAL)。保活=keepalive.sh的AGENT_SERVICES数组；备份backup_company_db.sh(03:20留14份)。⚠️09-12实测空转(company.db 8行/最后写09-02/无日志)→别提议补文档
§
环境坑：①国内服务器禁外网CDN→静态资源本地化；②Hub=python3 http.server 8895 serve ~/Desktop/hermes/hermes-hub/，子页同目录免开端口；③npm prefix=~/.npm-global/bin；④GitHub直连TLS不稳→jsDelivr/raw.githubusercontent，search API无认证60次/h限流
§
模型API备忘：max_tokens须6000(3000-4000长解读截断)；视觉仅auxiliary.vision配硅基Qwen3-VL(deepseek-v4-flash-vision-exp可直调)；n8n(5678 docker)无DeepSeek原生节点→OpenAI Chat Model节点+凭证(baseURL api.deepseek.com/v1,model=deepseek-v4-flash)
§
DeepSeek key sk-ce1a8ba2疑泄漏(09-06)，重置前勿复用；审计见llm-model-audit技能
§
玄学工具站：~/Desktop/hermes/{tarot 8901,bazi 8902,face 8903,fortune-wheel 8914}，FastAPI单服务(static+/api→v4-flash)，八字用6tail lunar-python。导航铁律：hub index.html由build_hub.py生成、手改会被rebuild覆盖，只改PROJECTS/PORT_KEYS，支持path二级页(玄学→8895/xuanxue.html)
§
Hermes检索降级：web_search超时/web_extract无backend→anysearch MCP(mcp__anysearch__search/extract)免配置，中文长文提取稳定
§
腾讯云暴露面靠控制台防火墙(iptables ts-input全ACCEPT+ufw未启)，服务监听0.0.0.0裸奔(LLM端点怕白嫖烧钱)；curl公网端口不通先ss -tlnp区分服务挂vs防火墙拦(曾误判)；分析中发现的故障只报告别顺手修(09-09纠正)
§
跨机采集(09-12)：采集跑用户本机(真IP+真profile)，机房IP+headless=封号；cua-driver只驱动本机桌面；优先级=浏览器自动化>SSH>目标机装Hermes>RDP。服务器TS100.105.38.39；8920-8940被Agent矩阵占、8941+空闲、内存剩1.5G→采集器别放服务器。详见web-scraping技能第八章
§
抖音后台采集(09-12)：罗盘盯盘+达人广场共用底座=本机采集器(Tailscale+SSH,只读不点)+上报8941+服务端诊断+飞书。达人广场已跑通(无导出按钮)：拦search_feed_author，列表为内部容器滚动加载(.auxo-table-body,须mouse.move到列表区+wheel1500=1页20条)，Mac端~/luopan-collector(channel=chrome免下chromium)。细节见web-scraping技能第八章
§
~/Desktop/hermes/luopan-monitor(8941，FastAPI+SQLite WAL，X-Token，已入keepalive)：表=creator_list/luopan_snapshot/ingest_log。采集器collectors/*.py跑Mac、走Tailscale上报100.105.38.39:8941(公网未放行)；daren_watch.py=30s增量上报。清洗见db.py
§
Mac语音UI=自研APEX(~/apex-src，原~/Desktop被TCC挡)：桥3210(sounddevice服务端录音,/listen /wake /new)、页面3000、clap-wake；launchd apex-{bridge,clap,ui}(KeepAlive→停用bootout)。麦克风授权在Hermes venv Python不在Chrome(后者恒静音不报错)。左面板=Hermes操作台(打字直驱Mac端agent+朗读)。Mac API 127.0.0.1:8642=有Desktop权限的远程shell。改码：本地改→rsync到Mac→npm run build
§
维修纪律(09-12)：已固化进Mac端SOUL.md(8.5-8.8)——证据先行+改代码前立基线、两轮未定位根因即停汇报、长任务离开主会话+超60条/new、验收必须量化。服务器侧：改他人代码先立基线；我不能自己/new→会话堆大请Yasin开新会话、结论先落盘；'未验'必须在回复里明写。memory replace 的 old_text 只做定位、替换的是整条→必须给完整新内容
§
语音(09-12)：手机飞书按住说话(电脑端不支持)→STT硅基Qwen3-ASR(stt.language显式zh)→文字进agent已验证。TTS=edge zh-CN-XiaoyiNeural。改stt/tts免重启网关。/voice on=回语音
§
APEX：apex.midage.icu(nginx直出/var/www/apex/，APEX_STATIC=1构建)+Mac自用localhost:3000；改名单/交付见server-service-deployment技能(apex-*)。分层铁律=门脸+耳朵+嘴留Mac、业务Agent留服务器；光点实时探测；分身=Hermes profile/Bot Mode。kiosk禁target=_blank(无标签栏回不去)，入口用就地浮层+顶部←；apex-work副本桥TTS_VOLUME未定义勿部署。打断(09-12已验可插话)：apex_barge.py耳朵+桥/state.barge，开口即掐afplay，旋钮在bridge plist env APEX_TTS_VOLUME=0.6/MARGIN=-1.5，改plist须bootout+bootstrap；单拍打断被否(误触发)，拍手只留双击唤醒。详见voice-barge-in技能
§
APEX语音链路加固(09-12)：bridge STT 8s×3重试+全失败出声、语速上限8→11字/秒、页面路径补时长分母、转写打raw；打断基线污染(她的档被插话顶高→越插越插不进)已修=候选期不喂基线+块间宽限APEX_BARGE_GAP_KEEP_S=2.5(真人复验待Yasin)；诊断/事故链见voice-barge-in技能references/