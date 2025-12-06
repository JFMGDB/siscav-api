import os
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from apps.api.src.api.v1.db.base import Base
from apps.api.src.api.v1.db.session import get_db
from apps.api.src.main import app

# Import models
from apps.api.src.api.v1.models.user import User
from apps.api.src.api.v1.models.authorized_plate import AuthorizedPlate
from apps.api.src.api.v1.models.access_log import AccessLog

# Setup test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_access_log_flow():
    db = TestingSessionLocal()
    from apps.api.src.api.v1.repositories.authorized_plate_repository import (
        AuthorizedPlateRepository,
    )
    
    # 1. Create an authorized plate
    AuthorizedPlateRepository.create(
        db, plate="ABC-1234", normalized_plate="ABC1234", description="Test Car"
    )
    db.close()
    
    # 2. Test Authorized Access
    # Create a dummy image file
    file_content = b"fake image content"
    files = {"file": ("test_image.jpg", file_content, "image/jpeg")}
    data = {"plate": "ABC-1234"}
    
    response = client.post("/api/v1/access_logs/", files=files, data=data)
    assert response.status_code == 200
    log = response.json()
    assert log["status"] == "Authorized"
    assert log["plate_string_detected"] == "ABC-1234"
    assert log["image_storage_key"].endswith(".jpg")
    
    # Verify file was saved (cleanup later)
    saved_path = Path(log["image_storage_key"])
    assert saved_path.exists()
    assert saved_path.read_bytes() == file_content
    saved_path.unlink() # Cleanup
    
    # 3. Test Denied Access
    files = {"file": ("test_image_denied.jpg", file_content, "image/jpeg")}
    data = {"plate": "XYZ-9999"} # Not in whitelist
    
    response = client.post("/api/v1/access_logs/", files=files, data=data)
    assert response.status_code == 200
    log = response.json()
    assert log["status"] == "Denied"
    assert log["plate_string_detected"] == "XYZ-9999"
    
    # Verify file was saved
    saved_path = Path(log["image_storage_key"])
    assert saved_path.exists()
    saved_path.unlink() # Cleanup
