"""CCXT-backed crypto market-data vendor.

Provides OHLCV and technical-indicator implementations for crypto assets,
sourced from a configurable CCXT exchange (``config["ccxt_exchange"]``,
default ``gemini``). The heavy ``ccxt`` dependency is imported lazily
inside the functions, so importing this module — which only registers the
source — stays cheap for equity-only runs and test collection.
"""

from datetime import datetime
from typing import Annotated

import pandas as pd
from dateutil.relativedelta import relativedelta

from .config import get_config
from .indicators import (
    INDICATOR_DESCRIPTIONS,
    format_indicator_window,
    stockstats_indicator_map,
)
from .source_registry import register_source

_MS_PER_DAY = 86_400_000

# Process-level memo: a backtest run calls get_indicators once per
# indicator (up to 8x) with the same fetch window — memoizing avoids
# hammering the exchange. Keyed by (exchange_id, market, start, end).
_OHLCV_MEMO: dict = {}


def _get_exchange():
    """Instantiate the configured CCXT exchange (lazy ``ccxt`` import)."""
    import ccxt

    exchange_id = (get_config().get("ccxt_exchange") or "gemini").strip().lower()
    if not hasattr(ccxt, exchange_id):
        raise ValueError(
            f"Unknown CCXT exchange '{exchange_id}'. "
            f"Pick a valid id from ccxt.exchanges."
        )
    return getattr(ccxt, exchange_id)({"enableRateLimit": True})


def _normalize_symbol(symbol: str) -> str:
    """Normalize a bare asset symbol to a CCXT market pair (quote in USD)."""
    s = symbol.strip().upper()
    return s if "/" in s else f"{s}/USD"


def _fetch_ohlcv_df(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch daily OHLCV as a DataFrame, bounded to ``end_date`` (no look-ahead).

    Returns columns Date/Open/High/Low/Close/Volume. ``end_date`` is
    inclusive to end-of-day; rows outside [start_date, end_date] are
    dropped so backtest runs never see future candles.
    """
    exchange = _get_exchange()
    market = _normalize_symbol(symbol)
    cache_key = (exchange.id, market, start_date, end_date)
    if cache_key in _OHLCV_MEMO:
        return _OHLCV_MEMO[cache_key].copy()

    start_ms = exchange.parse8601(f"{start_date}T00:00:00Z")
    end_ts = pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    end_ms = int(end_ts.timestamp() * 1000)

    rows = []
    cursor = start_ms
    while cursor <= end_ms:
        batch = exchange.fetch_ohlcv(market, timeframe="1d", since=cursor, limit=1000)
        if not batch:
            break
        rows.extend(batch)
        last_ts = batch[-1][0]
        if last_ts <= cursor:  # no forward progress — avoid an infinite loop
            break
        cursor = last_ts + _MS_PER_DAY
        if len(batch) < 1000:
            break

    columns = ["Date", "Open", "High", "Low", "Close", "Volume"]
    if not rows:
        return pd.DataFrame(columns=columns)

    df = pd.DataFrame(rows, columns=["ts", "Open", "High", "Low", "Close", "Volume"])
    df["Date"] = pd.to_datetime(df["ts"], unit="ms")
    df = df.drop(columns=["ts"]).drop_duplicates(subset=["Date"]).sort_values("Date")
    df = df[(df["Date"] >= pd.Timestamp(start_date)) & (df["Date"] <= end_ts)]
    df = df[columns].reset_index(drop=True)

    _OHLCV_MEMO[cache_key] = df
    return df.copy()


def get_ccxt_stock_data(
    symbol: Annotated[str, "crypto asset symbol, e.g. BTC or BTC/USD"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    """Retrieve daily OHLCV for a crypto asset from the configured CCXT exchange."""
    datetime.strptime(start_date, "%Y-%m-%d")
    datetime.strptime(end_date, "%Y-%m-%d")

    try:
        df = _fetch_ohlcv_df(symbol, start_date, end_date)
    except Exception as e:
        return f"Error retrieving crypto OHLCV for '{symbol}': {e}"

    if df.empty:
        return f"No data found for symbol '{symbol}' between {start_date} and {end_date}"

    out = df.copy()
    out["Date"] = out["Date"].dt.strftime("%Y-%m-%d")
    for col in ["Open", "High", "Low", "Close"]:
        out[col] = out[col].round(2)
    csv_string = out.to_csv(index=False)

    exchange_id = (get_config().get("ccxt_exchange") or "gemini")
    header = (
        f"# Crypto OHLCV for {_normalize_symbol(symbol)} on {exchange_id} "
        f"from {start_date} to {end_date}\n"
    )
    header += f"# Total records: {len(out)}\n"
    header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    return header + csv_string


def get_ccxt_indicators(
    symbol: Annotated[str, "crypto asset symbol, e.g. BTC or BTC/USD"],
    indicator: Annotated[str, "technical indicator to get the analysis and report of"],
    curr_date: Annotated[str, "The current trading date, YYYY-mm-dd"],
    look_back_days: Annotated[int, "how many days to look back"] = 30,
) -> str:
    """Retrieve a single technical indicator for a crypto asset.

    Reuses the shared stockstats engine over CCXT-sourced OHLCV. Data is
    bounded to ``curr_date`` so backtest runs see no future candles.
    """
    indicator = indicator.strip().lower()
    if indicator not in INDICATOR_DESCRIPTIONS:
        raise ValueError(
            f"Indicator {indicator} is not supported. "
            f"Please choose from: {list(INDICATOR_DESCRIPTIONS.keys())}"
        )
    datetime.strptime(curr_date, "%Y-%m-%d")

    # Fetch extra lead-in history so long indicators (e.g. 200 SMA) resolve.
    fetch_start = (
        datetime.strptime(curr_date, "%Y-%m-%d")
        - relativedelta(days=look_back_days + 260)
    ).strftime("%Y-%m-%d")

    try:
        df = _fetch_ohlcv_df(symbol, fetch_start, curr_date)
    except Exception as e:
        return f"Error retrieving crypto indicator data for '{symbol}': {e}"

    if df.empty:
        return f"No data found for symbol '{symbol}' up to {curr_date}"

    indicator_map = stockstats_indicator_map(df, indicator)
    return format_indicator_window(
        indicator,
        curr_date,
        look_back_days,
        indicator_map,
        missing_label="N/A: no candle for this date",
    )


register_source(
    "ccxt",
    {
        "get_stock_data": get_ccxt_stock_data,
        "get_indicators": get_ccxt_indicators,
    },
)
