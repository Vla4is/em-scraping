# Cellarbrations whisky scraper

> **Install inside a virtual environment.** Installing these packages into your global Python can break other projects and your Jupyter kernel.
> ```sh
> python -m venv .venv
> .venv\Scripts\activate      # Windows
> source .venv/bin/activate   # macOS / Linux
> ```

Scrapes the [whisky category](https://www.cellarbrations.com.au/sm/delivery/rsid/144981/categories/spirits/whisky-id-Whisky_Food) into CSV. One folder per task.

## Run

With a **VPN on**:

```sh
pip install -r requirements.txt
playwright install chromium
python cellarbrations/task1/task1.py   # first page
python cellarbrations/task2/task2.py   # all pages
python cellarbrations/task3/task3.py   # + description
python cellarbrations/task4/task4.py   # + measuring_unit, units
```

Each `taskN.py` runs `fetch_page.py` (saves the pages) and then `parse_page.py` (writes the CSV). It stops if the fetch fails.

Task 5 test (needs `pip install curl_cffi`, which isn't in `requirements.txt` because the pipeline doesn't use it):

```sh
python cellarbrations/task5/http_test.py
```

## Why a VPN

Cloudflare blocks my IP (403, "Sorry, you have been blocked"), even in a real browser. Over a VPN the site loads normally.

## Why Playwright, and only once

Playwright opens the page **once**, saves the raw HTML and closes. Parsing then runs **offline** on the saved file, so selectors can be tested and re-run without touching the site again. The products are already in the server HTML, so no rendering is needed.

## Archiving

So the pipeline can be re-run without editing anything or losing history:
- The fetch time (UTC) is in the filename and becomes `scraped_at`.
- Each run moves the previous page to `raw/archive/` and the previous CSV to `output/archive/`.
- Archiving happens only after a successful step, so a failed run never wipes the current file.

## Idempotency: why the raw HTML is kept

The saved pages let anyone re-run the parser offline, no VPN needed: `python cellarbrations/task4/parse_page.py`. Same pages in, same CSV out, byte for byte (checked: same MD5 as the committed CSV). `scraped_at` comes from the file name, so it doesn't change on re-runs.

## Task 1 output

`product_name`, `product_id`, `image` (JSON list), `url`, `price`, `was_price`, `scraped_at` (UTC). 30 rows, all text.

- `price`: what you pay now, as shown (e.g. `$55.00`).
- `was_price`: the pre-sale price (`$59.00`), only for products on sale; empty otherwise.

## Task 2: all pages

Same columns as Task 1, for every product in the category: 57 rows over 2 pages.

- **Follows the site's own pagination.** Each page's `<link rel="next">` gives the next one, until there is none, so the number of pages is never hard-coded.
- **Keeps the store.** The site's next link drops `/sm/delivery/rsid/144981`, so the script keeps its own URL and takes only the `?page=2&skip=30` part.
- **One browser, one run.** All pages are fetched in one session, 2 seconds apart, and saved as `fetched_page_<n>_<UTC time>.html` with one shared timestamp.
- **All or nothing.** Pages are held in memory until every one succeeds. If any page fails, nothing is saved or archived, so `raw/` never mixes two runs.
- **No duplicates.** A product that appears on two pages is kept once, by `product_id`.
- Safety stops: at most 50 pages, and never the same URL twice.

## Task 3: description

Adds `description`. It's already in each listing card (the text the product overlay shows), so no product pages are fetched. `<br />` tags become ` | `, and line breaks are collapsed so each row stays on one line.

## Task 4: size

Adds `measuring_unit` and `units` (e.g. `ml` / `700`, `l` / `1`), as the site gives them.

Task 4 reads the data from the JSON the site embeds in each page (`__PRELOADED_STATE__`) instead of the card text. The card's unit price looks like the size but isn't: Macallan 12 Sherry Cask (700 mL) shows `$21.43/100ml`. The JSON has the real bottle size (`unitOfSize`). Only `url` comes from the card link, because the JSON has none.

## Task 5: browser or plain HTTP?

No rendering is needed: the products are in the raw server HTML. A browser is only needed to get past Cloudflare. [task5/http_test.py](task5/http_test.py) tested pages 1 and 2 over the VPN:

| Approach | Result |
|---|---|
| Plain HTTP | 403, blocked |
| Plain HTTP + browser headers | 403, blocked |
| curl_cffi (imitates Chrome's connection) | 200, all 57 products |
| Playwright (real Chrome, Tasks 1–4) | 200, all 57 products |

curl_cffi is the lighter option (no browser, only the HTML is downloaded). The pipeline still uses Playwright; why, and what I'd change, is in [notes.txt](notes.txt).

See [notes.txt](notes.txt) for decisions and AI usage.
