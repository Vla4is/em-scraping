"""Task 5 evidence: can direct HTTP requests (no browser) get the listing pages past Cloudflare?

Three levels, from plainest to most browser-like, each on pages 1 and 2:
  bare      - plain HTTP client, default headers
  headers   - plain HTTP client + a Chrome User-Agent and Accept headers
  impersonate - curl_cffi imitating Chrome's TLS/HTTP2 fingerprint as well

Every response is saved to responses/ next to this script. Run with the VPN on.
"""
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from curl_cffi import requests

sys.stdout.reconfigure(encoding="utf-8")
URL = "https://www.cellarbrations.com.au/sm/delivery/rsid/144981/categories/spirits/whisky-id-Whisky_Food"
PAGES = {"page1": URL, "page2": URL + "?page=2&skip=30"}
BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/129.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-AU,en;q=0.9",
}
TESTS = {
    "bare": {},
    "headers": {"headers": BROWSER_HEADERS},
    "impersonate": {"impersonate": "chrome"},
}
OUT = Path(__file__).parent / "responses"
OUT.mkdir(exist_ok=True)

print(f"run at {datetime.now(timezone.utc):%Y-%m-%d %H:%M:%S} UTC")
for test, kwargs in TESTS.items():
    for page, url in PAGES.items():
        try:
            r = requests.get(url, timeout=30, **kwargs)
        except Exception as e:  # e.g. SSL interception by antivirus
            print(f"{test:12} {page}: ERROR {type(e).__name__}: {str(e)[:120]}")
            continue
        html = r.text
        title = html.split("<title>", 1)[-1].split("</title>", 1)[0].strip()[:50] if "<title>" in html else ""
        (OUT / f"{test}_{page}.html").write_text(html, encoding="utf-8")
        print(f"{test:12} {page}: status {r.status_code}, {len(r.content):>9,} bytes, "
              f"cards {html.count('ProductCardWrapper-'):>2}, title {title!r}")
        time.sleep(2)
