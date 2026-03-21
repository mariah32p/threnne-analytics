"""
Script 05: Find Unmapped Tropes (Diagnostic Tool)
=================================================
Scans the raw scraped CSVs and counts every shelf that is NOT
currently mapped in trope_dictionary.json.

Useful for finding emerging slang or subgenres we missed.
"""

import argparse
import csv
import glob
import json
import os
from collections import Counter
from pathlib import Path

import pandas as pd


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _default_taxonomy() -> str:
    return str(_repo_root() / "taxonomy" / "trope_dictionary.json")


def load_mapped_keys(taxonomy_path: str) -> set:
    """Returns a set of every string currently tracked in our dictionary."""
    with open(taxonomy_path, "r", encoding="utf-8") as f:
        raw_dict = json.load(f)

    mapped_keys = set()
    for variations in raw_dict.values():
        for variant in variations:
            mapped_keys.add(variant.lower())
    return mapped_keys


def find_unmapped(input_dirs: list, mapped_keys: set) -> tuple[Counter, int]:
    print("Scanning raw files for unmapped shelves...")
    unmapped_counter = Counter()

    ignore_list = {
        # Formats & general meta
        "to-read",
        "currently-reading",
        "favorites",
        "dnf",
        "owned",
        "books-i-own",
        "kindle",
        "audiobook",
        "library",
        "arc",
        "tbr",
        "romance",
        "contemporary",
        "fiction",
        "adult",
        "adult fiction",
        "adult-fiction",
        "series",
        "did-not-finish",
        "owned-books",
        "audiobooks",
        "audio",
        "ebooks",
        "novella",
        "short stories",
        "anthologies",
        "chapter books",
        "graphic novels",
        "comics",
        "amazon",
        "literature",
        "nonfiction",
        "novels",
        "book club",
        "books about books",
        "read in 2022",
        "read in 2023",
        # Audiences & demographics (MG / children — not YA)
        "middle grade",
        "childrens",
        "juvenile",
        # Brands & authors
        "colleen hoover",
        "jane austen",
        "black author",
        # Geography noise
        "scotland",
        "france",
        "paris",
        "ireland",
        "australia",
        "canada",
        "india",
        "new york",
        "london",
        "russia",
        "japan",
        "asia",
        "africa",
        "nigeria",
        "egypt",
        "ukraine",
        "south africa",
        "southern",
        "americana",
        # General non-romance fiction / meta
        "literary fiction",
        "memoir",
        "biography",
        "poetry",
        "art",
        "history",
        "philosophy",
        "self help",
        "politics",
        "religion",
        # Broad fiction / romance meta (not trope structure)
        "realistic fiction",
        "drama",
        "romantic",
        "love",
        "coming of age",
        # National / regional "literature" (catalog noise)
        "british literature",
        "german literature",
        "asian literature",
        "irish literature",
        # Misc shelf noise
        "roman",
        "world war ii",
        "holocaust",
        "american history",
        "american revolutionary war",
        "presidents",
        "american revolution",
        "alternate history",
        "archaeology",
        "china",
        "knitting",
        "shakespeare",
        "christian non fiction",
    }

    total_books_scanned = 0

    for directory in input_dirs:
        csv_files = glob.glob(os.path.join(directory, "*_processed.csv"))
        for file in sorted(csv_files):
            df = pd.read_csv(file)
            for _, row in df.iterrows():
                if pd.isna(row.get("shelves")) or row["shelves"] == "{}":
                    continue
                try:
                    shelves_dict = json.loads(row["shelves"])
                except (json.JSONDecodeError, TypeError):
                    continue

                total_books_scanned += 1

                for raw_shelf in shelves_dict.keys():
                    clean_shelf = raw_shelf.lower().strip()

                    if clean_shelf in mapped_keys:
                        continue
                    if clean_shelf in ignore_list:
                        continue
                    if "201" in clean_shelf or "202" in clean_shelf:
                        continue

                    unmapped_counter[clean_shelf] += 1

    print(f"\nScanned {total_books_scanned:,} books.")
    print("\n🔥 TOP 30 UNMAPPED SHELVES (Potentially missing tropes) 🔥")
    print(f"{'Rank':<5} | {'Raw Shelf Name':<35} | {'Book Count'}")
    print("-" * 60)

    for idx, (shelf, count) in enumerate(unmapped_counter.most_common(30)):
        print(f"{(idx + 1):<5} | {shelf:<35} | {count:,}")

    return unmapped_counter, total_books_scanned


def save_unmapped_csv(unmapped_counter: Counter, output_path: str) -> None:
    rows = [
        {"rank": i + 1, "raw_shelf": shelf, "book_count": count}
        for i, (shelf, count) in enumerate(unmapped_counter.most_common())
    ]
    out_df = pd.DataFrame(rows)
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    out_df.to_csv(output_path, index=False)
    print(f"\nFull list ({len(rows):,} unmapped shelves) saved to {output_path}")


def export_unmapped_alerts_csv(unmapped_counter: Counter, output_path: str, min_count: int = 3) -> None:
    """Write shelves seen on min_count+ books for CI / GitHub Actions review."""
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["trope", "count"])
        for shelf, count in unmapped_counter.most_common():
            if count >= min_count:
                writer.writerow([shelf, count])
    print(f"Alert file (count >= {min_count}) saved to {output_path}")


if __name__ == "__main__":
    root = _repo_root()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--taxonomy",
        default=_default_taxonomy(),
        help="Path to trope_dictionary.json",
    )
    parser.add_argument(
        "--epoch2_dir",
        default=str(root / "data" / "raw" / "epoch_2_backtest"),
        help="Directory with epoch 2 *_processed.csv files",
    )
    parser.add_argument(
        "--epoch3_dir",
        default=str(root / "data" / "raw" / "epoch_3_forecast"),
        help="Directory with epoch 3 *_processed.csv files",
    )
    parser.add_argument(
        "--output",
        default=str(root / "data" / "exports" / "unmapped_shelves.csv"),
        help="Path to write full unmapped shelf counts (CSV)",
    )
    args = parser.parse_args()

    mapped = load_mapped_keys(args.taxonomy)
    dirs_to_scan = [args.epoch2_dir, args.epoch3_dir]
    counter, _total = find_unmapped(dirs_to_scan, mapped)
    save_unmapped_csv(counter, args.output)

    # ==========================================
    # EXPORT FOR GITHUB ACTIONS BOT
    # ==========================================
    alerts_path = str(root / "backtester" / "data" / "exports" / "unmapped_alerts.csv")
    export_unmapped_alerts_csv(counter, alerts_path, min_count=3)
