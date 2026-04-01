import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.bcb.gov.br/estabilidadefinanceira/historicocotacoes", wait_until="networkidle")
        
        frame = page.frame_locator('iframe')

        print("Click radio")
        await frame.locator('input[name="RadOpcao"][value="2"]').click()

        print("Fill date")
        await frame.locator('input[name="DATAINI"]').fill("30/03/2026")

        print("Click Pesquisar")
        await frame.locator('.botao[value="Pesquisar"]').click()
        
        # Wait for either CSV button OR an error message
        try:
            print("Wait for page to load results or error")
            await page.wait_for_timeout(3000)
            
            # The form navigates to a new page within the iframe. So let's check the iframe content
            print("Content:")
            print(await frame.locator("body").inner_text())

        except Exception as e:
            print("Error", e)

        await browser.close()

asyncio.run(main())
