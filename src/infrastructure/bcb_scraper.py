import io
import csv
import os
from datetime import datetime
from typing import List
from playwright.async_api import async_playwright
from src.domain.entities import CurrencyQuotation
from src.domain.ports import QuotationProvider

CACHE_DIR = os.path.join(os.getcwd(), "data", "csvs")

class PlaywrightBCBScraper(QuotationProvider):
    def __init__(self):
        os.makedirs(CACHE_DIR, exist_ok=True)
        
    async def get_all_quotations_for_date(self, target_date: str) -> List[CurrencyQuotation]:
        dt_obj = datetime.strptime(target_date, "%d/%m/%Y")
        file_date_str = dt_obj.strftime("%d%m%Y")
        file_name = f"cotacaoTodasAsMoedas_{file_date_str}.csv"
        file_path = os.path.join(CACHE_DIR, file_name)
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                csv_text = f.read()
            return self._parse_all_currencies(csv_text, target_date)
            
        csv_text = await self._download_csv_from_playwright(target_date)
            
        return self._parse_all_currencies(csv_text, target_date)

    async def _download_csv_from_playwright(self, target_date: str) -> str:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            try:
                await page.goto("https://www.bcb.gov.br/estabilidadefinanceira/historicocotacoes", wait_until="networkidle")
                
                # O formulário de cotações está dentro de um iframe
                frame = page.frame_locator('iframe[src*="ptax_internet"]')
                
                # Selecionar "Cotações de fechamento de todas as moedas em uma data"
                radio_btn = frame.locator('input[name="RadOpcao"][value="2"]')
                await radio_btn.wait_for(state="visible", timeout=30000)
                await radio_btn.click()

                # Preencher a data
                date_input = frame.locator('input[name="DATAINI"]')
                await date_input.fill(target_date)

                # Clicar em Pesquisar
                search_btn = frame.locator('.botao[value="Pesquisar"]')
                await search_btn.click()

                try:
                    async with page.expect_download(timeout=15000) as download_info:
                        download_btn = frame.locator('a, button').filter(has_text="CSV").first
                        await download_btn.click()
                except Exception as e:
                    # Capturamos o texto do body para mostrar erro útil (ex: data sem cotação/feriado)
                    body_text = await frame.locator("body").inner_text()
                    raise ValueError(f"Não foi possível baixar o CSV para a data {target_date}. A página pode não conter cotações. Erro original: {str(e)}. Resposta do Banco Central: {body_text.strip()[:300]}") from e
                    
                download = await download_info.value
                import tempfile
                with tempfile.TemporaryDirectory() as tmpdir:
                    temp_path = os.path.join(tmpdir, "temp.csv")
                    await download.save_as(temp_path)
                    with open(temp_path, "r", encoding="utf-8", errors="replace") as f:
                        csv_text = f.read()
                return csv_text
            finally:
                await browser.close()

    def _parse_all_currencies(self, csv_text: str, target_date: str) -> List[CurrencyQuotation]:
        reader = csv.reader(io.StringIO(csv_text.strip()), delimiter=';')
        quotations = []
        
        # Estrutura: 31032026;220;A;USD;5,2188;5,2194;1,0000;1,0000
        # Colunas: 0:Data, 1:Codec, 2:Tipo, 3:Sigla, 4:CompraBRL, 5:VendaBRL, 6:ParidadeCompra, 7:ParidadeVenda
        # Paridade do PTAX para nós já será passada explicitamente, visto que o BCB manda o valor na coluna 6 e 7.
        
        for row in reader:
            if len(row) < 6:
                continue
            
            sigla = row[3].upper().strip()
            try:
                buy_brl = float(row[4].replace(',', '.'))
                sell_brl = float(row[5].replace(',', '.'))
                
                if len(row) >= 8:
                    parity_buy = float(row[6].replace(',', '.'))
                    parity_sell = float(row[7].replace(',', '.'))
                else:
                    parity_buy = 0.0
                    parity_sell = 0.0
                    
                quotations.append(CurrencyQuotation(
                    currency=sigla,
                    date=target_date,
                    buy_rate_brl=buy_brl,
                    sell_rate_brl=sell_brl,
                    usd_parity_buy=parity_buy,
                    usd_parity_sell=parity_sell
                ))
            except (IndexError, ValueError):
                continue
                
        if not quotations:
            raise ValueError(f"Não foram encontradas cotações válidas no CSV para a data {target_date}")
            
        return quotations
