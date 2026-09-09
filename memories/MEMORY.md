立项：先红蓝+数据验证→再六分身→IPO；新方案默认关联Obsidian(_kb/entities/按SCHEMA建页+更新index/log.md)，桌面副本~/Desktop/hermes/[项目名]/可选
§
量化糅合v2: ~/Desktop/hermes/quant-skill/quant_ensemble.py，权重tech=0.45/kronos=0.30/flow=0.25，flow<60%降权，命中率50-60%正常；verify_v2_daily.py当日口径,T+1。
§
内容偏好：大skill蒸馏成紧凑版(精炼cookbook>理论框架)；Obsidian ~/obsidian-vault/每4h蒸馏kb_context.md；数据表格保留、cron日报不压缩。
§
设计系统：网格bg≥0.08opacity/粒子≥1.5px；html5up模板优先(curl ZIP)；角色/贴纸Qwen-Image立绘→色键抠图→帧动画，不用CSS手绘
§
媒体工具：Manim ~/Desktop/hermes/manim-venv(CE v0.20.1，展示用manim-creative-scenes，数学用manim-video)；图生3D混元3D唯一可用(Tripo/Meshy被墙)，key~/Desktop/hermes/mecha3d/.env
§
Mac Tailscale 100.80.117.5(yasin)，SSH用户mac@；TCC挡读~/Desktop但~/.hermes/skills可读，跨机同步走skills目录；Mac主要烧费端(¥12-27/天vs服务器¥2-3)，查扣费先怀疑Mac端cron。
§
cron铁律：显式钉model/provider(hermes cron edit --model --provider)，用完整12位ID(8位短ID报Job not found)；disabled任务edit报Cannot activate须先改jobs.json或resume；LLM cron全挪7:00-7:55(DeepSeek 8点前全空闲价)；cron搜索禁web_search，curl直连GitHub Trending/HN/国内媒体+限15次；5个资讯/变现任务已停用(2026-09-02,恢复前不跑)
§
翻墙详见overseas-account-setup技能。Yasin：两台iPhone11共用美区ID Shadowrocket(一台iOS15.7只切AppStore不切iCloud)；TikTok须美国节点+English(US)，拔SIM或网页版(切节点=换区+风控)；机场：飞鸟FlyingBird(¥15/100G全IPLC)+山海(¥6)月付
§
小红书红线：个人店禁教育类目，卖课须企业店+定向邀约+ICP或第三方；AI虚假种草=封号，纯AI量产限流须勾选AI辅助+真人化改写；话术禁收益承诺/虚假人设/私域导流。
§
Yasin财务紧急(月支1万撑不过1月)救急优先。已验证真：U客直谈/快马日结(勿买98/198会员)、牛片网(需作品集)/圆领/淘宝代剪300-800/条、AI视频300-500/条；骗局：微赚/短剧出海'一次性费用'/游戏搬砖(时薪7-15)；避一品威客
§
TikHub key=~/Desktop/hermes/tikhub/.env，api.tikhub.io Bearer认证，402=欠额度；端点/明细→china-ai-platforms技能references/tikhub-endpoints.md；淘宝/拼多多/京东无公开API(蝉妈妈/飞瓜无API)，抖音/百度/搜狗反爬→先走TikHub别爬
§
Yasin方向：公域→私域(2026-09-08定)，抖音带货引流→个微起步(真人IP)>3000人再升级企微+SCRM。机器狗=国潮爆品(对标AI玩具工厂1.5万粉/专场12.4万粉，头部89万未垄断；痛点文案6变体+评论区转化)。私域SOP详版=traffic-acquisition-sop技能references/siyu-chengjie-sop.md；落地版~/Desktop/hermes/gongyu-siyu-sop/
§
Coze：PAT 1个月有效(2026-10-01重生成)；POST api.coze.cn/v3/chat，4200=缺bot_id(bot页URL取)。Dify：8850=nginx/8851=API/8852=web，UI-gated走UI别DB hack(模型=DeepSeek官方同Hermes key)。用户偏好：招聘截图直接分析岗位不查公司；'别查了'=停调研直接分析手头材料
§
公司Agent矩阵(16个,2026-09-02上线,09-09起纳入keepalive保活)：~/Desktop/hermes/company-agents/(common共享db已开WAL+venv fastapi/uvicorn/pandas)，保活=keepalive.sh AGENT_SERVICES数组(曾只靠start_all.sh手动起→09-09发现16个全挂未自愈)；每日备份backup_company_db.sh(03:20留14份)；日志/tmp/agent-*.log
§
环境坑：①国内服务器禁外网CDN——静态资源本地化；②Hub=python3 http.server 8895 serve ~/Desktop/hermes/hermes-hub/，子页同目录免开端口；③npm全局prefix=~/.npm-global/bin(EACCES先改)；④nexscope eCommerce-Skills装Hermes须补顶层name/description(原nexscope:命名空间)；⑤GitHub直连TLS不稳→jsDelivr/raw.githubusercontent，search API无认证60次/h限流
§
模型API备忘：max_tokens须6000(3000-4000长解读会截断)；视觉仅auxiliary.vision配硅基Qwen3-VL(官方deepseek-v4-flash-vision-exp可直调,正文在content)；n8n(5678 docker)无DeepSeek原生节点→OpenAI Chat Model节点+凭证「DeepSeek 官方 (v4-flash)」=openAiApi+baseURL api.deepseek.com/v1,model填deepseek-v4-flash
§
DeepSeek key sk-ce1a8ba2疑泄漏(09-06排查：服务器+Mac日志全flash零pro，控制台pro非本机产生)；重置前勿复用待Yasin API Keys页确认；审计见skill llm-model-audit(devops)
§
玄学工具站(2026-09-07)：~/Desktop/hermes/{tarot 8901,bazi 8902,face 8903,fortune-wheel 8914}；FastAPI单服务(static+/api→v4-flash,key同红蓝)；八字用6tail lunar-python排盘。导航铁律：hermes-hub/index.html由build_hub.py生成、手改会被rebuild覆盖(曾丢Agent入口)——只改PROJECTS/PORT_KEYS，支持path二级页(玄学→8895/xuanxue.html)
§
Hermes检索降级：web_search(DDG)超时/web_extract无extract backend时→anysearch MCP(mcp__anysearch__search/extract)免配置可用，中文长文提取稳定(woshipm/知乎/企微云)
§
磁盘状态(2026-09-09)：69G已用41G余25G；主因containerd 17G(Dify/n8n镜像,full-*容器已停3天镜像未删)；清理待Yasin拍板①prune≈1G②停容器+双tag≈3G③全删≈15G(Dify恢复compose up -d)。排查法见server-service-deployment磁盘节
§
腾讯云防火墙实况(09-09测)：iptables ts-input链全ACCEPT+ufw未启=公网暴露面全靠控制台防火墙，所有服务监听0.0.0.0裸奔风险(LLM端点可被白嫖烧钱)；curl公网端口000可能是服务挂或防火墙拦，先ss -tlnp区分(曾把16服务全挂误判成防火墙)。分析/对比任务中发现的故障只报告别顺手修(用户09-09纠正)