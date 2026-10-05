# Yasin 个人主页 — 红蓝品牌双色完整指纹

> 落地：`~/Desktop/hermes/portfolio/index.html`，端口 8894，2026-07-31 由简历页(求职向)改写为博主品牌页。
> 用途：下次做「红蓝分析法 / 创业方法论博主」相关页面直接复用本指纹，不重新发明。

## 定位

- 英文名 **Yasin**（Hero 主显），中文名郭岳兴
- Hero 标语（定稿）：**决策，不靠感觉**（短句，有观点；「帮创业者少踩坑的实战派」已被否——太长、偏描述）
- 差异化：红蓝分析法 + 六分身全方位分析 两套方法论体系

## 色值（CSS变量）

```css
:root{
  --bg:#05060a;            /* 页面底 */
  --bg-panel:#0a0d18;      /* 卡片底 */
  --bg-elev:#101528;       /* 悬浮层 */
  --text:#f2f4f8;
  --text-dim:#a8b0c5;
  --text-mute:#5d6783;
  --red:#ef4444;           /* 攻击/质疑/风险/案例数据 */
  --red-dim:rgba(239,68,68,.12);
  --blue:#3b82f6;          /* 提案/理性/信任/主CTA */
  --blue-dim:rgba(59,130,246,.12);
  --violet:#8b5cf6;        /* 案例状态标签 */
  --border:rgba(255,255,255,.07);
}
```

## 背景三层

1. `.bg-grid` — 网格线 `rgba(96,165,250,.05)`，56px，mask 顶部放射渐隐
2. `.bg-glow` — 三层径向渐变光晕（15%蓝10% / 85%红7% / 底部紫6%）
3. `#particles` Canvas — **红蓝双色粒子**（`Math.random()>0.5` 决定红/蓝），60颗桌面/30颗移动，半径0.4-2.0，速度±0.25，130px连线 `rgba(96,165,250,α)`，透明度 `0.35+0.25*sin(pulse)`

## 字体

- 标题/品牌/编号/流程/数据：`'JetBrains Mono','SFMono-Regular',Consolas,monospace`
- 正文：`-apple-system,'PingFang SC','Noto Sans SC','Microsoft YaHei',sans-serif`

## 页面结构（7段）

| 段 | 内容 |
|----|------|
| 导航 | 固定顶栏 `YASIN.`(Y蓝/A红) + mono链接(方法论/案例/数据/关于/联系) |
| Hero（v2定稿） | 顶部一行mono小字 `E-COMMERCE × AI AGENT · EST. 2008`（letter-spacing .45em）；**巨型 `YASIN` 红蓝渐变字**（weight 800, clamp 4.5-9.5rem, drop-shadow紫光）；红蓝渐变竖线分隔(1px×52px)；**中文细字标语「决策，不靠感觉」**（weight 300，letter-spacing .4em）；mono小字 `GUO YUEXING · 18 YEARS · SCUT CS`；双CTA(蓝主「方法论」/红ghost「案例」，2字无箭头)；scroll-hint 蓝→红渐变线 |
| 方法论 | 红蓝分析法卡(红边) + 六分身分析卡(蓝边)，步骤chip交替色 |
| 实战案例 | 4卡2×2：AI Agent矩阵(-60%蓝)、A股量化(9-D红)、服小助SaaS(7×24蓝)、抖音选品(SOP红)；每卡 `cc-status` 标签+`case-metric` 数字 |
| 数据背书 | 4格居中：18年(蓝) / 5000万(蓝) / 80%(红) / 7大Agent(红) |
| 关于我 | 左头像卡(Y字母渐变圆) + 右成长线叙事(2008→2010→2014→2023 All in AI)；tags 双色交替 |
| 联系 | 渐变顶线 contact-band + 邮箱/电话链接 |

## Hero 迭代历史（避坑）

- **v1（被否）**：eyebrow + 长h1「帮创业者少踩坑的实战派」红蓝渐变 + 副文案18年操盘 + meta标签(蓝=提案/红=攻击) + **七步流程条** + 双CTA带箭头。用户反馈：「不够简约高端大气，废话太多，没有中英字体排版的大气感」
- **v1.5（部分否）**：巨型YASIN白字+红点句号 → 红点「不协调」去掉；白字 → 红蓝渐变字；标语「帮创业者少踩坑的实战派」→ 改短句
- **v2（定稿）**：见上表。教训=首屏只留 巨型名字 + 短标语 + mono小字层级，装饰元素全部砍掉

## 关键组件

- **巨型英文名渐变**：`linear-gradient(120deg,#60a5fa 0%,#3b82f6 45%,#a78bfa 70%,#ef4444 100%)` + background-clip:text + `filter:drop-shadow(0 0 40px rgba(99,102,241,.25))`；font-family mono, weight 800, clamp(4.5rem,15vw,9.5rem)
- **红蓝分隔竖线**：`width:1px;height:52px;background:linear-gradient(180deg,var(--blue),var(--red))`
- **中文细标语**：weight 300, letter-spacing .4em, text-indent .4em（补偿末字字距）
- **CTA主按钮**：`linear-gradient(120deg,#3b82f6,#2563eb)` + 蓝色发光阴影
- **卡片**：bg-panel + 1px border + 顶部2px渐变光条(蓝/红) + hover translateY(-4px) + 深阴影
- **入场动画**：`.reveal`(opacity0+translateY24 → visible) + IntersectionObserver threshold 0.12；Hero用 `.fade-in .d1-d4` 递延

## 简历 → 品牌页转化要点

- 保留真实素材：AI Agent矩阵数据(-60%人工干预/成本-35%)、连续5000万销售目标、2000万年度目标、华南理工CS 2004-2008、邮箱电话
- 删掉求职信息：期望薪资/期望城市/性别年龄表格 → 换成品牌叙事
- 叙事主线：2008 KA(100+超市) → 2010城市经理(2000万) → 2014电商(睡衣服装5000万/年) → 2023 All in AI Agent → 现在(做产品+教方法论)

## 验证

- 交付闭环：write_file → browser_navigate(127.0.0.1:8894) → browser_vision 确认深色红蓝科技风到位（通过）
- 端口：8894 http.server 常驻；文件直接覆盖即生效无需重启
