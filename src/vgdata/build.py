"""build() - one call that assembles every dataset and reports what is wrong.

Usage:
    from vgdata import build
    ds = build()
    ds.flags          # data-quality report
    ds.master         # fund-level fundamentals
    ds.tr             # daily total returns
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from . import prices, quality, vanguard
from .config import PROCESSED, today_stamp

# The brief's roster (S7.2), used only to assert the feed covers what we expect.
BRIEF_ROSTER = """
VBIL VGUS VUSB VSDB VGSH VCSH BSV VTIP BND BIV VGIT VCIT VMBS VTC VTG VCRB VPLS
BNDP VGVT VTP BNDX BNDW BLV VCLT VGLT EDV VCHY VGHY VWOB VGMS VCEB VTI VOO VV
MGC VONE VTHR VO IVOO VXF VB VTWO VIOO VTV VUG MGV MGK VONV VONG VOOV VOOG VOE
VOT VBR VBK VFMV VFMO VFMF VFQY VFVA VIG VYM VIGI VYMI VDC VPU VHT VIS VAW VFH
VOX VCR VGT VDE VNQ VNQI VXUS VEU VEA VWO VEXC VGK VPL VSS VT VDG VDV ESGV VSGX
VDIG VUSG VUSV
""".split()


@dataclass
class Dataset:
    master: pd.DataFrame            # fund-level fundamentals, investable only
    dropped: pd.DataFrame           # structurally excluded, with reasons
    quotes: pd.DataFrame            # bid/ask + distribution calendar
    panel: dict = field(repr=False) # raw price fields
    tr: pd.DataFrame = field(repr=False)   # daily total return
    pr: pd.DataFrame = field(repr=False)   # daily price-only return
    flags: pd.DataFrame = field(repr=False)

    @property
    def blocking(self) -> pd.DataFrame:
        return self.flags[self.flags["severity"] == quality.BLOCK]

    def summary(self) -> str:
        n_block = len(self.blocking)
        counts = self.flags["severity"].value_counts().to_dict() if not self.flags.empty else {}
        return (
            f"universe {len(self.master)} ETFs (+{len(self.dropped)} excluded) | "
            f"returns {self.tr.shape[0]}d x {self.tr.shape[1]} | "
            f"flags {counts} | {'BLOCKED' if n_block else 'GATE 1 PASS'}"
        )


def build(force: bool = False, quotes: bool = True) -> Dataset:
    payload = vanguard.fetch_funddetail(force=force)
    all_etfs = vanguard.fund_master(payload)
    master, dropped = vanguard.investable_universe(all_etfs)

    panel = prices.fetch_prices(master.index, force=force)
    tr = prices.total_return(panel)
    pr = prices.price_return(panel)

    qdf = vanguard.fetch_quotes(master.index) if quotes else pd.DataFrame()

    flags = (
        quality.check_master(all_etfs, BRIEF_ROSTER)
        + quality.check_history(panel, master)
        + quality.check_adjustment(panel)
        + quality.check_vendor_agreement(panel, master)
    )
    ds = Dataset(master, dropped, qdf, panel, tr, pr, quality.report(flags))

    stamp = today_stamp()
    master.to_parquet(PROCESSED / f"fund_master_{stamp}.parquet")
    tr.to_parquet(PROCESSED / f"total_returns_{stamp}.parquet")
    pr.to_parquet(PROCESSED / f"price_returns_{stamp}.parquet")
    if not qdf.empty:
        qdf.to_parquet(PROCESSED / f"quotes_{stamp}.parquet")
    ds.flags.to_csv(PROCESSED / f"quality_flags_{stamp}.csv", index=False)
    return ds
