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
英语学习：ChatGPT语音纠错+YouTube英文字幕0.75倍速；海外软件优先中文界面；目标雅思7分(12个月每天2h，词汇3000-4000起点，听读7.5口语6-6.5)。
§
远程装Hermes：不配DeepSeek key(安全顾虑)；Windows机SSH连不上用向日葵兜底。
§
Hermes v0.20坑：config.yaml gateway.platforms必须是dict(feishu:{skip_context_files:false})，list格式导致网关崩溃。
§
Cron drift：模型变更后旧cron被跳过，编辑~/.hermes/cron/jobs.json改provider/model/provider_snapshot/model_snapshot四字段（cronjob update不支持；config.yaml须hermes config set）。默认deepseek/deepseek-v4-flash，模型变更须用户确认。web_search(DDG)中国服务器持续超时，用curl浏览器UA直抓+AnySearch MCP替代。
§
服务运维：保活~/Desktop/hermes/scripts/keepalive.sh+crontab每3分钟+@reboot；网关重启杀background http.server(html-project-hub坑6)；8002=服小助独立venv；8897=网关须nginx反代改写Host；改Hub(8895)先备份build_hub.py+index.html只动导航页，工具箱(8900)card-link禁丢，改完跑linkcheck.sh。
§
翻墙/机场：联通宽带主用GPT+视频；两台iPhone 11共用美区Apple ID下Shadowrocket，一台留iOS 15.7翻墙专用(只切App Store不切iCloud)；FB/TikTok须美国节点+English(US)，TikTok拔SIM卡或网页版；机场看51fan.pro(软文不可信)，已选飞鸟FlyingBird(¥15/100G全IPLC)+山海(¥6)月付实测，价格上官网确认。
§
小红书2026红线（变现建议必带）：个人店禁教育类目(2026.4起)，卖课须个体户/企业店+定向邀约+ICP证，主流玩法=引流+第三方平台(千聊/小鹅通/知识星球)交付；AI批量虚构种草=封号+法律风险(杭州首例判不正当竞争)，AI辅助须勾选标识，纯AI量产限流；话术禁收益承诺/虚假人设/私域导流。用户期望：平台操作类变现建议必须先查平台规则再给结论。