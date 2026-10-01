# Glossier scraper

- Target: https://www.glossier.com/collections/all. Lithuanian locale (`/en-lt/`) first, then the US (plain URL), because the task requires a re-run on the US locale. The output is CSV. They explicitly said to **KEEP IT SIMPLE**: no complex data engineering, the focus is on scraping. The repo also needs `requirements.txt` and `notes.txt`.
- Shopify, **server-rendered**, scraped with Scrapy. We **don't use `/products.json`**; the user scrapes the HTML for practice.
- Locale: switch `start_urls` by commenting one line. The plain URL is US only because the spiders don't send `Accept-Language`; with that header the site redirects by IP.
- One folder per task under `glossier/` (`taskN/glossier_spider.py`, `taskN/output/`). `glossier/raw/` holds saved pages for inspection.
- Task 1: first page of cards only. Task 2: unique products + category. Task 3: + description. Task 4: one row per variant.
- Data sources on a product page: `SDG.Data.productJson` (category `type`, `variants` with ID, name, `available`), `#description-item` (description), picker `data-variant-price` / `data-variant-compare-at-price` (per-variant price), `.js-price-original` / `.js-price-compare` (button price for products without a picker and for fixed sets).
- Sets are recognised by `[data-set-items-json]`. Task 4 skips them for now.
- Planned for sets: a separate sets spider and CSV. `set_items` holds a list per slot of the variant IDs you can pick (from `data-set-items-json` + the component blocks). Build-your-own sets have no price (it's computed by JavaScript); they get `set_discount_percent` (`data-flexible-discount-percent`) so BI can calculate it. The main Task 4 CSV gets a `variant_id` column to join on. Scrapy's HTTP cache is under consideration.
- On Windows, `bash` resolves to the WSL stub and fails. Use `"C:\Program Files\Git\bin\bash.exe"`.
- I assume the loaded data will be either upserted or fully reloaded downstream.
