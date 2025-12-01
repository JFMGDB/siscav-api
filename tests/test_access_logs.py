from pathlib import Path

import pytest

from app.api.v1.core.utils import normalize_plate
from app.api.v1.crud import crud_access_log, crud_authorized_plate
from app.api.v1.schemas.authorized_plate import AuthorizedPlateCreate


def test_access_log_flow(client, db_session):
    """Testa o fluxo completo de registro de acesso.

    Verifica:
    1. Criação de placa autorizada
    2. Acesso autorizado (placa na whitelist)
    3. Acesso negado (placa não na whitelist)
    """
    # 1. Cria uma placa autorizada
    plate_in = AuthorizedPlateCreate(plate="ABC-1234", description="Test Car")
    normalized = normalize_plate(plate_in.plate)
    crud_authorized_plate.create(db_session, obj_in=plate_in, normalized_plate=normalized)
    # Garante que a transação é commitada e visível para outras sessões
    db_session.commit()

    # 2. Testa acesso autorizado
    # Cria um arquivo de imagem fake
    file_content = b"fake image content"
    files = {"file": ("test_image.jpg", file_content, "image/jpeg")}
    data = {"plate": "ABC-1234"}

    response = client.post("/api/v1/access_logs/", files=files, data=data)
    assert response.status_code == 200
    log = response.json()
    assert log["status"] == "Authorized"
    assert log["plate_string_detected"] == "ABC-1234"
    assert log["image_storage_key"].endswith(".jpg")

    # Verifica que o arquivo foi salvo
    # Nota: A limpeza é feita automaticamente pela fixture cleanup_uploads
    saved_path = Path(log["image_storage_key"])
    assert saved_path.exists()
    assert saved_path.read_bytes() == file_content

    # 3. Testa acesso negado
    files = {"file": ("test_image_denied.jpg", file_content, "image/jpeg")}
    data = {"plate": "XYZ-9999"}  # Não está na whitelist

    response = client.post("/api/v1/access_logs/", files=files, data=data)
    assert response.status_code == 200
    log = response.json()
    assert log["status"] == "Denied"
    assert log["plate_string_detected"] == "XYZ-9999"

    # Verifica que o arquivo foi salvo
    # Nota: A limpeza é feita automaticamente pela fixture cleanup_uploads
    saved_path = Path(log["image_storage_key"])
    assert saved_path.exists()


def test_access_log_file_too_large(client):
    """Testa upload de arquivo que excede o tamanho máximo."""
    file_content = b"x" * (11 * 1024 * 1024)  # 11MB
    files = {"file": ("large.jpg", file_content, "image/jpeg")}
    data = {"plate": "ABC-1234"}

    response = client.post("/api/v1/access_logs/", files=files, data=data)
    assert response.status_code == 413
    assert "too large" in response.json()["detail"].lower()


def test_access_log_invalid_mime_type(client):
    """Testa upload com tipo MIME inválido."""
    file_content = b"fake content"
    files = {"file": ("file.txt", file_content, "text/plain")}
    data = {"plate": "ABC-1234"}

    response = client.post("/api/v1/access_logs/", files=files, data=data)
    assert response.status_code == 415
    assert "unsupported" in response.json()["detail"].lower()


@pytest.mark.parametrize(
    ("extension", "mime_type"),
    [
        (".jpg", "image/jpeg"),
        (".jpeg", "image/jpeg"),
        (".png", "image/png"),
        (".webp", "image/webp"),
    ],
)
def test_access_log_supported_formats(client, db_session, extension, mime_type):
    """Testa upload com diferentes formatos de imagem suportados."""
    # Cria uma placa autorizada
    plate_in = AuthorizedPlateCreate(plate="ABC-1234", description="Test Car")
    normalized = normalize_plate(plate_in.plate)
    crud_authorized_plate.create(db_session, obj_in=plate_in, normalized_plate=normalized)
    db_session.commit()

    # Testa upload com formato específico
    file_content = b"fake image content"
    files = {"file": (f"test_image{extension}", file_content, mime_type)}
    data = {"plate": "ABC-1234"}

    response = client.post("/api/v1/access_logs/", files=files, data=data)
    assert response.status_code == 200
    log = response.json()
    assert log["status"] == "Authorized"
    assert log["image_storage_key"].endswith(extension)


def test_list_access_logs(client, auth_token, db_session):
    """Testa listagem de logs de acesso com paginação."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Cria uma placa autorizada
    plate_in = AuthorizedPlateCreate(plate="ABC-1234", description="Test Car")
    normalized = normalize_plate(plate_in.plate)
    authorized_plate = crud_authorized_plate.create(
        db_session, obj_in=plate_in, normalized_plate=normalized
    )
    db_session.commit()

    # Cria alguns logs de acesso
    for i in range(3):
        crud_access_log.create(
            db_session,
            plate_string_detected=f"ABC-{1000 + i}",
            status="Authorized" if i % 2 == 0 else "Denied",
            image_storage_key=f"/uploads/test_{i}.jpg",
            authorized_plate_id=authorized_plate.id if i % 2 == 0 else None,
        )
    db_session.commit()

    # Testa listagem com paginação
    response = client.get("/api/v1/access_logs/?skip=0&limit=2", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data
    assert "has_next" in data
    assert "has_prev" in data
    assert len(data["items"]) == 2
    assert data["total"] >= 3
    assert data["has_next"] is True
    assert data["has_prev"] is False

    # Verifica que logs estão ordenados por timestamp descendente (mais recentes primeiro)
    if len(data["items"]) > 1:
        timestamps = [item["timestamp"] for item in data["items"]]
        assert timestamps == sorted(timestamps, reverse=True)


def test_list_access_logs_with_status_filter(client, auth_token, db_session):
    """Testa listagem de logs filtrados por status."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Cria logs com diferentes status
    crud_access_log.create(
        db_session,
        plate_string_detected="ABC-1234",
        status="Authorized",
        image_storage_key="/uploads/test1.jpg",
    )
    crud_access_log.create(
        db_session,
        plate_string_detected="XYZ-9999",
        status="Denied",
        image_storage_key="/uploads/test2.jpg",
    )
    db_session.commit()

    # Filtra por status Authorized
    response = client.get("/api/v1/access_logs/?status=Authorized", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert all(item["status"] == "Authorized" for item in data["items"])

    # Filtra por status Denied
    response = client.get("/api/v1/access_logs/?status=Denied", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert all(item["status"] == "Denied" for item in data["items"])


def test_list_access_logs_with_plate_filter(client, auth_token, db_session):
    """Testa listagem de logs filtrados por placa."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Cria logs com diferentes placas
    crud_access_log.create(
        db_session,
        plate_string_detected="ABC-1234",
        status="Authorized",
        image_storage_key="/uploads/test1.jpg",
    )
    crud_access_log.create(
        db_session,
        plate_string_detected="XYZ-9999",
        status="Denied",
        image_storage_key="/uploads/test2.jpg",
    )
    db_session.commit()

    # Filtra por placa
    response = client.get("/api/v1/access_logs/?plate=ABC", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert all("ABC" in item["plate_string_detected"] for item in data["items"])


def test_list_access_logs_requires_authentication(client):
    """Testa que listagem de logs requer autenticação."""
    response = client.get("/api/v1/access_logs/")
    assert response.status_code == 401
