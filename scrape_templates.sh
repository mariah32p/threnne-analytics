#!/bin/sh
# Epoch 2 (2018–2023 backtest) then Epoch 3 (2024–2025 forward edge).
# Run from anywhere: sh scrape_templates.sh (from goodreads/) or sh /path/to/scrape_templates.sh
set -eu
cd "$(dirname "$0")"

# Prefer project venv (PEP 668–safe); fall back to python3 on PATH.
if [ -x "./.venv/bin/python3" ]; then
  PY="./.venv/bin/python3"
else
  PY="python3"
fi

# --- 2018 Sweeps ---
$PY scrapers/list_scraper.py --url "https://www.goodreads.com/list/show/114793.Romance_2018" --pages 5 --output data/raw/epoch_2_backtest/2018_mf_template.csv
$PY scrapers/list_scraper.py --url "https://www.goodreads.com/list/show/122109.Best_M_M_Romance_of_2018" --pages 5 --output data/raw/epoch_2_backtest/2018_mm_template.csv
$PY scrapers/list_scraper.py --url "https://www.goodreads.com/list/show/120017.2018_F_F_Romance_Releases" --pages 3 --output data/raw/epoch_2_backtest/2018_ff_template.csv

# --- 2019 Sweeps ---
$PY scrapers/list_scraper.py --url "https://www.goodreads.com/list/show/117878.Romance_2019" --pages 5 --output data/raw/epoch_2_backtest/2019_mf_template.csv
$PY scrapers/list_scraper.py --url "https://www.goodreads.com/list/show/132302.M_M_Romance_Published_in_2019" --pages 5 --output data/raw/epoch_2_backtest/2019_mm_template.csv

# --- 2020 Sweeps ---
$PY scrapers/list_scraper.py --url "https://www.goodreads.com/list/show/137697.2020_Adult_Romance_Books" --pages 5 --output data/raw/epoch_2_backtest/2020_mf_template.csv
$PY scrapers/list_scraper.py --url "https://www.goodreads.com/list/show/138779.M_M_Romance_Published_in_2020" --pages 5 --output data/raw/epoch_2_backtest/2020_mm_template.csv

# --- 2021 Sweeps ---
$PY scrapers/list_scraper.py --url "https://www.goodreads.com/list/show/159278.Romance_Releases_2021" --pages 5 --output data/raw/epoch_2_backtest/2021_mf_template.csv
$PY scrapers/list_scraper.py --url "https://www.goodreads.com/list/show/157083.M_M_Romance_Published_in_2021" --pages 5 --output data/raw/epoch_2_backtest/2021_mm_template.csv

# --- 2022 Sweeps ---
$PY scrapers/list_scraper.py --url "https://www.goodreads.com/list/show/163035.2022_Contemporary_Romance_Releases" --pages 5 --output data/raw/epoch_2_backtest/2022_mf_template.csv
$PY scrapers/list_scraper.py --url "https://www.goodreads.com/list/show/171082.M_M_Romance_Published_in_2022" --pages 5 --output data/raw/epoch_2_backtest/2022_mm_template.csv

# --- 2023 Sweeps ---
$PY scrapers/list_scraper.py --url "https://www.goodreads.com/list/show/168719.2023_Contemporary_Romance_Releases" --pages 5 --output data/raw/epoch_2_backtest/2023_mf_template.csv
$PY scrapers/list_scraper.py --url "https://www.goodreads.com/list/show/179605.Best_M_M_of_2023" --pages 5 --output data/raw/epoch_2_backtest/2023_mm_template.csv

# --- 2024 Sweeps (Epoch 3) ---
$PY scrapers/list_scraper.py --url "https://www.goodreads.com/list/show/198335.October_2024_Most_Anticipated_Romance_Releases" --pages 5 --output data/raw/epoch_3_forecast/2024_mf_template.csv

# --- 2025 Sweeps (Epoch 3) ---
$PY scrapers/list_scraper.py --url "https://www.goodreads.com/list/show/196147.2025_Romance_Releases" --pages 5 --output data/raw/epoch_3_forecast/2025_mf_template.csv
$PY scrapers/list_scraper.py --url "https://www.goodreads.com/list/show/220786.2025_Romance_Books" --pages 5 --output data/raw/epoch_3_forecast/2025_mf_broad_template.csv

echo "All template scrapes finished."
