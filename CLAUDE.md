# CLAUDE.md

Project context for agents working in this repo. Read this before writing scrapers, ETL, or analysis code.

## What this project is

A pipeline that reconstructs a city's position on the economic-complexity / innovation frontier **from its retail surface** (scraped shopping-mall directories), then tests that reconstruction against the city's declared **national and corporate R&D roadmaps**. In one line: *economic complexity estimated from the consumption side, checked against strategy.*

Scope: Southeast Asian cities first — **Jakarta, Bangkok, Kuala Lumpur, Metro Manila, Ho Chi Minh City** (+ Hanoi). **Singapore** is the calibration benchmark (cleanest data; treat as an outlier, not a template).

## The core thesis the agent must internalise

The analysis is an **inference ladder** climbing from cheap/ubiquitous data to scarce/strategic data:

```
SHOPS → PRODUCTS → COMPLEXITY/INCOME → INDUSTRIAL STRUCTURE → RESEARCH FRONTIER → ROADMAPS
```

Two non-negotiable framings:

1. **The instrument reads COMPOSITION, not MAGNITUDE.** Mall directories tell you *what is on offer*, never *how much is bought*. Sales volume and footfall are proprietary and unavailable. Never infer transaction volume from tenant presence.

2. **Consumption complexity ≠ production complexity.** The Product Complexity Index (PCI) is defined over *exports*, i.e. what a place *makes*, not what it *buys*. A mall full of complex imports measures **affluence/demand**, not local productive capability. Affluence has four roads to the same luxury basket: complex exports, resource/financial **rents**, **remittances/transfers**, and accumulated wealth/capital inflows.

   → Therefore the **headline output is the RESIDUAL**: consumption-implied affluence *minus* what export complexity alone would predict. That residual is the **rentier / entrepôt / remittance index** — the strategically interesting per-city number, and a retail-side re-derivation of Hausmann's complexity–income gap. **Always net out resource rents and remittances before reading consumption as productive capability.**

3. The ladder is a **second, independent estimator of the income side** — not a replacement for trade data. The **disagreement** between the consumption estimate and the export-complexity estimate is the signal, not a bug.

## Pipeline stages

Each stage is a module: `src/stage{N}_*`. Inputs/outputs flow as versioned tables (parquet).

