"""vgdata - data layer for the WolfPack Vanguard ETF Challenge entry.

    import vgdata
    ds = vgdata.build()
    print(ds.summary())
    ds.flags        # resolve every BLOCK before touching the optimiser
"""
from .build import BRIEF_ROSTER, Dataset, build
from .config import DATA, INTERIM, PROCESSED, RAW, ROOT, load
from .prices import fetch_prices, observation_counts, price_return, total_return
from .rates import bill_total_return, fetch_tbill, proxy_series
from .spreads import blended_spread, corwin_schultz, cost_of_entry, estimate_spreads
from .vanguard import (
    fetch_funddetail,
    fetch_quotes,
    fund_master,
    investable_universe,
)

__all__ = [
    "build", "Dataset", "BRIEF_ROSTER",
    "load", "ROOT", "DATA", "RAW", "INTERIM", "PROCESSED",
    "fetch_funddetail", "fund_master", "fetch_quotes", "investable_universe",
    "fetch_prices", "total_return", "price_return", "observation_counts",
    "fetch_tbill", "bill_total_return", "proxy_series",
    "estimate_spreads", "corwin_schultz", "cost_of_entry", "blended_spread",
]
