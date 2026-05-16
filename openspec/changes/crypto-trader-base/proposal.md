## Why

TradingAgents is an equity-focused multi-agent committee. Its orchestration layer (LangGraph state graph, debate/judge flow, two-tier LLMs, deferred-reflection memory) is domain-agnostic and worth reusing, but its data layer and one of its analysts encode equity-only assumptions that are wrong for cryptocurrency. This change adapts the framework into a crypto swing-trading committee, starting with a backtest-first milestone so the deferred-reflection learning loop has real outcome history from day one — before any paper or live trading.

## What Changes

- Add a **crypto market-data vendor** (CCXT-based OHLCV + technical indicators) registered through the existing `data_vendors` / `tool_vendors` abstraction. Equity vendors (yfinance, alpha_vantage) remain untouched.
- **BREAKING for crypto runs:** replace the Fundamentals Analyst with an **On-Chain Analyst** — same committee role and node shape, but on-chain tools (supply/tokenomics, TVL, active addresses, exchange flows, dev activity) instead of balance-sheet / cashflow / income-statement / insider-transaction tools, which are meaningless for crypto.
- Adapt the **reflection layer** for crypto: benchmark alpha against **BTC** (not SPY), and resolve holding-period returns on a 24/7 calendar with no weekend/holiday buffer.
- Add a **backtest harness** that drives episodic historical runs (`propagate(coin, date)` across a date range) so the memory log accumulates resolved decisions with real outcomes.
- Tune debate, risk, and trader prompts with crypto vocabulary (volatility regimes, exchange counterparty risk, depeg risk) — prompt-level, no structural change.

Scope is deliberately limited to **spot, swing-trading (days/weeks), backtest-first**. Derivatives (perps, funding, leverage), live execution, and continuous 24/7 scheduling are explicit non-goals for this change.

## Capabilities

### New Capabilities
- `crypto-data-layer`: CCXT-backed market-data vendor (OHLCV, technical indicators) plus on-chain data providers, registered through the existing vendor-routing abstraction.
- `onchain-analyst`: New committee analyst that replaces the Fundamentals Analyst for crypto runs, sourcing tokenomics and on-chain metrics.
- `crypto-reflection`: BTC-benchmarked, 24/7-calendar outcome resolution in the deferred-reflection memory loop.
- `crypto-backtest`: Episodic historical run harness that replays `propagate` across a date range to seed the memory log with resolved outcomes.

### Modified Capabilities
<!-- openspec/specs/ is empty — no existing specs to modify. -->

## Impact

- **New code:** `dataflows/` crypto vendor modules; `agents/analysts/onchain_analyst.py`; a backtest driver.
- **Modified code:** `dataflows/interface.py` (`TOOLS_CATEGORIES` registration); `default_config.py` (`data_vendors` crypto options, BTC `benchmark_map` default); `graph/setup.py` (analyst selection); `graph/reflection.py` and `trading_graph.py` `_fetch_returns` / `_resolve_benchmark` (24/7 calendar, BTC baseline).
- **New dependencies:** `ccxt`; on-chain data API clients (e.g. CoinGecko, DefiLlama, an explorer API) — most require API keys.
- **Unchanged:** `llm_clients/`, `graph/` orchestration core, researcher/manager/risk/trader node structure.
- **Out of scope:** live order execution, derivatives, continuous scheduling — deferred to follow-up changes.
