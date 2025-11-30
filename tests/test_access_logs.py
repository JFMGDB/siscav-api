from pathlib import Path

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
