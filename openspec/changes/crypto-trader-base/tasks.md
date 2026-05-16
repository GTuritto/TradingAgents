# Implementation Plan — crypto-trader-base

Built in **8 phases**, each a shippable increment that ends with its own
verification subphase. Build phases in order — dependencies flow downward
(P1+P2 feed P3; P3 feeds P4–P6). Recommended: one working branch per
phase, smoke-tested before folding into `crypto-trader-base`.

Milestone reached at end of **P6**: a full BTC backtest sweep with an
aggregate performance report and a populated reflection memory log.

## 0. Phase 0 — Foundation & asset-class plumbing

Ships: an `asset_class` config switch; equity behavior unchanged.

### 0.1 Config keys

- [x] 0.1.1 Add `asset_class` config key (`"equity"` | `"crypto"`, default `"equity"`) to `default_config.py` with a `TRADINGAGENTS_ASSET_CLASS` env override
- [x] 0.1.2 Add `"BTC"` crypto default to `benchmark_map` and document crypto alpha resolution
- [x] 0.1.3 Add `ccxt_exchange` config key (default `"gemini"`) with a `TRADINGAGENTS_CCXT_EXCHANGE` env override

### 0.2 Dependencies

- [x] 0.2.1 Add `ccxt` to `pyproject.toml` dependencies, to be lazy-imported (mirroring the pattern in `llm_clients/factory.py`)

### 0.3 Verify Phase 0

- [x] 0.3.1 Smoke test: an equity run is unaffected, and `asset_class: crypto` is recognized by config without error

## 1. Phase 1 — Crypto market-data vendor & source registry

Ships: BTC OHLCV and technical indicators via a CCXT vendor (default
Gemini), reachable through a config-driven data-source registry.

### 1.1 CCXT vendor module

- [x] 1.1.1 Create a CCXT-backed vendor module under `dataflows/` exposing OHLCV retrieval, selecting the exchange from the `ccxt_exchange` config key (default `gemini`), lazily importing `ccxt`
- [x] 1.1.2 Wire crypto indicator computation to reuse the existing indicator engine over crypto OHLCV

### 1.2 Config-driven source registry

- [x] 1.2.1 Introduce a named data-source registry in `dataflows/` so adapters register under a name and `data_vendors` / `tool_vendors` select them by name
- [x] 1.2.2 Register the CCXT vendor adapter in the registry; raise a clear configuration error on an unknown source name

### 1.3 Vendor routing

- [x] 1.3.1 Route crypto market-data tool categories through the registry in `dataflows/interface.py` / `TOOLS_CATEGORIES`
- [x] 1.3.2 Ensure every crypto market-data tool accepts an as-of date and bounds returned data to it (no look-ahead)

### 1.4 Verify Phase 1

- [x] 1.4.1 Smoke test: fetch BTC OHLCV from Gemini for a date range and compute indicators
- [x] 1.4.2 Smoke test: switching `ccxt_exchange` to another CCXT exchange works with no code change
- [x] 1.4.3 Smoke test: equity vendors (yfinance, alpha_vantage) still route correctly under `asset_class: equity`

## 2. Phase 2 — On-chain data layer

Ships: BTC on-chain metrics from open-data providers.

### 2.1 Provider tools

- [x] 2.1.1 Create on-chain data adapter(s) under `dataflows/` for tokenomics, TVL, active addresses, exchange flows, dev activity, using open providers (CoinGecko, DefiLlama), each registered in the source registry from Phase 1.2
- [x] 2.1.2 Date-bound on-chain tools to the as-of date; flag any provider that cannot honor it

### 2.2 Graceful degradation

- [x] 2.2.1 Make each on-chain tool degrade to partial data when its API key is absent, rather than raising

### 2.3 Verify Phase 2

- [x] 2.3.1 Smoke test: fetch BTC on-chain metrics for a historical date
- [x] 2.3.2 Smoke test: a tool with a missing API key returns partial data without crashing the run

## 3. Phase 3 — On-Chain Analyst

Ships: a full BTC committee run with the On-Chain Analyst in the deep-value slot.

### 3.1 Analyst node

