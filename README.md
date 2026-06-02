# consumption_research_link

🌏 **Live site:** https://curioputterings.github.io/consumption-research-link/

<a href="https://buymeacoffee.com/curioputterings" target="_blank"><img src="https://img.shields.io/badge/Buy%20me%20a%20coffee-FFDD00?style=flat-square&logo=buy-me-a-coffee&logoColor=black" alt="Buy Me a Coffee"></a>

Reconstruct a city's position on the economic-complexity frontier **from its
retail surface** (scraped mall directories), net out the affluence that *isn't*
productive capability, and check the result against national **research
roadmaps**. In one line: *economic complexity estimated from the consumption
side, checked against strategy.*

This repo is the **controls / netting + integration layer** that the upstream
data repos lacked. It does not re-scrape or re-compute mall complexity — it
consumes their outputs and produces the one number the project is named for:
**the residual**.

## The ladder, and where each repo sits

```
SHOPS → PRODUCTS → COMPLEXITY/AFFLUENCE → STRUCTURE → RESEARCH FRONTIER → ROADMAPS
└─────────── malls/ (stages 1–2) ──────────┘          └ tech_sci_jobs/ ┘  └ national-tech-plans/ ┘
                         │                                      │                    │
                         └──────────────► THIS REPO ◄───────────┴────────────────────┘
                            controls/ netting → residual → stage5 roadmap link
```

| upstream repo | provides | rung |
| --- | --- | --- |
| `../malls` | per-city tenant catalogues + mall ECI/PCI/RCA | shops → complexity |
| `../tech_sci_jobs` | revealed techno-science frontier + ambition gap (jobs.db) | research frontier |
| `../national-tech-plans` | 34 national R&D roadmaps (8 domains each) | roadmaps |
| `../tertiary_quality` | university value-capture index | frontier (supporting) |

## What this repo adds

The upstream complexity work measures **consumption complexity** — what a place
*buys*. The project's thesis is that this is **not** production complexity, and
the gap between them is the signal. So here:

1. **stage2** (`src/stage2_consumption_affluence.py`) — a magnitude-free
   **consumption-affluence index** per city from the retail surface, led by
   *distinct luxury-brand variety* (a diversity measure in the spirit of ECI,
   robust to scraping-coverage gaps).
2. **controls** (`controls/fetch_macro.py`) — the netting layer: World Bank
   resource rents %GDP, remittances %GDP, GDP/cap PPP, Gini.
3. **the residual** (`src/stage_residual.py`) — **consumption affluence minus
   what export ECI predicts**, attributed to rents / remittances / entrepôt.
   → **[RESIDUAL.md](./RESIDUAL.md)** (the headline).
4. **stage5** (`src/stage5_roadmap_link.py`) — joins the residual to the declared
   research roadmaps and revealed frontier. → **[RESEARCH_LINK.md](./RESEARCH_LINK.md)**.

## Headline result

The method, knowing nothing but mall directories + public macro data, recovers
**Australia as a textbook resource-rentier** (affluent retail, near-bottom export
complexity, 13.4%-of-GDP resource rents) and **Malaysia/Indonesia** alongside it,
while placing **Thailand as aligned** (consumption matches export complexity).
Validation: the consumption proxy correlates **+0.81** with export ECI and
**+0.51** with GDP/cap — the residual is the gap the first correlation leaves.
See RESIDUAL.md for the table and (substantial) caveats.

> ⚠️ **Key caveat — the remittance road is under-read.** The expected
> remittance-economy signature (Philippines: 8.7%-of-GDP inbound remittances
> funding affluent-looking consumption) does **not** appear — Philippine
> consumption-affluence is *deflated*, most plausibly because PH malls were
> partly name-only scrapes (SM/Ayala generic tenants uncaptured), not because the
> catchment is genuinely down-market. So the negative residuals on Philippines
> and Bangladesh (single catalogued mall) are the **least trustworthy** cells in
> the table and the clearest next data-quality target. The positive/rentier tail
> (Australia, Malaysia, Indonesia) is robust; the negative/remittance tail is
> coverage-limited. Read accordingly.

## Run

```bash
./run_pipeline.sh
```

Scripts are stdlib-only (json/csv/urllib/sqlite3); any Python 3.10+ works (no
pandas needed). The World Bank step needs network. The upstream `malls/` and
`tech_sci_jobs/` repos are expected as **siblings** of this checkout; point
elsewhere with the `MALL_ROOT` / `JOBS_DB` env vars, or the interpreter with `PY`.

## Layout

```
config/cities.json            city → country/iso3, headline & benchmark flags
crosswalks/                   canonical, versioned artifacts (never hardcode inline)
  luxury_brands.json            brand → luxury tier
  category_affluence.json       scope category → affluence tilt
  export_eci.json               Atlas-2023 export ECI per country
controls/fetch_macro.py       World Bank netting variables → data/normalized/
src/stage2_consumption_affluence.py   retail surface → consumption affluence
src/stage_residual.py         THE RESIDUAL → data/derived/country_residual.csv
src/stage5_roadmap_link.py    residual ↔ roadmaps → data/derived/research_link.csv
data/raw/ → normalized/ → derived/    immutable raw; never mutate upstream
```

## Discipline (from CLAUDE.md)

- **Composition, not magnitude** — presence/variety/share only; never sales volume.
- **Affluence ≠ capability** — always net rents + remittances before reading
  consumption as production.
- **Crosswalks are canonical** — versioned under `crosswalks/`.
- Research instrument, not a forecast; establishes divergence, not causation.
