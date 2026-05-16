# C4 — Dynamic: a propagate() run

`propagate(ticker, date)` is one trading run. Before the committee runs,
the orchestrator resolves *past* decisions whose outcomes are now known
and feeds the lessons back in — the deferred-reflection learning loop.

```mermaid
C4Dynamic
  title Dynamic Diagram — propagate(ticker, date)

  Person(trader, "Trader", "Initiates a run")
  ContainerDb(memory, "Memory Log", "Markdown", "Decisions & reflections")
  Container(graph, "Agent Graph", "LangGraph", "The committee")

  Container_Boundary(orch, "TradingAgentsGraph") {
    Component(propagate, "propagate()", "Python", "Run entry point")
    Component(reflector, "Reflector", "Python + LLM", "Grades past decisions vs realized return")
    Component(signal, "Signal Processor", "Python + LLM", "Extracts the final rating")
  }

  Rel(trader, propagate, "1. propagate('BTC', date)")
  Rel(propagate, memory, "2. Read pending past decisions for this ticker")
  Rel(propagate, reflector, "3. Resolve outcomes — realized return vs benchmark")
  Rel(reflector, memory, "4. Write reflections, mark entries resolved")
  Rel(propagate, memory, "5. Read past context (decisions + lessons)")
  Rel(propagate, graph, "6. Run the committee with past context injected")
  Rel(graph, propagate, "7. Final trade decision")
  Rel(propagate, signal, "8. Extract BUY / HOLD / SELL rating")
  Rel(propagate, memory, "9. Store this decision as pending")
```

## Notes

- **Steps 2–4 are the learning loop.** A decision is logged as
  `pending`; on a later run for the same ticker its real outcome is
  known, so the Reflector grades it and writes a lesson. No model
  training — the feedback is memory the next run's prompts read.
- **Step 5 injects history.** Recent same-ticker decisions and
  cross-ticker lessons are read from the Memory Log and added to the
  initial agent state, so the committee reasons with hindsight.
- **Benchmark (step 3).** Realized return is measured against a
  benchmark — SPY for equities. Crypto runs benchmark against BTC; the
  24/7-calendar variant of this step is delivered in Phase 4 of the
  `crypto-trader-base` change.
- **Checkpointing.** When `checkpoint_enabled` is set, the graph is
  compiled with a per-ticker SQLite saver so a crashed run resumes from
  the last completed node.
