## ADDED Requirements

### Requirement: Crypto market-data vendor

The system SHALL provide a crypto market-data vendor that supplies OHLCV price data and technical indicators for cryptocurrency assets, registered through the existing `data_vendors` / `tool_vendors` vendor-routing abstraction.

#### Scenario: OHLCV retrieval for a crypto pair

- **WHEN** a market-data tool is invoked for a crypto asset with the crypto vendor selected
- **THEN** the system returns OHLCV data for the requested asset and timeframe sourced from a CCXT-backed exchange client

#### Scenario: Equity vendors unaffected

- **WHEN** a run is configured with `asset_class` of `equity`
- **THEN** the system routes data tools to the existing yfinance / alpha_vantage vendors and never invokes the crypto vendor

#### Scenario: Technical indicators on crypto data

- **WHEN** the indicator tool is invoked for a crypto asset after OHLCV data has been retrieved
- **THEN** the system computes the requested technical indicators over the crypto OHLCV series using the same indicator engine used for equities

### Requirement: On-chain data providers

The system SHALL provide on-chain data tools that supply tokenomics and chain-activity metrics (supply schedule, total value locked, active addresses, exchange flows, development activity) for cryptocurrency assets.

#### Scenario: On-chain metrics retrieval

- **WHEN** an on-chain data tool is invoked for a supported crypto asset
- **THEN** the system returns the requested on-chain metrics for that asset as of the requested date

#### Scenario: Missing provider API key

- **WHEN** an on-chain data tool is invoked but its provider API key is not configured
- **THEN** the tool returns a clear partial-data indication rather than raising an unhandled error, allowing the analyst to proceed with the metrics that are available

### Requirement: Date-bounded data access

Every crypto data tool SHALL accept an as-of date and return only data available on or before that date, so that backtest runs do not leak future information.

#### Scenario: Backtest as-of bounding

- **WHEN** a crypto data tool is invoked with an as-of date during a backtest run
- **THEN** the returned data contains no observations dated after the as-of date
