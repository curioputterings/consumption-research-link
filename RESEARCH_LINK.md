# Consumption → Research-Roadmap Link (SEA)

_Snapshot 2026-06-02. The repo's namesake: it joins the **consumption-side
residual** (RESIDUAL.md) to the **declared national research roadmaps** and the
**revealed techno-science frontier**, closing the inference ladder
`SHOPS → … → RESEARCH FRONTIER → ROADMAPS`. Built by `src/stage5_roadmap_link.py`._

## The two axes

- **Consumption axis** (this repo) — the residual and its label: is a country's
  affluence backed by productive complexity, or by **rents / remittances /
  entrepôt wealth**?
- **Research axis** (sibling [Techno-Science Observatory](../tech_sci_jobs) +
  [national-tech-plans](../national-tech-plans)) — **frontier** = mean revealed
  skill level across 8 strategic domains (1–5); **ambition gap** = mean
  (roadmap target − current skill). How far each roadmap reaches beyond today's
  base.

| country | residual | consumption reading | rents% | remit% | export ECI | frontier (1–5) | ambition gap | roadmap posture |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| **Malaysia**   | +0.79 | rentier | 6.9 | 0.4 | 1.03 | **1.89** | +0.11 | National Semiconductor Strategy (2024) on a real back-end/packaging base |
| **Indonesia**  | +0.48 | rentier (borderline) | 5.2 | 1.1 | −0.24 | **1.33** | **+0.33** | Resource-nationalist: nickel→EV-battery downstreaming; semiconductor ATP entry |
| **Vietnam**    | +0.29 | aligned, remittance-tilted | 2.5 | 4.5 | 0.35 | 1.44 | **0.00** | Semiconductor Strategy to 2030/2050 + rare-earths plan; export complexity rising |
| **Thailand**   | −0.17 | aligned | 1.8 | 1.8 | 0.89 | 1.67 | +0.22 | BCG model + late (2026) semiconductor strategy; EV 30@30 |
| **Singapore**  | −0.62 | complexity > consumption (benchmark) | 0.0 | 0.0 | 2.52 | **3.78** | −0.11 | RIE2025 / NQS / Semiconductor flagship — consolidating an existing frontier |
| **Philippines**| −0.80 | complexity > consumption* | 2.0 | 8.7 | 0.92 | _n/a_ | _n/a_ | not in the observatory's 30-country panel |

\* coverage-caveated (see RESIDUAL.md). Frontier/ambition n/a where the country
is outside the Techno-Science Observatory panel.

## The reading: four postures where the two axes meet

1. **Build-complexity-from-rents — Indonesia.** The riskiest, most interesting
   cell. Rentier-tilted affluence (residual +0.48 on 5.2% resource rents), the
   **lowest revealed frontier** in the set (1.33), yet the **largest ambition
   gap** (+0.33). Its roadmap is explicitly a *conversion bet*: ban raw-commodity
   exports, force nickel downstreaming into EV batteries, enter semiconductors at
   the back-end (ATP). This is precisely the rentier-to-capability move the
   residual flags — and where "foresight vs over-reach" is genuinely undecided.

2. **Rent-cushioned but grounded — Malaysia.** Also rentier (residual +0.79, the
   highest), but with a **real frontier base** (1.89, top of the developing set)
   and a **small ambition gap** (+0.11). Its semiconductor strategy leverages an
   existing assembly/test/packaging industry rather than reaching past it. Rents
   cushion; the roadmap stays near capability.

3. **Coherent climbers — Vietnam & Thailand.** Their consumption *aligns* with
   their export complexity (residuals near zero) and their ambition gaps are
   small (Vietnam exactly 0.00, Thailand +0.22). These are economies whose
   shelves, exports, and roadmaps tell the *same* story — Vietnam's rising export
   ECI (0.35 and climbing) backing a semiconductor strategy that matches its
   trajectory. The least divergence between specified future and present.

4. **Mature frontier — Singapore (benchmark).** The only economy *below* the
   line: consumption < complexity, frontier 3.78, **negative** ambition gap. Its
   roadmaps consolidate a frontier it already holds rather than reaching for one.
   Treated as calibration outlier, not template.

## So what

The residual and the ambition gap are **two independent estimators of the same
latent thing** — the distance between what a place *consumes/earns* and what it
can *make*. When they agree (Vietnam: aligned consumption, zero gap) the
development path is coherent. When they pull apart (Indonesia: rent-fed affluence,
thin base, largest reach) the roadmap is carrying the weight the productive
structure cannot yet bear — which is exactly where the **diffusion clock** (how
fast a roadmap priority becomes shelved reality, or doesn't) should be watched.

## Provenance & limits

- Frontier/ambition: `tech_sci_jobs/data/jobs.db` (`cells`, `ambition`),
  Gemini-grounded estimates — directional, not counts. Philippines and Bangladesh
  are outside that 30-country panel.
- Roadmap postures: `national-tech-plans/*.md` summary tables (official plan +
  issuing body per domain).
- Consumption residual: see RESIDUAL.md (n = 8, composition-only, PH/BD coverage
  caveats).
- This is a research instrument, not a forecast. It establishes *divergence*,
  not causation.
