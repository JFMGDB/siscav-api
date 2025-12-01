from pathlib import Path

import pytest

from apps.api.src.api.v1.crud import crud_authorized_plate
from apps.api.src.api.v1.schemas.authorized_plate import AuthorizedPlateCreate


def test_access_log_flow(client, db_session):
    """Testa o fluxo completo de registro de acesso.

    Verifica:
    1. Criação de placa autorizada
    2. Acesso autorizado (placa na whitelist)
    3. Acesso negado (placa não na whitelist)
    """
    # 1. Cria uma placa autorizada
    plate_in = AuthorizedPlateCreate(
        plate="ABC-1234", normalized_plate="ABC1234", description="Test Car"
    )
    crud_authorized_plate.create(db_session, plate_in)
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
    plate_in = AuthorizedPlateCreate(
        plate="ABC-1234", normalized_plate="ABC1234", description="Test Car"
    )
    crud_authorized_plate.create(db_session, plate_in)
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
