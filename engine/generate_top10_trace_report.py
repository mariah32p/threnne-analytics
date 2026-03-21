"""
Generate markdown trace reports from forecast_report.csv + parquets + raw epoch-3 CSVs.

Outputs:
  - reports/top10_rising_tropes_trace.md — global top 10 by weighted_score (CSV row order)
  - reports/forecast_signals_trace.md — same depth for API/dashboard splits (accelerating vs emerging)

Run from repo root:
  app/backend/.venv/bin/python engine/generate_top10_trace_report.py
"""

from __future__ import annotations

import glob
import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
SMOOTHING_DENOM = 2_360_000
TOP_N = 10
OUT_TOP10 = REPO_ROOT / "reports" / "top10_rising_tropes_trace.md"
OUT_SIGNALS = REPO_ROOT / "reports" / "forecast_signals_trace.md"


def load_taxonomy_flat(taxonomy_path: Path) -> tuple[dict[str, str], dict[str, list[str]]]:
    with open(taxonomy_path, encoding="utf-8") as f:
        raw = json.load(f)
    flat: dict[str, str] = {}
    for canonical, variants in raw.items():
        for v in variants:
            flat[v.lower()] = canonical
    return flat, raw


def shelf_variants_for_trope(canonical: str, raw_taxonomy: dict[str, list[str]]) -> list[str]:
    return list(raw_taxonomy.get(canonical, []))


def count_books_with_trope_in_processed_dir(
    canonical: str, flat_map: dict[str, str], processed_dir: Path
) -> tuple[int, dict[str, int]]:
    """Books (rows) in *_processed.csv that map at least one shelf to this trope."""
    per_file: dict[str, int] = {}
    total = 0
    for fp in sorted(glob.glob(str(processed_dir / "*_processed.csv"))):
        df = pd.read_csv(fp)
        name = os.path.basename(fp)
        n = 0
        for shelves_val in df.get("shelves", []):
            if pd.isna(shelves_val) or shelves_val == "{}":
                continue
            try:
                shelves_dict = json.loads(shelves_val)
            except (json.JSONDecodeError, TypeError):
                continue
            found = False
            for raw_shelf in shelves_dict.keys():
                c = flat_map.get(str(raw_shelf).lower().strip())
                if c == canonical:
                    found = True
                    break
            if found:
                n += 1
        per_file[name] = n
        total += n
    return total, per_file


