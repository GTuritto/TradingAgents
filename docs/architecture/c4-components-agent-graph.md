# C4 — Components: Agent Graph (the committee)

The Agent Graph is a LangGraph `StateGraph` that mirrors a trading firm:
specialist analysts feed an adversarial debate, which a manager judges,
a trader plans, a risk panel stress-tests, and a portfolio manager
decides. State flows through a shared blackboard (`AgentState`).

```mermaid
C4Component
  title Component Diagram — Agent Graph

  Container(orchestrator, "TradingAgentsGraph", "Python", "Builds & runs the graph")
  Container(llmclients, "LLM Client Factory", "Python", "Quick + deep model tiers")
  Container(dataflows, "Dataflows Layer", "Python", "Data tools")

  Container_Boundary(graph, "Agent Graph (LangGraph StateGraph)") {
    Component(market, "Market Analyst", "Agent · quick LLM", "Technical indicators")
    Component(sentiment, "Sentiment Analyst", "Agent · quick LLM", "News-sourced sentiment")
    Component(news, "News Analyst", "Agent · quick LLM", "Macro & ticker news")
    Component(deepvalue, "On-Chain / Fundamentals Analyst", "Agent · quick LLM", "Deep-value slot — On-Chain for crypto, Fundamentals for equity")
    Component(bull, "Bull Researcher", "Agent · quick LLM", "Argues the bull case")
    Component(bear, "Bear Researcher", "Agent · quick LLM", "Argues the bear case")
    Component(rm, "Research Manager", "Agent · deep LLM", "Judges the debate, writes the investment plan")
    Component(trader, "Trader", "Agent · quick LLM", "Turns the plan into a trade proposal")
    Component(risk, "Risk Debate", "3 agents · quick LLM", "Aggressive / Conservative / Neutral panel")
    Component(pm, "Portfolio Manager", "Agent · deep LLM", "Final five-tier trade decision")
    Component(cond, "Conditional Logic", "Python", "Routes analyst tool loops and caps debate rounds")
  }

  Rel(orchestrator, market, "Starts the pipeline at")
  Rel(market, sentiment, "Then")
  Rel(sentiment, news, "Then")
  Rel(news, deepvalue, "Then")
  Rel(deepvalue, bull, "Four analyst reports feed")
  Rel(bull, bear, "Debates")
  Rel(bear, bull, "Rebuts (count-capped rounds)")
  Rel(bear, rm, "Debate concludes at")
  Rel(rm, trader, "Investment plan to")
  Rel(trader, risk, "Trade proposal to")
  Rel(risk, pm, "Risk debate concludes at")
  Rel(cond, risk, "Caps rounds")
  Rel(market, dataflows, "Calls data tools via")
  Rel(deepvalue, dataflows, "Calls data tools via")
  Rel(market, llmclients, "Quick tier")
  Rel(pm, llmclients, "Deep tier")
```

## Notes

- **Deep-value slot.** One analyst slot is asset-class dependent:
  `graph/setup.py` places the **On-Chain Analyst** for `asset_class=crypto`
  and the **Fundamentals Analyst** for equities. Both write the same
  `fundamentals_report` state field, so the rest of the pipeline is
  unchanged.
- **Two LLM tiers.** ~13 agents use the `quick_think_llm`; the Research
  Manager and Portfolio Manager use the stronger `deep_think_llm`. Every
  agent reaches the LLM through the LLM Client Factory (only the Market
  and Portfolio Manager edges are drawn, to keep the diagram readable).
- **Analyst tool loops.** Each analyst is a ReAct loop — it calls data
  tools through the Dataflows Layer until it has enough to write its
  report. Only the Market and On-Chain analysts' tool edges are drawn;
  the Sentiment and News analysts use data tools the same way.
- **Debate is count-capped.** Bull ⇄ Bear and the 3-way risk panel loop
  for a configurable number of rounds (`max_debate_rounds`,
  `max_risk_discuss_rounds`) before handing off to their judge.
