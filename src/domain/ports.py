from abc import ABC, abstractmethod
from typing import List
from src.domain.entities import CurrencyQuotation

class QuotationProvider(ABC):
    """
    Interface (Port) que define o contrato para buscar a cotação de todas as moedas.
    """
    
    @abstractmethod
    async def get_all_quotations_for_date(self, target_date: str) -> List[CurrencyQuotation]:
        """
        Busca a cotação de todas as moedas para uma data específica.
        :param target_date: Data alvo no formato DD/MM/YYYY.
        :return: Lista de objetos CurrencyQuotation do dia contendo paridades USD.
        """
        pass

class QuotationRepository(ABC):
    """
    Interface (Port) que define o contrato para persistência das cotações (repositório).
    """
    
    @abstractmethod
    def save_quotations(self, target_date: str, quotations: List[CurrencyQuotation]) -> None:
        """
        Salva uma lista de cotações para uma dada data.
        :param target_date: Data alvo no formato DD/MM/YYYY.
        :param quotations: Lista de objetos CurrencyQuotation do dia.
        """
        pass

    @abstractmethod
    def get_quotations_by_date(self, target_date: str) -> List[CurrencyQuotation]:
        """
        Busca a cotação de todas as moedas salvas para uma data específica.
        :param target_date: Data alvo no formato DD/MM/YYYY.
        :return: Lista de objetos CurrencyQuotation do dia contendo paridades USD, ou lista vazia se não  encontrado.
        """
        pass
