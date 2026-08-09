# quant-trade Setup Reference

**Repo:** https://github.com/colinsweany/quant-trade
**Stars:** 37 | **License:** MIT
**Python:** >= 3.12 required | **Lines:** ~13,000 Python

## After Installation

| Property | Value |
|----------|-------|
| Install path | `~/Desktop/quant-trade/` |
| Venv | `~/Desktop/quant-trade/venv/` (Python 3.13) |
| Activate | `cd ~/Desktop/quant-trade && source venv/bin/activate` |
| Skill prefix | `quant-` (14 symlinked skills) |
| Plugin | `quant_tools` (symlinked to ~/.hermes/plugins/quant_tools) |
| A-share data | AKShare (free, no API key) |
| Crypto exchange | Binance/OKX via ccxt (requires API key config) |
| LLM features | Uses OPENAI_API_KEY from env (SiliconFlow compatible) |

## Available Tool Categories

- **Stock tools** — quote, klines, signal(MA+RSI), factors, list symbols
- **Financial stock tools** — valuation, 3-statement financials, growth rates
- **Financial extra tools** — industry ranking, concept ranking, northbound flow, dragon-tiger list
- **Backtest engine** — event-driven, Walk-Forward, T+1 simulation, HTML reports
- **Factor lab** — 36+ alpha factors, IC/IR validation, factor catalog
- **Strategy generator** — auto factor→strategy generation
- **Decision engine** — evidence-chain scoring
- **Paper research** — arxiv search, PDF formula extraction

## Usage Examples

```python
from plugins.quant_tools.stock_tools import _handle_get_stock_signal, _handle_get_stock_quote
from plugins.quant_tools.financial_stock_tools import _handle_get_stock_financial
from plugins.quant_tools.financial_extra_tools import _handle_get_industry_ranking
```

## Known Issues

- `_handle_get_stock_valuation` fails with `AttributeError: module 'akshare' has no attribute 'stock_a_indicator_lg'` — AKShare API drift. Workaround: use web_search for PE/PB data instead.
- A-share stock tools import `sys.path.insert(0, '.')` — must run from project root or adjust path.
