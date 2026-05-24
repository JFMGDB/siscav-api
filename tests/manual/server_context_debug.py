"""Script manual: simula contexto de sessão do servidor."""

import sys
from pathlib import Path
from uuid import UUID

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps.api.src.api.v1.core.security import create_access_token
from apps.api.src.api.v1.db.session import get_db
from apps.api.src.api.v1.deps import get_current_user
from apps.api.src.api.v1.models.user import User
from apps.api.src.api.v1.repositories.user_repository import UserRepository


def main() -> None:
    print("[1] Criando token...")
    db_gen = get_db()
    db = next(db_gen)

    try:
        user = db.query(User).filter(User.email == "admin@siscav.com").first()
        print(f"[2] User encontrado: {user.email} (ID: {user.id})")

        token = create_access_token(user.id)
        print("[3] Token criado")

        print("[4] Testando get_current_user...")
        current_user = get_current_user(token=token, db=db)
        print(f"[5] get_current_user OK: {current_user.email}")

        print("[6] Testando com nova sessão (como servidor)...")
        db2_gen = get_db()
        db2 = next(db2_gen)
        try:
            current_user2 = get_current_user(token=token, db=db2)
            print(f"[7] get_current_user com nova sessão OK: {current_user2.email}")
        except Exception as e:
            print(f"[7] ERRO com nova sessão: {type(e).__name__}: {e!s}")
            from jose import jwt

            from apps.api.src.api.v1.core.config import get_settings

            settings = get_settings()
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            user_id = UUID(payload["sub"])
            print(f"[8] Token sub: {user_id}")
            found = UserRepository.get_by_id(db2, user_id)
            print(
                f"[9] Repository.get_by_id resultado: {found.email if found else 'NÃO ENCONTRADO'}"
            )
            found2 = db2.get(User, user_id)
            print(f"[10] db.get resultado: {found2.email if found2 else 'NÃO ENCONTRADO'}")
        finally:
            db2.close()
    finally:
        db.close()


if __name__ == "__main__":
    main()
