沟通极简训斥狠厉语气，流量>产品先给流量方案+SOP。生存模式30天月入1万+0成本启动纯AI文字。三层决策(红蓝→六分身→IPO)，先红蓝+数据验证才能推。产品方案2-3轮迭代，用户自拼方案再执行。幻觉模式：不服小助默认例，不会代码不否决，蓝海可能黑海先验需求。先搜索调研不拍脑袋。
§
项目立项：调用project-four-persona-analysis技能，文件存~/Desktop/hermes/[项目名]/。多项目对比用multi-project-compare模板。
§
Yasin(郭岳兴)电商创业者，服小助AI客服SaaS+CHAOKE潮客+量化A股+抖音选品。华南理工计算机本科，43岁，18年电商运营。腾讯云43.138.221.174，DeepSeek V4-Flash。个体户可开抖店/拼多多。
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
硅基流动API: Qwen-Image/Kolors/通义万相，key在.env，出图~/Desktop/hermes/images/。Qwen-Image $0.02/张≈¥0.14，新用户赠14元额度。python直连会Connection reset必须用curl。
§
Delegation子Agent模板: red-blue-validator/six-persona-analyst/research-agent/executor-agent/qa-reviewer，引用~/Desktop/hermes/agent-templates/。
§
Obsidian vault ~/obsidian-vault/，每4h蒸馏到kb_context.md，新session自动加载。技能档案库含124活跃+15归档skill，归档可restore后用。
§
端口清单: 8000=服小助, 8001=中年人生, 8894=个人主页, 8895=Hub, 8900=方法论工具箱, 8913=game-zeying, 8915=像素画展厅(pixel-gallery, Manim动画版), 8920=红蓝分析法(systemd: red-blue), 8921=六分身(systemd: six-persona), 8922=市场调研(systemd: market-research), 8923=行业调研(systemd: industry-research)。方法论落地页统一模式：FastAPI+DeepSeek JSON输出，页面顶部展示分析逻辑，工具箱卡片加card-link。
§
页面角色/贴纸偏好：直接用AI生成立绘方案（Qwen-Image生成→ffmpeg+numpy色键抠图→帧动画+3D视差），用户已拍板「以后就直接炫酷角色」，不再用CSS手绘。完整流程已沉淀在visual-component-patterns技能。
§
红蓝分析法IP视觉语言：蓝=提案/理性(#3b82f6)，红=攻击/质疑(#ef4444)，深黑蓝底+红蓝双色粒子。博主品牌页已定稿portfolio/index.html(8894，英文名Yasin)：Hero=巨型YASIN红蓝渐变(无装饰性标点，用户觉得点号不协调)+中文细字距标语「决策，不靠感觉」+大留白极简。用户明确偏好：第一屏不要废话不要塞信息，粗体英文×细字距中文的对比是高端大气质感来源，按钮文案最简两字(方法论/案例)。完整指纹在ux-pro-max/references/yasin-personal-homepage.md。
§
火山方舟(ARK)已配置: key在/backend/.env的ARK_API_KEY(ark-开头)，base https://ark.cn-beijing.volces.com/api/v3。视频生成POST /contents/generations/tasks(注意generations非generators)，模型doubao-seedance-1-0-pro-fast-251015(720p≈0.4元/5秒,40秒出片)/1-5-pro-251215/2-0-260128，图片doubao-seedream-5-0-260128。每个模型送50万token免费。测试视频在~/Desktop/hermes/ark-video/cat_test.mp4。全链路已跑通。
§
Remotion已装 ~/Desktop/hermes/remotion-lab（remotion+@remotion/cli+react，chrome-headless-shell已下载，npm用腾讯云镜像）。代码驱动确定性视频（数据/文字/图表100%精确），与AI生视频互补，适合量化榜单/数据复盘类量产。
§
Remotion视频渲染已配置: ~/Desktop/hermes/remotion-lab (remotion+@remotion/cli+react, chrome-headless-shell已下载)。2核机concurrency=2。全流程+模板见skill remotion-video-production。
§
DeepSeek 真实API key在Hermes配置的.env文件里，config.yaml里的sk-gaw开头key是SiliconFlow的不是DeepSeek的（当初拿错key调DeepSeek报401）。红蓝分析法server.py会自己读.env。
§
AI分析落地页模式（红蓝8920/六分身8921）：FastAPI单服务同端口=静态页面+POST /api/analyze→DeepSeek。提示词内置Yasin铁律（收入打折/区分数据与推断/黑海风险/最小行动单元）。DeepSeek支持response_format json_object。工具箱(8900)卡片加card-link指向落地页。
§
Mac Tailscale IP 100.80.117.5 (yasin, macOS)，SSH 用户 mac@，已配 7890 代理隧道。macOS TCC 拦 SSH 读 ~/Desktop（Operation not permitted），但 ~/.hermes/skills 可读。跨机 skill 对比流程见 hermes-multi-machine §9。
§
Mac Tailscale IP 100.80.117.5，SSH 用户 mac@。macOS TCC 挡 SSH 读 ~/Desktop（Operation not permitted），但 ~/.hermes/skills 可读——跨机 skill 同步走 skills 目录。跨机同步/筛选/工具箱更新流程见 hermes-multi-machine + html-project-hub。
§
Manim环境: ~/Desktop/hermes/manim-venv (Manim CE v0.20.1, 中文用WenQuanYi Zen Hei字体)。像素画/展示类动画用manim-creative-scenes技能；数学解释视频用manim-video(bundled)。
§
像素画展厅(pixel-gallery)8915端口已升级为Manim动画+3D沉浸环形画廊，manim-venv在~/Desktop/hermes/。Yasin对「10个独立小动画」方案说太平淡，要整体沉浸式(3D页面/巡游大片)——动画类任务先给方向选项再全量干。