# 抖音数据平台可访问性报告

> 记录了常用抖音数据平台的访问方式、限制和降级路径。2026年7月更新。

## 平台清单

| 平台 | URL | 数据内容 | 访问方式 | 登录需求 | 反爬 |
|------|-----|---------|---------|---------|------|
| 蝉妈妈 | chanmama.com | 商品销量排行、达人排行、品牌排行 | computer_use | 需要注册登录 | 无，但核心数据付费 |
| 飞瓜数据 | feigua.cn | 商品/达人/直播数据分析 | computer_use | 需要付费 | 无 |
| 达多多 | daduoduo.com | 商品库、达人库、直播数据 | computer_use | 免费+付费 | 无 |
| 快选品 | kuaixuanpin.com | 广告选品数据 | computer_use | 需要付费 | 无 |
| 互联岛 | vvvvvv.com | 商品/达人/小店/品牌榜单 | computer_use | 需要注册登录 | Nuxt SPA，curl抓不到 |
| 中外玩具网 | ctoy.com.cn | 抖音玩具月销榜 | web_extract/computer_use | 不需要 | 堡垒云WAF+滑块验证 |
| 电商战报网 | ds.vvvvvv.com / vvvvvv.com | 各品类周报 | web_extract | 不需要 | 有限 |

## 各平台详细访问方法

### 互联岛 (vvvvvv.com)

- **商品页面**：主站 → 导航"商品" → 选择类目
- **关键类目ID**：
  - 居家日用：`1000005069`
  - 日用百货：`5`
  - 玩具：`1000001467`
  - 玩具乐器：`2`
  - 母婴用品：`1000005784`
- **子域名**：
  - goods.vvvvvv.com — 商品数据分析（有时502）
  - shop.vvvvvv.com — 小店数据分析
  - brand.vvvvvv.com — 品牌数据分析
- **注意**：完全Nuxt SPA渲染，curl/web_extract均无效，必须用computer_use+浏览器

### 中外玩具网 (ctoy.com.cn)

- **玩具热销榜索引**：`https://www.ctoy.com.cn/zx/b6b6d2f4cde6bedfc8c8cffab0f1.html`
- **其他榜单**：在 zx 目录下的不同页面
- **注意**：使用 堡垒云WAF 安全防护，会触发滑块验证码（5秒盾），computer_use会自动挡在验证页。对策：让用户手动完成验证。

### 蝉妈妈 (chanmama.com)

- **商品销量排行**：`https://www.chanmama.com/promotionRank/tikGoodsSale/`
- **每日探测榜**：`https://www.chanmama.com/strategyAnalysis/probeDayRank/`
- **热销品牌榜**：`https://www.chanmama.com/brandRank/promotionBrand/`
- **注意**：核心功能需付费会员（连续包季190元起）
- 免费可看：部分顶栏数据、排行榜概览

## 选品URL构造模板（适用于百度搜索）

```python
# 搜索日用百货热销
URL = f"https://www.baidu.com/s?wd=抖音+日用百货+爆款+TOP10+{年月}+佣金"

# 搜索玩具热销
URL = f"https://www.baidu.com/s?wd=抖音+玩具+潮玩+热卖榜+TOP10+{年月}"

# 搜索具体品类
URL = f"https://www.baidu.com/s?wd={品类}+抖音+热卖+月销+佣金"
```

## 已知公开文章/报告来源

| 来源 | 类型 | 频率 | 数据质量 |
|------|------|------|---------|
| 21经济报道 | 行业分析 | 不定期 | 高（引用蝉妈妈数据） |
| 亿邦动力 ebrun.com | 月度榜单 | 月 | 高 |
| 中外玩具网 | 月度玩具榜 | 月 | 高 |
| 知乎专栏 | 选品分析 | 不定期 | 中 |
| 抖音电商公众号 | 官方数据 | 不定期 | 最高 |
