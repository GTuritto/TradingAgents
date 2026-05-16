from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tradingagents.agents.utils.agent_utils import (
    build_instrument_context,
    get_chain_activity,
    get_dev_activity,
    get_language_instruction,
    get_tokenomics,
    get_tvl,
)


def create_onchain_analyst(llm):
    """Crypto deep-value analyst — the On-Chain Analyst.

    Occupies the same committee slot as the Fundamentals Analyst for
    crypto runs and writes into the same ``fundamentals_report`` state
    field, so downstream researchers and managers consume it unchanged.
    Its tools and prompt are crypto-native: tokenomics and on-chain
    metrics instead of corporate financial statements.
    """

    def onchain_analyst_node(state):
        current_date = state["trade_date"]
        instrument_context = build_instrument_context(state["company_of_interest"])

        tools = [
            get_tokenomics,
            get_tvl,
            get_dev_activity,
            get_chain_activity,
        ]

        system_message = (
            "You are a crypto research analyst tasked with analyzing the on-chain"
            " and tokenomics fundamentals of a cryptocurrency. Write a comprehensive"
            " report covering: supply and valuation (market capitalization, circulating"
            " supply, implied valuation), DeFi traction (total value locked and its"
            " recent trend), developer and ecosystem activity, and on-chain activity"
            " (active addresses and exchange flows) where available. Crypto assets have"
            " no earnings, balance sheets, or cash-flow statements — do NOT apply equity"
            " concepts such as P/E ratios, EPS, or dividend yield; reason instead in"
            " terms of network value, supply dynamics, adoption, and on-chain demand."
            " Some on-chain dimensions may be unavailable from open data providers; when"
            " a tool reports data as unavailable, note that explicitly and proceed with"
            " the metrics you do have rather than guessing. Provide specific, actionable"
            " insights with supporting evidence to help traders make informed decisions."
            " Use the available tools: `get_tokenomics` for supply and valuation,"
            " `get_tvl` for DeFi total value locked, `get_dev_activity` for developer and"
            " community activity, and `get_chain_activity` for active addresses and"
            " exchange flows."
            + " Make sure to append a Markdown table at the end of the report to"
            " organize key points in the report, organized and easy to read."
            + get_language_instruction()
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable,"
                    " prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop."
                    " You have access to the following tools: {tool_names}.\n{system_message}"
                    "For your reference, the current date is {current_date}. {instrument_context}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(instrument_context=instrument_context)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "fundamentals_report": report,
        }

    return onchain_analyst_node
