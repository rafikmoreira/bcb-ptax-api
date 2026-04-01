from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import Optional, List
from src.domain.entities import CurrencyQuotation, ConvertedAmount
from src.use_cases.get_ptax_quotation import GetPtaxQuotationUseCase
from src.infrastructure.bcb_scraper import PlaywrightBCBScraper
from src.infrastructure.sqlite_repository import SQLiteQuotationRepository

router = APIRouter(prefix="/api/v1", tags=["Quotation"])

def get_ptax_use_case() -> GetPtaxQuotationUseCase:
    provider = PlaywrightBCBScraper()
    repository = SQLiteQuotationRepository()
    return GetPtaxQuotationUseCase(provider=provider, repository=repository)

@router.get("/quotations", response_model=List[CurrencyQuotation])
async def list_all_quotations(
    reference_date: Optional[str] = None,
    use_case: GetPtaxQuotationUseCase = Depends(get_ptax_use_case)
):
    """
    Lista TODAS as moedas e suas informações extraídas do PTAX (BCB) na data solicitada, 
    incluindo taxas em BRL e as Paridades do site do BC.
    :param reference_date: DD/MM/YYYY (opcional)
    """
    if reference_date:
        ref_dt = datetime.strptime(reference_date, "%d/%m/%Y")
    else:
        ref_dt = datetime.now()
        
    try:
        quotations = await use_case.list_all_quotations(ref_dt)
        return quotations
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/quotation/{currency}")
async def get_currency_in_usd(
    currency: str,
    reference_date: Optional[str] = None,
    use_case: GetPtaxQuotationUseCase = Depends(get_ptax_use_case)
):
    """
    Retorna a cotação de 1 unidade da moeda (ex: EUR) lastreada/equivalente em Dólares (USD).
    :param currency: Sigla da moeda (EUR, JPY, GBP...)
    :param reference_date: DD/MM/YYYY (opcional)
    """
    if reference_date:
        ref_dt = datetime.strptime(reference_date, "%d/%m/%Y")
    else:
        ref_dt = datetime.now()
        
    try:
        return await use_case.get_currency_in_usd(currency, ref_dt)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/quotation/{currency}/convert", response_model=ConvertedAmount)
async def convert_currency_to_usd(
    currency: str,
    amount: float,
    reference_date: Optional[str] = None,
    use_case: GetPtaxQuotationUseCase = Depends(get_ptax_use_case)
):
    """
    Calcula a equivalência total em Dólares (USD) para um montante solicitado em uma moeda.
    Ex: /quotation/EUR/convert?amount=13000
    """
    if amount <= 0:
        raise HTTPException(status_code=400, detail="O valor de amount deve ser maior que 0.")
        
    if reference_date:
        ref_dt = datetime.strptime(reference_date, "%d/%m/%Y")
    else:
        ref_dt = datetime.now()
        
    try:
        return await use_case.convert_amount_in_usd(currency, amount, ref_dt)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
