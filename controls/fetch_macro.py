#!/usr/bin/env python3
"""
controls/fetch_macro.py — the netting layer's identification variables.

Pulls the macro controls that let stage-2 consumption affluence be read as
productive capability (CLAUDE.md thesis #2): you must net out resource RENTS and
REMITTANCES before reading a luxury retail surface as local capability. Affluence
has four roads to the same basket — complex exports, rents, remittances, and
accumulated wealth/inflows — and only the first is productive capability.

Source: World Bank Indicators API (free, no key). For each country we take the
LATEST non-null observation in a recent window and record its year (vintage),
because resource-rents/remittances series lag a few years and lag unevenly by
country.

Raw API responses are cached immutably under data/raw/ (timestamped); the
normalised table lands in data/normalized/macro_controls.csv.
"""
import json, os, sys, time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW = os.path.join(ROOT, "data", "raw")
NORM = os.path.join(ROOT, "data", "normalized")
os.makedirs(RAW, exist_ok=True)
os.makedirs(NORM, exist_ok=True)

ISO3 = ["SGP", "PHL", "MYS", "THA", "VNM", "IDN", "AUS", "NZL", "BGD"]

INDICATORS = {
    "gdp_pc_ppp":   "NY.GDP.PCAP.PP.CD",   # GDP per capita, PPP (current intl $)
    "resource_rents_pct_gdp": "NY.GDP.TOTL.RT.ZS",  # Total natural resources rents (% GDP)
    "remittances_pct_gdp":    "BX.TRF.PWKR.DT.GD.ZS",  # Personal remittances received (% GDP)
    "gini":         "SI.POV.GINI",         # Gini index (inequality caveat)
}

WINDOW = "2015:2024"  # take latest non-null inside this window


def fetch(indicator, iso, retries=4):
    url = (f"https://api.worldbank.org/v2/country/{iso}/indicator/{indicator}"
           f"?format=json&date={WINDOW}&per_page=200")
    last = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=45) as r:
                return json.load(r)
        except Exception as e:  # transient WB API timeouts are common
            last = e
            time.sleep(1.5 * (attempt + 1))
    raise last


def latest_nonnull(payload):
    """payload[1] is the obs list newest-first; return (value, year)."""
    if not isinstance(payload, list) or len(payload) < 2 or payload[1] is None:
        return None, None
    for obs in payload[1]:  # API returns newest first
        if obs.get("value") is not None:
            return float(obs["value"]), int(obs["date"])
    return None, None


def main():
    stamp = time.strftime("%Y%m%d")
    rows = {iso: {"iso3": iso} for iso in ISO3}
    raw_dump = {}
    for name, code in INDICATORS.items():
        for iso in ISO3:
            payload = fetch(code, iso)
            raw_dump[f"{code}:{iso}"] = payload
            val, yr = latest_nonnull(payload)
            rows[iso][name] = val
            rows[iso][name + "_year"] = yr
            print(f"{iso} {name:24s} = {val!s:>10}  ({yr})")
            time.sleep(0.15)

    raw_path = os.path.join(RAW, f"wb_macro_{stamp}.json")
    with open(raw_path, "w") as f:
        json.dump(raw_dump, f)
    print(f"\nraw cached -> {raw_path}")

    # write normalized csv
    cols = ["iso3"]
    for name in INDICATORS:
        cols += [name, name + "_year"]
    out = os.path.join(NORM, "macro_controls.csv")
    import csv
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for iso in ISO3:
            w.writerow(rows[iso])
    print(f"normalized -> {out}")


if __name__ == "__main__":
    main()
