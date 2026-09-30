"""Glossier scraper - Task 2: every unique product in the collection, with its category.

Cards on the collection page link to a variant (?variant=...), so one product can
have several cards (e.g. Cloud Paint Blush / Bronzer). The link is cut at "?" to get
the product page; Scrapy requests each URL once, so every product is visited once.
The category is not shown on the page; it comes from the product data the page embeds
(SDG.Data.productJson -> "type").

Set the collection URL in start_urls, then run from this folder:
    scrapy runspider glossier_spider.py -O output/name_of_the_output.csv
"""
import json
from datetime import datetime, timezone
import scrapy


class GlossierSpider(scrapy.Spider):
    name = "glossier"
    start_urls = ["https://www.glossier.com/en-lt/collections/all"]
    # start_urls = ["https://www.glossier.com/collections/all"]
    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 1,
        # Replaces Scrapy's defaults to drop Accept-Language: with it the site
        # geo-redirects by IP (e.g. to /en-lt/) instead of serving the URL we ask for.
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
        "FEED_EXPORT_ENCODING": "utf-8",
        "FEED_EXPORT_FIELDS": ["product_id", "product_name", "url", "category", "scraped_at"],
    }

    def parse(self, response):
        cards = response.css("article.js-product-item")
        self.logger.info("%s: %d cards", response.url, len(cards))

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

        yield {
            "product_id": str(product.get("id", "")),
            "product_name": product.get("title", ""),
            "url": response.url,
            "category": product.get("type", ""),
            "scraped_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }

    @staticmethod
    def product_json(response):
        ##We address the script that projects the product category , i found in the structure of the html page, useful for bu analysis.
        script = response.xpath('//script[contains(text(), "SDG.Data.productJson")]/text()').get() 
        if not script:
            return {}
        raw = script.split("SDG.Data.productJson=", 1)[1].strip()
        # raw_decode stops at the end of the object; more assignments follow on the same line.
        return json.JSONDecoder().raw_decode(raw)[0]