def trope_section_lines(
    rank: int,
    trope: str,
    row: pd.Series,
    base_df: pd.DataFrame,
    mod_df: pd.DataFrame,
    n_base: int,
    n_mod: int,
    raw_tax: dict[str, list[str]],
    flat_map: dict[str, str],
    raw_epoch3: Path,
    extra_why: list[str] | None = None,
) -> list[str]:
    col = f"trope_{trope}"
    b_count = int(base_df[col].sum()) if col in base_df.columns else 0
    m_count = int(mod_df[col].sum()) if col in mod_df.columns else 0

    share_b = b_count / n_base if n_base else 0.0
    share_m = m_count / n_mod if n_mod else 0.0
    pseudo = (1.0 / SMOOTHING_DENOM) if b_count == 0 else share_b
    raw_lift = share_m / pseudo if pseudo else float("inf")
    capped = float(np.clip(raw_lift, 0, 999.99))
    wscore = capped * math.log1p(m_count)
    variants = shelf_variants_for_trope(trope, raw_tax)
    raw_total, per_file = count_books_with_trope_in_processed_dir(trope, flat_map, raw_epoch3)

    lines: list[str] = []
    lines.append(f"### {rank}. `{trope}`")
    lines.append("")
    lines.append("#### Snapshot from `forecast_report.csv`")
    lines.append("")
    lines.append(
        f"| Field | Value |\n| --- | --- |\n"
        f"| trend_lift (exported, capped) | {row['trend_lift']} |\n"
        f"| weighted_score | {row['weighted_score']} |\n"
        f"| epoch3_count | {int(row['epoch3_count'])} |\n"
        f"| baseline_count | {int(row['baseline_count'])} |\n"
        f"| epoch3_share (%, in CSV) | {row['epoch3_share']} |\n"
        f"| baseline_share (%, in CSV) | {row['baseline_share']} |"
    )
    lines.append("")
    lines.append("#### Recomputed from parquets (sanity check)")
    lines.append("")
    denom_note = "smoothed 1/2.36M" if b_count == 0 else "true baseline share"
    lines.append(
        f"| Quantity | Value |\n| --- | --- |\n"
        f"| Books with trope in baseline | **{b_count:,}** / {n_base:,} |\n"
        f"| Books with trope in epoch 3 | **{m_count:,}** / {n_mod:,} |\n"
        f"| Baseline share (fraction) | `{share_b:.10g}` |\n"
        f"| Epoch 3 share (fraction) | `{share_m:.10g}` |\n"
        f"| Pseudo baseline share (denominator) | `{pseudo:.10g}` ({denom_note}) |\n"
        f"| Raw lift (before cap) | `{raw_lift:.4g}` |\n"
        f"| Lift after cap | `{capped:.2f}` |\n"
        f"| log1p(epoch3_count) | `{math.log1p(m_count):.6f}` |\n"
        f"| weighted_score (recomputed) | `{wscore:.2f}` |"
    )
    lines.append("")
    lines.append("#### Why this rank (plain language)")
    lines.append("")
    if capped >= 999.99 and raw_lift > 999.99:
        lines.append(
            f"- **Lift hit the 999.99× UI cap.** Uncapped lift was ~**{raw_lift:.4g}×**, driven by "
            f"epoch-3 share **{share_m:.4%}** vs a very small baseline share "
            f"({'smoothed' if b_count == 0 else 'natural'} denominator)."
        )
    else:
        lines.append(
            f"- Lift **{capped:.2f}×** from epoch-3 share **{share_m:.4%}** vs baseline share **{share_b:.4%}**."
        )
    lines.append(
        f"- **Weighted score** (global ranking): `{capped:.2f} * log1p({m_count})` ≈ **{wscore:.1f}**."
    )
    if extra_why:
        for bullet in extra_why:
            lines.append(f"- {bullet}")
    lines.append("")
    lines.append("#### Taxonomy shelves mapped to this trope")
    lines.append("")
    if variants:
        for v in variants:
            lines.append(f"- `{v}`")
    else:
        lines.append("- *(no variants in dictionary)*")
    lines.append("")
    lines.append("#### Raw epoch-3 `*_processed.csv` attribution (re-count from JSON shelves)")
    lines.append("")
    lines.append(
        f"- **Sum of per-file book hits:** {raw_total} (parquet modern count was **{m_count}**; "
        "small mismatches can happen if parquet was built from a different file set or duplicates were collapsed.)"
    )
    lines.append("")
    for fname, cnt in sorted(per_file.items(), key=lambda x: -x[1]):
        if cnt:
            lines.append(f"- `{fname}`: **{cnt}** books with a shelf mapping to `{trope}`")
    if all(c == 0 for c in per_file.values()):
        lines.append("- *(no hits in current `data/raw/epoch_3_forecast/*_processed.csv` — check paths)*")
    lines.append("")
    lines.append("---")
    lines.append("")
    return lines


def build_intro_lines(n_base: int, n_mod: int, title: str, bullets: list[str]) -> list[str]:
    lines = [f"# {title}", ""]
    lines.append("Generated from on-disk artifacts (forecast CSV + parquets + raw epoch-3 CSVs).")
    lines.append("")
    lines.append("## How to read this")
    lines.append("")
    for b in bullets:
        lines.append(b)
    lines.append(
        f"- **Epoch 1 (baseline)** parquet: `{n_base:,}` books (`data/processed/epoch_1_baseline.parquet`)."
    )
    lines.append(
        f"- **Epoch 3 (forecast modern)** parquet: `{n_mod:,}` books (`data/processed/epoch_3_forecast.parquet`)."
    )
    lines.append(
        "- **Lift math** (matches `engine/03_calculate_lift.py`): if `baseline_count == 0`, denominator uses "
        f"`1 / {SMOOTHING_DENOM:,}`; else true baseline share. Then `trend_lift` is **clipped to 999.99**. "
        "`weighted_score = trend_lift * log1p(epoch3_count)`."
    )
    lines.append("")
    return lines


