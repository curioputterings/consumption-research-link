#!/usr/bin/env python3
"""
src/stage_residual.py  —  THE HEADLINE OUTPUT.

Computes the RESIDUAL: consumption-implied affluence minus what export
complexity alone would predict. That residual is the project's rentier /
entrepot / remittance index — a retail-side re-derivation of Hausmann's
complexity-income gap (CLAUDE.md thesis #2, glossary "the residual").

Construction (deliberately assumption-light, n is small):
  1. City consumption-affluence (CA) = weighted mean of standardized signals
     from stage 2 (lux_intensity, lux_breadth[>=4 malls], premium_tilt[covered]).
  2. Aggregate CA to country (coverage-weighted mean over cities with enough
     data) — because the netting variables (export ECI, rents, remittances) are
     national.
  3. Standardize CA and export ECI across countries. residual = z(CA) - z(ECI).
     Both are unit-free ranks, so the residual is "how much more affluent the
     retail surface looks than the country's export complexity can explain."
     No fragile 9-point OLS slope is trusted; we report it only for reference.
  4. NET / ATTRIBUTE: read the positive residual against resource rents (% GDP)
     and remittances (% GDP). Classify each country:
        rentier     — residual largely co-located with high resource rents
        remittance  — ... with high inbound remittances
        entrepot    — high residual, low on both → trade/finance hub or wealth
        aligned     — residual ~ 0; consumption matches productive complexity
  5. Validate: CA should track GDP/cap (PPP). We report that correlation as a
     sanity check that the retail proxy is reading affluence at all.

Outputs:
  data/derived/city_affluence.csv     — per-city CA components (texture)
  data/derived/country_residual.csv   — the headline table
"""
import json, os, csv, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
NORM = os.path.join(ROOT, "data", "normalized")
DERIVED = os.path.join(ROOT, "data", "derived")
os.makedirs(DERIVED, exist_ok=True)

cfg = json.load(open(os.path.join(ROOT, "config", "cities.json")))
ECI = json.load(open(os.path.join(ROOT, "crosswalks", "export_eci.json")))["eci"]

# --- manual, cited fallbacks for the two WB remittance nulls -----------------
# Singapore is a net remittance SENDER; inbound received is negligible (~0).
# Vietnam's WB %GDP series is null in-window; World Bank/KNOMAD put inbound
# remittances at ~4.5% of GDP (US$13-14bn on ~US$430bn GDP, 2023). Documented
# here rather than silently imputed.
REMIT_FALLBACK = {"SGP": 0.0, "VNM": 4.5}

# component weights for the city composite. Luxury-brand VARIETY (how many
# distinct global maisons operate in the city) is the headline signal: it is a
# diversity measure in the exact spirit of economic complexity, magnitude-free,
# and robust to the heartland-mall dilution that punishes density/breadth. It is
# log-compressed (log1p) so a city is not rewarded linearly for catalogue size.
# Documented; sensitivity noted in RESIDUAL.md.
WT = {"z_variety": 0.45, "z_intensity": 0.30, "z_tilt": 0.25}


def read_csv(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def zscore(values):
    """z-score a list, ignoring None; returns dict index->z (None passthrough)."""
    xs = [v for v in values if v is not None]
    if len(xs) < 2:
        return [0.0 if v is not None else None for v in values]
    m = sum(xs) / len(xs)
    sd = math.sqrt(sum((v - m) ** 2 for v in xs) / (len(xs) - 1)) or 1.0
    return [((v - m) / sd if v is not None else None) for v in values]


def pearson(a, b):
    pairs = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    if len(pairs) < 3:
        return None
    xs, ys = zip(*pairs)
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in pairs)
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx == 0 or vy == 0:
        return None
    return cov / math.sqrt(vx * vy)


# ----------------------------------------------------------------------------
# 1. city consumption-affluence
# ----------------------------------------------------------------------------
cons = read_csv(os.path.join(NORM, "city_consumption.csv"))
for r in cons:
    for k in ("n_total", "n_malls", "n_classified", "ultra_variety"):
        r[k] = int(r[k])
    for k in ("lux_intensity", "lux_breadth", "premium_tilt"):
        r[k] = fnum(r[k])
    r["coverage_ok"] = int(r["coverage_ok"])
    r["log_variety"] = math.log1p(r["ultra_variety"])
    r["tilt_use"] = r["premium_tilt"] if r["coverage_ok"] else None

z_var = zscore([r["log_variety"] for r in cons])
z_int = zscore([r["lux_intensity"] for r in cons])
z_tlt = zscore([r["tilt_use"] for r in cons])
for r, zv, zi, zt in zip(cons, z_var, z_int, z_tlt):
    r["z_variety"], r["z_intensity"], r["z_tilt"] = zv, zi, zt
    parts = {"z_variety": zv, "z_intensity": zi, "z_tilt": zt}
    num = sum(WT[k] * v for k, v in parts.items() if v is not None)
    den = sum(WT[k] for k, v in parts.items() if v is not None)
    r["CA_city"] = num / den if den else None

