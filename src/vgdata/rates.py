"""Treasury bill yields from FRED, and the synthetic bill total return used to
proxy VBIL and VGUS before their February 2025 inception (brief S11.1).

FRED bill series are quoted on a *discount* basis, so they are converted to a
bond-equivalent daily accrual rather than divided by 252 naively.
"""
from __future__ import annotations

import pandas as pd
from pandas_datareader import data as pdr

from .config import INTERIM, today_stamp

SERIES = {"DTB4WK": "bill_1m", "DTB3": "bill_3m"}


def fetch_tbill(start: str = "2019-01-01", end: str | None = None, force: bool = False) -> pd.DataFrame:
    cache = INTERIM / f"tbill_{today_stamp()}.parquet"
    if cache.exists() and not force:
        return pd.read_parquet(cache)
    end = end or pd.Timestamp.today().date().isoformat()
    df = pdr.DataReader(list(SERIES), "fred", start, end).rename(columns=SERIES)
    df = df.ffill().dropna(how="all")
    df.index.name = "date"
    df.to_parquet(cache)
    return df


def bill_total_return(series: pd.Series, days_to_maturity: int = 30) -> pd.Series:
    """Daily total return of a rolled bill position held at the quoted discount rate.

    Discount rate d on a bill of n days maturity implies price P = 1 - d*n/360,
    so the bond-equivalent yield is (1-P)/P * 365/n. Held overnight, the accrual
    is that yield / 365.
    """
    d = series.astype(float) / 100.0
    price = 1.0 - d * days_to_maturity / 360.0
    bey = (1.0 - price) / price * 365.0 / days_to_maturity
    return (bey / 365.0).rename(series.name)


def proxy_series(panel_index: pd.DatetimeIndex, which: str = "bill_1m") -> pd.Series:
    """Daily total-return proxy aligned to the price panel's trading calendar."""
    bills = fetch_tbill()
    ret = bill_total_return(bills[which], 30 if which == "bill_1m" else 91)
    return ret.reindex(panel_index).ffill()
