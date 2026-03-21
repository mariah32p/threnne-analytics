#!/bin/sh
# Run goodreads_scraper.py on every *_template.csv under data/raw/.
# Writes sibling *_processed.csv (same directory).
set -u
cd "$(dirname "$0")"
export PYTHONUNBUFFERED=1

if [ -x "./.venv/bin/python3" ]; then
  PY="./.venv/bin/python3"
else
  PY="python3"
fi

mkdir -p data/logs
ENGINE_LOG="data/logs/engine_status.log"

find data/raw -type f -name '*_template.csv' | sort | while IFS= read -r tpl; do
  lines=$(wc -l < "$tpl" | awk '{print $1}')
  if [ ! -s "$tpl" ] || [ "$lines" -lt 2 ]; then
    echo "========================================"
    echo "SKIP (empty or header-only): $tpl"
    ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    echo "$ts BATCH_SKIP $tpl" >>"$ENGINE_LOG"
    continue
  fi
  out=$(echo "$tpl" | sed 's/_template\.csv$/_processed.csv/')
  echo "========================================"
  ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  echo "$ts START $tpl -> $out"
  echo "$ts BATCH_START $tpl -> $out" >>"$ENGINE_LOG"
  if ! $PY -u scrapers/goodreads_scraper.py \
    --template "$tpl" \
    --output "$out" \
    --status-log "$ENGINE_LOG"; then
    ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    echo "$ts FAILED (non-zero exit): $tpl"
    echo "$ts BATCH_FAILED exit=1 $tpl" >>"$ENGINE_LOG"
  else
    ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    echo "$ts DONE $out"
    echo "$ts BATCH_DONE $out" >>"$ENGINE_LOG"
  fi
done

echo "All goodreads_scraper template runs finished."
