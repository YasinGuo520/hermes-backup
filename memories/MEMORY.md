流量>产品，先给流量方案+SOP。三层决策(红蓝→六分身→IPO)，先红蓝+数据验证才能推。产品方案2-3轮迭代，用户自拼方案再执行。生存模式目标30天月入1万+0成本纯AI文字。
§
项目立项：调用project-four-persona-analysis技能，文件存~/Desktop/hermes/[项目名]/。
§
量化糅合系统v2: ~/Desktop/hermes/quant-skill/quant_ensemble.py，权重tech=0.45/kronos=0.30/flow=0.25，flow覆盖<60%自动降权，均线多头蓝筹命中率50-60%正常。旧系统~/projects/quant_self_evolve.py互不相通；--help误触发调权须--report-only。v2按推荐当日口径(verify_v2_daily.py)，backtest_quant_logs.py是T+1口径。诊断见a-share-market-data技能。
§
蒸馏偏好：主动蒸馏大skill成紧凑版，不加载160条规则。精炼cookbook比完整理论框架好。
§
设计系统：背景网格≥0.08opacity粒子≥1.5px。模板优先html5up.net(curl ZIP)部署8890-8899预览。前端迭代先出基础版等意见，不做第三轮新构图。全屏沉浸深色+交互元素。
§
Delegation子Agent模板: red-blue-validator/six-persona-analyst/research-agent/executor-agent/qa-reviewer，见~/Desktop/hermes/agent-templates/。
§
Obsidian vault ~/obsidian-vault/，每4h蒸馏到kb_context.md，新session自动加载。
§
端口清单: 8000=AI爆款主图(Docker), 8001=中年人生, 8002=服小助客服, 8894=个人主页, 8895=Hub, 8900=工具箱, 8913=game-zeying, 8915=像素画展厅, 8920=红蓝, 8921=六分身, 8922=市场调研, 8923=行业调研, 8931=mecha3d。
§
页面角色/贴纸用AI生成立绘(Qwen-Image→色键抠图→帧动画+3D视差)，不用CSS手绘，见visual-component-patterns。
§
红蓝分析法IP：蓝=提案/理性(#3b82f6)、红=攻击/质疑(#ef4444)，深黑蓝底+红蓝粒子，品牌页指纹见ux-pro-max/references/yasin-personal-homepage.md。落地页(8920红蓝/8921六分身)=FastAPI同端口静态页+POST /api/analyze→DeepSeek，server.py自己读.env，提示词内置铁律(收入打折/区分推断/黑海/最小行动单元)。
§
Remotion: ~/Desktop/hermes/remotion-lab。见skill remotion-video-production。
§
API密钥/通道：①DeepSeek真key在Hermes配置.env，config.yaml的sk-gaw是SiliconFlow非DeepSeek；官方API高峰10-11点503→fallback SiliconFlow(deepseek-ai/DeepSeek-V4-Flash, base_url=api.siliconflow.cn/v1, key_env=SILICONFLOW_API_KEY)；hermes config set存数组变字符串无效，须python yaml写列表。②硅基流动key在.env，Qwen-Image $0.02/张≈¥0.14，出图~/Desktop/hermes/images/，python直连Connection reset须curl。③火山方舟key在~/backend/.env ARK_API_KEY，base ark.cn-beijing.volces.com/api/v3，视频POST /contents/generations/tasks(generations非generators)，图片doubao-seedream-5-0-260128，Seedance见volcengine-ark-api技能。
§
Mac Tailscale IP 100.80.117.5 (yasin)，SSH用户mac@。macOS TCC挡SSH读~/Desktop但~/.hermes/skills可读——跨机同步走skills目录。见hermes-multi-machine。
§
Manim: ~/Desktop/hermes/manim-venv(CE v0.20.1,中文WenQuanYi Zen Hei)。像素画/展示类用manim-creative-scenes，数学解释用manim-video。
§
图生3D(mecha3d 8931): 腾讯混元3D API唯一可用通道(Tripo/Meshy被墙)，密钥~/Desktop/hermes/mecha3d/.env，见skill ai-image-to-3d。
§
服务保活: ~/Desktop/hermes/scripts/keepalive.sh + crontab每3分钟+@reboot。网关重启会杀background http.server，恢复见html-project-hub坑6。8002=服小助独立venv；8897=Hermes网关须nginx反代改写Host(否则400)。
§
改导航页(Hub 8895)铁律：①先备份build_hub.py+index.html ②只动导航页严禁影响其他端口 ③挂了keepalive.sh恢复 ④工具箱(8900)card-link禁止丢失，改完跑linkcheck.sh。
§
接码hero-sms.com/5sim(sms-activate已于2025-12关停)。
§
英语不好但主动练听说：ChatGPT语音纠错+YouTube英文字幕(0.75倍速)，材料电商/AI向。海外软件优先中文界面，英文界面用AI翻译/截图问AI。
§
远程装Hermes：不配DeepSeek key(安全顾虑，key只在自有环境配)；Windows机SSH连不上用向日葵兜底。
§
Hermes v0.20 config.yaml坑：gateway.platforms必须是dict(feishu:{skip_context_files:false})，list格式会导致网关崩溃。
§
翻墙网络：两台iPhone共用美区Apple ID(guoyuexing1@outlook.com)下Shadowrocket，iPhone 11留iOS 15.7当翻墙专用机（只切App Store不切iCloud）；FB调美国英文内容(电商研究)须美国节点+English(US)。宽带/机场偏好见user profile。
§
网络：联通宽带，翻墙主用途=GPT+视频；有两台iPhone 11，其中一台iOS 15.7留作翻墙专用机（拔SIM卡+美区ID装小火箭，TikTok用拔卡或网页版方案）。对出海有好奇心但未启动（问过LINE/WhatsApp/FB Ads Manager/Product Hunt）。自省：用户承认自己"分析多执行少"，认可"公开承诺+固定发布节奏"是解药——推动他时可用此杠杆（如公开日更、对读者承诺）。
§
机场/NPN翻墙选型：搜索软文站不可信，51fan.pro是相对有用的导航站（有老牌/稳定分类+标注跑路机场）。用户联通宽带去GPT+视频，预算敏感，倾向月付+先试用。最终选飞鸟FlyingBird(¥15/100G全IPLC)+山海(¥6)月付实测。华为CloudFetch/WgetCloud偏贵(¥75起)，Nexitally奶昔(2017最老牌)/AmyTelecom/MESL/TAG品牌交叉验证通过但需用户上官同确认价格。