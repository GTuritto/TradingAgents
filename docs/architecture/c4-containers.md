# C4 — Container Diagram

The major building blocks inside **TradingAgents**. It is a single Python
process; the "containers" below are its major subsystems and data stores.

```mermaid
C4Container
  title Container Diagram — TradingAgents

  Person(trader, "Trader / Researcher", "Runs analyses")
  System_Ext(llm, "LLM Provider", "OpenRouter / OpenAI / Anthropic / …")
  System_Ext(providers, "Market & On-chain Data Providers", "CCXT exchanges, CoinGecko, DefiLlama, Yahoo Finance, Alpha Vantage")

  System_Boundary(ta, "TradingAgents") {
    Container(cli, "CLI", "Python, Typer", "Interactive entry point — pick ticker, analysts, provider, models")
    Container(orchestrator, "TradingAgentsGraph", "Python", "Builds the agent graph, runs propagate(), wires the reflection loop")
    Container(graph, "Agent Graph", "LangGraph StateGraph", "The committee state machine — analysts, debate, risk, decision")
    Container(llmclients, "LLM Client Factory", "Python", "Provider-agnostic clients — quick + deep model tiers")
    Container(dataflows, "Dataflows Layer", "Python", "Config-driven data-source registry and vendor adapters")
    ContainerDb(memory, "Memory Log", "Append-only Markdown file", "Past decisions, realized outcomes, reflections")
    ContainerDb(cache, "Data Cache", "Local CSV + SQLite files", "Cached OHLCV and LangGraph checkpoints")
  }

  Rel(trader, cli, "Runs", "terminal")
  Rel(cli, orchestrator, "Configures and invokes")
  Rel(orchestrator, graph, "Builds and executes")
  Rel(orchestrator, memory, "Reads past context; writes decisions & reflections")
  Rel(graph, llmclients, "Prompts agents through")
  Rel(graph, dataflows, "Calls data tools through")
  Rel(llmclients, llm, "Calls", "HTTPS")
  Rel(dataflows, providers, "Fetches data from", "HTTPS")
  Rel(dataflows, cache, "Reads / writes")
```

## Notes

- **TradingAgentsGraph** (`graph/trading_graph.py`) is the orchestrator:
  it builds the graph for the configured `asset_class`, runs
  `propagate()`, and owns the deferred-reflection loop.
- **Agent Graph** is a LangGraph `StateGraph` — see
  [c4-components-agent-graph.md](c4-components-agent-graph.md).
- **Dataflows Layer** routes every data tool through a config-driven
  registry — see [c4-components-dataflows.md](c4-components-dataflows.md).
- **Memory Log** is a plain append-only Markdown file — the substrate of
  the deferred-reflection learning loop.
