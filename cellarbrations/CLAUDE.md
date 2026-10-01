# Cellarbrations scraper

- Target: https://www.cellarbrations.com.au/sm/delivery/rsid/144981/categories/spirits/whisky-id-Whisky_Food (store `rsid` 144981, AUD). 57 products over 2 pages, 30 per page.
- Deliverables: CSV per task, `README.md`, `notes.txt`, root `requirements.txt` (playwright, parsel; then `playwright install chromium`).
- Access: Cloudflare blocks the user's IP (403). Every live fetch needs the VPN on. Avast's HTTPS scanning breaks curl_cffi's certificate check; switch it off for `task5/http_test.py`.

## Layout

One self-contained folder per task, code duplicated on purpose:

```
taskN/
  taskN.py        # runs fetch_page.py, then parse_page.py; stops if fetch fails
  fetch_page.py   # Playwright: fetches all listing pages, saves raw HTML
  parse_page.py   # offline: raw HTML -> CSV
  raw/            # current run's pages (+ archive/)
  output/         # current CSV (+ archive/)
task5/
  http_test.py    # bare / headers / curl_cffi impersonate, pages 1-2 -> responses/
```

Task 1 fetches page 1 only (`raw/whisky_page1_<stamp>.html`, `output/whisky_page1_<stamp>.csv`). Tasks 2-4 fetch all pages (`raw/fetched_page_<n>_<stamp>.html`, `output/whisky_all_<stamp>.csv`). Scripts resolve paths from `Path(__file__).parent`, so they run from any working directory.

## Fetch (Tasks 2-4)

- Playwright Chromium, `headless=False`, one browser per run, `wait_until="domcontentloaded"`, saves `resp.text()` (raw server HTML, not rendered).
- Pagination: `link[rel="next"]::attr(href)`; that link drops `/sm/delivery/rsid/144981`, so the next URL is `URL + "?" + <its query>` (`?page=2&skip=30`). 2 s pause, max 50 pages, no repeated URL.
- A page is valid only if status 200 and it contains `ProductCardWrapper-`. All pages are held in memory; on any failure nothing is saved or archived.
- All pages of a run share one UTC timestamp `%Y-%m-%d_%H-%M-%S`, taken when page 1 answers. `scraped_at` is parsed back from the file name.
- `archive_old()` moves previous files to `archive/` only after success (raw in fetch, CSV in parse).

## Parse

- Reads every `raw/fetched_page_*_*.html`, sorted by page number; dedupes by `product_id`.
- Tasks 1-3, CSS selectors on each card `article[data-testid^="ProductCardWrapper-"]` (match class prefixes only, the suffixes are build-generated):
  - `product_id`: card `data-testid` minus `ProductCardWrapper-`
  - `product_name`: `h3[data-testid$="ProductNameTestId"]::text`
  - `url`: `a[class^="ProductCardHiddenLink"]::attr(href)`
  - `image`: `img::attr(src)`, written as a JSON list
  - `price`: `div[class^="ProductPrice--"]::text`
  - `was_price`: `div[class^="ProductWasPrice--"]::text` minus `was `, only on sale
  - `description` (Task 3): `div[class^="AriaProductTitle--"] p:nth-of-type(2)::text`
- Task 4 reads `window.__PRELOADED_STATE__=` (JSON, `json.JSONDecoder().raw_decode`) → `search`:
  - order: `products.category` (list of skus); data: `productCardDictionary[sku]`
  - `name`, `sku`, `image.default`, `price`, `wasPrice` (only if `isDiscounted`), `description`
  - `measuring_unit` / `units`: `unitOfSize.abbreviation` / `unitOfSize.size` (as given: `ml`/`700`, `l`/`1`)
  - `url` from the card link (the JSON has none)
  - Don't use the card unit price or `unitOfMeasure` for size: it's a comparison unit (e.g. `$21.43/100ml` on a 700 ml bottle).
- `clean_description()`: split on literal `<br />` (the only tag present), collapse whitespace per part, join with ` | `.
- CSV columns (Task 4): `product_name, product_id, image, url, price, was_price, description, measuring_unit, units, scraped_at`, all text. Parsing is idempotent: same raw pages give a byte-identical CSV.

## Environment

- Windows, repo `.venv` (Python 3.12). Run from `C:\dev\scraping`. For bash use `"C:\Program Files\Git\bin\bash.exe"`.
- curl_cffi is installed in `.venv` for `task5/http_test.py` only; it's not in `requirements.txt`.
