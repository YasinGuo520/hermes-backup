流量>产品，先给流量方案+SOP。三层决策(红蓝→六分身→IPO)，先红蓝+数据验证才能推。产品方案2-3轮迭代，用户自拼方案再执行。生存模式目标30天月入1万+0成本纯AI文字。
§
项目立项：调用project-four-persona-analysis技能，文件存~/Desktop/hermes/[项目名]/。多项目对比用multi-project-compare模板。
§
量化糅合系统v2: ~/Desktop/hermes/quant-skill/quant_ensemble.py，日志logs/*.json，权重tech=0.45/kronos=0.30/flow=0.25，flow覆盖<60%自动降权，本质均线多头蓝筹选股器命中率50-60%正常。15:30"自进化"是旧系统~/projects/quant_self_evolve.py(因子权重版，日志quant_recommend_log.json)，两套日志权重互不相通；--help误触发调权，看报告必须--report-only。v2准确率按推荐当日口径(verify_v2_daily.py)，backtest_quant_logs.py是T+1口径。诊断见a-share-market-data技能references/quant-ensemble-health-diagnostics.md。
§
蒸馏偏好：主动蒸馏大skill成紧凑版，不加载160条规则。精炼cookbook比保留完整理论框架好。
§
设计系统：背景网格≥0.08opacity粒子≥1.5px。模板优先html5up.net(curl ZIP)部署8890-8899预览。前端迭代先出基础版等意见，不做第三轮新构图。创意页先调研全球优秀案例，全屏沉浸深色系+交互元素。
§
硅基流动API: Qwen-Image/Kolors/通义万相，key在.env，出图~/Desktop/hermes/images/。Qwen-Image $0.02/张≈¥0.14。python直连会Connection reset必须用curl。
§
Delegation子Agent模板: red-blue-validator/six-persona-analyst/research-agent/executor-agent/qa-reviewer，见~/Desktop/hermes/agent-templates/。
§
Obsidian vault ~/obsidian-vault/，每4h蒸馏到kb_context.md，新session自动加载。
§
端口清单: 8000=AI爆款主图(Docker), 8001=中年人生, 8002=服小助客服, 8894=个人主页, 8895=Hub, 8900=工具箱, 8913=game-zeying, 8915=像素画展厅, 8920=红蓝, 8921=六分身, 8922=市场调研, 8923=行业调研, 8931=mecha3d。
§
页面角色/贴纸用AI生成立绘(Qwen-Image→色键抠图→帧动画+3D视差)，不用CSS手绘。见visual-component-patterns技能。
§
红蓝分析法IP：蓝=提案/理性(#3b82f6)、红=攻击/质疑(#ef4444)，深黑蓝底+红蓝粒子。品牌页指纹见ux-pro-max/references/yasin-personal-homepage.md。
§
火山方舟(ARK): key在/backend/.env的ARK_API_KEY，base https://ark.cn-beijing.volces.com/api/v3。视频POST /contents/generations/tasks(注意generations非generators)，模型doubao-seedance-1-0-pro-fast-251015(720p≈0.4元/5秒)/1-5-pro-251215/2-0-260128，图片doubao-seedream-5-0-260128。
§
Remotion: ~/Desktop/hermes/remotion-lab，代码驱动确定性视频，适合量化榜单/数据复盘量产。全流程见skill remotion-video-production。
§
DeepSeek真实API key在Hermes配置.env里；config.yaml里sk-gaw开头key是SiliconFlow不是DeepSeek。红蓝分析法server.py会自己读.env。
§
AI分析落地页(红蓝8920/六分身8921)：FastAPI单服务同端口=静态页+POST /api/analyze→DeepSeek。提示词内置Yasin铁律(收入打折/区分推断/黑海/最小行动单元)。工具箱(8900)card-link。
§
Mac Tailscale IP 100.80.117.5 (yasin, macOS)，SSH用户mac@。macOS TCC挡SSH读~/Desktop，但~/.hermes/skills可读——跨机同步走skills目录。见hermes-multi-machine。
§
Manim: ~/Desktop/hermes/manim-venv(CE v0.20.1,中文WenQuanYi Zen Hei)。像素画/展示类用manim-creative-scenes，数学解释用manim-video。动画类先给方向选项再全量干(要整体沉浸式不要平铺小动画)。
§
图生3D(mecha3d 8931): 腾讯混元3D API唯一可用通道(Tripo/Meshy被墙)。密钥~/Desktop/hermes/mecha3d/.env。坑与全流程见skill ai-image-to-3d。
§
服务保活: ~/Desktop/hermes/scripts/keepalive.sh + crontab每3分钟+@reboot。网关重启会杀光background http.server，批量恢复见html-project-hub常见坑6。8002=服小助独立venv；8897=Hermes网关必须nginx反代改写Host(否则Invalid Host header 400)。
§
改导航页(Hub 8895)铁律：①先备份build_hub.py+index.html ②只动导航页严禁重启/影响其他端口(曾搞挂10+服务) ③挂了用keepalive.sh恢复 ④工具箱(8900)card-link禁止丢失，改完跑linkcheck.sh验证。
§
接码hero-sms.com/5sim(sms-activate已于2025-12关停)。
§
英语不好但正主动练听说：ChatGPT语音对话纠错+YouTube英文字幕(0.75倍速)，材料要电商/AI行业向。海外软件优先中文界面，英文界面用AI翻译/截图问AI。
§
远程装Hermes：不配DeepSeek key（安全顾虑，key只在自有环境配）；Windows机SSH连不上用向日葵兜底。
§
DeepSeek官方API高峰(国内上午10-11点)503过载，已配fallback→SiliconFlow(deepseek-ai/DeepSeek-V4-Flash, base_url=https://api.siliconflow.cn/v1, key_env=SILICONFLOW_API_KEY)。hermes config set存数组变字符串无效，必须python yaml写列表。
§
Hermes v0.20 config.yaml坑：gateway.platforms必须是dict(feishu:{skip_context_files:false})，list格式会让网关崩溃AttributeError(list has no attribute get, gateway/run.py:4457)。