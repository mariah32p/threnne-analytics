"""
Script 01: Process UCSD Romance Dataset (Epoch 1 Baseline)
===========================================================
Input:   goodreads_books_romance.json.gz (UCSD 2017 snapshot)
Taxonomy: trope_dictionary.json
Output:  data/processed/ucsd_romance_clean.parquet

What this does:
- Dynamically loads the centralized Threnne trope dictionary.
- Extracts metadata and normalizes shelf names to canonical forms.
- Outputs a clean parquet ready for the Calculate Lift engine.
"""

import argparse
import gzip
import json
import os
from pathlib import Path

import pandas as pd
from tqdm import tqdm


def load_taxonomy(taxonomy_path: str) -> dict:
    """Flattens the JSON dictionary for O(1) lookup."""
    with open(taxonomy_path, "r", encoding="utf-8") as f:
        raw_dict = json.load(f)
    
    flat_map = {}
    for canonical, variations in raw_dict.items():
        for variant in variations:
            flat_map[variant.lower()] = canonical
    return flat_map


def process_ucsd_data(input_path: str, output_path: str, taxonomy_path: str):
    print(f"Loading taxonomy from {taxonomy_path}...")
    shelf_map = load_taxonomy(taxonomy_path)
    canonical_tropes = set(shelf_map.values())
    
    books = []
    
    print(f"Processing UCSD data from {input_path}...")
    with gzip.open(input_path, 'rt', encoding='utf-8') as f:
        for line in tqdm(f, desc="Parsing JSON rows"):
            record = json.loads(line)
            
            # Filter for books published 2010 or later to set our Epoch 1
            pub_year = record.get('publication_year')
            if not pub_year or not str(pub_year).isdigit() or int(pub_year) < 2010:
                continue
            
            book_data = {
                'book_id': record.get('book_id'),
                'title': record.get('title'),
                'publication_year': int(pub_year),
                'ratings_count': record.get('ratings_count', 0),
                'total_shelves_applied': 0  # Filled after shelves: count of canonical tropes on book
            }
            
            # Initialize trope counters to 0
            for trope in canonical_tropes:
                book_data[f"trope_{trope}"] = 0
                
            # Process user shelves (binary pivot: trope present = 1, same as modern epochs)
            for shelf in record.get('popular_shelves', []):
                name = shelf.get('name', '').lower()

                if name in shelf_map:
                    canonical_name = f"trope_{shelf_map[name]}"
                    book_data[canonical_name] = 1  # BINARY PIVOT

            book_data["total_shelves_applied"] = sum(
                book_data[f"trope_{t}"] for t in canonical_tropes
            )

            books.append(book_data)

    print("\nConverting to DataFrame...")
    df = pd.DataFrame(books)
    
    # Validation Logging
    print(f"\n--- Epoch 1 (2010-2017) Baseline Complete ---")
    print(f"Total Books: {len(df):,}")
    print(f"Total trope-presence flags (sum over books): {df['total_shelves_applied'].sum():,}")
    
    print("\nTop 5 Tropes by Book Frequency:")
    trope_cols = [c for c in df.columns if c.startswith('trope_')]
    top_tropes = df[trope_cols].sum().sort_values(ascending=False).head(5)
    for col, count in top_tropes.items():
         print(f"  {col.replace('trope_', '')}: {count:,}")

    # Save to Parquet
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_parquet(output_path, index=False)
    print(f"\nSaved to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to goodreads_books_romance.json.gz")
    parser.add_argument("--taxonomy", default="../taxonomy/trope_dictionary.json", help="Path to taxonomy JSON")
    parser.add_argument("--output", required=True, help="Path to output Parquet")
    args = parser.parse_args()

    process_ucsd_data(args.input, args.output, args.taxonomy)