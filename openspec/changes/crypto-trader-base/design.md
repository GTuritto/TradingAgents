## Context

TradingAgents orchestrates an equity-trading committee on a LangGraph state machine: sequential analysts (each a ReAct tool loop) → adversarial Bull/Bear debate with a judge → Trader → 3-way risk debate → Portfolio Manager. A deferred-reflection memory loop grades past decisions against realized returns and injects the lessons into future prompts.

The orchestration core is domain-agnostic. Three layers carry equity assumptions:

1. **Data layer** (`dataflows/`) — yfinance / alpha_vantage, equity-only sources.
2. **Fundamentals Analyst** — sources balance sheet, cashflow, income statement, insider transactions; none of these exist for crypto assets.
3. **Reflection layer** — benchmarks alpha against SPY and adds a 7-day buffer "for weekends/holidays" when resolving holding-period returns.

The framework already has a **vendor abstraction** (`data_vendors` category-level config + `tool_vendors` per-tool override, routed through `TOOLS_CATEGORIES` in `dataflows/interface.py`) and a **benchmark hook** (`_resolve_benchmark`, `benchmark_map`). Both are designed extension points and are the intended seams for this change.

## Goals / Non-Goals

**Goals:**
- Run the existing committee on a crypto asset (e.g. BTC, ETH) end to end in backtest, producing a BUY/HOLD/SELL decision.
- Add crypto market + on-chain data through the existing vendor abstraction without disturbing equity vendors.
- Replace the Fundamentals Analyst with an On-Chain Analyst of the same node shape.
- Make the deferred-reflection loop correct for crypto: BTC benchmark, 24/7 calendar.
- Accumulate a memory log of resolved decisions via a backtest harness, so paper trading later starts with learned lessons rather than an empty log.

**Non-Goals:**
- Live order execution against an exchange.
- Derivatives: perpetual futures, funding rates, leverage, liquidation modeling.
- Continuous / 24-7 scheduled invocation (the episodic `propagate(asset, date)` model is kept).
- Intraday timescales — the committee deliberates in minutes; only swing horizons (days/weeks) are honest.
- Replacing equity support; equity and crypto coexist, selected by config.

## Decisions

