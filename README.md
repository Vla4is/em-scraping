# Project for euromonitor

Python version: Python 3.12.10

Glossier (glossier.com) scraper, built with Scrapy. Each task lives in its own
folder under `glossier/` with its own spider and output.

## Setup

```sh
pip install -r requirements.txt
```

## Choosing the country (LT / US)

Each spider's `start_urls` is set directly in the file, near the top of the
class. To switch country, comment/uncomment the right line, e.g.:

```python
start_urls = ["https://www.glossier.com/en-lt/collections/all"]  # Lithuania
# start_urls = ["https://www.glossier.com/collections/all"]       # US
```

Only one line should be active at a time — the other must stay commented out.

## Running a task

Activate the venv first, then run from inside that task's folder. Each spider
follows pagination and writes straight to `output/`, overwriting any existing
file of the same name (`-O`, capital letter).

### Task 1 — product cards from the collection page

```sh
cd glossier/task1
scrapy runspider glossier_spider.py -O output/task1-lt.csv
```

Columns: `product_name, product_id, image, url, price, regular_price, scraped_at`.
One row per card — the same product can appear more than once if it's shown
as separate cards (e.g. Cloud Paint Blush / Bronzer).

### Task 2 — unique products with category

```sh
cd glossier/task2
scrapy runspider glossier_spider.py -O output/task2-lt.csv
```

Columns: `product_id, product_name, url, category, scraped_at`. Each product
appears once (the `?variant=` part of the card link is dropped before
visiting the product page); the category comes from data embedded in the
product page, not from anything visible on it.

### Task 3 — unique products with category and description

```sh
cd glossier/task3
scrapy runspider glossier_spider.py -O output/task3-lt.csv
```

Same as Task 2, plus a `description` column. Build-your-own sets and most
fixed sets have no description in the source data, so that field is empty
for them — see `notes.txt`.

## Notes

- Each run takes roughly 10 seconds (Task 1) to 2 minutes (Tasks 2–3, which
  visit every product page) due to the 1-second delay between requests.
- `ROBOTSTXT_OBEY` is on for every spider.
- See `notes.txt` for assumptions, decisions, tradeoffs, and AI usage.
