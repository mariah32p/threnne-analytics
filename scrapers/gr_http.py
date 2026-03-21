"""Shared HTTP client for Goodreads scrapers (Cloudflare-friendly)."""

from __future__ import annotations

import random
import time

import cloudscraper


def make_scraper():
    """Mimic a real browser for basic bot-protection (e.g. Cloudflare)."""
    return cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "desktop": True}
    )


def polite_sleep() -> None:
    time.sleep(random.uniform(3.5, 7.2))


def fetch_url(scraper, url: str, timeout: int = 30):
    polite_sleep()
    return scraper.get(url, timeout=timeout)
