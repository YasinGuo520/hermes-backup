# Rider-Waite 78 张塔罗图源（中国服务器）

## 结论（2026-09-07 实测）

- **Wikimedia Commons（commons.wikimedia.org / upload.wikimedia.org）从国内服务器直连不通**（curl 000）——主图源不可用。
- 可用路径：GitHub repo `mixvlad/TarotCards`（78卡 Rider-Waite 720px，公有领域，来源 Wikimedia）走 **jsDelivr** CDN：`https://cdn.jsdelivr.net/gh/mixvlad/TarotCards@main/tarot/rider-waite/720px/{file}`
- 下载后**必须本地化**到 `~/Desktop/hermes/tarot/static/cards/`（Yasin 铁律：前端零外网依赖）。78张共约 21MB。jsDelivr 串行慢（240s 超时没下完），用 `xargs -P 8` 并行。

## 命名规律

文件列表：`tarot/rider-waite/720px/{NN_Name}.jpg`（另有 full/360px/thumbs 目录同 repo 可用）

- 大阿卡纳 22 张：`00_Fool.jpg` … `21_World.jpg`（中间见 SKILL.md 清单：01_Magician, 02_High_Priestess, 03_Empress, 04_Emperor, 05_Hierophant, 06_Lovers, 07_Chariot, 08_Strength, 09_Hermit, 10_Wheel_of_Fortune, 11_Justice, 12_Hanged_Man, 13_Death, 14_Temperance, 15_Devil, 16_Tower, 17_Star, 18_Moon, 19_Sun, 20_Judgement）
- 小阿卡纳 56 张：`{Suit}{NN}.jpg`，Suit ∈ {Wands权杖, Cups圣杯, Swords宝剑, Pents星币}，NN=01-14 → 01=Ace(王牌)，02-10=二…十，11=Page侍从，12=Knight骑士，13=Queen王后，14=King国王
- 排除 `Cover.jpg`/`Cover_Rare.jpg`（不是牌）。

拉文件清单的可靠方式（GitHub API 树，注意国内 api.github.com 可达）：
`curl -s https://api.github.com/repos/mixvlad/TarotCards/git/trees/HEAD?recursive=1` → 过滤 `tarot/rider-waite/720px/*.jpg` 且不含 Cover。

## 前端数据生成（避免手写 78 条出错）

用 Python 按上面规则生成 `TAROT_CARDS` 数组 → 写 `static/cards.js`：每项 `{file, name_en, name_cn, type}`，先 `json.dumps` 再与磁盘文件存在性校验（missing=0 才算齐）。

## 备选 repo（搜索时发现）

- `sixseeds/tarot-api`：78卡 public domain，图片在 GitHub Pages（`petaloverflow.github.io/tarot-api/cards/ar00.jpg`）
- npm `@cometpisces/tarot-kit-images`：78 R-W images（jsDelivr npm 通道）

## 前端要点

牌背用 CSS 渐变+叠加阴影模拟牌堆（不占图片）；正/逆位随机 30%，逆位翻牌动画 `rotateY(180deg) rotate(180deg)`（transition 1.6s 更有仪式感）；洗牌动画用 deck 抖动 CSS。
