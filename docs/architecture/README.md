# Architecture — TradingAgents

C4-model architecture documentation. Diagrams use Mermaid's C4 syntax and
render on GitHub.

## Diagrams

| Level | Document | Shows |
|-------|----------|-------|
| 1 — Context | [c4-context.md](c4-context.md) | The system and the external services it depends on |
| 2 — Container | [c4-containers.md](c4-containers.md) | The major subsystems and data stores inside TradingAgents |
| 3 — Component | [c4-components-agent-graph.md](c4-components-agent-graph.md) | The agent committee — analysts, debate, risk, decision |
| 3 — Component | [c4-components-dataflows.md](c4-components-dataflows.md) | The config-driven data-source registry and vendors |
| Dynamic | [c4-dynamic-propagate.md](c4-dynamic-propagate.md) | A `propagate()` run and the deferred-reflection loop |

## The system in one paragraph

TradingAgents runs a committee of LLM-powered agents that mirrors a
trading firm. Specialist analysts gather evidence, an adversarial
Bull/Bear debate is judged into an investment plan, a trader proposes an
action, a three-way risk panel stress-tests it, and a portfolio manager
issues the final five-tier decision. Across runs, a deferred-reflection
loop grades past decisions against realized returns and feeds the
lessons back through the agents' prompts — learning without training.

## Asset classes

The framework runs on **equities** and **cryptocurrencies**, chosen by
the `asset_class` config key. The orchestration is asset-class agnostic;
two layers differ:

- **Data** — crypto runs use CCXT exchanges, CoinGecko and DefiLlama;
  equity runs use Yahoo Finance and Alpha Vantage.
- **Deep-value analyst** — the On-Chain Analyst for crypto, the
  Fundamentals Analyst for equities, in the same committee slot.

Crypto support is being added through the `crypto-trader-base` OpenSpec
change (see `openspec/changes/crypto-trader-base/`). These diagrams
reflect the system as of that change's Phase 3 — the crypto data layer
and On-Chain Analyst are in place; the crypto-specific reflection
benchmark (Phase 4) and backtest harness (Phase 6) are still in progress.
