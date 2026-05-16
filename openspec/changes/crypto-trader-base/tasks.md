## 1. Config and asset-class plumbing

- [ ] 1.1 Add `asset_class` config key (`"equity"` | `"crypto"`, default `"equity"`) to `default_config.py` with a `TRADINGAGENTS_ASSET_CLASS` env override
- [ ] 1.2 Add `"BTC"` crypto default to `benchmark_map` and document crypto alpha resolution
- [ ] 1.3 Add `ccxt` to `pyproject.toml` dependencies

## 2. Crypto market-data vendor

- [ ] 2.1 Create a CCXT-backed vendor module under `dataflows/` exposing OHLCV retrieval, lazily importing `ccxt`
- [ ] 2.2 Wire crypto indicator computation to reuse the existing indicator engine over crypto OHLCV
- [ ] 2.3 Register the `ccxt` vendor in `TOOLS_CATEGORIES` / vendor routing in `dataflows/interface.py`
- [ ] 2.4 Ensure every crypto market-data tool accepts an as-of date and bounds returned data to it
- [ ] 2.5 Verify equity vendors (yfinance, alpha_vantage) still route correctly under `asset_class: equity`

## 3. On-chain data tools

- [ ] 3.1 Create on-chain data module(s) under `dataflows/` for tokenomics, TVL, active addresses, exchange flows, dev activity (start with free providers — CoinGecko, DefiLlama)
- [ ] 3.2 Make each on-chain tool degrade gracefully to partial data when its API key is absent
- [ ] 3.3 Date-bound on-chain tools to the as-of date; flag any provider that cannot honor it

## 4. On-Chain Analyst

- [ ] 4.1 Create `agents/analysts/onchain_analyst.py` mirroring the Fundamentals Analyst node shape, bound only to on-chain tools
- [ ] 4.2 Write the On-Chain Analyst system prompt (crypto vocabulary; no P/E or earnings framing)
- [ ] 4.3 Update `graph/setup.py` to select On-Chain vs Fundamentals Analyst into the deep-value slot based on `asset_class`
- [ ] 4.4 Confirm the On-Chain Analyst writes its report into the shared-state field consumed downstream

## 5. Crypto reflection layer

- [ ] 5.1 Update `_resolve_benchmark` to return `BTC` for `asset_class: crypto` when no explicit `benchmark_ticker` is set
- [ ] 5.2 Update `_fetch_returns` to drop the weekday/holiday buffer for crypto assets (24/7 calendar)
- [ ] 5.3 Verify deferred resolution still resolves pending crypto entries on the next same-asset run

## 6. Crypto prompt tuning

- [ ] 6.1 Review and tune Bull/Bear researcher prompts for crypto reasoning
- [ ] 6.2 Review and tune Aggressive/Conservative/Neutral risk prompts (volatility regimes, exchange counterparty risk, depeg risk)
- [ ] 6.3 Review and tune Trader and Portfolio Manager prompts for crypto position framing

## 7. Backtest harness

- [ ] 7.1 Create a backtest driver that loops `propagate(asset, date)` over a date range and cadence in chronological order
- [ ] 7.2 Confirm the chronological sweep produces a chain of resolved decisions in the memory log
- [ ] 7.3 Add aggregate performance reporting (realized return and BTC alpha across resolved decisions)

## 8. Verification

- [ ] 8.1 Run a single end-to-end crypto committee run for BTC on a historical date and inspect the logged decision
- [ ] 8.2 Run a short multi-date backtest sweep and confirm reflections and the aggregate report are produced
- [ ] 8.3 Run an equity smoke test to confirm no regression in equity behavior
- [ ] 8.4 Add tests for asset-class routing, crypto benchmark resolution, and as-of date bounding
