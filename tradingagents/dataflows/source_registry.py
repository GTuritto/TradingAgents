"""Named registry of data-source adapters.

Each data source (a crypto exchange, an on-chain provider, a news
provider) registers its per-method implementations under a vendor name.
``interface.py`` folds the registry into its routing table, so adding a
new source is a ``register_source()`` call in the source's own module
rather than an edit to ``interface.py``'s import block. Selecting an
already-registered source for a tool category is then pure configuration
(``data_vendors`` / ``tool_vendors``).
"""

from typing import Callable, Dict

# {source_name: {method_name: implementation}}
_SOURCES: Dict[str, Dict[str, Callable]] = {}


def register_source(name: str, methods: Dict[str, Callable]) -> None:
    """Register a data source's method implementations under ``name``.

    ``methods`` maps method names (e.g. "get_stock_data") to the callable
    that serves them. Calling this again for the same name merges in the
    additional methods.
    """
    _SOURCES.setdefault(name, {}).update(methods)


def registered_sources() -> Dict[str, Dict[str, Callable]]:
    """Return a copy of the {source_name: {method: impl}} registry."""
    return {name: dict(methods) for name, methods in _SOURCES.items()}
