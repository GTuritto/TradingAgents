"""CoinGecko on-chain data adapter.

Serves tokenomics and developer-activity metrics from CoinGecko's open
API. Works keyless; ``COINGECKO_API_KEY`` (a free Demo key) is used when
present to raise rate limits. Every call degrades to a clear partial
message on any error rather than raising, so a missing key or a rate
limit never crashes a run.
"""

import os
from datetime import datetime

import requests

from .source_registry import register_source

_BASE = "https://api.coingecko.com/api/v3"
_TIMEOUT = 20

# Symbol -> CoinGecko coin id. Unknown symbols fall back to a lowercased
# guess; a wrong guess simply yields a graceful "data unavailable".
_COIN_IDS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "XRP": "ripple",
    "SOL": "solana",
    "BNB": "binancecoin",
    "ADA": "cardano",
    "DOGE": "dogecoin",
}

# Memo of /history responses keyed by (coin_id, curr_date): tokenomics and
# dev-activity both read the same snapshot, and a backtest sweep re-asks
# for the same dates — memoizing avoids redundant rate-limited calls.
_HISTORY_MEMO: dict = {}


def _coin_id(symbol: str) -> str:
    base = symbol.split("/")[0].strip().upper()
    return _COIN_IDS.get(base, base.lower())


def _headers() -> dict:
    key = os.getenv("COINGECKO_API_KEY")
    return {"x-cg-demo-api-key": key} if key else {}


def _history(coin_id: str, curr_date: str) -> dict:
    """Fetch the CoinGecko /coins/{id}/history snapshot for an as-of date."""
    cache_key = (coin_id, curr_date)
    if cache_key in _HISTORY_MEMO:
        return _HISTORY_MEMO[cache_key]

    date_param = datetime.strptime(curr_date, "%Y-%m-%d").strftime("%d-%m-%Y")
    resp = requests.get(
        f"{_BASE}/coins/{coin_id}/history",
        params={"date": date_param, "localization": "false"},
        headers=_headers(),
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()
    _HISTORY_MEMO[cache_key] = data
    return data


def get_tokenomics(symbol: str, curr_date: str) -> str:
    """Supply and valuation metrics for a crypto asset as of ``curr_date``."""
    coin_id = _coin_id(symbol)
    try:
        market = _history(coin_id, curr_date).get("market_data") or {}
        price = (market.get("current_price") or {}).get("usd")
        mcap = (market.get("market_cap") or {}).get("usd")
        volume = (market.get("total_volume") or {}).get("usd")

        if price is None and mcap is None:
            return (
                f"# Tokenomics for {symbol} as of {curr_date}\n"
                "No CoinGecko market data available for this date."
            )

        lines = [
            f"# Tokenomics for {symbol} ({coin_id}) as of {curr_date}",
            "# Source: CoinGecko",
        ]
        if price is not None:
            lines.append(f"Price (USD): {price:,.2f}")
        if mcap is not None:
            lines.append(f"Market Cap (USD): {mcap:,.0f}")
        if volume is not None:
            lines.append(f"24h Volume (USD): {volume:,.0f}")
        if price and mcap:
            lines.append(f"Implied Circulating Supply: {mcap / price:,.0f}")
        return "\n".join(lines)
    except Exception as e:
        return (
            f"# Tokenomics for {symbol} as of {curr_date}\n"
            f"Data unavailable (CoinGecko: {e}). "
            "Set COINGECKO_API_KEY to improve reliability."
        )


def get_dev_activity(symbol: str, curr_date: str) -> str:
    """Developer and community activity for a crypto asset as of ``curr_date``.

    Sourced from the CoinGecko /history snapshot. CoinGecko no longer
    populates historical developer/community fields, so this commonly
    degrades to an "unavailable" message — by design, since falling back
    to *current* dev data would leak future information into backtests.
    """
    coin_id = _coin_id(symbol)
    try:
        snapshot = _history(coin_id, curr_date)
        dev = snapshot.get("developer_data") or {}
        community = snapshot.get("community_data") or {}

        metrics = []
        dev_fields = [
            ("GitHub stars", "stars"),
            ("GitHub forks", "forks"),
            ("Total issues", "total_issues"),
            ("Closed issues", "closed_issues"),
            ("PRs merged", "pull_requests_merged"),
            ("PR contributors", "pull_request_contributors"),
            ("Commits (4 weeks)", "commit_count_4_weeks"),
        ]
        for label, key in dev_fields:
            if dev.get(key) is not None:
                metrics.append(f"{label}: {dev[key]}")
        if community.get("reddit_subscribers") is not None:
            metrics.append(f"Reddit subscribers: {community['reddit_subscribers']}")
        if community.get("twitter_followers") is not None:
            metrics.append(f"Twitter followers: {community['twitter_followers']}")

        if not metrics:
            return (
                f"# Developer activity for {symbol} as of {curr_date}\n"
                "Developer/community activity is unavailable: CoinGecko no longer "
                "serves historical developer data for an as-of date. Proceeding "
                "without developer-activity metrics (a keyed or GitHub-API source "
                "would be needed for backtest-safe historical dev activity)."
            )
        header = [
            f"# Developer & community activity for {symbol} ({coin_id}) as of {curr_date}",
            "# Source: CoinGecko",
        ]
        return "\n".join(header + metrics)
    except Exception as e:
        return (
            f"# Developer activity for {symbol} as of {curr_date}\n"
            f"Data unavailable (CoinGecko: {e})."
        )


register_source(
    "coingecko",
    {
        "get_tokenomics": get_tokenomics,
        "get_dev_activity": get_dev_activity,
    },
)
