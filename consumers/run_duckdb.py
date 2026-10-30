#!/usr/bin/env python3
"""DuckDB SQL Runner for Challenge 03 (Enterprise FinOps).

Executes queries from consumers/duckdb.sql against the local parquet dataset
and displays tabular outputs.
"""

import sys
from pathlib import Path
import duckdb

def main():
    repo_root = Path(__file__).resolve().parent.parent
    sql_path = repo_root / "consumers" / "duckdb.sql"
    data_path = repo_root / "sample" / "data" / "c03-beyond-the-mainframe" / "gold" / "workload_cost_daily.parquet"

    if not data_path.exists():
        print(f"Error: Gold dataset not found at {data_path}.", file=sys.stderr)
        print("Please run: python build/build.py build --challenge c03-beyond-the-mainframe --version v1 --out sample/data/c03-beyond-the-mainframe", file=sys.stderr)
        sys.exit(1)

    print("=" * 80)
    print(" Innovation Forum × R1X — Challenge 03: Beyond the Mainframe")
    print(" DuckDB Query Execution Engine")
    print("=" * 80)

    con = duckdb.connect()

    # Create local view
    con.execute(f"CREATE OR REPLACE VIEW cost AS SELECT * FROM read_parquet('{data_path}');")
    print(f"\n[OK] View 'cost' created from {data_path}\n")

    queries = [
        ("Query 1: Table Summary & Grain Verification",
         "SELECT count(*) AS rows, count(DISTINCT workload_id) AS workloads, min(usage_date) AS from_date, max(usage_date) AS to_date FROM cost;"),

        ("Query 2: Uniqueness Key Check (Expected: 0 duplicates)",
         "SELECT count(*) - count(DISTINCT (workload_id, usage_date)) AS duplicate_rows FROM cost;"),

        ("Query 3: Spend by Owner (Highlighting UNALLOCATED spend)",
         """SELECT business_unit,
                   round(sum(cost_gbp), 2) AS cost_gbp,
                   round(100 * sum(cost_gbp) / sum(sum(cost_gbp)) OVER (), 1) AS pct_of_total
            FROM cost GROUP BY 1 ORDER BY cost_gbp DESC LIMIT 15;"""),

        ("Query 4: Unit Economics & Normalisation by Platform",
         """SELECT platform,
                   round(sum(cost_gbp), 0) AS cost_gbp,
                   round(sum(vcpu_hours), 0) AS vcpu_hours,
                   round(sum(cost_gbp) / sum(vcpu_hours), 4) AS cost_per_vcpu_hour,
                   round(avg(utilisation_pct), 1) AS mean_utilisation_pct
            FROM cost GROUP BY 1 ORDER BY cost_per_vcpu_hour DESC;"""),

        ("Query 5: Near-Idle Waste Workloads (Utilisation < 5%)",
         """SELECT workload_id, platform, business_unit,
                   round(sum(cost_gbp), 2) AS annual_cost_gbp,
                   round(avg(utilisation_pct), 1) AS mean_utilisation_pct
            FROM cost GROUP BY 1, 2, 3 HAVING avg(utilisation_pct) < 5
            ORDER BY annual_cost_gbp DESC LIMIT 15;""")
    ]

    for title, q in queries:
        print("-" * 80)
        print(f" {title}")
        print("-" * 80)
        df = con.execute(q).df()
        print(df.to_string(index=False))
        print()

    print("=" * 80)
    print(" All DuckDB queries completed successfully.")
    print(" Launch the Streamlit dashboard for visual presentation:")
    print("   .venv/bin/streamlit run consumers/app.py")
    print("=" * 80)

if __name__ == "__main__":
    main()