def main() -> None:
    forecast_path = REPO_ROOT / "data" / "exports" / "forecast_report.csv"
    baseline_pq = REPO_ROOT / "data" / "processed" / "epoch_1_baseline.parquet"
    modern_pq = REPO_ROOT / "data" / "processed" / "epoch_3_forecast.parquet"
    taxonomy_path = REPO_ROOT / "taxonomy" / "trope_dictionary.json"
    raw_epoch3 = REPO_ROOT / "data" / "raw" / "epoch_3_forecast"

    flat_map, raw_tax = load_taxonomy_flat(taxonomy_path)
    forecast = pd.read_csv(forecast_path)
    forecast["baseline_count"] = pd.to_numeric(forecast["baseline_count"], errors="coerce").fillna(0).astype(int)

    base_df = pd.read_parquet(baseline_pq)
    mod_df = pd.read_parquet(modern_pq)
    n_base = len(base_df)
    n_mod = len(mod_df)

    accelerating = forecast[forecast["baseline_count"] > 50].head(TOP_N)
    emerging = forecast[forecast["baseline_count"] <= 50].head(TOP_N)
    global_top = forecast.head(TOP_N)

    # --- File 1: global top 10 ---
    lines = build_intro_lines(
        n_base,
        n_mod,
        "Top 10 rising tropes — trace report (global weighted_score rank)",
        [
            "- **Order** = first 10 rows of `data/exports/forecast_report.csv` (sorted by `weighted_score` descending in `03_calculate_lift.py`).",
            "- This is **not** the same as the dashboard split (see `forecast_signals_trace.md`).",
        ],
    )
    lines.append("## Tropes")
    lines.append("")
    for rank, (_, row) in enumerate(global_top.iterrows(), start=1):
        trope = str(row["trope"])
        extra = None
        if rank == 1 and trope == "HE_FALLS_FIRST":
            extra = [
                "**Global #1 vs #2:** `ACCIDENTAL_PREGNANCY` also hits the lift cap; **HE_FALLS_FIRST** wins on **weighted_score** because **19** forecast books vs **7** → larger `log1p(count)`."
            ]
        lines.extend(
            trope_section_lines(
                rank, trope, row, base_df, mod_df, n_base, n_mod, raw_tax, flat_map, raw_epoch3, extra_why=extra
            )
        )

    OUT_TOP10.parent.mkdir(parents=True, exist_ok=True)
    OUT_TOP10.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_TOP10}")

    # --- File 2: dashboard / API split ---
    lines2 = build_intro_lines(
        n_base,
        n_mod,
        "Forecast signals — trace report (Accelerating vs Emerging)",
        [
            "- Matches **`GET /api/v1/forecast/tropes`** / dashboard: **Accelerating** = `baseline_count > 50`, first 10 rows in **forecast CSV order** within that filter; **Emerging** = `baseline_count <= 50`, first 10 in that slice.",
        ],
    )
    lines2.append("## Accelerating trends (`baseline_count` > 50)")
    lines2.append("")
    for rank, (_, row) in enumerate(accelerating.iterrows(), start=1):
        trope = str(row["trope"])
        lines2.extend(
            trope_section_lines(
                rank, trope, row, base_df, mod_df, n_base, n_mod, raw_tax, flat_map, raw_epoch3
            )
        )
    lines2.append("## Emerging terminology (`baseline_count` ≤ 50)")
    lines2.append("")
    for rank, (_, row) in enumerate(emerging.iterrows(), start=1):
        trope = str(row["trope"])
        lines2.extend(
            trope_section_lines(
                rank, trope, row, base_df, mod_df, n_base, n_mod, raw_tax, flat_map, raw_epoch3
            )
        )

    OUT_SIGNALS.write_text("\n".join(lines2), encoding="utf-8")
    print(f"Wrote {OUT_SIGNALS}")


if __name__ == "__main__":
    main()
