# bookcrawler

A small [Scrapy](https://scrapy.org/) project for Lab 5. It crawls the practice site
[books.toscrape.com](https://books.toscrape.com/) and produces IR-ready records (one per book) that can be
indexed or used as a retrieval corpus.

## Project layout

```
bookcrawler/
├── scrapy.cfg                 # Scrapy project config
├── bookcrawler/
│   ├── settings.py            # Crawl settings (politeness, user agent, feed encoding)
│   ├── spiders/books.py       # The `books` spider
│   ├── items.py               # Default Scrapy item stub (unused; spider yields dicts)
│   ├── pipelines.py           # Default pipeline stub (not enabled)
│   └── middlewares.py         # Default middleware stubs (not enabled)
├── books_scrapy.json          # Sample output (40 books)
├── books_scrapy.csv           # Same output as CSV
└── books_scrapy_preview.json  # Small preview of the output
```

## Setup

```bash
pip install scrapy
```

## Running the spider

Run from this directory (the one containing `scrapy.cfg`):

```bash
# Default: crawl the first 2 listing pages (~40 books)
scrapy crawl books -O books_scrapy.json

# Crawl more listing pages (the site has 50)
scrapy crawl books -a max_pages=5 -O books_scrapy.json

# CSV or JSON Lines output
scrapy crawl books -O books_scrapy.csv
scrapy crawl books -O books_scrapy.jsonl
```

`-O` overwrites the output file; use `-o` to append instead. Note that `FEED_MODE = "create"` is set in the
settings.

### Spider argument

| Argument    | Default | Description                                         |
|-------------|---------|-----------------------------------------------------|
| `max_pages` | `2`     | Number of listing pages to crawl (minimum 1).       |

## How it works

1. `parse` reads a listing page, follows every book link, then follows the "next" link until `max_pages`
   listing pages have been visited.
2. `parse_book` extracts the fields from each book's detail page and yields one dict.

## Output fields

| Field          | Description                                                          |
|----------------|----------------------------------------------------------------------|
| `doc_id`       | First 12 hex chars of the SHA-1 of the URL (stable document ID).     |
| `title`        | Book title.                                                          |
| `text`         | `"<title>. <description>"` – the field to index for search.          |
| `description`  | Product description (may be empty).                                  |
| `url`          | Detail page URL.                                                     |
| `category`     | Category from the breadcrumb (e.g. `Travel`).                        |
| `price_gbp`    | Price as a float, `£` stripped.                                      |
| `rating`       | Star rating as an integer 1–5.                                       |
| `availability` | Stock text, e.g. `In stock (19 available)`.                          |
| `source`       | Always `books.toscrape.com`.                                         |

## Politeness settings

Configured in [bookcrawler/settings.py](bookcrawler/settings.py):

- `ROBOTSTXT_OBEY = True`
- `CONCURRENT_REQUESTS_PER_DOMAIN = 1`
- `DOWNLOAD_DELAY = 0.5` seconds
- `DOWNLOAD_TIMEOUT = 20` seconds
- `USER_AGENT = "CADT-IR-Lab5/1.0 (educational sandbox crawler)"`
- `FEED_EXPORT_ENCODING = "utf-8"`

## Notes

- The target site is a sandbox built for scraping practice; do not point this spider at real sites without
  checking their terms and `robots.txt`.
- Some descriptions in the sample output look duplicated or truncated (e.g. ending in `...more`) because of
  how the source markup is parsed; clean the `description` field before indexing if that matters.
# bookcrawler-lab5-IR
