"""Glossier scraper - Task 4: every variant of every product, treated as its own product.

Same crawl as Task 3. Each product page lists its variants (sizes, shades, flavours)
in SDG.Data.productJson -> "variants"; every variant becomes one row, named and linked
on its own (?variant=<id>) and marked in or out of stock. Sets are skipped for now.

Cards on the collection page link to a variant (?variant=...), so one product can
have several cards (e.g. Cloud Paint Blush / Bronzer). The link is cut at "?" to get
the product page; Scrapy requests each URL once, so every product is visited once.
The category is not shown on the page; it comes from the product data the page embeds
(SDG.Data.productJson -> "type"). The description is the visible paragraph
<p id="description-item">, which sets have too.

Set the collection URL in start_urls, then run from this folder:
    scrapy runspider glossier_spider.py -O output/name_of_the_output.csv
"""
import json
from datetime import datetime, timezone
import scrapy


class GlossierSpider(scrapy.Spider):
    name = "glossier"
    # start_urls = ["https://www.glossier.com/en-lt/collections/all"]
    start_urls = ["https://www.glossier.com/collections/all"]
    #for scraping the set links
    # start_urls = ["https://www.glossier.com/en-lt/collections/sets"]
    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 1,
        "SCHEDULER_MEMORY_QUEUE": "scrapy.squeues.FifoMemoryQueue",   # first in, first out
        "CONCURRENT_REQUESTS": 1,                                      # one request at a time
        # Replaces Scrapy's defaults to drop Accept-Language: with it the site
        # geo-redirects by IP (e.g. to /en-lt/) instead of serving the URL we ask for.
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
        "FEED_EXPORT_ENCODING": "utf-8",
        "FEED_EXPORT_FIELDS": ["product_id", "variant_id", "product_name", "variant_name", "url", "category", "description", "price", "discounted_price", "is_flexible_set", "flexible_discount_percent", "in_stock", "scraped_at"],
    }

    def parse(self, response):
        cards = response.css("article.js-product-item")
        self.logger.info("%s: %d cards", response.url, len(cards))
        #grabbing the url of the product
        for card in cards:
            href = card.css(".pi__title a::attr(href)").get()
            if href:
                yield response.follow(href.split("?")[0], callback=self.parse_product)

        # Stop on the last page (no rel="next"), or on an empty page as a safety net.
        next_page = response.css('[rel="next"]::attr(href)').get()
        if cards and next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_product(self, response):
        # Only set pages carry the set's contents in data-set-items-json; they need their own handling.
        # if response.css("[data-set-items-json]"):
        #     self.logger.info("Skipping set: %s", response.url)
        #     return

        product = self.product_json(response)
        if not product.get("type"):
            self.logger.warning("No category found on %s", response.url)

        description = " ".join(" ".join(response.css("#description-item ::text").getall()).split())
        scraped_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        prices = self.variant_prices(response)
        is_flexible_set, flexible_discount_percent = self.flexible_set(response, product.get("id"))
        # Products without a variant picker: the "Add to bag" price (the class without -sticky / -product-add-on).
        button_price = (self.money(response.css(".js-price-original ::text").getall()),
                        self.money(response.css(".js-price-compare ::text").getall()))

        for variant in product.get("variants", []):
            current, old = prices.get(str(variant["id"]), button_price)
            yield {
                "product_id": str(product.get("id", "")),
                # Unique across the store, so it is the key that set rows refer to.
                "variant_id": str(variant["id"]),
                "product_name": product.get("title", ""),
                # e.g. "XS" or "Black Cherry"; empty (None) for products without options instead of "Default Title".
                "variant_name": variant.get("public_title") or "",
                "url": f"{response.url}?variant={variant['id']}",
                "category": product.get("type", ""),
                "description": description,
                # When discounted, the site shows the old price struck through next to the current one.
                "price": old or current,
                "discounted_price": current if old else "",
                "is_flexible_set": is_flexible_set,
                "flexible_discount_percent": flexible_discount_percent,
                "in_stock": variant.get("available"),
                "scraped_at": scraped_at,
            }

    def flexible_set(self, response, product_id):
        # Build-your-own set -> (True, "15.0"): no fixed price exists, only the discount the site's
        # JavaScript applies to the picked items. Fixed sets and products -> (False, "").
        # The set button must be this product's own: other products' pages can advertise a set.
        if not response.css(f'[data-set-items-json][data-set-product-id="{product_id}"]'):
            return False, ""
        percent = response.css("[data-flexible-discount-percent]::attr(data-flexible-discount-percent)").get()
        return (True, percent) if percent else (False, "")

    def variant_prices(self, response):
        # Each picker option carries its variant's price. Other products' pickers on the page
        # never share these variant IDs, and repeated pickers repeat the same prices.
        prices = {}
        for option in response.css("input.config__radio[data-variant-id][data-variant-price]"):
            prices.setdefault(option.attrib["data-variant-id"], (
                self.money([option.attrib["data-variant-price"]]),
                self.money([option.attrib.get("data-variant-compare-at-price", "")]),
            ))
        return prices

    @staticmethod
    def money(texts):
        # First non-empty text, e.g. "€85,95 EUR" -> "€85,95"; a zero amount ("€0,00") means no price.
        text = next((" ".join(t.split()) for t in texts if t.strip()), "")
        if text[-4:-3] == " " and text[-3:].isalpha():
            text = text[:-4]
        return text if any(c in "123456789" for c in text) else ""

    @staticmethod
    def product_json(response):
        ##We address the script that projects the product category , i found in the structure of the html page, useful for bu analysis.
        script = response.xpath('//script[contains(text(), "SDG.Data.productJson")]/text()').get() 
        if not script:
            return {}
        raw = script.split("SDG.Data.productJson=", 1)[1].strip()
        # raw_decode stops at the end of the object; more assignments follow on the same line.
        return json.JSONDecoder().raw_decode(raw)[0]
