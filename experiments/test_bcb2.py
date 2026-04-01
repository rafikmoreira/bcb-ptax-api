import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.bcb.gov.br/estabilidadefinanceira/historicocotacoes", wait_until="networkidle")
        
        # Check if there is an iframe
        for frame in page.frames:
            print(f"Frame URL: {frame.url}")
            
        print("Page title:", await page.title())
        
        # Print texts of labels
        locs = await page.locator("label").all_inner_texts()
        print("Labels found:", locs)

        await browser.close()

asyncio.run(main())
