"""Vanguard fund-level data.

Two public JSON endpoints, both plain HTTP, no auth, no browser:

  list/funddetail/all        SEC yield, expense ratio, inception, asset class,
                             risk, NAV/market price, YTD, trailing returns
  vmf/api/{TICKER}/delayedPrice   bid/ask, ex-dividend date, pay date

SEC yield is a fund disclosure, not a market price, so it is available from
nowhere else. Everything numeric in the brief is re-derived from here.
"""
from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
import requests

from .config import HEADERS, RAW, load, today_stamp

FUNDDETAIL_URL = "https://investor.vanguard.com/investment-products/list/funddetail/all"
QUOTE_URL = "https://investor.vanguard.com/vmf/api/{ticker}/delayedPrice"

# Footnote the feed attaches to TIPS funds. Detecting the flag from the text
# beats maintaining a hardcoded ticker list that silently goes stale.
REAL_YIELD_FOOTNOTE = "DOES NOT INCLUDE ANY INCOME ADJUSTMENT"


def fetch_funddetail(force: bool = False) -> dict:
    """Pull the full Vanguard fund feed, caching one dated copy per day."""
    path = RAW / f"vanguard_funddetail_{today_stamp()}.json"
    if path.exists() and not force:
        return json.loads(path.read_text())
    resp = requests.get(FUNDDETAIL_URL, headers=HEADERS, timeout=90)
    resp.raise_for_status()
    payload = resp.json()
    path.write_text(json.dumps(payload))
    return payload


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return float("nan")


def _date(x):
    return str(x)[:10] if x else None


def fund_master(payload: dict | None = None) -> pd.DataFrame:
    """One row per ETF, with the fields the optimiser and the EDA need."""
    payload = payload or fetch_funddetail()
    rows = []
    for ent in payload["fund"]["entity"]:
        prof = ent.get("profile", {})
        if not prof.get("isETF"):
            continue
        yld = ent.get("yield") or {}
        notes = " | ".join(n.get("footnoteText", "") for n in (yld.get("yieldNote") or []))
        ret = (ent.get("monthEndAvgAnnualRtn") or {}).get("fundReturn") or {}
        price = (ent.get("dailyPrice") or {})
        rows.append(
            {
                "ticker": prof.get("ticker"),
                "name": prof.get("longName"),
                "fund_id": prof.get("fundId"),
                "cusip": prof.get("cusip"),
                "expense_ratio": _num(prof.get("expenseRatio")) / 100.0,
                "expense_ratio_asof": _date(prof.get("expenseRatioAsOfDate")),
                "sec_yield": _num(yld.get("yieldPct")) / 100.0,
                "sec_yield_asof": _date(yld.get("asOfDate")),
                # TIPS publish a REAL yield. Mixing it into a nominal expected
                # return vector understates it (brief appendix A.10).
                "yield_is_real": REAL_YIELD_FOOTNOTE in notes,
                "yield_note": notes,
                "inception": _date(prof.get("inceptionDate")),
                "asset_class": (prof.get("fundCategory", {}).get("high") or {}).get("name"),
                "category": prof.get("category"),
                "style": prof.get("customizedStyle"),
                "duration_bucket": prof.get("fixedIncomeInvestmentStyleName"),
                "management_style": prof.get("fundManagementStyle"),
                "is_index": (prof.get("fundFact") or {}).get("isIndex"),
                "is_money_market": (prof.get("fundFact") or {}).get("isMoneyMarket"),
                "risk_code": (ent.get("risk") or {}).get("code"),
                "risk_level": (ent.get("risk") or {}).get("level"),
                "nav": _num((price.get("regular") or {}).get("price")),
                "market_price": _num((price.get("market") or {}).get("price")),
                "price_asof": _date((price.get("market") or {}).get("asOfDate")),
                "ytd_pct": _num((ent.get("ytd") or {}).get("regular")) / 100.0,
                "ret_1y": _num(ret.get("oneYrPct")) / 100.0,
                "ret_since_inception": _num(ret.get("sinceInceptionPct")) / 100.0,
                "ret_asof": _date(ret.get("asOfDate")),
            }
        )
    df = pd.DataFrame(rows).set_index("ticker").sort_index()
    df["inception"] = pd.to_datetime(df["inception"])
    df["age_years"] = (pd.Timestamp.today() - df["inception"]).dt.days / 365.25
    return df


