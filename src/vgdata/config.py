"""Config loading and project paths. Every constant lives in config.yaml."""
from __future__ import annotations

import datetime as dt
from functools import lru_cache
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
RAW, INTERIM, PROCESSED = DATA / "raw", DATA / "interim", DATA / "processed"
REPORTS = ROOT / "reports"

for _p in (RAW, INTERIM, PROCESSED, REPORTS):
    _p.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def load() -> dict:
    with open(ROOT / "config.yaml") as fh:
        return yaml.safe_load(fh)


def today_stamp() -> str:
    return dt.date.today().isoformat().replace("-", "")


USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
)
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/json",
    "Referer": "https://investor.vanguard.com/investment-products/list/etfs",
}