# write city texture table
with open(os.path.join(DERIVED, "city_affluence.csv"), "w", newline="") as f:
    cols = ["city", "country", "iso3", "region", "headline", "bench",
            "n_total", "n_malls", "ultra_variety", "lux_intensity", "premium_tilt",
            "coverage_ok", "z_variety", "z_intensity", "z_tilt", "CA_city"]
    w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    for r in sorted(cons, key=lambda r: -(r["CA_city"] or -9)):
        w.writerow(r)

# ----------------------------------------------------------------------------
# 2. aggregate CA to country (coverage-weighted mean over cities w/ n_total>=300)
# ----------------------------------------------------------------------------
macro = {r["iso3"]: r for r in read_csv(os.path.join(NORM, "macro_controls.csv"))}
by_country = {}
for r in cons:
    if r["n_total"] < 300 or r["CA_city"] is None:
        continue
    by_country.setdefault(r["iso3"], []).append(r)

countries = []
for iso, rows in by_country.items():
    wsum = sum(x["n_classified"] for x in rows) or 1
    ca = sum(x["CA_city"] * x["n_classified"] for x in rows) / wsum
    primate = max(rows, key=lambda x: x["n_total"])
    m = macro.get(iso, {})
    remit = fnum(m.get("remittances_pct_gdp"))
    if remit is None:
        remit = REMIT_FALLBACK.get(iso)
    countries.append({
        "iso3": iso,
        "country": rows[0]["country"],
        "region": rows[0]["region"],
        "bench": rows[0]["bench"],
        "n_cities": len(rows),
        "primate_city": primate["city"],
        "CA": ca,
        "export_eci": ECI.get(iso, {}).get("eci"),
        "eci_rank": ECI.get(iso, {}).get("rank"),
        "gdp_pc_ppp": fnum(m.get("gdp_pc_ppp")),
        "resource_rents_pct_gdp": fnum(m.get("resource_rents_pct_gdp")),
        "remittances_pct_gdp": remit,
        "gini": fnum(m.get("gini")),
    })

# ----------------------------------------------------------------------------
# 3. residual = z(CA) - z(ECI)
# ----------------------------------------------------------------------------
z_ca = zscore([c["CA"] for c in countries])
z_eci = zscore([c["export_eci"] for c in countries])
for c, za, ze in zip(countries, z_ca, z_eci):
    c["z_CA"] = za
    c["z_ECI"] = ze
    c["residual"] = za - ze  # >0 : affluence beyond export complexity

# reference OLS slope (CA ~ ECI), reported but not used for the residual
slope_ref = pearson([c["CA"] for c in countries], [c["export_eci"] for c in countries])

# ----------------------------------------------------------------------------
# 4. attribute the residual: rentier vs remittance vs entrepot
# ----------------------------------------------------------------------------
RENT_HI, REMIT_HI = 5.0, 4.0   # % GDP thresholds (documented)
RESID_HI = 0.5                 # ~0.5 sd of residual = "notably affluent-for-complexity"
for c in countries:
    rents = c["resource_rents_pct_gdp"] or 0
    remit = c["remittances_pct_gdp"] or 0
    res = c["residual"]
    if res >= RESID_HI:
        if rents >= RENT_HI and rents >= remit:
            c["label"] = "rentier"
        elif remit >= REMIT_HI and remit > rents:
            c["label"] = "remittance"
        else:
            c["label"] = "entrepot/wealth"
    elif res <= -RESID_HI:
        c["label"] = "complexity>consumption"
    else:
        c["label"] = "aligned"

# validation: does CA track income?
val_ca_gdp = pearson([c["CA"] for c in countries], [c["gdp_pc_ppp"] for c in countries])
val_ca_eci = pearson([c["CA"] for c in countries], [c["export_eci"] for c in countries])

# ----------------------------------------------------------------------------
# write headline table + console report
# ----------------------------------------------------------------------------
countries.sort(key=lambda c: -c["residual"])
cols = ["iso3", "country", "region", "primate_city", "n_cities", "CA",
        "z_CA", "export_eci", "z_ECI", "residual", "label",
        "gdp_pc_ppp", "resource_rents_pct_gdp", "remittances_pct_gdp", "gini"]
with open(os.path.join(DERIVED, "country_residual.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    for c in countries:
        w.writerow({k: (round(c[k], 4) if isinstance(c[k], float) else c[k]) for k in cols})

print("=" * 92)
print("HEADLINE RESIDUAL  —  consumption-implied affluence minus export-complexity prediction")
print("=" * 92)
print(f"{'country':13s}{'CA_z':>7}{'ECI':>7}{'ECIz':>7}{'RESID':>8}  "
      f"{'rents%':>7}{'remit%':>7}  {'label':<22}")
for c in countries:
    print(f"{c['country']:13s}{c['z_CA']:>7.2f}{c['export_eci']:>7.2f}{c['z_ECI']:>7.2f}"
          f"{c['residual']:>8.2f}  {(c['resource_rents_pct_gdp'] or 0):>7.1f}"
          f"{(c['remittances_pct_gdp'] or 0):>7.1f}  {c['label']:<22}")
print("-" * 92)
print(f"validation  corr(CA, GDPpc PPP) = {val_ca_gdp:+.2f}   "
      f"corr(CA, export ECI) = {val_ca_eci:+.2f}")
print(f"            (the residual is the gap the second correlation leaves on the table)")
print(f"\nwrote -> data/derived/country_residual.csv  and  data/derived/city_affluence.csv")
