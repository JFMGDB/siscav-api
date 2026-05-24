"""
Seed demonstration data for the SISCAV system.

Usage (from repo root with PYTHONPATH=.):
    python scripts/seed_demo.py

Creates:
1. An admin user (admin@siscav.com / admin123) with is_admin=true
2. Sample plates in the whitelist

If the user already exists without admin privileges, promote manually:
UPDATE users SET is_admin = 1 WHERE email = 'admin@siscav.com';
(see docs/api/README.md — First Administrator section).
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

# Add repo root to PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from apps.api.src.api.v1.core.config import get_settings
from apps.api.src.api.v1.core.security import get_password_hash
from apps.api.src.api.v1.models.user import User
from apps.api.src.api.v1.models.authorized_plate import AuthorizedPlate
from apps.api.src.api.v1.utils.plate import normalize_plate

settings = get_settings()

engine = create_engine(settings.database_url, echo=True)
SessionLocal = sessionmaker(bind=engine)

is_sqlite = "sqlite" in settings.database_url.lower()

DEMO_USER = {
    "email": "admin@siscav.com",
    "password": "admin123",
}

DEMO_PLATES = [
    ("ABC1234", "Test vehicle 1 - Legacy format"),
    ("XYZ5678", "Test vehicle 2 - Legacy format"),
    ("ABC1D23", "Test vehicle 3 - Mercosul format"),
    ("BRA2E19", "Test vehicle 4 - Mercosul format"),
]


def seed_user(db):
    """Create admin user if it does not exist."""
    existing = db.query(User).filter(User.email == DEMO_USER["email"]).first()
    if existing:
        print(f"[OK] User already exists: {DEMO_USER['email']}")
        return existing

    now = datetime.now(timezone.utc)
    user = User(
        email=DEMO_USER["email"],
        hashed_password=get_password_hash(DEMO_USER["password"]),
        is_admin=True,
    )
    if is_sqlite:
        user.created_at = now
        user.updated_at = now
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"[OK] User created: {DEMO_USER['email']} (password: {DEMO_USER['password']})")
    return user


def seed_plates(db):
    """Create demo plates if they do not exist."""
    now = datetime.now(timezone.utc)
    for plate, description in DEMO_PLATES:
        normalized = normalize_plate(plate)
        existing = db.query(AuthorizedPlate).filter(
            AuthorizedPlate.normalized_plate == normalized
        ).first()

        if existing:
            print(f"[OK] Plate already exists: {plate} ({normalized})")
            continue

        plate_obj = AuthorizedPlate(
            plate=plate,
            normalized_plate=normalized,
            description=description,
        )
        if is_sqlite:
            plate_obj.created_at = now
            plate_obj.updated_at = now
        db.add(plate_obj)
        db.commit()
        print(f"[OK] Plate registered: {plate} ({normalized}) - {description}")


def main():
    print("=" * 60)
    print("SISCAV - Demo Seed Script")
    print("=" * 60)
    print(f"\nDatabase: {settings.database_url}\n")

    db = SessionLocal()
    try:
        print("\n--- Creating admin user ---")
        seed_user(db)

        print("\n--- Registering authorized plates ---")
        seed_plates(db)

        print("\n" + "=" * 60)
        print("SEED COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nAccess credentials:")
        print(f"  Email: {DEMO_USER['email']}")
        print(f"  Password: {DEMO_USER['password']}")
        print("\nAuthorized plates for testing:")
        for plate, desc in DEMO_PLATES:
            print(f"  - {plate}: {desc}")
        print("\nNext steps:")
        print("  1. Start the API: uvicorn apps.api.src.main:app --reload")
        print("  2. Open: http://localhost:8000/docs")
        print("  3. Log in and test the whitelist")
        print("=" * 60)
    finally:
        db.close()


if __name__ == "__main__":
    main()
