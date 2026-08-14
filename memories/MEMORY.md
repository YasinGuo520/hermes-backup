流量>产品，先给流量方案+SOP。三层决策(红蓝→六分身→IPO)，先红蓝+数据验证。产品方案2-3轮迭代，用户自拼方案再执行。
§
项目立项：调用project-four-persona-analysis技能，文件存~/Desktop/hermes/[项目名]/。
§
量化糅合v2: ~/Desktop/hermes/quant-skill/quant_ensemble.py，权重tech=0.45/kronos=0.30/flow=0.25，flow覆盖<60%降权，命中率50-60%正常；旧系统~/projects/quant_self_evolve.py不相通；--help误触发调权须--report-only；v2按当日口径(verify_v2_daily.py)，backtest是T+1；诊断见a-share-market-data技能。
§
蒸馏偏好：主动蒸馏大skill成紧凑版，不加载160条规则。精炼cookbook比完整理论框架好。
§
设计系统：背景网格≥0.08opacity粒子≥1.5px，模板优先html5up.net(curl ZIP)部署8890-8899，前端先基础版不做第三轮新构图，全屏沉浸深色+交互；页面角色/贴纸用AI生成立绘(Qwen-Image→色键抠图→帧动画+3D视差)不用CSS手绘，见visual-component-patterns。
§
Delegation子Agent模板: red-blue-validator/six-persona-analyst/research-agent/executor-agent/qa-reviewer，见~/Desktop/hermes/agent-templates/。
§
Obsidian vault ~/obsidian-vault/，每4h蒸馏到kb_context.md，新session自动加载。
§
端口清单: 8000=AI爆款主图(Docker), 8001=中年人生, 8002=服小助客服, 8894=个人主页, 8895=Hub, 8900=工具箱, 8913=game-zeying, 8915=像素画展厅, 8920=红蓝, 8921=六分身, 8922=市场调研, 8923=行业调研, 8931=mecha3d。
§
红蓝分析法IP：蓝=提案/理性(#3b82f6)、红=攻击/质疑(#ef4444)，深黑蓝底+红蓝粒子，品牌页指纹见ux-pro-max/references/yasin-personal-homepage.md。落地页(8920红蓝/8921六分身)=FastAPI同端口静态页+POST /api/analyze→DeepSeek，server.py自己读.env，提示词内置铁律(收入打折/区分推断/黑海/最小行动单元)。
§
媒体工具：Remotion ~/Desktop/hermes/remotion-lab；Manim ~/Desktop/hermes/manim-venv(CE v0.20.1,中文字体，像素/展示用manim-creative-scenes，数学用manim-video)；图生3D(8931)腾讯混元3D唯一可用通道(Tripo/Meshy被墙)，密钥~/Desktop/hermes/mecha3d/.env。
§
API：①DeepSeek真key在Hermes配置.env，config.yaml的sk-gaw是SiliconFlow非DeepSeek；官方高峰10-11点503→fallback SiliconFlow(deepseek-ai/DeepSeek-V4-Flash, base_url=api.siliconflow.cn/v1, key_env=SILICONFLOW_API_KEY)；hermes config set存数组变字符串无效须python yaml写列表。②硅基流动key在.env，Qwen-Image $0.02/张≈¥0.14，出图~/Desktop/hermes/images/，python直连Connection reset须curl。③火山方舟key在~/backend/.env ARK_API_KEY，base ark.cn-beijing.volces.com/api/v3，视频/图片接口见volcengine-ark-api技能。
§
Mac Tailscale IP 100.80.117.5 (yasin)，SSH用户mac@。macOS TCC挡SSH读~/Desktop但~/.hermes/skills可读——跨机同步走skills目录。见hermes-multi-machine。
§
接码用hero-sms.com/5sim（sms-activate已停）。
§
英语学习：ChatGPT语音纠错+YouTube英文字幕0.75倍速(电商/AI材料)；海外软件优先中文界面，英文界面AI翻译/截图问AI。2026-08定目标考雅思7分（咨询过计划：12个月每天2h，词汇3000-4000起点，听读冲7.5写作口语6-6.5组合）。
§
远程装Hermes：不配DeepSeek key(安全顾虑)；Windows机SSH连不上用向日葵兜底。
§
Hermes v0.20坑：config.yaml gateway.platforms必须是dict(feishu:{skip_context_files:false})，list格式导致网关崩溃。
§
Cron provider drift：模型配置变更后旧cron被跳过，编辑~/.hermes/cron/jobs.json改provider/model/provider_snapshot/model_snapshot四字段（cronjob update不支持；config.yaml须hermes config set，patch被拒）。根因=v0.20升级冲掉模型配置，OPENAI_API_KEY失败大量fallback走deepseek扣费。默认deepseek/deepseek-v4-flash，模型变更须用户确认。web_search(DDG)从中国服务器持续超时，用curl浏览器UA直抓+AnySearch MCP替代。
§
服务运维：保活~/Desktop/hermes/scripts/keepalive.sh+crontab每3分钟+@reboot；网关重启杀background http.server(恢复见html-project-hub坑6)；8002=服小助独立venv；8897=Hermes网关须nginx反代改写Host。改Hub(8895)铁律：先备份build_hub.py+index.html，只动导航页，挂了keepalive.sh恢复，工具箱(8900)card-link禁丢，改完跑linkcheck.sh。
§
翻墙/机场：联通宽带，主用途GPT+视频；两台iPhone 11共用美区Apple ID(guoyuexing1@outlook.com)下Shadowrocket，一台留iOS 15.7翻墙专用(只切App Store不切iCloud)；FB/TikTok须美国节点+English(US)，TikTok拔SIM卡+时区美国或网页版。机场选型看51fan.pro老牌/稳定分类(软文不可信)；已选飞鸟FlyingBird(¥15/100G全IPLC)+山海(¥6)月付实测，Nexitally/AmyTelecom/MESL/TAG交叉验证过，价格上官网确认。