**D1 — CCXT as the market-data vendor, with a config-selectable exchange defaulting to Gemini.**
yfinance exposes `BTC-USD` but coverage is thin, laggy, and single-source. CCXT unifies 100+ exchanges behind one API, gives real OHLCV at multiple timeframes, and is the de-facto standard. It is registered as a new vendor value (`"ccxt"`) under the existing `data_vendors` categories — equity vendors are untouched. The specific exchange is a config key (`ccxt_exchange`), defaulting to **`gemini`** (the user's trading venue); any other CCXT-supported exchange is a config change, no code change. *Alternative considered:* a direct exchange-specific client — rejected, ties the framework to one exchange and forfeits the config-selectable seam.

**D2 — On-Chain Analyst replaces, not extends, the Fundamentals Analyst for crypto.**
The committee role ("the deep-value/fundamental member") is preserved; only its tools and prompt change. Selection is config-driven via `selected_analysts` and an asset-class flag, so `graph/setup.py` builds either `fundamentals` or `onchain` into the same slot. *Alternative considered:* adding On-Chain as a 5th analyst — rejected, lengthens the pipeline and the Fundamentals node would still run with no valid data for crypto.

**D3 — Asset class is an explicit config key, not inferred from the symbol.**
A `BTC/USDT` pair is unambiguous, but bare tickers (`ETH`) are not. An explicit `asset_class: "crypto" | "equity"` config key drives vendor selection, analyst selection, and benchmark resolution. *Alternative considered:* symbol-pattern sniffing — rejected as the brittle stringly-typed approach the codebase already suffers from in routing.

**D4 — Reflection: BTC benchmark + 24/7 calendar.**
`benchmark_map` gains a crypto default of `BTC` (alpha = asset return − BTC return). `_fetch_returns` drops the `+7` weekday buffer for crypto assets — every calendar day is a trading day. Outcome resolution still happens on the next same-asset run (deferred-reflection mechanism unchanged).

**D5 — Backtest harness is a thin driver, not a new engine.**
The harness loops `propagate(asset, date)` over a historical date range, reusing the existing episodic machinery. Because reflection resolves on the *next* same-asset run, a sequential date sweep naturally produces a chain of resolved decisions. No new orchestration code — just a driver script and date iteration.

**D6 — First milestone scope: BTC only, open-data providers, generalist analyst.**

- **On-chain data sources** are open / free providers — CoinGecko and DefiLlama to start, with room to add other open providers later. No paid tiers (Glassnode and similar) in this change; their absence must not block a run (see graceful-degradation risk below).
- **Asset universe** for the first backtest is **BTC only**. ETH, XRP, and a broader basket are explicit follow-up expansions, taken on once the single-asset loop is proven end to end.
- **On-Chain Analyst** ships as a **single generalist prompt**. Per-asset-type specialization (L1 vs. DeFi token vs. memecoin, which have very different on-chain signals) is deferred until the asset universe actually broadens — it has no value while only BTC is in scope.

**D7 — Data sources are a config-driven registry, not hard-wired imports.**
The user wants to add new data sources by configuration. Each data source (the CCXT exchange, each on-chain provider, each news provider) is an *adapter* registered under a name in a source registry. The existing `data_vendors` (category-level) and `tool_vendors` (per-tool override) config keys then select which registered adapter serves each tool category — this part already exists and is reused as-is. Adding a brand-new source is: write a small adapter conforming to the source interface, register it under a name, and select it via config. This keeps `dataflows/interface.py` free of a growing thicket of conditional imports and makes "add a source" a config operation for any already-registered adapter. *Alternative considered:* a fully generic, config-described HTTP adapter that needs zero adapter code for plain REST sources — attractive but unbounded in scope; flagged as an open question, not committed here. *Alternative considered:* keep hard-wiring vendors in `interface.py` — rejected, it does not scale as providers multiply and contradicts the user's config-extensibility requirement.

## Risks / Trade-offs

- **Look-ahead bias in backtest** → On-chain and news tools must accept and honor an as-of date; any tool that returns "latest" data leaks the future. Each crypto tool MUST be date-bounded; flag tools that cannot be.
- **On-chain API keys and cost** → Glassnode/Dune/explorer APIs are paid or rate-limited. Mitigation: start with free tiers (CoinGecko, DefiLlama), make on-chain tools degrade gracefully when a key is absent (the analyst still runs with partial data).
- **LLM latency vs. backtest length** → a multi-year daily backtest is thousands of committee runs. Mitigation: backtest on a sampled cadence (e.g. weekly) and a short asset list first; the swing horizon makes daily granularity unnecessary.
- **Reflection lessons may decay faster in crypto** → regime shifts are sharper than in equities; an old lesson can mislead. Mitigation: out of scope to solve here, but `memory_log_max_entries` rotation already exists as a blunt control — note it, don't build more.
- **Crypto prompt tuning is shallow if rushed** → risk debators reasoning with equity mental models (P/E, earnings) produce nonsense. Mitigation: prompt review is a real task, not an afterthought.

## Migration Plan

Additive — no migration of existing equity behavior. Equity runs are unchanged because crypto paths are gated on `asset_class`. Rollback is config-only: set `asset_class: "equity"`. New dependency `ccxt` is isolated to crypto vendor modules and imported lazily, mirroring the existing lazy-import pattern in `llm_clients/factory.py`.

## Open Questions

Resolved during exploration (see Decision D6): on-chain providers (CoinGecko + DefiLlama, open data only), first asset (BTC only), and analyst scope (single generalist prompt).

Remaining:

- Exact backtest **date range and cadence** for the first BTC sweep — the swing horizon points to a weekly cadence over a multi-month historical window, but the precise span is an apply-time detail to fix once data coverage from CoinGecko/DefiLlama for that period is confirmed.
- Whether the config-driven registry (D7) should eventually support a **generic config-described HTTP adapter** so that plain REST data sources can be added with zero adapter code. Out of scope for this change; revisit once a few real adapters exist and their shared shape is clear.
