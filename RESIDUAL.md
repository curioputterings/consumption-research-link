# The Residual — consumption-implied affluence net of export complexity

_Snapshot 2026-06-02. The headline output of this repo (CLAUDE.md glossary,
"the residual"). A retail-side re-derivation of Hausmann's complexity–income
gap: we replace **income** with a **consumption-side affluence proxy** estimated
from shopping-mall directories, regress it against **export complexity (ECI)**,
and read the gap. A positive gap is the **rentier / entrepôt / remittance
index** — affluence a country's productive complexity alone cannot explain._

## What the number is (and is not)

Two framings are load-bearing (CLAUDE.md theses #1–#2):

1. **Composition, not magnitude.** Every consumption signal is a rate, share, or
   variety count read off *what is on offer* in mall directories — never a sales
   volume or footfall (those are proprietary and unavailable). We never claim how
   much is bought.
2. **Affluence, not capability.** A mall full of complex imports measures the
   catchment's *demand/affluence*, not the country's *productive capability*.
   Affluence has four roads to the same luxury basket — complex exports, resource
   **rents**, **remittances**, and accumulated **wealth/inflows**. The residual
   isolates the three non-productive roads by netting out the first.

## Method

```
SHOPS → consumption-affluence (CA) ──┐
                                     ├── residual = z(CA) − z(export ECI)
export ECI (Atlas 2023) ─────────────┘            ↓
                                  net against resource rents % GDP + remittances % GDP
                                                  ↓
                            label: rentier · remittance · entrepôt/wealth · aligned
```

- **CA (consumption affluence)** — a city composite of three magnitude-free
  signals from `src/stage2_consumption_affluence.py`, z-scored across 33 cities:
  - **luxury-brand variety** (0.45) — count of *distinct* global maisons present
    (a diversity measure in the exact spirit of economic complexity; detected on
    store names so it survives category-classification gaps), log-compressed;
  - **luxury intensity** (0.30) — weighted luxury occurrences per store;
  - **premium category tilt** (0.25) — Jewellery/Beauty/Fashion up, Value/
    Supermarket down; used only where category coverage is adequate.
  Aggregated to country by coverage-weighted mean over cities with ≥300 stores.
- **Export ECI** — Harvard Growth Lab, Atlas of Economic Complexity (2023),
  `crosswalks/export_eci.json`. The independent productive-capability estimator.
- **Residual** — `z(CA) − z(ECI)` across the 8 covered countries. A unit-free
  rank gap; we deliberately avoid trusting a fragile 8-point OLS slope.
- **Netting controls** — World Bank: natural-resource rents (% GDP) and personal
  remittances received (% GDP), `controls/fetch_macro.py`.

## Validation — does the retail proxy read affluence at all?

| check | correlation |
| --- | --- |
| CA vs GDP per capita (PPP) | **+0.51** |
| CA vs export ECI | **+0.81** |

The proxy tracks income and complexity in the right direction and magnitude. The
residual is precisely the part of affluence the second correlation leaves on the
table.

## Headline table

ECI = export Economic Complexity Index (Atlas 2023). residual = z(CA) − z(ECI);
positive ⇒ retail surface looks *more* affluent than export complexity predicts.

| country | CA (z) | ECI | ECI (z) | **residual** | rents %GDP | remit %GDP | reading |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **Malaysia**   |  1.29 |  1.03 |  0.50 | **+0.79** |  6.9 | 0.4 | **rentier** |
| **Australia**  | −0.50 | −0.82 | −1.09 | **+0.59** | 13.4 | 0.1 | **rentier** (textbook) |
| **Indonesia**  | −0.11 | −0.24 | −0.59 | **+0.48** |  5.2 | 1.1 | rentier (borderline) |
| **Vietnam**    |  0.20 |  0.35 | −0.08 | **+0.29** |  2.5 | 4.5 | aligned, remittance-tilted |
| **Thailand**   |  0.21 |  0.89 |  0.38 | **−0.17** |  1.8 | 1.8 | **aligned** |
| **Bangladesh** | −1.86 | −1.08 | −1.31 | **−0.55** |  0.6 | 6.1 | complexity > consumption* |
| **Singapore**  |  1.16 |  2.52 |  1.78 | **−0.62** |  0.0 | 0.0 | complexity > consumption (benchmark) |
| **Philippines**| −0.40 |  0.92 |  0.41 | **−0.80** |  2.0 | 8.7 | complexity > consumption* |

\* heavily coverage-caveated — see below.

## What the residual recovers

- **Australia is the proof of concept.** The method, knowing *nothing* about
  Australia's mining sector, places it as a **resource-rentier**: a retail
  surface more affluent than its export complexity (ECI −0.82, among the lowest
  in the rich world) can explain, with the gap sitting on top of the highest
  resource rents in the sample (13.4% of GDP). This is the Hausmann gap, read
  from shop directories.
- **Malaysia** is the same story at SEA scale — high affluence, mid ECI,
  oil/gas/palm rents at 6.9% of GDP. **Indonesia** is a borderline third
  (residual +0.48, rents 5.2%); its nickel-downstreaming roadmap (see
  RESEARCH_LINK.md) is the rentier-to-complexity conversion attempt.
- **Thailand is aligned.** Its export complexity (ECI 0.89: electronics, autos)
  and its retail affluence sit on the same line — productive capability and
  consumption agree. Nothing to explain away.
- **Singapore** (the calibration benchmark, treated as outlier per CLAUDE.md)
  sits *below* the line: even the region's deepest luxury market (54 distinct
  maisons) cannot out-rank a world-#1 export ECI. Consistent with an economy
  whose complexity, not its consumption, is the extreme.

## Caveats (do not over-read)

- **n = 8 countries.** Illustrative, not inferential. New Zealand is dropped
  (both catalogued cities < 300 stores).
- **Coverage confound on the negative tail.** Philippines and Bangladesh CA are
  deflated by *scraping coverage*, not only by genuinely down-market malls: PH
  malls were partly name-only (SM/Ayala generic tenants uncaptured), and Dhaka is
  a single catalogued mall. Their "complexity > consumption" labels are the least
  trustworthy cells in the table. Notably, the *expected* remittance-economy
  signature (PH remittances 8.7% of GDP funding affluent-looking consumption)
  does **not** surface — most plausibly a data-coverage artifact, and the clearest
  next data-quality target.
- **ECI assembly inflation.** Philippines' ECI (0.92) rests on electronics
  *assembly*; like all ECI it can overstate deep capability — a known reason a
  high-ECI country can still look "consumption-poor."
- **Composition only.** Presence of maisons ≠ volume of luxury sold. The index
  reads how *many distinct* affluent catchments a city sustains, never how much
  they transact.

## Reproduce

```bash
# stdlib only (json/csv/urllib); any python3 works. malls/ is expected as a
# sibling checkout — else set MALL_ROOT.
python3 controls/fetch_macro.py              # World Bank → data/normalized/macro_controls.csv
python3 src/stage2_consumption_affluence.py  # malls    → data/normalized/city_consumption.csv
python3 src/stage_residual.py                # residual → data/derived/country_residual.csv
```

Inputs are versioned: `crosswalks/export_eci.json` (Atlas vintage),
`crosswalks/luxury_brands.json`, `crosswalks/category_affluence.json`.
