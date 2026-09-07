# lunar-python 排盘 API 实测明细（2026-09-07, lunar_python 版验证）

pip: `pip install lunar_python`（6tail/lunar-python，与 lunar-javascript 同作者同算法；服务器无 node 时用此版）。

## 换算入口

```python
from lunar_python import Solar, Lunar
solar = Solar.fromYmdHms(1990, 5, 15, 10, 30, 0)
lunar = solar.getLunar()          # 公历→农历
# 农历→公历：
lunar2 = Lunar.fromYmdHms(1990, 4, 21, 10, 0, 0)  # (农历年,月,日,时,分,秒)
solar2 = lunar2.getSolar()        # .toYmd()
```

实测：农历一九九〇年四月廿一 10:30 ↔ 公历 1990-05-15 10:30 ✓

## EightChar 取数（lunar.getEightChar()）

| 方法 | 返回 | 备注 |
|---|---|---|
| `getYear()/getMonth()/getDay()/getTime()` | `'庚午'` 四柱干支 | 年=`ec.getYear()`（柱，非生肖） |
| `getDayGan()` | 日干（日主） | |
| `getYearShiShenGan()` 等 | 单字符串 | 日干十神=日主 |
| `getYearShiShenZhi()` 等 | **数组** `['正官','正印']` | 支藏十神；⚠️ 与 Gan 系列返回类型不同 |
| `getYearHideGan()` 等 | **数组** 藏干 `['丁','己']` | |
| `getYearNaYin()` 等 | 纳音 '路旁土' | |
| `getSolar().getXingZuo()` | 星座 | |
| `lunar.getYearShengXiao()` / `lunar.toString()` | 生肖 / 农历串 | |

不存在的方法（AttributeError）：`getYearShiShenGanHide`（藏干十神已由 get*ShiShenZhi 给出，别另找）。

## 五行统计（展示层自己算，不属历法）

天干五行：甲乙木 丙丁火 戊己土 庚辛金 壬癸水；地支本气五行：子水丑土寅木卯木辰土巳火午火未土申金酉金戌土亥水。

## 大运 / 流年

```python
yun = ec.getYun(1)   # 1=男命(顺排)，0=女命(逆排)——实测男壬午起/女庚辰起，顺逆正确
start_solar = yun.getStartSolar().toYmd()   # 起运公历日
# 起运表述：f"出生后 {yun.getStartYear()} 年 {yun.getStartMonth()} 个月 {yun.getStartDay()} 天起运"
dayun = yun.getDaYun()
# ⚠️ dayun[0] 是「出生→起运前」空段，getGanZhi() 为空字符串——遍历时必须跳过空干支段，真大运从 index 1 起
#    （若跳过了空段取 index，回取 DaYun 对象要 +1 偏移：yun.getDaYun()[skip_count + i]）
for d in yun.getDaYun():
    if not d.getGanZhi(): continue
    d.getStartYear(), d.getEndYear(), d.getGanZhi()
# 某步大运的流年：
ln = yun.getDaYun()[i].getLiuNian()  # i 对应未跳空段的原始下标
[x.getYear(), x.getGanZhi() for x in ln]
```

## 参考实现

`~/Desktop/hermes/bazi/server.py`：POST /api/bazi 收 {year,month,day,hour,gender,isLunar} → 排盘 + DeepSeek 白话解读（传统文化/性格框架 prompt，避免宿命化表述），前端 8902。
