## ADDED Requirements

### Requirement: On-Chain Analyst committee member

The system SHALL provide an On-Chain Analyst that occupies the deep-value analyst slot in the committee for crypto runs, sourcing tokenomics and on-chain metrics instead of corporate financial statements.

#### Scenario: On-Chain Analyst selected for crypto runs

- **WHEN** the graph is built with `asset_class` of `crypto`
- **THEN** the On-Chain Analyst node occupies the analyst slot that the Fundamentals Analyst occupies for equity runs

#### Scenario: Fundamentals Analyst selected for equity runs

- **WHEN** the graph is built with `asset_class` of `equity`
- **THEN** the Fundamentals Analyst node is used and the On-Chain Analyst node is absent from the graph

#### Scenario: On-Chain Analyst produces a report

- **WHEN** the On-Chain Analyst node runs for a crypto asset
- **THEN** it writes an on-chain analysis report into shared state in the same field consumed by downstream researcher and manager nodes

### Requirement: On-Chain Analyst tool set

The On-Chain Analyst SHALL be bound to on-chain data tools (tokenomics, total value locked, active addresses, exchange flows, development activity) and SHALL NOT be bound to balance-sheet, cashflow, income-statement, or insider-transaction tools.

#### Scenario: Equity-only tools excluded

- **WHEN** the On-Chain Analyst node is constructed
- **THEN** its bound tool set contains no balance-sheet, cashflow, income-statement, or insider-transaction tools
