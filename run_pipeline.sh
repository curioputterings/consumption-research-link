#!/usr/bin/env bash
# Run the consumption→research link end to end.
# Scripts are stdlib-only (json/csv/urllib/sqlite3), so any Python 3.10+ works.
# Override the interpreter with the PY env var if needed.
# The upstream malls/ and tech_sci_jobs/ repos are expected as siblings of this
# repo; override with MALL_ROOT / JOBS_DB env vars otherwise.
set -euo pipefail
cd "$(dirname "$0")"
PY="${PY:-python3}"

echo "[1/4] controls — World Bank macro (rents, remittances, GDP/cap, Gini)"
"$PY" controls/fetch_macro.py

echo "[2/4] stage2 — consumption affluence from mall directories"
"$PY" src/stage2_consumption_affluence.py

echo "[3/4] residual — consumption affluence net of export ECI  (HEADLINE)"
"$PY" src/stage_residual.py

echo "[4/4] stage5 — link residual to research roadmaps + frontier"
"$PY" src/stage5_roadmap_link.py

echo
echo "Done. Outputs:"
echo "  data/derived/country_residual.csv   (headline residual / rentier index)"
echo "  data/derived/city_affluence.csv      (per-city texture)"
echo "  data/derived/research_link.csv       (consumption ↔ roadmap)"
echo "  RESIDUAL.md, RESEARCH_LINK.md         (writeups)"
