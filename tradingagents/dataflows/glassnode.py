"""Keyed on-chain activity adapter (graceful-degradation seam).

Active-address counts and exchange net-flows are genuine on-chain metrics
that no open provider serves; they require a keyed provider such as
Glassnode. Per the crypto-trader-base design (decision D6), no paid
provider is integrated in this change. This module is the registered seam
for that future adapter: with no key configured it degrades to a clear
"unavailable" message so the On-Chain Analyst proceeds on the metrics it
does have, never crashing the run.
"""

import os

from .source_registry import register_source


def get_chain_activity(symbol: str, curr_date: str) -> str:
    """Active addresses and exchange flows for a crypto asset as of ``curr_date``.

    Degrades gracefully: returns an "unavailable" partial report when no
    keyed on-chain provider is configured.
    """
    if not os.getenv("GLASSNODE_API_KEY"):
        return (
            f"# On-chain activity for {symbol} as of {curr_date}\n"
            "Active-address and exchange-flow metrics are unavailable: no keyed "
            "on-chain provider is configured. Set GLASSNODE_API_KEY to enable "
            "this dimension once the Glassnode adapter lands. Proceeding without "
            "on-chain activity metrics."
        )
    return (
        f"# On-chain activity for {symbol} as of {curr_date}\n"
        "GLASSNODE_API_KEY is set, but the Glassnode adapter is a planned "
        "follow-up to the crypto-trader-base change (design D6). Active-address "
        "and exchange-flow metrics are not yet sourced."
    )


register_source("glassnode", {"get_chain_activity": get_chain_activity})
