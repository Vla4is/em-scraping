"""Task 1, step 2: parse the newest fetched page (raw/whisky_page1_<UTC time>.html) into a CSV.

Runs offline. scraped_at comes from the file name, i.e. when fetch_page.py got the page.
"""
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from parsel import Selector

HERE = Path(__file__).parent
RAW = HERE / "raw"
OUTPUT = HERE / "output"
PAGE_NAME = "whisky_page1"
FIELDS = ["product_name", "product_id", "image", "url", "price", "was_price", "scraped_at"]


def archive_old(out_dir: Path, page_name: str) -> None:
    """Move earlier CSVs of this page into output/archive/, so output/ holds only the current one."""
    archive = out_dir / "archive"
    archive.mkdir(exist_ok=True)
    for old in out_dir.glob(f"{page_name}_*.csv"):
        old.replace(archive / old.name)
        print(f"Archived {old.name}")


# Newest fetch; the time in the name sorts correctly as text. raw/readable/ is not matched.
files = sorted(RAW.glob(f"{PAGE_NAME}_*.html"))
if not files:
    sys.exit(f"No {PAGE_NAME}_*.html in {RAW}. Run fetch_page.py first.")
src = files[-1]

# whisky_page1_2026-10-01_17-40-27 -> 2026-10-01T17:40:27+00:00
stamp = src.stem.removeprefix(f"{PAGE_NAME}_")
scraped_at = datetime.strptime(stamp, "%Y-%m-%d_%H-%M-%S").replace(tzinfo=timezone.utc).isoformat()

page = Selector(text=src.read_text(encoding="utf-8"))
rows = []
for card in page.css('article[data-testid^="ProductCardWrapper-"]'):
    rows.append({
        "product_name": card.css('h3[data-testid$="ProductNameTestId"]::text').get(default="").strip(),
        "product_id": card.attrib["data-testid"].removeprefix("ProductCardWrapper-"),
        # Spec says array of strings; stored as a JSON list in the CSV cell.
        "image": json.dumps(card.css("img::attr(src)").getall()),
        "url": card.css('a[class^="ProductCardHiddenLink"]::attr(href)').get(),
        # Site's names: ProductPrice = what you pay now; ProductWasPrice = "was $59.00", only on sale.
        "price": card.css('div[class^="ProductPrice--"]::text').get(default="").strip(),
        "was_price": card.css('div[class^="ProductWasPrice--"]::text').get(default="").strip().removeprefix("was ").strip(),
        "scraped_at": scraped_at,
    })

# Keep the previous CSV in place if this parse found nothing.
if not rows:
    sys.exit(f"No product cards found in {src.name}; nothing written.")

OUTPUT.mkdir(exist_ok=True)
archive_old(OUTPUT, PAGE_NAME)
out = OUTPUT / f"{src.stem}.csv"
with out.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(rows)
print(f"{len(rows)} products from {src.name} -> {out}")
