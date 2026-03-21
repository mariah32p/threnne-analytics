"""
Daily discovery scraper — genre / list hubs with pacing and strict pagination.
Builds or updates a seed CSV (book_title, author, goodreads_url) for goodreads_scraper.py.

- Target URLs vary by weekday (volatile hubs daily; slower hubs weekly).
- Max 2 pages per hub to keep the forecast window tight.
- Uses cloudscraper + random delays between requests.
- Merges with existing seed file: drop_duplicates(subset=['book_id'], keep='last').
"""

from __future__ import annotations

import argparse
import datetime
import os
import re
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import pandas as pd
from bs4 import BeautifulSoup

from gr_http import fetch_url, make_scraper

BOOK_SHOW_RE = re.compile(r"/book/show/(\d+)")
MAX_PAGES_PER_HUB = 2


def build_target_urls() -> list[str]:
    today = datetime.datetime.now().weekday()  # 0 = Monday, 6 = Sunday

    target_urls = [
        "https://www.goodreads.com/genres/new_releases/romance",
        "https://www.goodreads.com/genres/new_releases/contemporary-romance",
        "https://www.goodreads.com/genres/new_releases/romantasy",
    ]

    if today == 2:  # Wednesday
        target_urls.extend(
            [
                "https://www.goodreads.com/genres/most_read/romance",
                "https://www.goodreads.com/genres/most_read/romantasy",
            ]
        )

    if today == 6:  # Sunday
        target_urls.extend(
            [
                "https://www.goodreads.com/list/show/204351.2025_Romance_Releases",
            ]
        )

    return target_urls


def book_id_from_url(url: str) -> int | None:
    if not isinstance(url, str):
        return None
    m = BOOK_SHOW_RE.search(url)
    return int(m.group(1)) if m else None


def paged_url(base: str, page: int) -> str:
    parsed = urlparse(base)
    q = parse_qs(parsed.query)
    q["page"] = [str(page)]
    new_query = urlencode(q, doseq=True)
    return urlunparse(parsed._replace(query=new_query))


def parse_books_from_genre_or_explore_html(html: str) -> list[dict]:
    """Extract /book/show/{id} links from genre / new-releases style pages."""
    soup = BeautifulSoup(html, "html.parser")
    seen: set[int] = set()
    books: list[dict] = []

    for a in soup.find_all("a", href=True):
        href = a["href"].split("?")[0]
        if "/book/show/" not in href:
            continue
        if not href.startswith("http"):
            href = "https://www.goodreads.com" + href
        bid = book_id_from_url(href)
        if bid is None or bid in seen:
            continue
        seen.add(bid)
        title = a.get_text(strip=True) or f"book_{bid}"
        books.append(
            {
                "book_title": title,
                "author": "",
                "goodreads_url": href,
                "reviews_count": None,
                "avg_rating": None,
                "shelves": None,
            }
        )
    return books


def parse_books_from_listopia_html(html: str) -> list[dict]:
    """Listopia-style table rows (same idea as list_scraper)."""
    soup = BeautifulSoup(html, "html.parser")
    books: list[dict] = []
    seen: set[int] = set()

    rows = soup.find_all("tr", itemtype="http://schema.org/Book")
    for row in rows:
        title_tag = row.find("a", class_="bookTitle")
        author_tag = row.find("a", class_="authorName")
        if not title_tag or not title_tag.get("href"):
            continue
        raw_url = "https://www.goodreads.com" + title_tag["href"]
        clean_url = raw_url.split("?")[0]
        bid = book_id_from_url(clean_url)
        if bid is None or bid in seen:
            continue
        seen.add(bid)
        author = author_tag.get_text(strip=True) if author_tag else ""
        title = title_tag.get_text(strip=True) or f"book_{bid}"
        books.append(
            {
                "book_title": title,
                "author": author,
                "goodreads_url": clean_url,
                "reviews_count": None,
                "avg_rating": None,
                "shelves": None,
            }
        )
    return books


def scrape_hub(scraper, base_url: str, max_pages: int = MAX_PAGES_PER_HUB) -> list[dict]:
    all_books: list[dict] = []
    is_list = "/list/show/" in base_url

    for page in range(1, max_pages + 1):
        url = base_url if page == 1 else paged_url(base_url, page)

        resp = fetch_url(scraper, url)
        if resp.status_code != 200:
            print(f"  [{base_url} p{page}] HTTP {resp.status_code}")
            break
        chunk = parse_books_from_listopia_html(resp.text) if is_list else parse_books_from_genre_or_explore_html(resp.text)
        if not chunk:
            print(f"  [{base_url} p{page}] No books parsed; stopping this hub.")
            break
        all_books.extend(chunk)
        print(f"  [{base_url} p{page}] +{len(chunk)} books (running total {len(all_books)})")

    return all_books


def merge_seed(existing_path: str, incoming: pd.DataFrame) -> pd.DataFrame:
    if incoming.empty and os.path.exists(existing_path):
        return pd.read_csv(existing_path)

    incoming = incoming.copy()
    incoming["book_id"] = incoming["goodreads_url"].map(book_id_from_url)
    incoming = incoming.dropna(subset=["book_id"])
    incoming["book_id"] = incoming["book_id"].astype(int)
    incoming = incoming.drop_duplicates(subset=["book_id"], keep="last")

    if not os.path.exists(existing_path):
        return incoming.drop(columns=["book_id"], errors="ignore")

    old = pd.read_csv(existing_path)
    old["book_id"] = old["goodreads_url"].map(book_id_from_url)
    old = old.dropna(subset=["book_id"])
    old["book_id"] = old["book_id"].astype(int)

    combined = pd.concat([old, incoming], ignore_index=True)
    combined = combined.drop_duplicates(subset=["book_id"], keep="last")
    combined = combined.drop(columns=["book_id"], errors="ignore")
    return combined


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Daily Goodreads discovery → seed CSV")
    parser.add_argument(
        "--output",
        default="data/raw/epoch_3_forecast/daily_seed.csv",
        help="Cumulative seed CSV for goodreads_scraper.py",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=MAX_PAGES_PER_HUB,
        help="Max pagination depth per hub (default 2)",
    )
    args = parser.parse_args()

    targets = build_target_urls()
    print(f"Weekday={datetime.datetime.now().weekday()} hubs={len(targets)}")
    scraper = make_scraper()

    rows: list[dict] = []
    for hub in targets:
        print(f"Hub: {hub}")
        rows.extend(scrape_hub(scraper, hub, max_pages=args.max_pages))

    fresh = pd.DataFrame(rows)
    if fresh.empty:
        print("No books discovered this run.")
    merged = merge_seed(args.output, fresh)

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    merged.to_csv(args.output, index=False)
    print(f"Saved {len(merged)} rows to {args.output}")
