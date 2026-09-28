# GitHub 量化 skill 调研 — 2026-08-27

用途：回答「GitHub上有什么量化skill、哪个胜率最高、怎么搭配」时的证据库。

## 核心结论

**GitHub 上不存在「A股短线、公布过实测胜率」的 skill 可替换。** 敢公布胜率的只有加密领域；声称高年化的是 2014-2017 老旧回测，不可当前信。我们的 skill 47.2% 有真实日志——反而比网上所有声称都可信。

**因此不是「换哪个」，是「补三个洞」**（见底部改进路线）。

## 仓库对比表（9个，按相关度）

| Repo | 市场 | 方法 | 胜率数据 | 可信度 |
|---|---|------|---------|-------|
| **guanglioriki/Guangli-Quantitative-Stock-Selection-Strategy**（2★，Codex skill） | A股 | 低波30%+低换手30%+高分红+方向冲击残差+252日高点接近+水位线持续残差；12仓80%资金、逆向波动率加权、T+1竞价限价(前收×1.03)、60日时间退出+月末rank衰减退出 | 未公布胜率，但冻结生产基线+东财模拟盘自动化 | ★★★ 公式完整可复现，`references/strategy-spec.md` 有完整公式 |
| **ZhiwenZuo/Multi-factor-stock-selection-model**（17★） | A股 | 随机森林回归预测下季收益(NQMret)，每期取Top-N组合 | 声称年化33.7%，**2014-03~2017-06 老旧回测** | ★ 区间过时，不可当当前表现 |
| **Superior-Trade/superior-skills**（206★） | ❌ 加密(Hyperliquid) | Donchian强趋势门控(ADX门) / Bollinger 4h均值回归(ADX<25) | ✅ **唯一敢公布真实回测**：Donchian 100%（6笔，+6.69%，0回撤）；Bollinger 65.5%（84笔，+8.77%，18.5%回撤），162天实盘数据 | ★★★ 数据真，但非A股 |
| **Nzssm1/dsh-factor-investing**（4★，DSH预设） | A股向 | 多因子研究纪律：因子IC≠有用，必须**增量alpha检验**（对已知因子回归、截距α显著才算新信息）；市值/行业中性化；多重检验校正(t>3)；样本外纪律；Rust核心确定性计算 | 不产推荐，纯方法论 | ★★★ 纪律框架，正是我们缺的验证环节 |
| **OnePunchMonk/AgentQuant**（178★） | 通用(美股/ETF) | **regime门控**：先判市场环境（VIX百分位+多周期动量+SMA趋势），LLM→grid search→回测锦标赛（Sharpe/Calmar/Sortino/maxDD/bootstrap Sharpe p5），失败重试，SQLite记忆 | 有完整回测流水线，无A股数据 | ★★★ 流程先进 |
| **The-Swarm-Corporation/AutoHedge**（4293★） | 加密(Solana) | 多智能体自动对冲基金（Director/Quant/Risk/Execution四agent） | 无A股数据 | ★ 不适用 |
| **TruthHun/multi-factor-stock-selection**（84★） | A股 | Fama三因子多因子 | 无胜率声称 | ★★ |
| **1984tkr/multi-factor-stock-selection**（54★） | A股 | Python+Tushare+Backtrader完整多因子 | 无胜率声称 | ★★ |
| **Parsnip77/Multi-factor-Model-for-Stock-Selection**（15★） | A股 | WorldQuant Alpha101 因子复现+评估+合成+回测 Pipeline | 无胜率声称 | ★★ |

## 三个改进洞（按优先级，对应我们8月最惨三周）

| 洞 | 证据 | 补法（抄谁） |
|---|---|------|
| ① 无市场环境门控 | 8/13~8/19 大盘阴跌期间照样推8只全灭（8/14 0/8、8/19 均-3.63%） | 抄 AgentQuant：大盘在MA20下方或连跌3日 → 当日停推/减半。零成本，当天可上线 |
| ② 因子没验证、没中性化 | 每次评分混了小市值/高波动偏好；18天日志可算真实IC | 抄 dsh-factor-investing：9因子算 IC/ICIR，IC≤0 直接砍；新因子必须过增量alpha检验+市值/行业中性化 |
| ③ 缺低波/换手因子 | 我们纯技术指标打分；Guangli用低波+低换手+高分红长期有效（A股低波异象） | 抄 Guangli v22：加权中加入 lowvol_rank / low_turnover_rank |

## 调研方法（下次复用）

- GitHub API：`https://api.github.com/search/repositories?q=<关键词>&sort=stars&order=desc`，关键词试 `quant trading agent`、`stock selection llm agent`、`multi-factor stock selection` 等
- 拉 README：raw 会 404 时先查 default_branch（`/repos/{repo}` 返回），再 `https://raw.githubusercontent.com/{repo}/{branch}/README.md`
- 根 README 404 但仓库有内容 → 用 `api.github.com/repos/{repo}/contents/{dir}` 列目录，再 `-H "Accept: application/vnd.github.raw"` 拉具体文件（如 Guangli 的 README/SKILL.md 在 `v22-strategy/` 子目录）
- 搜胜率数字的优先级：回测声明（win rate/年化）> 模拟盘自动化 > 方法论框架；**只给方法论没数据的 repo 不能当「高胜率」卖点**
- 判断声称可信度：看数据区间（老回测=过时）、看有没有真实日志/实盘、看市场类型（加密≠A股）