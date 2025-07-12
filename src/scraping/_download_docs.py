"""
This script downloads documents from scraping IDs using asynchronous HTTP requests.
"""

import asyncio
from itertools import batched

from httpx import AsyncClient
from tqdm import tqdm

from src.common import cached_request
from src.common.types import ScrapingID
from src.common.utils import get_document_path, load_scraping_ids


async def download_docs():
    """
    Main function to download documents from scraping IDs.
    """
    sem = asyncio.Semaphore(10)
    scraping_ids = load_scraping_ids()
    async with AsyncClient(timeout=60) as client:
        with tqdm(total=len(scraping_ids)) as pbar:
            # Process the scraping IDs in batches of 100
            for batch in batched(scraping_ids, 100):
                tasks = (
                    _process(scraping_id, client, sem, pbar) for scraping_id in batch
                )
                # Gather will run these tasks concurrently, but each task
                # will respect the semaphore limit
                await asyncio.gather(*tasks)


async def _process(
    scraping_id: ScrapingID, client: AsyncClient, sem: asyncio.Semaphore, pbar: tqdm
):
    """
    Process a single scraping ID. This function is called concurrently for each
    scraping ID.
    """
    output_path = get_document_path(scraping_id["id"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not output_path.exists():
        content = await cached_request.get(scraping_id["url"], client, sem=sem)
        output_path.write_bytes(content)

    # Update the progress bar after each completed (or skipped) item
    pbar.update(1)
