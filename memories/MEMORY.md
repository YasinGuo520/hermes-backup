沟通极简训斥狠厉语气，流量>产品先给流量方案+SOP。生存模式30天月入1万+0成本启动纯AI文字。三层决策(红蓝→六分身→IPO)，先红蓝+数据验证才能推。产品方案2-3轮迭代，用户自拼方案再执行。不默认服小助示例，不会代码不否决，蓝海可能黑海先验需求，先搜索调研不拍脑袋。
§
项目立项：调用project-four-persona-analysis技能，文件存~/Desktop/hermes/[项目名]/。多项目对比用multi-project-compare模板。
§
量化糅合系统v2: ~/Desktop/hermes/quant-skill/quant_ensemble.py(9维TA+资金流+Kronos本地缓存)。cron 8:45出Top8+板块推荐，收盘15:30自进化。权重tech=0.45/kronos=0.30/flow=0.25。分歧度>0.5跳过>0.3观望。量化看板每日8:50同步。A股标准红涨#ef4444绿跌#22c55e。
§
蒸馏偏好：主动蒸馏大skill成紧凑版，不加载160条规则。精炼cookbook比保留完整理论框架好。
§
前端迭代：先出基础版等他提意见再加/改，不做第三轮新构图。
§
创意页面：先调研全球优秀设计，多阶段叙事+交互元素(气球/礼物盒/confetti/音乐)，全屏沉浸深色系。
§
设计系统：深色科技风(极光粒子+玻璃卡片+渐变紫)>后台管理。不同项目不同风格(杂志/赛博/暗金/玄学/CRT/矩阵/卡通)。背景网格≥0.08opacity粒子≥1.5px连接线≥0.8px。模板优先html5up.net(curl ZIP)部署8890-8899预览。导航Hub深紫渐变+科技网格+紫色网络节点Canvas。
§
硅基流动API: Qwen-Image/Kolors/通义万相，key在.env，出图~/Desktop/hermes/images/。Qwen-Image $0.02/张≈¥0.14，新用户赠14元。python直连会Connection reset必须用curl。
§
Delegation子Agent模板: red-blue-validator/six-persona-analyst/research-agent/executor-agent/qa-reviewer，引用~/Desktop/hermes/agent-templates/。
§
Obsidian vault ~/obsidian-vault/，每4h蒸馏到kb_context.md，新session自动加载。
§
端口清单: 8000=AI爆款主图生成器(Docker), 8001=中年人生, 8002=服小助AI客服, 8894=个人主页, 8895=Hub, 8900=方法论工具箱, 8913=game-zeying, 8915=像素画展厅, 8920=红蓝分析法, 8921=六分身, 8922=市场调研, 8923=行业调研, 8931=机甲3D太空展示(mecha3d)。
§
页面角色/贴纸：直接用AI生成立绘(Qwen-Image→ffmpeg+numpy色键抠图→帧动画+3D视差)，已拍板「以后就直接炫酷角色」，不用CSS手绘。流程在visual-component-patterns技能。
§
红蓝分析法IP视觉语言：蓝=提案/理性(#3b82f6)，红=攻击/质疑(#ef4444)，深黑蓝底+红蓝双色粒子。博主品牌页已定稿portfolio/index.html(8894，英文名Yasin)：Hero=巨型YASIN红蓝渐变(无装饰性标点)+中文细字距标语「决策，不靠感觉」+大留白。第一屏不废话，粗体英文×细字距中文是高端质感来源，按钮最简两字(方法论/案例)。完整指纹在ux-pro-max/references/yasin-personal-homepage.md。
§
火山方舟(ARK): key在/backend/.env的ARK_API_KEY(ark-开头)，base https://ark.cn-beijing.volces.com/api/v3。视频POST /contents/generations/tasks(注意generations非generators)，模型doubao-seedance-1-0-pro-fast-251015(720p≈0.4元/5秒)/1-5-pro-251215/2-0-260128，图片doubao-seedream-5-0-260128。每模型送50万token免费。全链路已跑通。
§
Remotion: ~/Desktop/hermes/remotion-lab (remotion+@remotion/cli+react, chrome-headless-shell已下载, npm腾讯云镜像, 2核机concurrency=2)。代码驱动确定性视频(数据/文字/图表100%精确)，适合量化榜单/数据复盘量产。全流程见skill remotion-video-production。
§
DeepSeek真实API key在Hermes配置.env里，config.yaml里sk-gaw开头key是SiliconFlow不是DeepSeek(当初拿错key报401)。红蓝分析法server.py会自己读.env。
§
AI分析落地页模式(红蓝8920/六分身8921)：FastAPI单服务同端口=静态页面+POST /api/analyze→DeepSeek。提示词内置Yasin铁律(收入打折/区分数据与推断/黑海风险/最小行动单元)。DeepSeek支持response_format json_object。工具箱(8900)卡片加card-link。
§
Mac Tailscale IP 100.80.117.5 (yasin, macOS)，SSH用户mac@。macOS TCC挡SSH读~/Desktop(Operation not permitted)，但~/.hermes/skills可读——跨机同步走skills目录。流程见hermes-multi-machine + html-project-hub。
§
Manim环境: ~/Desktop/hermes/manim-venv (Manim CE v0.20.1, 中文用WenQuanYi Zen Hei)。像素画/展示类用manim-creative-scenes；数学解释用manim-video。
§
像素画展厅(pixel-gallery)8915: Manim动画+3D沉浸环形画廊,manim-venv在~/Desktop/hermes/。动画类任务先给方向选项再全量干(嫌平铺小动画太淡,要整体沉浸式)。
§
图生3D链路(墙内已跑通，演示页8931): 腾讯混元3D API是唯一可用通道(Tripo/Meshy被墙)。密钥在~/Desktop/hermes/mecha3d/.env。关键坑: sk-开头key无效必须AKID签名认证；开通服务后必须手动领免费额度否则ResourceInsufficient；SDK模块ai3d.v20250513非v20241218；pip必须用阿里云镜像(pypi超时/腾讯源ProxyError)；OBJ zip需obj2gltf转GLB；Three.js importmap必须精确到文件不能通配addons/。全流程见skill ai-3d-model-pipeline。
§
服务保活: ~/Desktop/hermes/scripts/keepalive.sh + crontab每3分钟+@reboot(脚本在html-project-hub skill scripts/)。网关重启会杀光background http.server(实测15口剩4口)，批量恢复映射见html-project-hub常见坑6。8000=爆款主图经socat转8080(Docker compose映射8080:8000)，8002=服小助独立venv, 8897=Hermes网关必须用nginx反代改写Host(not socat,否则Invalid Host header 400)。
§
改导航页(Hub 8895)铁律：①先备份build_hub.py+index.html再改(曾覆盖丢深紫科技风) ②只动导航页严禁重启/影响其他端口服务(曾搞挂10+服务) ③挂了用keepalive.sh恢复不手动逐个拉 ④工具箱(8900)card-link(红蓝8920/六分身8921/市场调研8922/行业调研8923)禁止丢失,改完跑~/Desktop/hermes/scripts/linkcheck.sh验证
§
接码hero-sms.com/5sim(sms-activate已于2025-12关停)。
§
英语不好但正主动练听说：ChatGPT语音对话纠错+YouTube英文字幕(0.75倍速)，材料要电商/AI行业向。海外软件优先中文界面，英文界面用AI翻译/截图问AI。
§
ChatGPT已注册成功(美国节点+Apple登录)，免费版，Plus未订阅(升级可走美区礼品卡App内购)