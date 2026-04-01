import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Goto URL")
        await page.goto("https://www.bcb.gov.br/estabilidadefinanceira/historicocotacoes", wait_until="networkidle")
        
        frame = page.frame_locator("iframe")
        label_locator = frame.locator('text="Cotações de fechamento de todas as moedas"')
        print("Wait for label")
        await label_locator.wait_for(state="visible", timeout=10000)
        await label_locator.click()

        print("Wait for date input")
        date_input = frame.locator('input[name="DATAINI"], input[placeholder*="dd/mm/aaaa"], input[type="date"]').first
        await date_input.fill("30/03/2026")

        print("Click Pesquisar")
        search_btn = frame.locator('button, input[type="button"], input[type="submit"]').filter(has_text="Pesquisar").first
        if await search_btn.count() == 0:
            search_btn = frame.locator('input[value="Pesquisar"]')
        await search_btn.click()

        print("Wait for download")
        try:
            async with page.expect_download(timeout=5000) as download_info:
                download_btn = frame.locator('a, button').filter(has_text="CSV").first
                await download_btn.click(timeout=5000)
            download = await download_info.value
            print("Download successful:", download.suggested_filename)
        except Exception as e:
            print("Download failed, possibly due to future date.", e)
            print("Checking page content for alert/message")
            print(await frame.locator("body").inner_text())

        await browser.close()

asyncio.run(main())
