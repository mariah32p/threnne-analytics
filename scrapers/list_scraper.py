"""
Goodreads List Scraper — The Dragnet
=====================================
Scrapes a Goodreads Listopia URL to gather unbiased book URLs for epoch backtesting.
Output format acts as the input template for `goodreads_scraper.py`.

Usage:
    python data_pipeline/goodreads/scrapers/list_scraper.py \
        --url "https://www.goodreads.com/list/show/194383.Best_Romance_of_2024" \
        --pages 5 \
        --output backtester/data/raw/epoch_3_forecast/2024_list_sweep.csv
"""

import argparse
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}
RATE_LIMIT = 2

def scrape_list_page(url: str, page_num: int) -> list[dict]:
    print(f"Scraping page {page_num}...")
    try:
        response = requests.get(f"{url}?page={page_num}", headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"  Failed with status {response.status_code}")
            return []
    except Exception as e:
        print(f"  Request failed: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    books = []
    
    # Goodreads Listopia lists use standard table rows for books
    rows = soup.find_all("tr", itemtype="http://schema.org/Book")
    
    for row in rows:
        title_tag = row.find("a", class_="bookTitle")
        author_tag = row.find("a", class_="authorName")
        
        if title_tag and author_tag:
            title = title_tag.get_text(strip=True)
            author = author_tag.get_text(strip=True)
            # Clean up URL (remove tracking params)
            raw_url = "https://www.goodreads.com" + title_tag["href"]
            clean_url = raw_url.split("?")[0]
            
            books.append({
                "book_title": title,
                "author": author,
                "goodreads_url": clean_url,
                "reviews_count": None,  # To be filled by goodreads_scraper.py
                "avg_rating": None,     # To be filled by goodreads_scraper.py
                "shelves": None         # To be filled by goodreads_scraper.py
            })
            
    return books

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="Goodreads Listopia URL")
    parser.add_argument("--pages", type=int, default=1, help="Number of pages to scrape")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args()

    all_books = []
    for p in range(1, args.pages + 1):
        books = scrape_list_page(args.url, p)
        if not books:
            print("  No books found or end of list reached. Stopping.")
            break
        all_books.extend(books)
        time.sleep(RATE_LIMIT)

    df = pd.DataFrame(all_books)
    import os
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    df.to_csv(args.output, index=False)
    
    print(f"\n{'='*50}")
    print(f"Successfully swept {len(df)} books into {args.output}")
    print(f"Ready for goodreads_scraper.py")