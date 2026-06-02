#!/usr/bin/env python3
"""
src/stage2_consumption_affluence.py

Stage 2 of the ladder (SHOPS -> PRODUCTS -> COMPLEXITY/AFFLUENCE), the
consumption-side estimator. Reads the per-city tenant catalogues scraped under
malls/<city>_shopping/.../data/stores.json and derives a city-level CONSUMPTION
AFFLUENCE index from the *composition* of the retail surface.

Thesis discipline (CLAUDE.md):
  #1 Composition, not magnitude. Every signal here is a RATE or a SHARE — a
     presence density, never a transaction volume. We never claim how much is
     bought, only what is on offer.
  #2 This is AFFLUENCE/DEMAND, not productive capability. The number says the
     catchment can afford a complex import basket; netting against export ECI
     (the residual, computed downstream) is what separates the four roads to
     that basket (complex exports vs rents vs remittances vs wealth inflows).

Three composition signals, each robust to a different weakness:
  A. lux_intensity  — weighted luxury-house store occurrences / total stores.
                      Detected on store_name, so it SURVIVES the category-
                      classification gaps (name-only scrapes) that bias the
                      category mix. A 'Louis Vuitton' counts even if its scope
                      field is null.
  B. lux_breadth    — share of a city's malls that host >=1 ultra-luxury maison.
                      Mall-level presence: how many distinct affluent catchments
                      exist. Robust to differing catalogue size.
  C. premium_tilt   — category-mix tilt (Jewellery/Beauty/Fashion up, Value/
                      Supermarket down). Most exposed to coverage gaps, so it
                      carries the least weight and we emit a coverage flag.

Output: data/normalized/city_consumption.csv (all components + coverage flags).
The composite index and z-scoring happen in src/stage_residual.py, where export
ECI is also in scope.
"""
import json, os, csv, glob, unicodedata, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
NORM = os.path.join(ROOT, "data", "normalized")
os.makedirs(NORM, exist_ok=True)

cfg = json.load(open(os.path.join(ROOT, "config", "cities.json")))
CITIES = cfg["cities"]
# mall_root is relative to the repo root (sibling checkout) by default; override
# with the MALL_ROOT env var if the upstream malls repo lives elsewhere.
MALL_ROOT = os.environ.get("MALL_ROOT") or os.path.normpath(
    os.path.join(ROOT, cfg["mall_root"]))
LUX = json.load(open(os.path.join(ROOT, "crosswalks", "luxury_brands.json")))
CATW = json.load(open(os.path.join(ROOT, "crosswalks", "category_affluence.json")))["tilt"]

ULTRA = LUX["tiers"]["ultra"]
PREMIUM = LUX["tiers"]["premium"]
W = LUX["weights"]


def fold(s):
    """lower-case, strip accents, collapse non-alnum to single spaces, pad."""
    if not s:
        return " "
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[^a-z0-9&]+", " ", s)
    return " " + s.strip() + " "


# pre-fold brand tokens, longest first so 'louis vuitton' beats a stray 'louis'
ULTRA_F = sorted(({fold(b).strip() for b in ULTRA}), key=len, reverse=True)
PREM_F = sorted(({fold(b).strip() for b in PREMIUM}), key=len, reverse=True)


def brand_tier(name_folded):
    """Return ('ultra'|'premium'|None, matched_token|None) for a folded name.
    Whole-token containment: the brand must appear surrounded by spaces."""
    for b in ULTRA_F:
        if f" {b} " in name_folded:
            return "ultra", b
    for b in PREM_F:
        if f" {b} " in name_folded:
            return "premium", b
    return None, None


def stores_path(city):
    p = os.path.join(MALL_ROOT, f"{city}_shopping", "shopping", "data", "stores.json")
    return p if os.path.exists(p) else None


