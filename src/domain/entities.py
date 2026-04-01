from pydantic import BaseModel, Field
from typing import List

class CurrencyQuotation(BaseModel):
    currency: str = Field(..., description="Sigla da moeda, ex: USD, EUR, GBP")
    date: str = Field(..., description="Data da cotação consultada no formato DD/MM/YYYY")
    buy_rate_brl: float = Field(..., description="Cotação de compra da moeda em Reais")
    sell_rate_brl: float = Field(..., description="Cotação de venda da moeda em Reais")
    usd_parity_buy: float = Field(..., description="Paridade (quantidade de USD para compor 1 unidade, ou vice-versa, dependendo do tipo da moeda) ou conversão direta para dólar de compra")
    usd_parity_sell: float = Field(..., description="Paridade convertida da moeda para venda em Dólar")
    
class ConvertedAmount(BaseModel):
    currency: str = Field(...)
    amount: float = Field(..., description="Quantidade original requisitada")
    usd_value_buy: float = Field(..., description="Total em Dólares baseado na taxa de compra")
    usd_value_sell: float = Field(..., description="Total em Dólares baseado na taxa de venda")
    reference_date: str = Field(...)
    rate_used_buy: float = Field(...)
    rate_used_sell: float = Field(...)
