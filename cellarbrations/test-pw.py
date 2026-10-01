from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.on("response", lambda r: print(r.status, r.url)
            if "storefrontgateway" in r.url else None)
    page.goto("https://www.cellarbrations.com.au/")
    # page.wait_for_timeout(5000)
    input("Browse freely, then press Enter here to save and close...")
    print("title:", page.title())
    print("final url:", page.url)
    page.screenshot(path="cellarbrations/raw/pw-screenshot.png", full_page=True)
    with open("cellarbrations/raw/pw-page.html", "w", encoding="utf-8") as f:
        f.write(page.content())
    browser.close()