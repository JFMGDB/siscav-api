import os

os.environ.setdefault("DEVICE_INGEST_KEY", "test-device-ingest-key")
os.environ.setdefault("ENVIRONMENT", "development")

from fastapi.testclient import TestClient

from tests.conftest import TEST_USER_EMAIL, TEST_USER_PASSWORD


def test_create_user_and_login(client: TestClient, test_user):
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
    )
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert tokens["token_type"] == "bearer"


def test_whitelist_crud(client: TestClient, auth_token: str):
    headers = {"Authorization": f"Bearer {auth_token}"}

    response = client.post(
        "/api/v1/whitelist/",
        headers=headers,
        json={
            "plate": "ABC-1234",
            "normalized_plate": "ABC1234",
            "description": "Test Car",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["plate"] == "ABC-1234"
    assert "id" in data
    plate_id = data["id"]

    response = client.get(f"/api/v1/whitelist/{plate_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == plate_id

    response = client.get("/api/v1/whitelist/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1

    response = client.put(
        f"/api/v1/whitelist/{plate_id}",
        headers=headers,
        json={
            "plate": "ABC-9999",
            "normalized_plate": "ABC9999",
            "description": "Updated",
        },
    )
    assert response.status_code == 200
    assert response.json()["plate"] == "ABC-9999"

    response = client.delete(f"/api/v1/whitelist/{plate_id}", headers=headers)
    assert response.status_code == 200

    response = client.get(f"/api/v1/whitelist/{plate_id}", headers=headers)
    assert response.status_code == 404
