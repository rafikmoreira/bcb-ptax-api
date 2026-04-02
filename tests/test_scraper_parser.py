import pytest
from src.infrastructure.bcb_scraper import PlaywrightBCBScraper
from src.domain.exceptions import QuotationNotFoundError

def test_parse_all_currencies():
    scraper = PlaywrightBCBScraper()
    csv_text = """31032026;978;A;EUR;5,4000;5,4100;1,08;1,09
31032026;220;A;USD;4,9870;4,9876;1,0000;1,0000
31032026;123;A;GBP;6,1010;6,1020;1,25;1,26
"""
    quotations = scraper._parse_all_currencies(csv_text, "2026-03-31")
    
    assert len(quotations) == 3
    
    eur = next(q for q in quotations if q.currency == "EUR")
    assert eur.date == "2026-03-31"
    assert eur.buy_rate_brl == 5.4000
    assert eur.usd_parity_buy == 1.08

    usd = next(q for q in quotations if q.currency == "USD")
    assert usd.buy_rate_brl == 4.9870
    assert usd.usd_parity_buy == 1.00

def test_parse_csv_for_usd_not_found():
    scraper = PlaywrightBCBScraper()
    csv_text = """linha_vazia
    
    outralinha
"""
    with pytest.raises(QuotationNotFoundError, match="Não foram encontradas cotações válidas"):
        scraper._parse_all_currencies(csv_text, "2026-03-31")
