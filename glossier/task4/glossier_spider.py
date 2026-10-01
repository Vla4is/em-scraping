"""Glossier scraper - Task 4: every variant of every product, treated as its own product.

Same crawl as Task 3. Each product page lists its variants (sizes, shades, flavours)
in SDG.Data.productJson -> "variants"; every variant becomes one row, named and linked
on its own (?variant=<id>) and marked in or out of stock. A set is one row; set_variant_ids
lists, per slot, the variant IDs the buyer can pick, each of which has its own row.

Cards on the collection page link to a variant (?variant=...), so one product can
have several cards (e.g. Cloud Paint Blush / Bronzer). The link is cut at "?" to get
the product page; Scrapy requests each URL once, so every product is visited once.
The category is not shown on the page; it comes from the product data the page embeds
(SDG.Data.productJson -> "type"). The description is the visible paragraph
<p id="description-item">, which sets have too.

Set the collection URL in start_urls, then run from this folder:
    scrapy runspider glossier_spider.py -O output/name_of_the_output.csv
"""
import csv
import json
from datetime import datetime, timezone
import scrapy
from scrapy.exporters import CsvItemExporter


class QuotedCsvExporter(CsvItemExporter):
    # Every CSV value in quotes, so all columns read as text (IDs stay as typed, no 8.94E+12 in Excel).
    def __init__(self, *args, **kwargs):
        super().__init__(*args, quoting=csv.QUOTE_ALL, **kwargs)


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
        "FEED_EXPORTERS": {"csv": QuotedCsvExporter},
        "FEED_EXPORT_FIELDS": ["product_id", "variant_id", "product_name", "variant_name", "url", "image", "category", "description", "price", "discounted_price", "is_flexible_set", "flexible_discount_percent", "set_variant_ids", "in_stock", "scraped_at"],
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
        product = self.product_json(response)
        if not product.get("type"):
            self.logger.warning("No category found on %s", response.url)

        description = " ".join(" ".join(response.css("#description-item ::text").getall()).split())
        scraped_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        prices = self.variant_prices(response)
        is_flexible_set, flexible_discount_percent = self.flexible_set(response, product.get("id"))
        set_variant_ids = self.set_variant_ids(response, product.get("id"))
        image = self.main_image(response)
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
                "image": image,
                "category": product.get("type", ""),
                "description": description,
                # When discounted, the site shows the old price struck through next to the current one.
                "price": old or current,
                "discounted_price": current if old else "",
                "is_flexible_set": str(is_flexible_set),
                "flexible_discount_percent": flexible_discount_percent,
                "set_variant_ids": set_variant_ids,
                "in_stock": str(variant.get("available")),
                "scraped_at": scraped_at,
            }

    def main_image(self, response):
        # The product's main gallery photo as a one-item JSON array (the brief's "array of strings").
        # Build-your-own sets have no gallery in the HTML (JavaScript builds it), so they get "".
        img = response.css("#gallery.pv-gallery #photos.pv-gallery__items .pv-gallery__main-image "
                           ".ir.ir--product img.pv-gallery__image")
        if not img:
            return ""
        src = img[0].attrib.get("src") or img[0].attrib.get("data-src", "")
        # Everything after "?" is imgix resize options, including a "{width}" placeholder.
        return json.dumps([response.urljoin(src.split("?")[0])])

    def flexible_set(self, response, product_id):
        # Build-your-own set -> (True, "15.0"): no fixed price exists, only the discount the site's
        # JavaScript applies to the picked items. Fixed sets and products -> (False, "").
        # The set button must be this product's own: other products' pages can advertise a set.
        if not response.css(f'[data-set-items-json][data-set-product-id="{product_id}"]'):
            return False, ""
        percent = response.css("[data-flexible-discount-percent]::attr(data-flexible-discount-percent)").get()
        return (True, percent) if percent else (False, "")

    def set_variant_ids(self, response, product_id):
        # Set -> JSON list with one list per slot, e.g. "[[id, id], [id]]"; anything else -> "".
        # Every slot type (fixed product or build-your-own choice) is an <li> of the set's own list.
        if not response.css(f'[data-set-items-json][data-set-product-id="{product_id}"]'):
            return ""
        slots = []
        for slot in response.css(".pv-set-configurable .product-set__list > li"):
            ids = slot.css("input[data-variant-id]::attr(data-variant-id)").getall()
            if not ids and slot.attrib.get("data-variant-id"):
                # A component without options (e.g. Crème de You) carries its only variant itself.
                ids = [slot.attrib["data-variant-id"]]
            if not ids:
                self.logger.warning("Empty set slot on %s", response.url)
            slots.append([int(i) for i in dict.fromkeys(ids)])
        return json.dumps(slots)

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
