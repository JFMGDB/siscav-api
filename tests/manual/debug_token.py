"""Manual helper: decode a JWT and validate user lookup in the configured DB."""

import sys
from pathlib import Path
from uuid import UUID

from jose import jwt

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps.api.src.api.v1.core.config import get_settings
from apps.api.src.api.v1.db.session import SessionLocal
from apps.api.src.api.v1.models.user import User
from apps.api.src.api.v1.repositories.user_repository import UserRepository


def main() -> None:
    token = input("Paste the JWT: ").strip()
    if not token:
        raise SystemExit("Missing token")

    settings = get_settings()

    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    print("\n[1] Decoded token:")
    print(f"   sub (user_id): {payload.get('sub')}")
    print(f"   type: {payload.get('type')}")
    print(f"   exp: {payload.get('exp')}")

    user_id = UUID(payload["sub"])
    print(f"\n[2] Looking up user ID: {user_id}")

    db = SessionLocal()
    try:
        user_direct = db.query(User).filter(User.id == user_id).first()
        print(f"   Direct query: {user_direct.email if user_direct else 'NOT FOUND'}")

        user_get = db.get(User, user_id)
        print(f"   db.get(): {user_get.email if user_get else 'NOT FOUND'}")

        user_repo = UserRepository.get_by_id(db, user_id)
        print(f"   Repository: {user_repo.email if user_repo else 'NOT FOUND'}")
    finally:
        db.close()


if __name__ == "__main__":
    main()

