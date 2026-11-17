import hashlib
import re

import scrapy

RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self, max_pages=2, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_pages = max(1, int(max_pages))
        self.pages_seen = 0

    def parse(self, response):
        """Listing page: follow each book link, then the next listing page."""
        self.pages_seen += 1

        for card in response.css("article.product_pod"):
            href = card.css("h3 a::attr(href)").get()
            if href:
                yield response.follow(href, callback=self.parse_book)

        # Stop after max_pages listing pages (bounded crawl).
        if self.pages_seen < self.max_pages:
            next_href = response.css("li.next a::attr(href)").get()
            if next_href:
                yield response.follow(next_href, callback=self.parse)

    def parse_book(self, response):
        """Detail page: yield one IR-ready dict per book."""
        title = (response.css("div.product_main h1::text").get() or "").strip()

        # The description can be missing, so join whatever text we find.
        parts = response.css("#product_description + p::text").getall()
        description = " ".join(p.strip() for p in parts if p.strip())

        category = response.css("ul.breadcrumb li:nth-child(3) a::text").get()
        category = category.strip() if category else None

        # Price text looks like "£51.77" -> keep only the number.
        price_text = response.css("div.product_main p.price_color::text").get() or ""
        match = re.search(r"\d+(?:\.\d+)?", price_text)
        price_gbp = float(match.group()) if match else None

        # Rating is stored in the class, for example "star-rating Three".
        rating = None
        rating_class = response.css("div.product_main p.star-rating::attr(class)").get() or ""
        for word in rating_class.split():
            if word in RATINGS:
                rating = RATINGS[word]

        avail_parts = response.css("div.product_main p.availability::text").getall()
        availability = " ".join(" ".join(avail_parts).split()) or None

        yield {
            "doc_id": hashlib.sha1(response.url.encode("utf-8")).hexdigest()[:12],
            "title": title,
            "text": f"{title}. {description}".strip(),
            "description": description,
            "url": response.url,
            "category": category,
            "price_gbp": price_gbp,
            "rating": rating,
            "availability": availability,
            "source": "books.toscrape.com",
        }
