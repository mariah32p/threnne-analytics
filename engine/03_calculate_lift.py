"""
Script 03: Calculate Trend Lift (Book-Level Frequency)
======================================================
Inputs:
  - data/processed/epoch_1_baseline.parquet
  - data/processed/epoch_2_backtest.parquet OR epoch_3_forecast.parquet
Output:
  - A definitive ranking of Rising Tropes (.csv report)

The Math:
  baseline_share = books_with_trope / total_baseline_books
  modern_share   = books_with_trope / total_modern_books
  trend_lift     = modern_share / baseline_share
  weighted_score = trend_lift * log(modern_book_count)
"""

import argparse
import os

import numpy as np
import pandas as pd


def get_epoch_shares(parquet_path: str, epoch_name: str) -> pd.DataFrame:
    """Calculates the percentage of books that contain each trope."""
    print(f"Loading {epoch_name} from {os.path.basename(parquet_path)}...")
    df = pd.read_parquet(parquet_path)

    total_books = len(df)
    trope_cols = [c for c in df.columns if c.startswith("trope_")]

    epoch_data = []
    for col in trope_cols:
        trope_name = col.replace("trope_", "")
        count = df[col].sum()
        share = count / total_books if total_books > 0 else 0

        epoch_data.append(
            {
                "trope": trope_name,
                f"{epoch_name}_count": count,
                f"{epoch_name}_share": share,
            }
        )

    print(f"  -> Analyzed {total_books:,} books.")
    return pd.DataFrame(epoch_data)


def calculate_lift(
    baseline_df: pd.DataFrame,
    modern_df: pd.DataFrame,
    modern_name: str,
    min_books: int = 10,
) -> pd.DataFrame:
    """Merges the epochs and applies the Threnne Trend Lift Math."""
    print("\nCalculating Trend Lift...")

    df = pd.merge(baseline_df, modern_df, on="trope", how="inner")

    df = df[df[f"{modern_name}_count"] >= min_books].copy()

    # THE CORE MATH (With Laplace Add-1 Smoothing)
    # If a trope didn't exist in the baseline, assume it appeared exactly 1 time out of 2.36 million books.
    pseudo_baseline_share = np.where(
        df["baseline_count"] == 0, (1.0 / 2360000), df["baseline_share"]
    )

    df["trend_lift"] = df[f"{modern_name}_share"] / pseudo_baseline_share

    # Optional UI Cap: Hard-cap the visual lift at 999x so the charts don't break
    df["trend_lift"] = np.clip(df["trend_lift"], 0, 999.99)

    # THE VOLUME FILTER (Penalty Box)
    df["weighted_score"] = df["trend_lift"] * np.log1p(df[f"{modern_name}_count"])

    df["trend_lift"] = df["trend_lift"].round(2)
    df["weighted_score"] = df["weighted_score"].round(2)
    df["baseline_share"] = (df["baseline_share"] * 100).round(2)
    df[f"{modern_name}_share"] = (df[f"{modern_name}_share"] * 100).round(2)

    df = df.sort_values(by="weighted_score", ascending=False)

    return df[
        [
            "trope",
            "trend_lift",
            "weighted_score",
            f"{modern_name}_count",
            "baseline_count",
            f"{modern_name}_share",
            "baseline_share",
        ]
    ]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", required=True, help="Path to epoch_1_baseline.parquet")
    parser.add_argument("--modern", required=True, help="Path to modern parquet (Epoch 2 or 3)")
    parser.add_argument(
        "--modern_name",
        default="modern",
        help="Label for the modern columns (e.g. 'epoch2' or 'epoch3')",
    )
    parser.add_argument("--output", required=True, help="Where to save the final report CSV")
    parser.add_argument(
        "--min_books",
        type=int,
        default=5,
        help="Minimum modern books featuring trope to qualify",
    )
    args = parser.parse_args()

    baseline_df = get_epoch_shares(args.baseline, "baseline")
    modern_df = get_epoch_shares(args.modern, args.modern_name)

    final_report = calculate_lift(
        baseline_df,
        modern_df,
        modern_name=args.modern_name,
        min_books=args.min_books,
    )

    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    final_report.to_csv(args.output, index=False)

    print(f"\n🔥 TOP 15 RISING TROPES (vs Baseline) 🔥")
    print(f"{'Rank':<5} | {'Trope':<30} | {'Lift':<6} | {'Books'}")
    print("-" * 65)

    for idx, row in final_report.head(15).reset_index(drop=True).iterrows():
        lift_str = f"{row['trend_lift']}x"
        print(
            f"{(idx + 1):<5} | {row['trope']:<30} | {lift_str:<6} | "
            f"{int(row[f'{args.modern_name}_count']):,}"
        )

    print(f"\nFull report saved to {args.output}")
