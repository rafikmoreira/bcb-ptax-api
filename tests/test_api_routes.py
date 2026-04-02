from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient

from src.api.main import app
from src.api.dependencies import get_ptax_use_case
from src.domain.entities import CurrencyQuotation, ConvertedAmount, CurrencyUsdRate
from src.domain.exceptions import DomainError


def make_mock_use_case(quotations=None, raises=None):
    mock = MagicMock()

    if raises:
        mock.list_all_quotations = AsyncMock(side_effect=raises)
        mock.get_currency_in_usd = AsyncMock(side_effect=raises)
        mock.convert_amount_in_usd = AsyncMock(side_effect=raises)
    else:
        default_quotations = quotations or [
            CurrencyQuotation(
                currency="USD",
                date="2026-04-01",
                buy_rate_brl=5.00,
                sell_rate_brl=5.00,
                usd_parity_buy=1.0,
                usd_parity_sell=1.0,
            ),
            CurrencyQuotation(
                currency="EUR",
                date="2026-04-01",
                buy_rate_brl=5.50,
                sell_rate_brl=5.50,
                usd_parity_buy=1.1,
                usd_parity_sell=1.1,
            ),
        ]
        mock.list_all_quotations = AsyncMock(return_value=default_quotations)
        mock.get_currency_in_usd = AsyncMock(return_value=CurrencyUsdRate(
            currency="EUR",
            date="2026-04-01",
            buy_rate_usd=1.1,
            sell_rate_usd=1.1,
            brl_buy=5.50,
            brl_sell=5.50,
        ))
        mock.convert_amount_in_usd = AsyncMock(return_value=ConvertedAmount(
            currency="EUR",
            amount=100.0,
            usd_value_buy=110.0,
            usd_value_sell=110.0,
            reference_date="2026-04-01",
            rate_used_buy=1.1,
            rate_used_sell=1.1,
        ))

    return mock


# ---------------------------------------------------------------------------
# GET /api/v1/quotations
# ---------------------------------------------------------------------------

class TestListAllQuotations:
    def test_returns_200_without_date(self):
        mock = make_mock_use_case()
        app.dependency_overrides[get_ptax_use_case] = lambda: mock

        with TestClient(app) as client:
            response = client.get("/api/v1/quotations")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

        app.dependency_overrides.clear()

    def test_returns_200_with_valid_date(self):
        mock = make_mock_use_case()
        app.dependency_overrides[get_ptax_use_case] = lambda: mock

        with TestClient(app) as client:
            response = client.get("/api/v1/quotations?reference_date=2026-04-01")

        assert response.status_code == 200

        app.dependency_overrides.clear()

    def test_returns_400_with_invalid_date_format(self):
        with TestClient(app) as client:
            response = client.get("/api/v1/quotations?reference_date=04-01-2026")

        assert response.status_code == 400
        assert "YYYY-MM-DD" in response.json()["detail"]

    def test_returns_404_when_provider_raises_domain_error(self):
        mock = make_mock_use_case(raises=DomainError("Data sem cotações disponíveis."))
        app.dependency_overrides[get_ptax_use_case] = lambda: mock

        with TestClient(app) as client:
            response = client.get("/api/v1/quotations")

        assert response.status_code == 404

        app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# GET /api/v1/quotations/{currency}
# ---------------------------------------------------------------------------

class TestGetCurrencyInUsd:
    def test_returns_200_for_valid_currency(self):
        mock = make_mock_use_case()
        app.dependency_overrides[get_ptax_use_case] = lambda: mock

        with TestClient(app) as client:
            response = client.get("/api/v1/quotations/EUR")

        assert response.status_code == 200
        assert response.json()["currency"] == "EUR"

        app.dependency_overrides.clear()

    def test_returns_400_with_invalid_date_format(self):
        with TestClient(app) as client:
            response = client.get("/api/v1/quotations/EUR?reference_date=01-04-2026")

        assert response.status_code == 400
        assert "YYYY-MM-DD" in response.json()["detail"]

    def test_returns_404_for_unknown_currency(self):
        mock = make_mock_use_case(raises=DomainError("Não foi possível encontrar as cotações para XYZ ou USD na data baseada."))
        app.dependency_overrides[get_ptax_use_case] = lambda: mock

        with TestClient(app) as client:
            response = client.get("/api/v1/quotations/XYZ")

        assert response.status_code == 404
        assert "XYZ" in response.json()["detail"]

        app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# GET /api/v1/quotations/{currency}/convert
# ---------------------------------------------------------------------------

class TestConvertCurrencyToUsd:
    def test_returns_200_with_valid_params(self):
        mock = make_mock_use_case()
        app.dependency_overrides[get_ptax_use_case] = lambda: mock

        with TestClient(app) as client:
            response = client.get("/api/v1/quotations/EUR/convert?amount=100")

        assert response.status_code == 200
        assert response.json()["currency"] == "EUR"

        app.dependency_overrides.clear()

    def test_returns_422_when_amount_is_missing(self):
        with TestClient(app) as client:
            response = client.get("/api/v1/quotations/EUR/convert")

        assert response.status_code == 422
        body = response.json()
        campos = [err["campo"] for err in body["detail"]]
        assert "amount" in campos

    def test_returns_422_when_amount_is_not_a_number(self):
        with TestClient(app) as client:
            response = client.get("/api/v1/quotations/EUR/convert?amount=abc")

        assert response.status_code == 422
        body = response.json()
        assert any("número válido" in err["erro"] for err in body["detail"])

    def test_returns_400_when_amount_is_zero(self):
        with TestClient(app) as client:
            response = client.get("/api/v1/quotations/EUR/convert?amount=0")

        assert response.status_code == 400
        assert response.json()["detail"] == "O valor de amount deve ser maior que 0."

    def test_returns_400_when_amount_is_negative(self):
        with TestClient(app) as client:
            response = client.get("/api/v1/quotations/EUR/convert?amount=-50")

        assert response.status_code == 400
        assert response.json()["detail"] == "O valor de amount deve ser maior que 0."

    def test_returns_400_with_invalid_date_format(self):
        with TestClient(app) as client:
            response = client.get("/api/v1/quotations/EUR/convert?amount=100&reference_date=2026/04/01")

        assert response.status_code == 400
        assert "YYYY-MM-DD" in response.json()["detail"]

    def test_returns_404_for_unknown_currency(self):
        mock = make_mock_use_case(raises=DomainError("Não foi possível encontrar XYZ ou USD para a conversão."))
        app.dependency_overrides[get_ptax_use_case] = lambda: mock

        with TestClient(app) as client:
            response = client.get("/api/v1/quotations/XYZ/convert?amount=100")

        assert response.status_code == 404

        app.dependency_overrides.clear()
