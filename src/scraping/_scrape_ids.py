"""
Scrape case IDs from the Bundesgerichtshof (BGH) website.
"""

import asyncio
import json
import re
import uuid
from itertools import count
from typing import List

from httpx import URL, AsyncClient
from lxml import html
from tqdm import tqdm

from src.common import cached_request, config
from src.common.types import ScrapingID
from src.common.utils import flatten_text

BASE_URL = URL("https://juris.bundesgerichtshof.de/cgi-bin/rechtsprechung/")
BASE_PARAMS = "list.py?Gericht=bgh&Art=en&Datum={year}&Seite={page}"
AKTENZEICHEN_PATTERN = re.compile(r"\w+\sZR\s\d+/\d+")


async def scrape_ids() -> List[ScrapingID]:
    """
    Main entry point to scrape multiple years (2005 through 2024) from BGH
    and save ScrapingID metadata into a JSONL file.
    """
    # Adjust the timeout if you expect big delays or slow connections
    sem = asyncio.Semaphore(10)
    async with AsyncClient(timeout=60) as client:
        with tqdm() as pbar:
            # Create a list (generator would also work) of coroutines to scrape each year
            tasks = [
                scrape_ids_for_year(year, client, sem, pbar)
                for year in range(2005, 2025)
            ]
            # Run scraping coroutines in parallel
            results_per_year = await asyncio.gather(*tasks)

    # Flatten the list of lists
    all_results = [
        scraping_id for sublist in results_per_year for scraping_id in sublist
    ]

    # Write out to a JSONL file
    content = "\n".join(json.dumps(r, default=lambda x: str(x)) for r in all_results)
    config.CASE_IDS_JSONL.parent.mkdir(parents=True, exist_ok=True)
    config.CASE_IDS_JSONL.write_text(content, encoding="utf-8")

    return all_results


async def scrape_ids_for_year(
    year: int, client: AsyncClient, sem: asyncio.Semaphore, pbar: tqdm
) -> List[ScrapingID]:
    """
    Scrapes a single year's worth of case metadata from BGH website.
    """
    # This pattern checks for link URLs that match the exact format for the document pages.
    # Example: "document.py?Gericht=bgh&Art=en&Datum=2020&Seite=0&nr=1234&anz=12&pos=3"
    link_pattern = re.compile(
        rf"document\.py\?Gericht=bgh&Art=en&Datum={year}&Seite=\d+&nr=\d+&anz=\d+&pos=\d+"
    )

    results = []

    # We iterate over pages, starting from 0 until we no longer find the "next page" link.
    for page in count(0):
        # Construct the URL for this year/page.
        url = BASE_URL.join(BASE_PARAMS.format(year=year, page=page))
        content = await cached_request.get(url, client, sem=sem)
        tree = html.fromstring(content)

        # Extract all <a class="doklink"> elements and check if they match our link pattern
        for a in tree.xpath("//a[@class='doklink']"):
            href = a.get("href", "")
            if href and link_pattern.match(href):
                # Flatten the text (removes weird whitespace, newlines, etc.)
                aktenzeichen = flatten_text(a.text)
                if AKTENZEICHEN_PATTERN.fullmatch(aktenzeichen):
                    # Add the parameter "Blank=1.pdf" to get direct PDF access
                    doc_url = BASE_URL.join(href).copy_add_param("Blank", "1.pdf")
                    results.append(
                        ScrapingID(
                            id=uuid.uuid5(uuid.NAMESPACE_URL, str(doc_url)),
                            year=year,
                            case_number=aktenzeichen,
                            url=doc_url,
                        )
                    )
                    pbar.update(1)
            elif not href.endswith(".pdf"):
                print(f"Unexpected link: {href}")

        # Check if the next page link exists
        page_links = tree.xpath("//a[@class='pagelink']/@href")
        next_page_param = BASE_PARAMS.format(year=year, page=page + 1)
        if next_page_param not in page_links:
            break

    return results
