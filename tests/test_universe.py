"""Guards on the universe filter and the return reconstruction.

The municipal filter once matched "Com-muni-cation Services" and silently
dropped VOX. Substring filters over fund names are exactly the kind of thing
that fails quietly, so they get a test.
"""
from __future__ import annotations

import pandas as pd
import pytest

import vgdata
from vgdata import prices, vanguard

MUNICIPALS = {"VTEB", "VCRM", "VTEI", "VTEL", "VTES", "VSDM", "VTEC", "MUNY"}
TARGET_MATURITY = {f"VBC{c}" for c in "ABCDEFGHIJ"}


@pytest.fixture(scope="module")
def master():
    return vanguard.fund_master()


def test_feed_covers_the_brief_roster(master):
    missing = [t for t in vgdata.BRIEF_ROSTER if t not in master.index]
    assert not missing, f"brief roster tickers absent from the Vanguard feed: {missing}"


def test_municipal_filter_does_not_eat_sector_funds(master):
    kept, dropped = vanguard.investable_universe(master)
    # VOX is Communication Services, not a municipal bond fund.
    assert "VOX" in kept.index, "VOX was excluded; the municipal regex is matching a substring"
    for t in ("VDC", "VHT", "VIS", "VAW", "VFH", "VCR", "VGT", "VDE", "VNQ", "VPU"):
        assert t in kept.index, f"sector ETF {t} was wrongly excluded"


def test_exclusions_are_exactly_what_the_brief_specifies(master):
    _, dropped = vanguard.investable_universe(master)
    assert set(dropped.index) == MUNICIPALS | TARGET_MATURITY


def test_tips_flagged_as_real_yield(master):
    assert master.loc["VTIP", "yield_is_real"]
    assert master.loc["VTP", "yield_is_real"]
    assert not master.loc["VCSH", "yield_is_real"]


def test_total_return_includes_the_distribution():
    """A bill fund's return must survive the ex-date drop.

    VBIL's price falls ~29 bp on every ex-date and rises ~1-3 bp otherwise, so a
    price-only series scores near zero while the total-return series does not.
    """
    panel = prices.fetch_prices(["VBIL"])
    tr = prices.total_return(panel)["VBIL"].dropna()
    pr = prices.price_return(panel)["VBIL"].dropna()
    assert tr.mean() > pr.mean(), "dividends are not entering the total return"
    assert pr.min() < -20e-4, "expected a visible ex-date drop in the price series"
    assert tr.min() > -10e-4, "total return should not show the ex-date cliff"


def test_sawtooth_branches_differ_and_mean_is_unchanged():
    """The crediting convention must move sigma, not the mean.

    A distribution paid late does not change what the account earns over the
    window, only when the value arrives. If a change to the simulator ever moves
    the mean, the cash accounting has broken.
    """
    from vgdata import sawtooth as sw

    ds = vgdata.build()
    w = pd.Series({"VBIL": 0.5, "VGUS": 0.5})
    close = ds.panel["close"][w.index].dropna().tail(60)
    div = ds.panel["dividends"].reindex(close.index)[w.index].fillna(0.0)

    ex = sw.simulate_account(close, div, w, credit="ex_date").stats()
    pay = sw.simulate_account(close, div, w, credit="pay_date").stats()

    assert abs(ex["mean_bp"] - pay["mean_bp"]) < 0.05, "crediting date changed the mean return"
    assert pay["sd_bp"] > ex["sd_bp"] * 2, "lagged credit should inflate volatility"
    assert ex["sharpe"] > pay["sharpe"]


def test_integer_shares_and_cash_cap():
    """No fractional shares, and residual cash must clear the 10% organiser cap."""
    from vgdata import sawtooth as sw

    ds = vgdata.build()
    w = pd.Series({"VBIL": 0.25, "VGUS": 0.25, "VUSB": 0.22, "VGSH": 0.18, "VSDB": 0.10})
    close = ds.panel["close"][w.index].dropna().tail(40)
    div = ds.panel["dividends"].reindex(close.index)[w.index].fillna(0.0)
    path = sw.simulate_account(close, div, w, capital=250_000)

    assert (path.shares == path.shares.round()).all(), "fractional shares were bought"
    assert 0 <= path.residual_cash < 0.10 * 250_000, f"residual cash {path.residual_cash:.0f} breaches the cap"


def test_corr_shrink_preserves_variances():
    """The covariance fix must not touch the diagonal.

    Ledoit-Wolf on a universe holding both T-bill and equity funds inflates
    VBIL's volatility about 13x, which hides the entire short-end trade from the
    optimiser. `corr_shrink` must leave every sample variance exactly intact.
    """
    import numpy as np
    from vgdata import optimise as opt

    ds = vgdata.build()
    uni = ["VBIL", "VGUS", "VUSB", "VGSH", "VCSH", "VTI", "VGT", "VDE"]
    R = opt.common_window(opt.branch_returns(ds.panel, uni, credit="ex_date"), uni)

    sample = np.sqrt(np.diag(opt.covariance(R, "sample")))
    shrunk = np.sqrt(np.diag(opt.covariance(R, "corr_shrink")))
    np.testing.assert_allclose(shrunk, sample, rtol=1e-10)

    lw = np.sqrt(np.diag(opt.covariance(R, "ledoit_wolf")))
    vbil = R.columns.get_loc("VBIL")
    assert lw[vbil] > 5 * sample[vbil], "expected Ledoit-Wolf to inflate VBIL; guard is stale"


def test_max_sharpe_respects_cap_and_budget():
    import numpy as np
    from vgdata import optimise as opt

    ds = vgdata.build()
    uni = ["VBIL", "VGUS", "VUSB", "VGSH", "VSDB", "VTIP", "VCSH", "BSV"]
    R = opt.common_window(opt.branch_returns(ds.panel, uni, credit="ex_date"), uni)
    S = opt.covariance(R, "corr_shrink")
    mu = opt.expected_returns(ds.master, R.columns)
    w = opt.max_sharpe(mu, S, cap=0.25)

    assert abs(w.sum() - 1.0) < 1e-6, "weights must be fully invested"
    assert (w >= -1e-9).all(), "long-only violated"
    assert w.max() <= 0.25 + 1e-6, "position cap violated"