def _one_quote(ticker: str) -> dict:
    """Bid/ask and distribution timing for a single ticker."""
    out = {"ticker": ticker}
    try:
        r = requests.get(QUOTE_URL.format(ticker=ticker), headers=HEADERS, timeout=30)
        eq = r.json()["quotes"][0]["equity"]
        p = eq.get("pricing", {})
        # Two quote pairs are published and neither is reliable alone. The
        # closing pair can be a stale wide quote left at the bell (VGK prints
        # 85.56/91.35 against an 88.63 last trade); the live pair can be an
        # after-hours quote. Take whichever is tighter as an upper bound, and
        # let the Corwin-Schultz estimate in spreads.py carry the real number.
        pairs = []
        for lo, hi in (("closeBidPrice", "closeAskPrice"), ("bidPrice", "askPrice")):
            b, a = _num(p.get(lo)), _num(p.get(hi))
            if b > 0 and a > 0 and a >= b:
                pairs.append((a - b, b, a))
        last = _num(p.get("lastTradePrice"))
        if pairs:
            _, bid, ask = min(pairs)
            mid = (bid + ask) / 2
            spread_bp = (ask - bid) / mid * 1e4
        else:
            bid = ask = mid = spread_bp = float("nan")
        out.update(
            bid=bid,
            ask=ask,
            mid=mid,
            last=last,
            spread_bp=spread_bp,
            # Buying crosses the spread: StockTrak fills at real-time bid/ask.
            half_spread_bp=spread_bp / 2,
            # A quoted mid far from the last trade means the quote is stale.
            quote_stale=bool(last > 0 and mid == mid and abs(mid / last - 1) > 0.002),
            ex_div_date=_date(eq.get("exDividendDateTime")),
            pay_date=_date(eq.get("dividendPayDateTime")),
            dividend_per_share=_num(eq.get("dividendPerShare")),
        )
    except Exception as exc:  # noqa: BLE001 - recorded, not raised
        out["error"] = f"{type(exc).__name__}: {exc}"
    return out


def fetch_quotes(tickers, max_workers: int = 8) -> pd.DataFrame:
    """Bid/ask + distribution calendar for a list of tickers."""
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        rows = list(pool.map(_one_quote, list(tickers)))
    df = pd.DataFrame(rows).set_index("ticker")
    if {"ex_div_date", "pay_date"}.issubset(df.columns):
        ex = pd.to_datetime(df["ex_div_date"], errors="coerce")
        pay = pd.to_datetime(df["pay_date"], errors="coerce")
        df["pay_lag_days"] = (pay - ex).dt.days
    return df


def investable_universe(master: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Apply the brief's structural exclusions. Returns (kept, dropped)."""
    cfg = load()["universe"]
    reason = pd.Series("", index=master.index)

    if cfg.get("exclude_municipal"):
        # Tax exemption is worthless in a simulation, so municipals pay a yield
        # giveaway for a benefit that cannot be realised (brief S7.3).
        # Word-boundary anchored: a bare "Muni" substring also matches
        # "Com-muni-cation Services" and would wrongly drop VOX.
        pat = r"\bMunicipal\b|\bMuni\b|\bTax-Exempt\b"
        muni = master["category"].fillna("").str.contains(pat, case=False, regex=True) | master[
            "name"
        ].fillna("").str.contains(pat, case=False, regex=True)
        reason[muni & (reason == "")] = "municipal: strictly dominated without taxes"

    if cfg.get("exclude_target_maturity"):
        tgt = master["name"].fillna("").str.contains("Target Maturity", case=False)
        reason[tgt & (reason == "")] = "target-maturity: insufficient history"

    dropped = master[reason != ""].assign(drop_reason=reason[reason != ""])
    return master[reason == ""].copy(), dropped
