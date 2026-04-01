import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://ptax.bcb.gov.br/ptax_internet/consultaBoletim.do?method=exibeFormularioConsultaBoletim", wait_until="networkidle")
        
        # Check texts
        print("Page text in iframe:", await page.content())

        await browser.close()

asyncio.run(main())
