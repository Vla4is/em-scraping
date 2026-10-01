"""Glossier collection scraper - Task 1: every product card on the collection page.

The page loads more cards as you scroll; those come from ?page=2, 3, ... so the
spider follows the rel="next" link until there is none.

Set the collection URL in start_urls, then run from this folder:
    scrapy runspider glossier_spider.py -O output/task1-lt.csv

    in order to run it correctly from the terminal you need to have scrapy in your python
    the command to run it:
    scrapy runspider glossier_spider.py -O output/task1-lt.csv 
"""
import json
from datetime import datetime, timezone
import scrapy


class GlossierSpider(scrapy.Spider):
    name = "glossier"
    #please uncomment the country you need. I kept it simple.
    #LIT version
    # start_urls = ["https://www.glossier.com/en-lt/collections/all"]
    #US version
    start_urls = ["https://www.glossier.com/collections/all"]

    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 1,
        # Replaces Scrapy's defaults to drop Accept-Language: with it the site
        # geo-redirects by IP (e.g. to /en-lt/) instead of serving the URL we ask for.
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
        "FEED_EXPORT_ENCODING": "utf-8",
        "FEED_EXPORT_FIELDS": [
            "product_name", "product_id", "image", "url",
            "price", "regular_price", "scraped_at",
        ],
    }

    def parse(self, response):
        scraped_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        cards = response.css("article.js-product-item")
        self.logger.info("%s: %d cards", response.url, len(cards))

        for card in cards:
            # The visible price block is the one without "hide"; the hidden ones belong to other variants.
            price_block = card.css(".pi__price:not(.hide)")

            yield {
                # Visible title, not microdata: it tells apart split cards like "Cloud Paint Blush" / "Bronzer".
                "product_name": self.clean(card.css(".pi__title a::text").get()),
                "product_id": card.attrib.get("data-product-id"),
                "image": json.dumps(self.card_images(card, response)),
                "url": response.urljoin(card.css(".pi__title a::attr(href)").get()),
                # Direct text nodes only, so the hidden "Sale price" screen-reader label is skipped.
                "price": self.clean(" ".join(price_block.css(".pi__price--current::text").getall())),
                "regular_price": self.clean(" ".join(price_block.css(".pi__price--compare-at s::text").getall())),
                "scraped_at": scraped_at,
            }

        # Stop on the last page (no rel="next"), or on an empty page as a safety net.
        next_page = response.css('[rel="next"]::attr(href)').get()
        if cards and next_page:
            yield response.follow(next_page, callback=self.parse)

    def card_images(self, card, response):
        urls = []
        for img in card.css("img.js-product-item-image, img.js-product-item-image-hover"):
            # The first cards load eagerly (src); the rest are lazy-loaded (data-src).
            src = img.attrib.get("src") or img.attrib.get("data-src")
            if src:
                # Everything after "?" is imgix resize options, including a "{width}" placeholder.
                urls.append(response.urljoin(src.split("?")[0]))
        return urls

    @staticmethod
    def clean(text):
        return " ".join(text.split()) if text else ""
