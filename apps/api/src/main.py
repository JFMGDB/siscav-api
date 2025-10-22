from fastapi import FastAPI

app = FastAPI(title="Sistema de Controle de Acesso Veicular API", version="0.1.0")


# Endpoint raiz
@app.get("/")
def read_root():
    return {"message": "SISCAV API está online"}


# Endpoint de Health Check
@app.get("/api/v1/health")
def health_check():
    return {"status": "ok"}
