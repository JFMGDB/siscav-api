from fastapi import FastAPI
from .api.v1.api import api_router

app = FastAPI(title="Sistema de Controle de Acesso Veicular API", version="0.1.0")


# Endpoint raiz
@app.get("/")
def read_root():
    return {"message": "SISCAV API está online"}

# Agrega os roteadores da API v1
app.include_router(api_router, prefix="/api/v1")
