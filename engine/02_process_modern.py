"""
Script 02: Process Modern Epochs (The Binary Pivot)
===================================================
Input:   CSVs in data/raw/epoch_2_backtest/ OR data/raw/epoch_3_forecast/
Output:  data/processed/epoch_2_backtest.parquet OR epoch_3_forecast.parquet

What this does:
- Ingests the scraped CSVs with null-valued shelves {"romance": null}.
- Maps the keys to the Threnne trope dictionary.
- Counts Book-Level Frequency (1 if trope is present on book, 0 if not).
"""

import argparse
import glob
import json
import os
from pathlib import Path

import pandas as pd


def _default_taxonomy_path() -> str:
    return str(Path(__file__).resolve().parent.parent / "taxonomy" / "trope_dictionary.json")


def load_taxonomy(taxonomy_path: str) -> dict:
    with open(taxonomy_path, "r", encoding="utf-8") as f:
        raw_dict = json.load(f)
    flat_map = {}
    for canonical, variations in raw_dict.items():
        for variant in variations:
            flat_map[variant.lower()] = canonical
    return flat_map


def process_epoch_directory(input_dir: str, output_path: str, taxonomy_map: dict):
    print(f"Sweeping directory: {input_dir}")
    csv_files = glob.glob(os.path.join(input_dir, "*_processed.csv"))

    if not csv_files:
        print("No processed CSVs found in this directory!")
        return

    all_books = []

    for file in sorted(csv_files):
        print(f"  Processing {os.path.basename(file)}...")
        df = pd.read_csv(file)

        for _, row in df.iterrows():
            if pd.isna(row.get("shelves")) or row["shelves"] == "{}":
                continue

            try:
                shelves_dict = json.loads(row["shelves"])
            except (json.JSONDecodeError, TypeError):
                continue

            book_record = {
                "book_title": row.get("book_title", "Unknown"),
                "goodreads_url": row.get("goodreads_url", ""),
            }

            found_tropes = set()
            for raw_shelf in shelves_dict.keys():
                canonical = taxonomy_map.get(raw_shelf.lower().strip())
                if canonical:
                    found_tropes.add(canonical)

            for trope in set(taxonomy_map.values()):
                book_record[f"trope_{trope}"] = 1 if trope in found_tropes else 0

            if found_tropes:
                all_books.append(book_record)

    if not all_books:
        print("No books with recognized tropes; skipping Parquet write.")
        return

    final_df = pd.DataFrame(all_books)

    trope_cols = [c for c in final_df.columns if c.startswith("trope_")]
    final_df["total_shelves_applied"] = final_df[trope_cols].sum(axis=1)

    print(f"\n--- Processing Complete ---")
    print(f"Total Books Validated: {len(final_df):,}")

    print("\nTop 5 Tropes by Book Frequency:")
    top_tropes = final_df[trope_cols].sum().sort_values(ascending=False).head(5)
    for col, count in top_tropes.items():
        print(f"  {col.replace('trope_', '')}: {count:,} books")

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    final_df.to_parquet(output_path, index=False)
    print(f"\nSaved to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_dir",
        required=True,
        help="Directory containing _processed.csv files",
    )
    parser.add_argument("--output", required=True, help="Path to output Parquet")
    parser.add_argument(
        "--taxonomy",
        default=_default_taxonomy_path(),
        help="Path to trope_dictionary.json",
    )
    args = parser.parse_args()

    taxonomy = load_taxonomy(args.taxonomy)
    process_epoch_directory(args.input_dir, args.output, taxonomy)
