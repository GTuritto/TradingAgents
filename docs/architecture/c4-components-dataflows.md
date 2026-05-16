# C4 — Components: Dataflows Layer

Every data tool an agent calls is routed through a config-driven
registry. A tool names a *category*; configuration (`data_vendors` /
`tool_vendors`) names the *vendor*; the registry resolves the vendor to
an *adapter*. Adding a new data source is a `register_source()` call in
the adapter's own module — no edit to the router.

```mermaid
C4Component
  title Component Diagram — Dataflows Layer

  Container(graph, "Agent Graph", "LangGraph", "Analyst agents")
  System_Ext(providers, "Data Providers", "Exchanges, CoinGecko, DefiLlama, Yahoo, Alpha Vantage")

  Container_Boundary(df, "Dataflows Layer") {
    Component(tools, "Data Tools", "LangChain @tool", "get_stock_data, get_indicators, get_tokenomics, get_tvl, …")
    Component(interface, "Vendor Router", "interface.py", "route_to_vendor() — category → vendor → impl, with fallback")
    Component(registry, "Source Registry", "source_registry.py", "Named adapters — sources self-register")
    Component(indicators, "Indicator Engine", "indicators.py + stockstats", "Vendor-agnostic technical indicators")
    Component(ccxt, "CCXT Vendor", "ccxt_vendor.py", "Crypto OHLCV — configurable exchange, Gemini default")
    Component(coingecko, "CoinGecko Adapter", "coingecko.py", "Tokenomics, developer activity")
    Component(defillama, "DefiLlama Adapter", "defillama.py", "DeFi total value locked")
    Component(glassnode, "Glassnode Seam", "glassnode.py", "On-chain activity — degrades gracefully, no key integrated")
    Component(yfinance, "Yahoo Finance Vendor", "y_finance.py", "Equity OHLCV, fundamentals, news")
    Component(alphavantage, "Alpha Vantage Vendor", "alpha_vantage*.py", "Equity market / fundamentals / news")
  }

  Rel(graph, tools, "Calls")
  Rel(tools, interface, "Routes through")
  Rel(interface, registry, "Resolves registered sources via")
  Rel(ccxt, registry, "Registers into")
  Rel(coingecko, registry, "Registers into")
  Rel(defillama, registry, "Registers into")
  Rel(glassnode, registry, "Registers into")
  Rel(interface, yfinance, "Dispatches to")
  Rel(interface, alphavantage, "Dispatches to")
  Rel(ccxt, indicators, "Computes indicators via")
  Rel(yfinance, indicators, "Computes indicators via")
  Rel(ccxt, providers, "Fetches from", "HTTPS")
  Rel(coingecko, providers, "Fetches from", "HTTPS")
  Rel(defillama, providers, "Fetches from", "HTTPS")
  Rel(yfinance, providers, "Fetches from", "HTTPS")
  Rel(alphavantage, providers, "Fetches from", "HTTPS")
```

## Notes

- **Equity vs crypto vendors coexist.** Yahoo Finance and Alpha Vantage
  are declared directly in the router; crypto sources (CCXT, CoinGecko,
  DefiLlama, Glassnode) arrive through the **Source Registry** and are
  folded into the routing table on import.
- **Shared indicator engine.** `indicators.py` holds the vendor-agnostic
  stockstats engine and window formatting. Both the CCXT and Yahoo
  vendors reuse it, so crypto and equity indicator reports are identical
  in shape.
- **Graceful degradation.** Every adapter returns a clear partial-data
  message on error instead of raising. The Glassnode seam always
  degrades today — active-address / exchange-flow data needs a keyed
  provider that is not integrated (see the `crypto-trader-base` design,
  decision D6).
- **As-of bounding.** Crypto tools accept an as-of date and never return
  observations after it — required for look-ahead-free backtesting.
