# PTAX Quotation API

Uma API construída com **FastAPI** seguindo os princípios da **Clean Architecture** para consultar, de forma automatizada, dados de cotação do **Banco Central do Brasil (BCB)** através da taxa PTAX. O projeto utiliza o **Playwright** para fazer o download automático dos arquivos CSV da cotação e calcula a equivalência das moedas atreladas ao Dólar Americano (USD).

## Principais Funcionalidades

- **Automação (Scraping):** Faz download e cache na máquina local do arquivo de cotação PTAX diretamente da página web do BCB usando Playwright.
- **Cálculo de Paridade USD:** Calcula o lastro de moedas listadas cruzadas pelo Dólar com base na PTAX, considerando Dólar e as respectivas paridades.
- **Cache Local e Lógica de Dias Úteis:** Lida com datas de referência para cotação, ignorando finais de semana ou usando cache dos dados (armazenados na pasta `data/`).
- **Sistema de Logs:** Utiliza infraestrutura de logs dedicada construída de forma robusta e transparente entre as camadas.

## Tecnologias e Ferramentas

- Python 3.14+
- [FastAPI](https://fastapi.tiangolo.com/)
- [Playwright](https://playwright.dev/python/)
- [uv](https://github.com/astral-sh/uv) (Gerenciador de pacotes rápido)
- [pytest](https://docs.pytest.org/) para testes automatizados

## Instalação

O projeto foi migrado para utilizar o `uv` como gerenciador de dependências em substituição ao `venv` clássico ou `pip`.

1. Clone o repositório e acesse a pasta do projeto:
   ```bash
   git clone <repo-url>
   cd take-ptax
   ```

2. Sincronize e instale as dependências usando `uv`:
   ```bash
   uv sync
   ```

3. Instale os navegadores do Playwright necessários para baixar as cotações do BCB:
   ```bash
   uv run playwright install chromium
   ```

## Como Executar

Inicie a aplicação localmente utilizando o `uv` via terminal. A API estará acessível por padrão em `http://0.0.0.0:8000`.

```bash
uv run python main.py
```

Você também pode acessar a documentação interativa gerada automaticamente pelo FastAPI via navegador:
- [Swagger UI: http://localhost:8000/docs](http://localhost:8000/docs)
- [ReDoc: http://localhost:8000/redoc](http://localhost:8000/redoc)

## Principais Endpoints da API

O `reference_date` pode ser opcionalmente enviado nos endpoints no formato `DD/MM/YYYY` (ex: `01/04/2026`). Caso não seja enviado, a data atual do momento da requisição é utilizada.

### 1. Listar todas as cotações
Retorna a lista de todas as moedas e suas informações extraídas do PTAX na data especificada, contendo suas taxas perante o BRL e as Paridades.
`GET /api/v1/quotations?reference_date=DD/MM/YYYY`

### 2. Equivalência de 1 unidade para USD
Retorna a cotação equivalente a 1 unidade da moeda desejada (ex: EUR, JPY) lastreada/equivalente em Dólares (USD).
`GET /api/v1/quotation/{currency}?reference_date=DD/MM/YYYY`

### 3. Converter um Montante para USD
Calcula a equivalência total em Dólares (USD) com base na cotação para o montante específico passado como valor.
`GET /api/v1/quotation/{currency}/convert?amount={valor}&reference_date=DD/MM/YYYY`
- Exemplo: `/api/v1/quotation/EUR/convert?amount=13000`

## Testes Automatizados

O projeto utiliza o framework `pytest` com o plugin assíncrono `pytest-asyncio`. Para executar os testes da aplicação garantindo a integridade dos casos de uso, infraestrutura de classes e roteamentos:

```bash
uv run pytest
```
