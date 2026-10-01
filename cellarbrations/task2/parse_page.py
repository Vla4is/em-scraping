"""Task 2, step 2: parse every fetched page (raw/fetched_page_<n>_<UTC time>.html) into one CSV.

Runs offline. scraped_at comes from the file names, i.e. when fetch_page.py got the pages.
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
FIELDS = ["product_name", "product_id", "image", "url", "price", "was_price", "scraped_at"]


def archive_old(out_dir: Path) -> None:
    """Move earlier CSVs into output/archive/, so output/ holds only the current one."""
    archive = out_dir / "archive"
    archive.mkdir(exist_ok=True)
    for old in out_dir.glob("*.csv"):
        old.replace(archive / old.name)
        print(f"Archived {old.name}")


# raw/ holds only the current run (fetch_page.py archives older ones); archive/ and readable/ are not matched.
# Sort by page number, not as text, so page 10 comes after page 9.
files = sorted(RAW.glob("fetched_page_*_*.html"), key=lambda f: int(f.stem.split("_")[2]))
if not files:
    sys.exit(f"No fetched_page_*.html in {RAW}. Run fetch_page.py first.")

# fetched_page_1_2026-10-01_17-40-27 -> 2026-10-01T17:40:27+00:00 (same for every page of the run)
stamp = files[0].stem.split("_", 3)[3]
scraped_at = datetime.strptime(stamp, "%Y-%m-%d_%H-%M-%S").replace(tzinfo=timezone.utc).isoformat()

rows, seen = [], set()
for src in files:
    page = Selector(text=src.read_text(encoding="utf-8"))
    cards = page.css('article[data-testid^="ProductCardWrapper-"]')
    print(f"{src.name}: {len(cards)} cards")
    for card in cards:
        product_id = card.attrib["data-testid"].removeprefix("ProductCardWrapper-")
        if product_id in seen:  # a product shown on two pages is kept once
            print(f"  duplicate {product_id} skipped")
            continue
        seen.add(product_id)
        rows.append({
            "product_name": card.css('h3[data-testid$="ProductNameTestId"]::text').get(default="").strip(),
            "product_id": product_id,
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
    sys.exit("No product cards found; nothing written.")

OUTPUT.mkdir(exist_ok=True)
archive_old(OUTPUT)
out = OUTPUT / f"whisky_all_{stamp}.csv"
with out.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(rows)
print(f"{len(rows)} products from {len(files)} pages -> {out}")
