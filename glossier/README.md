# Glossier catalogue scraper

Scrapes the full Glossier catalogue ([glossier.com/collections/all](https://www.glossier.com/collections/all))
into CSV, from the first page of product cards up to **every variant of every product**, sets included,
for both **Lithuania** and the **United States**.

Built with Scrapy on plain HTML: no browser and no hidden APIs (`/products.json` exists, but this
is a scraping exercise). Each task lives in its own folder, so it can be reviewed step by step.

| Task | What it scrapes | Rows (LT / US) |
|---|---|---|
| [task1](task1/) | Product cards on the first collection page | 19 / 19 |
| [task2](task2/) | Every product in the catalogue, with its category | 95 / 96 |
| [task3](task3/) | Task 2 plus each product's description | 95 / 96 |
| [task4](task4/) | **Every variant as its own row**: price, discount, stock, image, sets | 321 / 330 |
| Task 5 | Task 4 on the US site: same spider, US URL | see task4 |

Row counts are from the runs on 2026-10-01; the catalogue changes over time.

## Quick start

From the repo root (Python 3.12.10):

```sh

pip install -r requirements.txt

cd task...
scrapy runspider glossier_spider.py -O output/task4-us.csv
#Or in task 4 you can do
bash run-spider.sh
```

Run each spider from inside its task folder. `-O` overwrites the file. Every run is a full snapshot.
Every CSV value is written in quotes, so all columns read as text. Tasks 2–4 take about 2 minutes each (one request
per second, about 100 product pages), Task 1 a few seconds.

Task 4 also has [run-spider.sh](task4/run-spider.sh), which runs both countries and writes a log file next to
each CSV. Run one line at a time and switch the country between them (see below).

## Choosing the country

The country is the URL, set at the top of each spider. Uncomment one line:

```python
start_urls = ["https://www.glossier.com/en-lt/collections/all"]   # Lithuania (EUR)
# start_urls = ["https://www.glossier.com/collections/all"]       # United States (USD)
```

The plain URL stays on the US site from anywhere, because the spiders don't send `Accept-Language`;
with that header the site redirects by IP. No proxy or VPN is needed. Only one line should be active at a time.

## Tasks 1–3 output

**Task 1: product cards from the first page.**
Columns: `product_name, product_id, image, url, price, regular_price, scraped_at`.
One row per card. The same product can appear more than once if it's shown as separate cards
(e.g. Cloud Paint Blush / Bronzer). `image` holds the card's main and hover photos.

**Task 2: unique products with category.**
Columns: `product_id, product_name, url, category, scraped_at`. Each product appears once: the `?variant=`
part of the card link is dropped before visiting the product page. The category comes from data embedded in
the product page, not from anything visible on it.

**Task 3: Task 2 plus description.**
Adds a `description` column: the text of the description paragraph on the product page
(`<p id="description-item">`).

## Task 4 output

One row per variant (shade, size, scent). `variant_id` is unique across the store and is the key.
I tried to maximize the business value from the dataset, so I have created the following architecture

| Column | Meaning |
|---|---|
| `product_id`, `variant_id` | Shopify IDs. `variant_id` is the primary key |
| `product_name`, `variant_name` | e.g. `Cloud Paint` + `Puff`; `variant_name` is empty for single-option products |
| `url` | Product page with `?variant=<id>` |
| `image` | JSON array with the product's main photo URL |
| `category` | Shopify product type from the page data (e.g. `Fragrance`, `Merch`) |
| `description` | The description paragraph shown on the page |
| `price`, `discounted_price` | Regular price as shown (e.g. `€108,95`, `$18`). `discounted_price` only when on sale |
| `is_flexible_set`, `flexible_discount_percent` | Build-your-own sets: no fixed price, only a discount on the picked items |
| `set_variant_ids` | Sets only: one list per slot of the variant IDs the buyer can pick, e.g. `[[id, id], [id]]` |
| `in_stock` | `True` / `False` per variant |
| `scraped_at` | UTC timestamp |

### How sets work

Glossier sells three kinds of sets, and all of them become one row with `set_variant_ids`:

- **Fixed sets** (e.g. Balm Dotcom Trio): page price and image as usual.
- **Build-your-own sets** (Fragrance Duo, Fragrance Trio, Fragrance Two Ways, Travel Spray + Balm): the site's
  JavaScript prices the set from the buyer's picks, so the row has no price and no image. It has
  `flexible_discount_percent` instead. Each pickable item has its own row (price and image), so BI can price
  any combination.
- **Mixed sets**: fixed items plus a choice. Same model, a slot with one ID or with many.

```
Fragrance Duo  set_variant_ids = [[5 scent IDs], [5 scent IDs]]   flexible_discount_percent = 15.0
                                     │
                                     └─> each ID is a variant_id row with its own price and image
```

## Checking the output

[task4/profile.ipynb](task4/profile.ipynb) profiles one CSV (set `PATH` at the top) and checks:
- uniqueness of `variant_id`, `url` and the name pair;
- empty values;
- that every row has a price or a discount percentage;
- that every ID in a set has its own row;
- image outliers (4 expected: the build-your-own sets);
- stock.

[task3/profile.ipynb](task3/profile.ipynb) does the same for the product-level output.

## Project layout

```
glossier/
├── task1/ … task4/
│   ├── glossier_spider.py     # one self-contained spider per task
│   ├── output/                # CSVs (+ logs for task4)
│   └── profile.ipynb          # tasks 3–4: output checks
├── raw/                       # pages saved with curl, for inspecting selectors offline
└── fetch-all-prod.sh          # the curl commands that saved them
```

## Being polite

`robots.txt` is obeyed, there's a 1-second delay, one request at a time and about 100 pages per run.
Requests are processed in order, so rows follow the site's order.

## More

See [notes.txt](notes.txt) for assumptions, decisions, known limitations and how AI was used.
