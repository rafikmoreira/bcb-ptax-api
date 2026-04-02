class DomainError(Exception):
    """Base exception for all domain-level errors."""


class QuotationNotFoundError(DomainError):
    """Raised when quotation data is not available for the given parameters."""


class ScrapingError(DomainError):
    """Raised when the scraper fails to retrieve data from the external source."""
