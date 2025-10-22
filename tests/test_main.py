from fastapi.testclient import TestClient

from apps.api.src.main import app

client = TestClient(app)


def test_read_root():
    """Testa o endpoint raiz"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "SISCAV API está online"}


def test_health_check():
    """Testa o endpoint de health check"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_api_title():
    """Testa se a API tem o título correto"""
    assert app.title == "Sistema de Controle de Acesso Veicular API"
    assert app.version == "0.1.0"


def test_invalid_endpoint():
    """Testa um endpoint inexistente"""
    response = client.get("/endpoint-inexistente")
    assert response.status_code == 404
