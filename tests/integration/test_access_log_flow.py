"""E2E flow: authorized and denied access log ingest with image on disk."""

from pathlib import Path

from fastapi.testclient import TestClient

from tests.conftest import TEST_DEVICE_INGEST_KEY

_DEVICE = {"X-Device-Key": TEST_DEVICE_INGEST_KEY}


def test_access_log_authorized_and_denied_flow(client: TestClient, auth_token: str):
    """Fluxo completo: whitelist, ingest autorizado e negado, com arquivo persistido."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    client.post(
        "/api/v1/whitelist/",
        headers=headers,
        json={
            "plate": "ABC-1234",
            "normalized_plate": "ABC1234",
            "description": "Test Car",
        },
    )

    file_content = b"fake image content"
    files = {"file": ("test_image.jpg", file_content, "image/jpeg")}
    data = {"plate": "ABC-1234"}

    response = client.post("/api/v1/access_logs/", files=files, data=data, headers=_DEVICE)
    assert response.status_code == 200
    log = response.json()
    assert log["status"] == "Authorized"
    assert log["plate_string_detected"] == "ABC-1234"
    assert log["image_storage_key"].endswith(".jpg")

    saved_path = Path(log["image_storage_key"])
    assert saved_path.exists()
    assert saved_path.read_bytes() == file_content
    saved_path.unlink()

    files = {"file": ("test_image_denied.jpg", file_content, "image/jpeg")}
    data = {"plate": "XYZ-9999"}

    response = client.post("/api/v1/access_logs/", files=files, data=data, headers=_DEVICE)
    assert response.status_code == 200
    log = response.json()
    assert log["status"] == "Denied"
    assert log["plate_string_detected"] == "XYZ-9999"

    saved_path = Path(log["image_storage_key"])
    assert saved_path.exists()
    saved_path.unlink()
