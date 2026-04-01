from fastapi import FastAPI
from src.api.routes import router

app = FastAPI(
    title="PTAX Quotation API",
    description="API que acessa e retorna cotações de Dólar de forma automatizada via site do Banco Central.",
    version="1.0.0"
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
