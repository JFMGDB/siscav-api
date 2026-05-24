"""Script manual: fluxo de autenticação contra o banco configurado em DATABASE_URL."""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps.api.src.api.v1.core.config import get_settings
from apps.api.src.api.v1.core.security import create_access_token
from apps.api.src.api.v1.db.session import SessionLocal
from apps.api.src.api.v1.deps import get_current_user
from apps.api.src.api.v1.models.user import User
from apps.api.src.api.v1.repositories.user_repository import UserRepository
from jose import jwt


def main() -> None:
    db = SessionLocal()
    settings = get_settings()
    try:
        user = db.query(User).filter(User.email == "admin@siscav.com").first()
        print(f"[1] User encontrado: {user.email if user else None}")
        if not user:
            print("ERRO: Usuário não encontrado no banco!")
            sys.exit(1)

        print(f"[2] User ID: {user.id}")

        token = create_access_token(user.id)
        print(f"[3] Token criado: {token[:50]}...")

        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        print(f"[4] Token sub (user_id): {payload['sub']}")

        found_user = UserRepository.get_by_id(db, user.id)
        print(f"[5] Repository.get_by_id() encontrou: {found_user.email if found_user else None}")

        try:
            current_user = get_current_user(token=token, db=db)
            print(f"[6] get_current_user() funcionou: {current_user.email}")
            print("\n[OK] Fluxo de autenticação está funcionando corretamente!")
        except Exception as e:
            print(f"[6] get_current_user() falhou: {type(e).__name__}: {str(e)}")
            import traceback

            traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
