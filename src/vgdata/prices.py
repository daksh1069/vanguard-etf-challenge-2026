"""Price and dividend history from Yahoo, cached to parquet.

Both adjusted and unadjusted closes are kept deliberately:

  unadjusted  what StockTrak charts and what the account's *position value*
              follows, including the ex-date drop
  adjusted    total return, for covariance and expected-return estimation

The gap between them is the distribution sawtooth, which is the whole question
in brief S9.1.
"""
from __future__ import annotations

import warnings

import pandas as pd
import yfinance as yf

from .config import INTERIM, load, today_stamp

warnings.filterwarnings("ignore", category=FutureWarning)


def fetch_prices(tickers, start: str | None = None, force: bool = False) -> dict[str, pd.DataFrame]:
    """Download OHLCV + dividends for every ticker in one batched call.

    Returns a dict of tidy frames keyed by field: close, adj_close, volume,
    dividends, high, low, open.
    """
    cfg = load()["data"]
    start = start or cfg["history_start"]
    tickers = sorted(set(tickers))
    cache = INTERIM / f"prices_{today_stamp()}.parquet"

    raw = None
    if cache.exists() and not force:
        cached = pd.read_parquet(cache)
        # The cache key is the date, so a universe change on the same day would
        # otherwise silently serve a panel that is missing tickers.
        have = {c.split("|")[0] for c in cached.columns}
        if set(tickers) <= have:
            raw = cached

    if raw is None:
        raw = yf.download(
            tickers,
            start=start,
            auto_adjust=False,
            actions=True,
            group_by="ticker",
            progress=False,
            threads=True,
        )
        raw.columns = [f"{a}|{b}" for a, b in raw.columns]
        raw.to_parquet(cache)

    out: dict[str, pd.DataFrame] = {}
    field_map = {
        "Close": "close",
        "Adj Close": "adj_close",
        "Volume": "volume",
        "Dividends": "dividends",
        "High": "high",
        "Low": "low",
        "Open": "open",
    }
    for yahoo_field, name in field_map.items():
        cols = {c.split("|")[0]: c for c in raw.columns if c.endswith(f"|{yahoo_field}")}
        if not cols:
            continue
        frame = raw[list(cols.values())].copy()
        frame.columns = list(cols.keys())
        out[name] = frame.sort_index(axis=1)

    if not isinstance(out["close"].index, pd.DatetimeIndex):
        for k in out:
            out[k].index = pd.to_datetime(out[k].index)
    for k in out:
        out[k].index = out[k].index.tz_localize(None) if out[k].index.tz else out[k].index
        out[k].index.name = "date"
    return out


def total_return(panel: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Daily total return rebuilt from unadjusted close + dividends.

    Computed independently of Yahoo's 'Adj Close' so the two can be reconciled;
    a mismatch is the failure mode that would silently corrupt every downstream
    return (PLAN Phase 2.2).
    """
    close, div = panel["close"], panel["dividends"].fillna(0.0)
    div = div.reindex(columns=close.columns, fill_value=0.0).reindex(close.index, fill_value=0.0)
    return ((close + div) / close.shift(1) - 1.0).iloc[1:]


def price_return(panel: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Price-only return: what a position's mark-to-market does, ex-distribution."""
    return panel["close"].pct_change().iloc[1:]


def observation_counts(panel: dict[str, pd.DataFrame]) -> pd.Series:
    return panel["close"].notna().sum().sort_values()
