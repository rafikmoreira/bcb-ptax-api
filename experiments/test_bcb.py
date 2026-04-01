import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.bcb.gov.br/estabilidadefinanceira/historicocotacoes")
        await page.screenshot(path="bcb.png")
        print(await page.content())
        await browser.close()

asyncio.run(main())
