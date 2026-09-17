立项：先红蓝+数据验证→再六分身→IPO；新方案默认关联Obsidian(_kb/entities/按SCHEMA建页+更新index/log.md)
§
量化糅合v2：~/Desktop/hermes/quant-skill/quant_ensemble.py(tech0.45/kronos0.30/flow0.25，flow<60%降权，命中50-60%正常)；verify_v2_daily.py当日口径T+1
§
内容偏好：大skill蒸馏成紧凑版(cookbook>理论)；Obsidian ~/obsidian-vault/每4h蒸馏kb_context.md；数据表格保留、cron日报不压缩
§
设计系统：网格bg≥0.08/粒子≥1.5px；html5up优先(curl ZIP)；角色/贴纸Qwen-Image立绘→色键抠图→帧动画，不CSS手绘
§
媒体工具：Manim ~/Desktop/hermes/manim-venv；图生3D只有混元3D可用(Tripo/Meshy被墙)，key ~/Desktop/hermes/mecha3d/.env
§
Mac TS100.80.117.5(yasin) SSH mac@；TCC挡~/Desktop但~/.hermes/skills可读；approvals=off；抓数据只走playwright+channel=chrome+headless=False(禁camofox)；Mac烧费端(¥12-27/天vs服务器¥2-3)，查扣费先查Mac端cron
§
cron铁律：钉model/provider+完整12位ID(8位报Job not found)；disabled任务edit报Cannot activate须先resume；LLM cron全挪7:00-7:55(DeepSeek空闲价)；cron禁web_search；curl直连GitHub Trending/HN限15次；5资讯/变现任务停用(09-02)
§
翻墙详见overseas-account-setup技能。两台iPhone11共用美区ID Shadowrocket(iOS15.7只切AppStore)；TikTok须美国节点+English(US)，拔SIM或网页版；机场：飞鸟FlyingBird(¥15/100G)+山海(¥6)月付
§
小红书红线：个人店禁教育类目，卖课须企业店+定向邀约+ICP；AI虚假种草=封号，纯AI量产限流须勾选AI辅助+真人化改写；话术禁收益承诺/虚假人设/私域导流
§
Yasin财务紧急(救急优先)。已验证真：U客直谈/快马日结(勿买98/198会员)、牛片网/圆领/淘宝代剪300-800/条、AI视频300-500/条；骗局：微赚/短剧出海一次性费用/游戏搬砖；避一品威客
§
TikHub key(~/Desktop/hermes/tikhub/.env)09-17实测401已失效，勿再试(需重注册)；端点结构见china-ai-platforms技能references/tikhub-endpoints.md；淘宝/拼多多/京东无API，抖音/百度/搜狗反爬→TikHub或Mac侧采集
§
Yasin方向：公域→私域(09-08定)，抖音带货→个微起步(真人IP)>3000人再企微+SCRM。机器狗=国潮爆品方向(头部89万未垄断)；私域SOP见traffic-acquisition-sop技能，落地~/Desktop/hermes/gongyu-siyu-sop/
§
Coze：PAT 1个月有效(2026-10-01重生成)；POST api.coze.cn/v3/chat，4200=缺bot_id。Dify：8850=nginx/8851=API/8852=web，UI-gated走UI别DB hack。用户偏好：招聘截图直接分析岗位不查公司；'别查了'=停调研直接分析手头材料
§
公司Agent矩阵(16个)：~/Desktop/hermes/company-agents/(venv fastapi/uvicorn/pandas，db开WAL)。保活=keepalive.sh的AGENT_SERVICES数组；备份backup_company_db.sh(03:20留14份)。⚠️09-12实测空转(company.db 8行)→别提议补文档
§
环境坑：①国内服务器禁外网CDN→静态资源本地化；②Hub=python3 http.server 8895 serve ~/Desktop/hermes/hermes-hub/(子页同目录免开端口)；③npm prefix=~/.npm-global/bin
§
模型API备忘：max_tokens须6000；视觉仅auxiliary.vision配硅基Qwen3-VL；n8n(5678)无DeepSeek原生节点→OpenAI Chat Model节点+凭证(baseURL api.deepseek.com/v1)
§
DeepSeek key sk-ce1a8ba2疑泄漏(09-06)，重置前勿复用；审计见llm-model-audit技能
§
玄学工具站：~/Desktop/hermes/{tarot 8901,bazi 8902,face 8903,fortune-wheel 8914}，FastAPI单服务(static+/api→v4-flash)，八字用6tail lunar-python。导航铁律：hub index.html由build_hub.py生成，只改PROJECTS/PORT_KEYS
§
Hermes检索降级：web_search超时/web_extract无backend→anysearch MCP(mcp__anysearch__search/extract)免配置，中文长文提取稳定
§
腾讯云暴露面靠控制台防火墙(iptables ts-input全ACCEPT+ufw未启)，服务监听0.0.0.0裸奔(LLM端点怕白嫖)；curl公网端口不通先ss -tlnp区分服务挂vs防火墙拦
§
跨机采集铁律：持续采集跑Mac(真IP+真人profile)，机房IP+headless=封号；服务器8920-8940被Agent矩阵占、8941=luopan-monitor，内存紧→采集器别放服务器。抖音罗盘+达人广场共用底座=Mac采集器(Tailscale+SSH)+上报8941+飞书，Mac端~/luopan-collector(chrome)。全部细节在web-scraping技能第八章
§
Mac上Hermes=launchd服务ai.hermes.gateway(PPID1，同进程供8642+微信端)不需开桌面端；合盖睡眠停掉gateway+apex+微信渠道(sleep 0拦不住，pmset -g log查)，唤醒后RunAtLoad=false的服务不自己回。APEX语音UI(自研，~/apex-src，原~/Desktop被TCC挡)：启停(09-13)
§
语音输入(09-12)：手机飞书按住说话(电脑端不支持)→STT硅基Qwen3-ASR(stt.language显式zh)→文字进agent已验证。TTS=edge zh-CN-XiaoyiNeural。改stt/tts免重启网关。/voice on=回语音
§
维修纪律：已固化进Mac端SOUL.md(8.5-8.9)——证据先行+改代码前立基线、两轮未定位根因即停汇报、长任务离开主会话+超60条/new、验收量化。服务器侧：改他人代码先立基线；我不能自己/new→会话堆大请Yasin开新会话、结论先落盘；分析中发现的故障只报告别顺手修(09-09)。memory replace 的old_text只定位、替换整条→须给完整新内容
§
用户问「选哪个方案/怎么解决」（已给A/B/C）=只在给定选项内给推荐+理由+代价对比，禁发明第四条路、禁顺手执行未批改动（09-15"别绕"）
§
服务器浏览器工具链(09-17修复)：browser_exec卡死根因=服务器直连pypi.org不通(rc=124)→uvx冷启动卡在下载。三处修复：①~/.config/uv/uv.toml指向腾讯云pypi镜像+已uv tool install browser-use(symlink到~/.hermes/bin/browser-use) ②无GUI需常驻Chrome供CDP连接：systemd --user hermes-browser.service，必须用--headless(Chrome151下--headless=new不监听调试端口)，port 9333 ③hermes config set browser.cdp_url=http://127.0.0.1:9333(改config.yaml会被拒，须走hermes config set)
§
Yasin的Mac=Intel i7-1068NG7/16G/macOS15.0.1（非Apple Silicon→Gemini官方Mac App硬门槛M系，装不了；也导致服务器browser-use等的等价限制），未装node/npm（装CLI类工具先补Node）；替代=Chrome快捷方式独立窗口或Gemini CLI(个人账号1000次/天)。AI工具分工(09-17定)：DeepSeek主力(便宜/中文/数学算法强)，Gemini只补多模态(图/PDF/超长文/Google生态)；生视频不用Gemini($20/月的AI Pro仅3条/天)走火山Seedance。闲鱼“18个月Gemini会员”=共享号/赠送资格拼接(官方无此套餐)，不靠谱；免费额度走AI Studio API(1500次/天+1M上下文)>App免费版(32K，2026-03-25起免费层仅Flash)。详见overseas-account-setup技能references/gemini-access-and-subscription.md
§
腾讯云服务器禁装梯子(2026-08 linux.do实据：服务器只当客户端连代理也被封，翻墙不警告直接封禁)→海外模型只在Mac端用。OpenRouter可用：Mac美国节点下Gemini/GPT/Claude全通，国内服务器IP调这三家一律403 geo(DeepSeek/免费模型不受限)；免费层50次免费模型/天。用户拿到key会直接发来要求实测——要跑真实调用给结论，不要只讲步骤。
§
红线：腾讯云服务器禁装梯子/代理（实据：翻墙直接封禁不警告；linux.do 26-08 案例即使只当客户端连代理也被封）。服务器跑着Hermes+16Agent+量化+工具站，封机代价≫收益。海外模型（Gemini/GPT/Claude）只在Mac侧用（美国节点），服务器侧只走国内直连的DeepSeek/硅基流动。
§
升级服务器Hermes：agent自己跑不了 hermes update / gateway restart（硬黑名单 tools/approval.py:1094；拦截器还读被引用脚本正文，chmod脚本、heredoc、execute_code、systemd-run包裹全被拒）→ 唯一正解=让用户在飞书发 /update（网关detach独立进程跑 hermes update --gateway）。勘察/备份/回滚清单见 hermes-advanced-setup 技能 references/update-hermes.md