"""Task 1, step 1: fetch page 1 of the whisky category and save the raw HTML.

The file name carries the page name and the fetch time (UTC), so the parse step can use it as scraped_at:
    raw/whisky_page1_2026-10-01_14-32-05.html
"""
import sys
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "https://www.cellarbrations.com.au/sm/delivery/rsid/144981/categories/spirits/whisky-id-Whisky_Food"
PAGE_NAME = "whisky_page1"
RAW = Path(__file__).parent / "raw"  # next to this script, wherever it's run from
RAW.mkdir(parents=True, exist_ok=True)


def archive_old(raw_dir: Path, page_name: str) -> None:
    """Move earlier fetches of this page into raw/archive/, so raw/ holds only the current one."""
    archive = raw_dir / "archive"
    archive.mkdir(exist_ok=True)
    for old in raw_dir.glob(f"{page_name}_*.html"):
        old.replace(archive / old.name)
        print(f"Archived {old.name}")


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # headless is more likely to be flagged by Cloudflare
    page = browser.new_page()
    resp = page.goto(URL)
    fetched_at = datetime.now(timezone.utc)  # moment the server answered
    # Raw HTML exactly as the server sent it, before JavaScript runs (= what the selectors were designed on).
    html = resp.text()
    status = resp.status
    browser.close()

# Don't save Cloudflare's block page as if it were data.
if status != 200 or "ProductCardWrapper-" not in html:
    sys.exit(f"Fetch failed: status {status}, product cards found: {'ProductCardWrapper-' in html}. VPN on?")

# Only now, after a good fetch, so a failed run never leaves raw/ without a current page.
archive_old(RAW, PAGE_NAME)

# No ':' in Windows file names, so the time uses '-'.
out = RAW / f"{PAGE_NAME}_{fetched_at:%Y-%m-%d_%H-%M-%S}.html"
out.write_text(html, encoding="utf-8")
print(f"Saved {out} (status {status})")
