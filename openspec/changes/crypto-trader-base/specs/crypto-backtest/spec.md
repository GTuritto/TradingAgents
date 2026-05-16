## ADDED Requirements

### Requirement: Episodic backtest harness

The system SHALL provide a backtest harness that replays the trading committee across a historical date range for one or more crypto assets, reusing the existing episodic `propagate` machinery.

#### Scenario: Backtest over a date range

- **WHEN** the harness is run for a crypto asset with a start date, end date, and cadence
- **THEN** the committee is invoked once per scheduled date in chronological order, each invocation producing a logged decision

#### Scenario: Reflection chain across the sweep

- **WHEN** the harness completes a chronological sweep for an asset
- **THEN** earlier decisions in the sweep are resolved with realized outcomes and reflections by the subsequent same-asset runs, leaving the memory log populated with resolved entries

#### Scenario: No look-ahead in a backtest run

- **WHEN** the committee runs for a given backtest date
- **THEN** every data and news tool invoked is bounded to that date and returns no information dated after it

### Requirement: Backtest performance reporting

The backtest harness SHALL report aggregate performance for a completed sweep, including realized return and alpha versus BTC.

#### Scenario: Aggregate report after a sweep

- **WHEN** a backtest sweep completes for an asset
- **THEN** the harness reports the aggregate realized return and the aggregate BTC-relative alpha across the resolved decisions in the sweep