- [x] 3.1.1 Create `agents/analysts/onchain_analyst.py` mirroring the Fundamentals Analyst node shape, bound only to on-chain tools
- [x] 3.1.2 Write the On-Chain Analyst system prompt — single generalist prompt, crypto vocabulary, no P/E or earnings framing

### 3.2 Graph wiring

- [x] 3.2.1 Update `graph/setup.py` to select On-Chain vs Fundamentals Analyst into the deep-value slot based on `asset_class`
- [x] 3.2.2 Confirm the On-Chain Analyst writes its report into the shared-state field consumed by downstream researcher and manager nodes

### 3.3 Verify Phase 3

- [x] 3.3.1 Smoke test: a single end-to-end BTC committee run produces a BUY/HOLD/SELL decision

## 4. Phase 4 — Crypto reflection layer

Ships: correct outcome resolution for crypto — BTC benchmark, 24/7 calendar.

### 4.1 Benchmark

- [x] 4.1.1 Update `_resolve_benchmark` to return `BTC` for `asset_class: crypto` when no explicit `benchmark_ticker` is set

### 4.2 Calendar

- [x] 4.2.1 Update `_fetch_returns` to drop the weekday/holiday buffer for crypto assets (every calendar day is a trading day)

### 4.3 Verify Phase 4

- [x] 4.3.1 Smoke test: two sequential BTC runs — the second resolves the first's pending entry with realized return and BTC alpha

## 5. Phase 5 — Crypto prompt tuning

Ships: committee debate that reasons in crypto terms.

### 5.1 Research & risk prompts

- [ ] 5.1.1 Review and tune Bull/Bear researcher prompts for crypto reasoning
- [ ] 5.1.2 Review and tune Aggressive/Conservative/Neutral risk prompts (volatility regimes, exchange counterparty risk, depeg risk)

### 5.2 Decision prompts

- [ ] 5.2.1 Review and tune Trader and Portfolio Manager prompts for crypto position framing

### 5.3 Verify Phase 5

- [ ] 5.3.1 Smoke test: inspect a BTC run's debate transcript for crypto-appropriate reasoning (no equity-only concepts)

## 6. Phase 6 — Backtest harness  *(milestone)*

Ships: a full BTC backtest sweep with an aggregate performance report.

### 6.1 Driver

- [ ] 6.1.1 Create a backtest driver that loops `propagate(asset, date)` over a date range and cadence in chronological order
- [ ] 6.1.2 Fix the first BTC sweep's date range and cadence (weekly cadence over a multi-month window; confirm provider data coverage)

### 6.2 Reporting

- [ ] 6.2.1 Confirm the chronological sweep produces a chain of resolved decisions in the memory log
- [ ] 6.2.2 Add aggregate performance reporting — realized return and BTC alpha across resolved decisions

### 6.3 Verify Phase 6

- [ ] 6.3.1 Smoke test: run a short multi-date BTC sweep; confirm reflections and the aggregate report are produced

## 7. Phase 7 — Hardening & verification

Ships: test coverage and a confirmed no-regression baseline.

### 7.1 Automated tests

- [ ] 7.1.1 Add tests for asset-class routing (crypto vs equity vendor/analyst selection)
- [ ] 7.1.2 Add tests for crypto benchmark resolution and the 24/7 calendar
- [ ] 7.1.3 Add tests for as-of date bounding in crypto data tools

### 7.2 Regression & audit

- [ ] 7.2.1 Run an equity smoke test to confirm no regression in equity behavior
- [ ] 7.2.2 Audit all crypto data/news tools for look-ahead bias (no observation dated after the as-of date)

### 7.3 Documentation

- [ ] 7.3.1 Update `README.md` to document crypto support (`asset_class`, OpenRouter provider, CCXT + on-chain data sources, the On-Chain Analyst)
- [ ] 7.3.2 Add a `CHANGELOG.md` entry for the crypto-trader-base change
- [ ] 7.3.3 Refresh the `docs/architecture/` C4 diagrams to the final shipped state

### 7.4 Verify Phase 7

- [ ] 7.4.1 Full test suite passes; equity and crypto paths both green
