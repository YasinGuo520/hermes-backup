沟通极简训斥狠厉，流量>产品先给流量方案+SOP。生存模式30天月入1万+0成本纯AI文字。三层决策(红蓝→六分身→IPO)，先红蓝+数据验证才能推。产品方案2-3轮迭代，用户自拼方案再执行。不默认服小助示例；蓝海可能黑海先验需求，先调研不拍脑袋。
§
项目立项：调用project-four-persona-analysis技能，文件存~/Desktop/hermes/[项目名]/。多项目对比用multi-project-compare模板。
§
量化糅合系统v2: ~/Desktop/hermes/quant-skill/quant_ensemble.py(9维TA+资金流+Kronos本地缓存)。cron 8:45出Top8+板块，15:30收盘自进化。权重tech=0.45/kronos=0.30/flow=0.25。分歧度>0.5跳过>0.3观望。看板8:50同步。
§
蒸馏偏好：主动蒸馏大skill成紧凑版，不加载160条规则。精炼cookbook比保留完整理论框架好。
§
设计系统：深色科技风(极光粒子+玻璃卡片+渐变紫)>后台；不同项目不同风格(杂志/赛博/暗金/玄学/CRT/矩阵/卡通)；背景网格≥0.08opacity粒子≥1.5px；模板优先html5up.net(curl ZIP)部署8890-8899预览；Hub深紫渐变+科技网格+紫色节点Canvas。前端迭代：先出基础版等提意见再加/改，不做第三轮新构图。创意页先调研全球优秀设计，多阶段叙事+交互元素(气球/礼物盒/confetti/音乐)，全屏沉浸深色系。
§
硅基流动API: Qwen-Image/Kolors/通义万相，key在.env，出图~/Desktop/hermes/images/。Qwen-Image $0.02/张≈¥0.14。python直连会Connection reset必须用curl。
§
Delegation子Agent模板: red-blue-validator/six-persona-analyst/research-agent/executor-agent/qa-reviewer，引用~/Desktop/hermes/agent-templates/。
§
Obsidian vault ~/obsidian-vault/，每4h蒸馏到kb_context.md，新session自动加载。
§
端口清单: 8000=AI爆款主图(Docker), 8001=中年人生, 8002=服小助客服, 8894=个人主页, 8895=Hub, 8900=工具箱, 8913=game-zeying, 8915=像素画展厅, 8920=红蓝, 8921=六分身, 8922=市场调研, 8923=行业调研, 8931=mecha3d。
§
页面角色/贴纸直接用AI生成立绘(Qwen-Image→ffmpeg+numpy色键抠图→帧动画+3D视差)，不用CSS手绘。流程在visual-component-patterns技能。
§
红蓝分析法IP：蓝=提案/理性(#3b82f6)、红=攻击/质疑(#ef4444)，深黑蓝底+红蓝粒子。博主品牌页portfolio/index.html(8894,英文名Yasin)已定稿，Hero=巨型YASIN红蓝渐变+细字距「决策，不靠感觉」+大留白，按钮最简两字。完整指纹在ux-pro-max/references/yasin-personal-homepage.md。
§
火山方舟(ARK): key在/backend/.env的ARK_API_KEY(ark-开头)，base https://ark.cn-beijing.volces.com/api/v3。视频POST /contents/generations/tasks(注意generations非generators)，模型doubao-seedance-1-0-pro-fast-251015(720p≈0.4元/5秒)/1-5-pro-251215/2-0-260128，图片doubao-seedream-5-0-260128。
§
Remotion: ~/Desktop/hermes/remotion-lab，代码驱动确定性视频(数据/文字/图表100%精确)，适合量化榜单/数据复盘量产。全流程见skill remotion-video-production。
§
DeepSeek真实API key在Hermes配置.env里；config.yaml里sk-gaw开头key是SiliconFlow不是DeepSeek。红蓝分析法server.py会自己读.env。
§
AI分析落地页(红蓝8920/六分身8921)：FastAPI单服务同端口=静态页+POST /api/analyze→DeepSeek。提示词内置Yasin铁律(收入打折/区分数据与推断/黑海风险/最小行动单元)。工具箱(8900)card-link。
§
Mac Tailscale IP 100.80.117.5 (yasin, macOS)，SSH用户mac@。macOS TCC挡SSH读~/Desktop(Operation not permitted)，但~/.hermes/skills可读——跨机同步走skills目录。流程见hermes-multi-machine。
§
Manim: ~/Desktop/hermes/manim-venv(CE v0.20.1,中文WenQuanYi Zen Hei)。像素画/展示类用manim-creative-scenes，数学解释用manim-video。像素画展厅(pixel-gallery)8915=Manim+3D沉浸环形画廊；动画类先给方向选项再全量干(要整体沉浸式不要平铺小动画)。
§
图生3D(mecha3d 8931): 腾讯混元3D API唯一可用通道(Tripo/Meshy被墙)。密钥~/Desktop/hermes/mecha3d/.env。坑: sk-开头key无效须AKID签名；开通后手动领免费额度否则ResourceInsufficient；SDK ai3d.v20250513；pip用阿里云镜像。全流程见skill ai-3d-model-pipeline。
§
服务保活: ~/Desktop/hermes/scripts/keepalive.sh + crontab每3分钟+@reboot。网关重启会杀光background http.server，批量恢复见html-project-hub常见坑6。8002=服小助独立venv；8897=Hermes网关必须nginx反代改写Host(否则Invalid Host header 400)。
§
改导航页(Hub 8895)铁律：①先备份build_hub.py+index.html再改(曾覆盖丢深紫科技风) ②只动导航页严禁重启/影响其他端口(曾搞挂10+服务) ③挂了用keepalive.sh恢复 ④工具箱(8900)card-link(红蓝/六分身/市场调研/行业调研)禁止丢失，改完跑linkcheck.sh验证
§
接码hero-sms.com/5sim(sms-activate已于2025-12关停)。
§
英语不好但正主动练听说：ChatGPT语音对话纠错+YouTube英文字幕(0.75倍速)，材料要电商/AI行业向。海外软件优先中文界面，英文界面用AI翻译/截图问AI。