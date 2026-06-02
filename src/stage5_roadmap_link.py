#!/usr/bin/env python3
"""
src/stage5_roadmap_link.py  —  closing the ladder: CONSUMPTION  ->  ROADMAPS.

This is the repo's namesake link. It places, side by side for each SEA country:

  (a) the CONSUMPTION-side read  — the residual + rentier/remittance/aligned
      label from src/stage_residual.py (what funds the affluence: productive
      complexity, resource rents, remittances, or entrepot/wealth);

  (b) the REVEALED RESEARCH FRONTIER — mean techno-science skill level and
      frontier proximity across the 8 strategic domains, from the sibling
      Techno-Science Observatory (tech_sci_jobs/data/jobs.db, cells table,
      gemini_research estimates); and

  (c) the DECLARED ROADMAP AMBITION GAP — mean (target_level - current skill)
      across domains, from the same DB's ambition table: how far each national
      R&D roadmap reaches beyond today's revealed capability.

The synthesis (written into RESEARCH_LINK.md) reads the divergence: a rentier
economy with a low frontier base but a large ambition gap is attempting to
convert rents into complexity by roadmap fiat (foresight or over-reach); an
"aligned" economy whose consumption already tracks its export complexity and
whose ambition gap is modest is on a coherent path.

Output: data/derived/research_link.csv
"""
import json, os, csv, sqlite3, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DERIVED = os.path.join(ROOT, "data", "derived")
# the sibling Techno-Science Observatory's SQLite DB; sibling checkout by
# default, override with the JOBS_DB env var.
JOBS_DB = os.environ.get("JOBS_DB") or os.path.normpath(
    os.path.join(ROOT, "..", "tech_sci_jobs", "data", "jobs.db"))

# iso3 (our convention) -> iso2 (jobs.db convention)
ISO3_TO_2 = {"IDN": "ID", "THA": "TH", "MYS": "MY", "VNM": "VN",
             "PHL": "PH", "SGP": "SG"}


def read_csv(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def frontier_signals(iso2):
    """mean skill, mean frontier, ambition target, gap across domains."""
    c = sqlite3.connect(JOBS_DB)
    skills = [r[0] for r in c.execute(
        "select skill_level from cells where country_iso=? and source='gemini_research'"
        " and skill_level is not null", (iso2,))]
    fronts = [r[0] for r in c.execute(
        "select frontier from cells where country_iso=? and source='gemini_research'"
        " and frontier is not null", (iso2,))]
    # pair current skill with declared target per domain for the gap
    cur = {r[0]: r[1] for r in c.execute(
        "select domain, max(skill_level) from cells where country_iso=?"
        " and skill_level is not null group by domain", (iso2,))}
    tgt = {r[0]: r[1] for r in c.execute(
        "select domain, target_level from ambition where country_iso=?"
        " and target_level is not null", (iso2,))}
    c.close()
    gaps = [tgt[d] - cur.get(d, 0) for d in tgt]
    return {
        "frontier_skill_mean": round(statistics.mean(skills), 2) if skills else None,
        "frontier_prox_mean": round(statistics.mean(fronts), 3) if fronts else None,
        "ambition_target_mean": round(statistics.mean(tgt.values()), 2) if tgt else None,
        "ambition_gap_mean": round(statistics.mean(gaps), 2) if gaps else None,
        "n_domains": len(cur),
    }


def main():
    resid = {r["iso3"]: r for r in read_csv(os.path.join(DERIVED, "country_residual.csv"))}
    rows = []
    for iso3, iso2 in ISO3_TO_2.items():
        r = resid.get(iso3)
        if not r:
            continue
        fs = frontier_signals(iso2)
        rows.append({
            "iso3": iso3,
            "country": r["country"],
            "CA_z": round(float(r["z_CA"]), 2),
            "export_eci": float(r["export_eci"]),
            "residual": round(float(r["residual"]), 2),
            "consumption_label": r["label"],
            "resource_rents_pct_gdp": round(float(r["resource_rents_pct_gdp"]), 1),
            "remittances_pct_gdp": round(float(r["remittances_pct_gdp"]), 1),
            **fs,
        })

    rows.sort(key=lambda r: -r["residual"])
    cols = ["iso3", "country", "residual", "consumption_label",
            "resource_rents_pct_gdp", "remittances_pct_gdp",
            "export_eci", "frontier_skill_mean", "frontier_prox_mean",
            "ambition_target_mean", "ambition_gap_mean", "n_domains"]
    out = os.path.join(DERIVED, "research_link.csv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    print("=" * 100)
    print("CONSUMPTION  ->  RESEARCH ROADMAP LINK  (SEA)")
    print("=" * 100)
    print(f"{'country':13s}{'resid':>7}{'consumption':>16}{'rents%':>8}{'remit%':>8}"
          f"{'ECI':>7}{'frontier':>9}{'ambition':>9}{'gap':>6}")
    for r in rows:
        print(f"{r['country']:13s}{r['residual']:>7.2f}{r['consumption_label']:>16}"
              f"{r['resource_rents_pct_gdp']:>8.1f}{r['remittances_pct_gdp']:>8.1f}"
              f"{r['export_eci']:>7.2f}{(r['frontier_skill_mean'] or 0):>9.2f}"
              f"{(r['ambition_target_mean'] or 0):>9.2f}{(r['ambition_gap_mean'] or 0):>6.2f}")
    print(f"\nwrote -> {out}")


if __name__ == "__main__":
    main()