def process_city(city, meta):
    path = stores_path(city)
    if not path:
        return None
    recs = json.load(open(path))
    if not recs:
        return None

    n_total = len(recs)
    cat_counts = {}
    n_classified = 0
    ultra_hits = premium_hits = 0
    malls_with_ultra = set()
    malls_all = set()
    ultra_brands = set()    # distinct ultra maisons present (diversity signal)
    premium_brands = set()

    for r in recs:
        mall = (r.get("mall") or "").strip() or "__unknown__"
        malls_all.add(mall)
        scope = (r.get("scope_of_business") or "").strip()
        if scope:
            n_classified += 1
            cat_counts[scope] = cat_counts.get(scope, 0) + 1
        tier, tok = brand_tier(fold(r.get("store_name")))
        if tier == "ultra":
            ultra_hits += 1
            malls_with_ultra.add(mall)
            ultra_brands.add(tok)
        elif tier == "premium":
            premium_hits += 1
            premium_brands.add(tok)

    n_malls = len(malls_all)
    lux_weighted = W["ultra"] * ultra_hits + W["premium"] * premium_hits
    lux_intensity = lux_weighted / n_total if n_total else 0.0
    lux_breadth = len(malls_with_ultra) / n_malls if n_malls else 0.0

    # category shares over classified stores, premium tilt
    shares = {c: cat_counts.get(c, 0) / n_classified for c in CATW} if n_classified else {}
    premium_tilt = sum(shares.get(c, 0.0) * w for c, w in CATW.items())

    n_cats = sum(1 for c in CATW if cat_counts.get(c, 0) > 0)
    # coverage quality: a city with few categories present and a high share of
    # the three "fallback" buckets (F&B/Supermarket/Services) was largely
    # name-only — its category tilt is unreliable (CLAUDE.md caveat).
    fallback_share = sum(shares.get(c, 0.0) for c in
                         ("Food & Beverage", "Supermarket & Convenience", "Services"))
    coverage_ok = (n_classified >= 100 and n_cats >= 9 and fallback_share < 0.80)

    return {
        "city": city,
        "country": meta["country"],
        "iso3": meta["iso3"],
        "region": meta["region"],
        "headline": int(bool(meta.get("headline"))),
        "bench": int(bool(meta.get("bench"))),
        "n_total": n_total,
        "n_classified": n_classified,
        "n_malls": n_malls,
        "n_categories": n_cats,
        "ultra_hits": ultra_hits,
        "premium_hits": premium_hits,
        "ultra_variety": len(ultra_brands),
        "premium_variety": len(premium_brands),
        "malls_with_ultra": len(malls_with_ultra),
        "lux_intensity": round(lux_intensity, 6),
        "lux_breadth": round(lux_breadth, 4),
        "premium_tilt": round(premium_tilt, 4),
        "fallback_share": round(fallback_share, 4),
        "coverage_ok": int(coverage_ok),
    }


def main():
    rows = []
    for city, meta in CITIES.items():
        row = process_city(city, meta)
        if row:
            rows.append(row)
        else:
            print(f"  (skip {city}: no stores.json)")
    rows.sort(key=lambda r: -r["lux_breadth"])

    cols = list(rows[0].keys())
    out = os.path.join(NORM, "city_consumption.csv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    print(f"\n{len(rows)} cities -> {out}\n")
    rows.sort(key=lambda r: -r["ultra_variety"])
    print(f"{'city':14s}{'iso':5s}{'n_tot':>7}{'uVar':>6}{'ultra':>7}{'mlux':>6}"
          f"{'intens':>9}{'breadth':>9}{'tilt':>8}{'cov':>5}")
    for r in rows:
        print(f"{r['city']:14s}{r['iso3']:5s}{r['n_total']:>7}{r['ultra_variety']:>6}"
              f"{r['ultra_hits']:>7}{r['malls_with_ultra']:>6}{r['lux_intensity']:>9.4f}"
              f"{r['lux_breadth']:>9.3f}{r['premium_tilt']:>8.3f}{r['coverage_ok']:>5}")


if __name__ == "__main__":
    main()
