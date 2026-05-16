## ADDED Requirements

### Requirement: BTC alpha benchmark for crypto assets

The deferred-reflection layer SHALL benchmark crypto asset returns against Bitcoin when computing alpha, instead of an equity index.

#### Scenario: Crypto benchmark resolution

- **WHEN** the benchmark is resolved for a run with `asset_class` of `crypto` and no explicit `benchmark_ticker` is set
- **THEN** the resolved benchmark is BTC and the reflection alpha is computed as the asset return minus the BTC return

#### Scenario: Explicit benchmark override honored

- **WHEN** `benchmark_ticker` is explicitly set for a crypto run
- **THEN** the explicit benchmark overrides the BTC default

### Requirement: 24/7 calendar for outcome resolution

When resolving holding-period returns for a crypto asset, the system SHALL treat every calendar day as a trading day and SHALL NOT apply the weekday/holiday buffer used for equities.

#### Scenario: Holding-period return without weekday buffer

- **WHEN** holding-period returns are fetched for a crypto asset over a holding window
- **THEN** the return is measured across consecutive calendar days with no extra buffer days added for weekends or holidays

#### Scenario: Deferred resolution mechanism preserved

- **WHEN** a crypto decision is logged and a later same-asset run occurs
- **THEN** the earlier pending entry is resolved with realized return, BTC alpha, and a reflection note, using the existing deferred-reflection mechanism