- **stage1_shops_to_products** — classify each scraped tenant into a goods/services basket on a shared taxonomy (HS for goods, a services scheme for the rest). LLM-assisted classification. *Output:* tenant → product-category table.
- **stage2_products_to_complexity** — join product categories to PCI; derive an income/affluence index from the price-tier and luxury-vs-necessity mix. *Output:* per-mall complexity + affluence scores.
- **stage3_complexity_to_structure** — infer feasible industrial structure via the Product Space / relatedness; **triangulate with real industry & labour data**, do not infer blind. *Output:* implied sector mix per city.
- **stage4_structure_to_frontier** — map sectors to the knowledge frontier via patent + publication relatedness (IPC/CPC ↔ industry concordances). *Output:* relevant research-frontier vector per city.
- **stage5_frontier_to_roadmaps** — parse roadmap docs; extract declared priorities; compute the gap vs the inferred frontier. *Output:* divergence map (foresight vs over-reach).
- **controls/** — the netting layer (export composition, rents, remittances, subnational catchment) that makes stage 2's residual meaningful. **Run before interpreting any stage-2 output.**

## Data sources (with access mode)

### Consumption surface (stage 1)
- **Mall-operator sites** — primary tenant lists. Prefer the hidden JSON endpoint behind the store-locator map over HTML parsing. Per-city, bespoke. `[scrape]`
- **Google Places API** — enrichment, geocode, categories. `[API, paid]`
- **OpenStreetMap / Overpass API** — universal POI baseline, same schema every city. `[API, free]`
- **Wayback Machine CDX API** — historical directory snapshots → the diffusion clock. `[API, free]`

### Complexity & trade (stages 2–3 + export control)
- **Harvard Growth Lab — Atlas of Economic Complexity** — PCI/ECI tables, Product Space network. `[bulk + API, free]`
- **OEC (Observatory of Economic Complexity)** — `[API, some tiers paid — verify]`
- **UN Comtrade API** — bilateral trade by HS product; the independent export-complexity estimator. `[API, free w/ key]`
- **BACI (CEPII)** — cleaned bilateral trade. `[bulk, free]`

### Macro controls (identification layer — cheapest part of the build)
- **World Bank Indicators API** — GDP/capita, natural-resource rents (% GDP), personal remittances (% GDP), Gini. `[API, free]`
- **KNOMAD** — bilateral remittance matrices. `[bulk, free]`
- **IMF** — national accounts. `[API, free]`

### Subnational / mall-catchment wealth (THE binding constraint)
- **Meta Relative Wealth Index** (Humanitarian Data Exchange / Data for Good) — gridded relative wealth, strong SEA coverage. `[bulk, free — verify hosting]`
- **VIIRS night-time lights** (NOAA / Earth Observation Group) — `[raster, free]`
- **WorldPop**, **Google Open Buildings** — population & footprint grids. `[raster, free]`
- NB: these proxy catchment *affluence*, never transaction volume.

### Research frontier (stage 4)
- **Google Patents** (BigQuery public dataset), **WIPO PATENTSCOPE**, **PatentsView (USPTO) API** — invention output, universal across SEA. `[API/bulk, free-ish]`
- **OpenAlex** — scholarly publication graph. `[API, free]`
- **IPC/CPC ↔ industry concordances** (OECD/WIPO) — public.

### Roadmaps (stage 5)
- National R&D strategy PDFs — parse, per country.
- **SEC EDGAR API** — corporate R&D-spend lines for listed firms. `[API, free]`
- Corporate patents/filings for declared priorities.

### National open-data portals (enrichment — uneven, do not depend on)
- **SG**: data.gov.sg, OneMap, URA — strongest (outlier).
- **MY**: data.gov.my (`api.data.gov.my`), OpenDOSM — strong, RESTful.
- **TH**: data.go.th (CKAN API), data.bangkok.go.th.
- **ID**: data.go.id (Satu Data), satudata.jakarta.go.id; geospatial via Jakarta Satu / BIG.
- **PH**: data.gov.ph — patchy, often links out; verify currency.
- **VN**: weak — rely on the universal backbone (OSM, Places, patents, mall scraping).

## Invariants & gotchas (do not violate)

- Composition ≠ magnitude (see thesis #1). No volume claims from presence data.
- Always net rents + remittances before reading consumption as production (thesis #2).
- Mall data → **local catchment** purchasing power, not national. Weight with RWI/night-lights; account for inequality and spatial unit.
- **Crosswalks are canonical artifacts.** The retail-category ↔ HS map and IPC ↔ industry map are the main error sources — version them under `crosswalks/`, never hardcode inline.
- **Scraping discipline:** read `robots.txt` and ToS; rate-limit; cache raw responses immutably; **timestamp every scrape** (the diffusion clock needs history); prefer official APIs and hidden JSON over HTML; **never defeat anti-bot or CAPTCHA** — if a source is gated (LinkedIn, most property portals), use an official API or skip it.
- Verify API access tiers before relying — OEC paid tiers and the RWI host are the most volatile.

## Conventions

- **Languages:** Python for scraping/ETL; R for the complexity & econometric analysis. (Adjust to actual stack.)
- **Data layout:** `data/raw/` (immutable, timestamped) → `data/normalized/` → `data/derived/`. Never mutate raw.
- **Secrets:** API keys in `.env` (gitignored). Never commit keys.
- **Per-city config:** one file under `config/cities/`. Keep city logic data-driven, not branched in code.
- **Reproducibility:** pin data vintages and crosswalk versions in each derived table's metadata.

## Glossary

- **ECI / PCI** — Economic / Product Complexity Index (Hidalgo–Hausmann). Defined over exports.
- **Product Space / relatedness** — network of which capabilities sit near which; predicts feasible structural moves.
- **The residual** — consumption-implied affluence minus export-complexity-implied affluence; the rentier/entrepôt/remittance index. The project's headline output.
- **Diffusion clock** — change over time in the gap between roadmap-priority sectors and tenant mix; how fast the specified future becomes the shelved present.
- **RWI** — Relative Wealth Index (Meta); gridded catchment-wealth proxy.
