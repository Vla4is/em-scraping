"""Task 2, step 1: fetch every page of the whisky category and save the raw HTML.

Follows <link rel="next"> until there is none. All pages of one run share one timestamp (UTC):
    raw/fetched_page_1_2026-10-01_14-32-05.html
    raw/fetched_page_2_2026-10-01_14-32-05.html
"""
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from parsel import Selector
from playwright.sync_api import sync_playwright

URL = "https://www.cellarbrations.com.au/sm/delivery/rsid/144981/categories/spirits/whisky-id-Whisky_Food"
RAW = Path(__file__).parent / "raw"  # next to this script, wherever it's run from
RAW.mkdir(parents=True, exist_ok=True)
MAX_PAGES = 50      # guard against a broken "next" link looping forever
PAUSE_SECONDS = 2   # be gentle between pages

#moves the old file into the archived folder, in order to write the new one and not to confuse the parser.
def archive_old(raw_dir: Path) -> None:
    """Move every page of the previous run into raw/archive/, so raw/ holds only the current run."""
    archive = raw_dir / "archive"
    archive.mkdir(exist_ok=True)
    for old in raw_dir.glob("*.html"):
        old.replace(archive / old.name)
        print(f"Archived {old.name}")


pages = []  # HTML of each page, kept in memory until every page has succeeded
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # headless is more likely to be flagged by Cloudflare
    page = browser.new_page()
    url, seen, fetched_at = URL, set(), None
    while url and url not in seen and len(pages) < MAX_PAGES:
        seen.add(url)
        if pages:
            time.sleep(PAUSE_SECONDS)
        # The products are in the raw HTML, so there's no need to wait for images/scripts.
        resp = page.goto(url, wait_until="domcontentloaded")
        fetched_at = fetched_at or datetime.now(timezone.utc)  # moment page 1 answered
        html = resp.text()
        # Don't save Cloudflare's block page as if it were data; abandon the whole run.
        if resp.status != 200 or "ProductCardWrapper-" not in html:
            browser.close()
            sys.exit(f"Fetch failed on page {len(pages) + 1}: status {resp.status}. Nothing saved. VPN on?")
        pages.append(html)
        print(f"Fetched page {len(pages)} ({html.count('ProductCardWrapper-')} cards)")

        # The site's next link drops the store (/sm/delivery/rsid/144981), so keep our URL and take only its query.
        next_href = Selector(text=html).css('link[rel="next"]::attr(href)').get()
        url = f"{URL}?{urlsplit(next_href).query}" if next_href else None
    browser.close()

# Only now, after every page succeeded, so a failed run never mixes old and new pages.
archive_old(RAW)

# No ':' in Windows file names, so the time uses '-'.
stamp = f"{fetched_at:%Y-%m-%d_%H-%M-%S}"
for n, html in enumerate(pages, start=1):
    out = RAW / f"fetched_page_{n}_{stamp}.html"
    out.write_text(html, encoding="utf-8")
    print(f"Saved {out.name}")
