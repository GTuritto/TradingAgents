from langchain_core.tools import tool
from typing import Annotated
from tradingagents.dataflows.interface import route_to_vendor


@tool
def get_tokenomics(
    symbol: Annotated[str, "crypto asset symbol, e.g. BTC"],
    curr_date: Annotated[str, "as-of date in yyyy-mm-dd format"],
) -> str:
    """
    Retrieve supply and valuation (tokenomics) metrics for a crypto asset
    as of a given date: price, market cap, trading volume, and implied
    circulating supply. Uses the configured onchain_data vendor.
    """
    return route_to_vendor("get_tokenomics", symbol, curr_date)


@tool
def get_tvl(
    symbol: Annotated[str, "crypto asset symbol, e.g. BTC"],
    curr_date: Annotated[str, "as-of date in yyyy-mm-dd format"],
) -> str:
    """
    Retrieve DeFi total value locked (TVL) for a crypto asset's chain as
    of a given date, including the recent TVL trend. Uses the configured
    onchain_data vendor.
    """
    return route_to_vendor("get_tvl", symbol, curr_date)


@tool
def get_dev_activity(
    symbol: Annotated[str, "crypto asset symbol, e.g. BTC"],
    curr_date: Annotated[str, "as-of date in yyyy-mm-dd format"],
) -> str:
    """
    Retrieve developer and community activity for a crypto asset as of a
    given date: GitHub commits, stars, forks, issues, and community
    following. Uses the configured onchain_data vendor.
    """
    return route_to_vendor("get_dev_activity", symbol, curr_date)


@tool
def get_chain_activity(
    symbol: Annotated[str, "crypto asset symbol, e.g. BTC"],
    curr_date: Annotated[str, "as-of date in yyyy-mm-dd format"],
) -> str:
    """
    Retrieve on-chain activity for a crypto asset as of a given date:
    active addresses and exchange net-flows. These metrics require a
    keyed on-chain provider; the tool reports the dimension as
    unavailable when none is configured.
    """
    return route_to_vendor("get_chain_activity", symbol, curr_date)
