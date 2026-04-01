import asyncio
from src.infrastructure.bcb_scraper import PlaywrightBCBScraper

async def test():
    scraper = PlaywrightBCBScraper()
    res = await scraper.get_all_quotations_for_date("30/03/2026")
    print("Sucesso, total:", len(res))

asyncio.run(test())
