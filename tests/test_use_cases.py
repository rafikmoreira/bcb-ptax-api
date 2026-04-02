import pytest
from datetime import datetime
from src.domain.entities import CurrencyQuotation
from src.domain.ports import QuotationProvider
from src.use_cases.get_ptax_quotation import GetPtaxQuotationUseCase, get_previous_business_day

class MockQuotationProvider(QuotationProvider):
    async def get_all_quotations_for_date(self, target_date: str) -> list[CurrencyQuotation]:
        return [
            CurrencyQuotation(
                currency="USD",
                date=target_date,
                buy_rate_brl=5.00,
                sell_rate_brl=5.00,
                usd_parity_buy=1.0,
                usd_parity_sell=1.0
            ),
            CurrencyQuotation(
                currency="EUR",
                date=target_date,
                buy_rate_brl=5.50,
                sell_rate_brl=5.50,
                usd_parity_buy=1.1,
                usd_parity_sell=1.1
            )
        ]

@pytest.mark.asyncio
async def test_get_currency_in_usd_use_case():
    provider = MockQuotationProvider()
    use_case = GetPtaxQuotationUseCase(provider)
    
    result = await use_case.get_currency_in_usd("EUR", reference_date=datetime(2026, 10, 2))
    
    assert result.currency == "EUR"
    assert result.buy_rate_usd == 1.10
    assert result.sell_rate_usd == 1.10

@pytest.mark.asyncio
async def test_convert_amount_in_usd_use_case():
    provider = MockQuotationProvider()
    use_case = GetPtaxQuotationUseCase(provider)
    
    fake_date = datetime(2026, 10, 2)
    result = await use_case.convert_amount_in_usd("EUR", 13000, reference_date=fake_date)
    
    assert result.currency == "EUR"
    assert result.amount == 13000
    assert result.usd_value_buy == 14300.0
    assert result.usd_value_sell == 14300.0

def test_get_previous_business_day_monday():
    monday = datetime(2026, 10, 5)
    previous = get_previous_business_day(monday)
    assert previous.strftime("%Y-%m-%d") == "2026-10-02"
