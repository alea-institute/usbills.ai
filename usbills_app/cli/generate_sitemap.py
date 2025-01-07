"""
CLI task to generate sitemap.xml file.
"""

# imports
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List

# packages
from sqlalchemy import select

# project
from usbills_app.db import Bill, managed_async_session
from usbills_app.logger import create_logger

# create logger
LOGGER = create_logger(__name__)

# XML templates
SITEMAP_HEADER = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
"""

SITEMAP_FOOTER = """</urlset>"""

URL_TEMPLATE = """  <url>
    <loc>{}</loc>
    <lastmod>{}</lastmod>
    <changefreq>{}</changefreq>
    <priority>{}</priority>
  </url>
"""

# URL config
BASE_URL = "https://usbills.ai"
STATIC_URLS = [
    {"path": "/", "changefreq": "daily", "priority": 1.0},
    {"path": "/about", "changefreq": "monthly", "priority": 0.8},
    {"path": "/leaderboard", "changefreq": "daily", "priority": 0.9},
    {"path": "/privacy", "changefreq": "yearly", "priority": 0.5},
]


async def get_bill_urls() -> List[str]:
    """Get URLs for all bills in database.

    Returns:
        List[str]: List of sitemap URL entries
    """
    urls = []

    async with managed_async_session() as session:
        # Get all bills ordered by date
        stmt = select(Bill.slug, Bill.date).order_by(Bill.date.desc())
        result = await session.execute(stmt)
        bills = result.all()

        LOGGER.info(f"Generating sitemap entries for {len(bills)} bills")

        # Generate URL entries
        for slug, date in bills:
            lastmod = date.strftime("%Y-%m-%d")
            url_entry = URL_TEMPLATE.format(
                f"{BASE_URL}/bills/{slug}",
                lastmod,
                "monthly",  # Bills don't change often after initial posting
                0.7,  # Priority for bill pages
            )
            urls.append(url_entry)

    return urls


async def generate_sitemap() -> None:
    """Generate sitemap.xml file."""
    LOGGER.info("Starting sitemap generation")

    try:
        # Get bill URLs
        bill_urls = await get_bill_urls()

        # Generate static page URLs
        static_urls = []
        for url_config in STATIC_URLS:
            url_entry = URL_TEMPLATE.format(
                f"{BASE_URL}{url_config['path']}",
                datetime.now().strftime("%Y-%m-%d"),
                url_config["changefreq"],
                url_config["priority"],
            )
            static_urls.append(url_entry)

        # Create static directory if it doesn't exist
        static_dir = Path("static")
        static_dir.mkdir(exist_ok=True)

        # Write sitemap file
        sitemap_path = static_dir / "sitemap.xml"
        with open(sitemap_path, "w", encoding="utf-8") as f:
            f.write(SITEMAP_HEADER)
            for url in static_urls + bill_urls:
                f.write(url)
            f.write(SITEMAP_FOOTER)

        LOGGER.info(
            f"Generated sitemap with {len(static_urls)} static URLs and "
            f"{len(bill_urls)} bill URLs at {sitemap_path}"
        )

    except Exception as e:
        LOGGER.error(f"Failed to generate sitemap: {e}")
        raise


async def main() -> None:
    """Main entry point."""
    await generate_sitemap()


if __name__ == "__main__":
    asyncio.run(main())
