from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import Optional, List
from src.domain.entities import CurrencyQuotation, ConvertedAmount, CurrencyUsdRate
from src.domain.exceptions import DomainError
from src.use_cases.get_ptax_quotation import GetPtaxQuotationUseCase
from src.api.dependencies import get_ptax_use_case

router = APIRouter(prefix="/api/v1", tags=["Quotation"])

def parse_reference_date(reference_date: Optional[str]) -> datetime:
    if reference_date:
        try:
            return datetime.strptime(reference_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de data inválido. Use YYYY-MM-DD.")
    return datetime.now()

router = APIRouter(prefix="/api/v1", tags=["Quotation"])


@router.get("/quotations", response_model=List[CurrencyQuotation], summary="Listar todas as cotações PTAX")
async def list_all_quotations(
    reference_date: Optional[str] = None,
    use_case: GetPtaxQuotationUseCase = Depends(get_ptax_use_case)
):
    """
    Lista TODAS as moedas e suas informações extraídas do PTAX (BCB) na data solicitada,
    incluindo taxas em BRL e as Paridades do site do BC.
    :param reference_date: YYYY-MM-DD (opcional)
    """
    ref_dt = parse_reference_date(reference_date)

    try:
        return await use_case.list_all_quotations(ref_dt)
    except DomainError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/quotations/{currency}", response_model=CurrencyUsdRate, summary="Equivalência da moeda em USD")
async def get_currency_in_usd(
    currency: str,
    reference_date: Optional[str] = None,
    use_case: GetPtaxQuotationUseCase = Depends(get_ptax_use_case)
):
    """
    Retorna a cotação de 1 unidade da moeda (ex: EUR) lastreada/equivalente em Dólares (USD).
    :param currency: Sigla da moeda (EUR, JPY, GBP...)
    :param reference_date: YYYY-MM-DD (opcional)
    """
    ref_dt = parse_reference_date(reference_date)

    try:
        return await use_case.get_currency_in_usd(currency, ref_dt)
    except DomainError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/quotations/{currency}/convert", response_model=ConvertedAmount, summary="Converter montante para USD")
async def convert_currency_to_usd(
    currency: str,
    amount: float,
    reference_date: Optional[str] = None,
    use_case: GetPtaxQuotationUseCase = Depends(get_ptax_use_case)
):
    """
    Calcula a equivalência total em Dólares (USD) para um montante solicitado em uma moeda.
    Ex: /quotations/EUR/convert?amount=13000
    """
    if amount <= 0:
        raise HTTPException(status_code=400, detail="O valor de amount deve ser maior que 0.")

    ref_dt = parse_reference_date(reference_date)

    try:
        return await use_case.convert_amount_in_usd(currency, amount, ref_dt)
    except DomainError as e:
        raise HTTPException(status_code=404, detail=str(e))
