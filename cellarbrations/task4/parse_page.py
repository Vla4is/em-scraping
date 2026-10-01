"""Task 4, step 2: parse every fetched page (raw/fetched_page_<n>_<UTC time>.html) into one CSV,
with descriptions and the product size (measuring_unit + units).

Runs offline. scraped_at comes from the file names, i.e. when fetch_page.py got the pages.

Data comes from the JSON the site embeds in each page (window.__PRELOADED_STATE__), not from the card text:
the card's unit price ("$21.43/100ml") is a comparison price, not the bottle size, and was wrong for some products.
Only the product URL is taken from the card's link, because the JSON has none.
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
FIELDS = ["product_name", "product_id", "image", "url", "price", "was_price", "description",
          "measuring_unit", "units", "scraped_at"]
STATE_MARKER = "window.__PRELOADED_STATE__="


def load_state(html: str) -> dict:
    """Read the JSON object that follows window.__PRELOADED_STATE__= in a <script> tag."""
    start = html.find(STATE_MARKER)
    if start == -1:
        raise ValueError("no __PRELOADED_STATE__ in page")
    state, _ = json.JSONDecoder().raw_decode(html, start + len(STATE_MARKER))
    return state


def clean_description(text: str) -> str:
    """The site's text holds literal <br /> tags (the only tag found): split on them, join the parts with ' | '.

    Each part's whitespace is collapsed to single spaces, because some texts contain real line breaks
    (e.g. 279578), which would split the CSV cell over two lines.
    """
    parts = (" ".join(p.split()) for p in (text or "").split("<br />"))
    return " | ".join(p for p in parts if p)


def format_amount(size) -> str:
    """700 -> '700', 1 -> '1', 1.5 -> '1.5' (no trailing '.0')."""
    if size is None:
        return ""
    return str(int(size)) if float(size).is_integer() else str(size)


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
    html = src.read_text(encoding="utf-8")
    search = load_state(html)["search"]
    products = search["productCardDictionary"]   # sku -> product data
    order = search["products"]["category"]       # skus in the order shown on the page
    # The only field the JSON lacks: the product link, taken from each card.
    urls = {
        card.attrib["data-testid"].removeprefix("ProductCardWrapper-"):
            card.css('a[class^="ProductCardHiddenLink"]::attr(href)').get()
        for card in Selector(text=html).css('article[data-testid^="ProductCardWrapper-"]')
    }
    print(f"{src.name}: {len(order)} products")
    for product_id in order:
        if product_id in seen:  # a product shown on two pages is kept once
            print(f"  duplicate {product_id} skipped")
            continue
        seen.add(product_id)
        p = products[product_id]
        size = p.get("unitOfSize") or {}  # the bottle size, e.g. {"size": 700, "abbreviation": "ml"}
        rows.append({
            "product_name": p["name"].strip(),
            "product_id": product_id,
            # Spec says array of strings; stored as a JSON list in the CSV cell.
            "image": json.dumps([p["image"]["default"]] if p.get("image", {}).get("default") else []),
            "url": urls.get(product_id, ""),
            # price = what you pay now; wasPrice repeats the price unless the product is discounted.
            "price": p["price"],
            "was_price": p["wasPrice"] if p.get("isDiscounted") else "",
            "description": clean_description(p.get("description")),
            "measuring_unit": size.get("abbreviation", ""),
            "units": format_amount(size.get("size")),
            "scraped_at": scraped_at,
        })

# Keep the previous CSV in place if this parse found nothing.
if not rows:
    sys.exit("No products found; nothing written.")

for column in ("url", "units"):
    missing = [r["product_id"] for r in rows if not r[column]]
    if missing:
        print(f"  no {column} for {len(missing)} products: {missing}")

OUTPUT.mkdir(exist_ok=True)
archive_old(OUTPUT)
out = OUTPUT / f"whisky_all_{stamp}.csv"
with out.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(rows)
print(f"{len(rows)} products from {len(files)} pages -> {out}")
