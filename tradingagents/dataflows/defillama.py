"""DefiLlama on-chain data adapter.

Serves DeFi total-value-locked (TVL) for an asset's chain from DefiLlama's
fully open, keyless API. As-of correctness is enforced by filtering the
historical series to data points on or before ``curr_date``. Any error
degrades to a clear partial message rather than raising.
"""

from datetime import datetime, timezone

import requests

from .source_registry import register_source

_BASE = "https://api.llama.fi"
_TIMEOUT = 20
_DAY_SECONDS = 86_400

# Symbol -> DefiLlama chain name. Unknown symbols fall back to a
# capitalized guess; a wrong guess yields a graceful "data unavailable".
_CHAINS = {
    "BTC": "Bitcoin",
    "ETH": "Ethereum",
    "XRP": "XRPL",
    "SOL": "Solana",
    "BNB": "BSC",
    "ADA": "Cardano",
}


def _chain(symbol: str) -> str:
    base = symbol.split("/")[0].strip().upper()
    return _CHAINS.get(base, base.capitalize())


def get_tvl(symbol: str, curr_date: str) -> str:
    """DeFi total value locked for the asset's chain as of ``curr_date``."""
    chain = _chain(symbol)
    try:
        resp = requests.get(
            f"{_BASE}/v2/historicalChainTvl/{chain}", timeout=_TIMEOUT
        )
        resp.raise_for_status()
        series = resp.json()

        cutoff = (
            datetime.strptime(curr_date, "%Y-%m-%d")
            .replace(tzinfo=timezone.utc)
            .timestamp()
        )
        # As-of bound: keep only data points dated on or before curr_date.
        past = [p for p in series if p.get("date", 0) <= cutoff]
        if not past:
            return (
                f"# DeFi TVL for {symbol} ({chain}) as of {curr_date}\n"
                "No DefiLlama TVL data on or before this date."
            )

        latest = past[-1]
        as_of = datetime.fromtimestamp(latest["date"], tz=timezone.utc).strftime(
            "%Y-%m-%d"
        )
        lines = [
            f"# DeFi TVL for {symbol} ({chain} chain) as of {curr_date}",
            "# Source: DefiLlama (keyless)",
            f"TVL (USD): {latest['tvl']:,.0f}",
            f"As-of data point: {as_of}",
        ]
        prior = [p for p in past if p["date"] <= latest["date"] - 30 * _DAY_SECONDS]
        if prior and prior[-1]["tvl"]:
            change = (latest["tvl"] - prior[-1]["tvl"]) / prior[-1]["tvl"] * 100
            lines.append(f"~30d TVL change: {change:+.1f}%")
        return "\n".join(lines)
    except Exception as e:
        return (
            f"# DeFi TVL for {symbol} as of {curr_date}\n"
            f"Data unavailable (DefiLlama: {e})."
        )


register_source("defillama", {"get_tvl": get_tvl})
