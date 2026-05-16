# C4 — System Context

The system context for **TradingAgents**: who uses it and which external
services it depends on.

```mermaid
C4Context
  title System Context — TradingAgents

  Person(trader, "Trader / Researcher", "Runs analyses and reviews trade decisions")

  System(ta, "TradingAgents", "Multi-agent LLM trading framework — a committee of specialist agents that debate and decide a trade")

  System_Ext(llm, "LLM Provider", "OpenRouter / OpenAI / Anthropic / Google / xAI — powers every agent")
  System_Ext(exchanges, "Crypto Exchanges", "Gemini and 100+ others via CCXT — crypto OHLCV")
  System_Ext(coingecko, "CoinGecko", "Crypto tokenomics and market data")
  System_Ext(defillama, "DefiLlama", "DeFi total-value-locked data")
  System_Ext(yahoo, "Yahoo Finance", "Equity OHLCV, fundamentals, news, benchmark returns")
  System_Ext(av, "Alpha Vantage", "Equity market, fundamental and news data")

  Rel(trader, ta, "Runs trading analyses, reviews decisions", "CLI / Python API")
  Rel(ta, llm, "Prompts agents, receives reasoning", "HTTPS / OpenAI-compatible API")
  Rel(ta, exchanges, "Fetches crypto OHLCV", "CCXT / HTTPS")
  Rel(ta, coingecko, "Fetches tokenomics", "HTTPS")
  Rel(ta, defillama, "Fetches DeFi TVL", "HTTPS")
  Rel(ta, yahoo, "Fetches equity data & benchmarks", "HTTPS")
  Rel(ta, av, "Fetches equity data", "HTTPS")
```

## Notes

- **One LLM provider per run.** The provider is config-selected
  (`llm_provider`). With OpenRouter it acts as a gateway to many model
  families behind a single key.
- **Data sources are asset-class dependent.** Crypto runs use CCXT
  exchanges + CoinGecko + DefiLlama; equity runs use Yahoo Finance +
  Alpha Vantage. The asset class is set by the `asset_class` config key.
- TradingAgents is a CLI tool / Python library — it runs on the user's
  own machine, so there is no separate deployment topology to diagram.
