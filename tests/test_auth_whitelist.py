from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from apps.api.src.api.v1.db.base import Base
from apps.api.src.api.v1.db.session import get_db
from apps.api.src.main import app

# Import models to register them with Base
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

def test_create_user_and_login():
    db = TestingSessionLocal()
    from apps.api.src.api.v1.crud import crud_user
    from apps.api.src.api.v1.schemas.user import UserCreate
    
    # Check if user exists
    user = crud_user.get_by_email(db, "test@example.com")
    if not user:
        user_in = UserCreate(email="test@example.com", password="password123")
        user = crud_user.create(db, user_in)
    db.close()
    
    # Test Login
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert tokens["token_type"] == "bearer"
    
    assert tokens["token_type"] == "bearer"
    
    # return tokens["access_token"]  <-- Don't return in test function
    
def get_token():
    # Helper to get token
    db = TestingSessionLocal()
    from apps.api.src.api.v1.crud import crud_user
    from apps.api.src.api.v1.schemas.user import UserCreate
    
    # Check if user exists
    user = crud_user.get_by_email(db, "test@example.com")
    if not user:
        user_in = UserCreate(email="test@example.com", password="password123")
        user = crud_user.create(db, user_in)
    db.close()
    
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": "test@example.com", "password": "password123"},
    )
    return response.json()["access_token"]

def test_whitelist_crud():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create
    response = client.post(
        "/api/v1/whitelist/",
        headers=headers,
        json={"plate": "ABC-1234", "normalized_plate": "ABC1234", "description": "Test Car"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["plate"] == "ABC-1234"
    assert "id" in data
    plate_id = data["id"]
    
    # Read
    response = client.get(f"/api/v1/whitelist/{plate_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == plate_id
    
    # List
    response = client.get("/api/v1/whitelist/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1
    
    # Update
    response = client.put(
        f"/api/v1/whitelist/{plate_id}",
        headers=headers,
        json={"plate": "ABC-9999", "normalized_plate": "ABC9999", "description": "Updated"},
    )
    assert response.status_code == 200
    assert response.json()["plate"] == "ABC-9999"
    
    # Delete
    response = client.delete(f"/api/v1/whitelist/{plate_id}", headers=headers)
    assert response.status_code == 200
    
    # Verify Delete
    response = client.get(f"/api/v1/whitelist/{plate_id}", headers=headers)
    assert response.status_code == 404
