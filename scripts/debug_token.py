"""Debug do token JWT."""

import sys
from pathlib import Path

root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from uuid import UUID

from jose import jwt

from apps.api.src.api.v1.core.config import get_settings
from apps.api.src.api.v1.db.session import SessionLocal
from apps.api.src.api.v1.models.user import User
from apps.api.src.api.v1.repositories.user_repository import UserRepository

# Token obtido do login (você precisa colar o token aqui)
token = input("Cole o token JWT: ").strip()

settings = get_settings()

try:
    # Decodificar token
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    print("\n[1] Token decodificado:")
    print(f"   sub (user_id): {payload.get('sub')}")
    print(f"   type: {payload.get('type')}")
    print(f"   exp: {payload.get('exp')}")

    # Buscar usuário
    user_id = UUID(payload["sub"])
    print(f"\n[2] Buscando usuário com ID: {user_id}")

    db = SessionLocal()
    try:
        # Testar busca direta
        user_direct = db.query(User).filter(User.id == user_id).first()
        print(f"   Busca direta (query): {user_direct.email if user_direct else 'NÃO ENCONTRADO'}")

        # Testar com get()
        user_get = db.get(User, user_id)
        print(f"   Busca com db.get(): {user_get.email if user_get else 'NÃO ENCONTRADO'}")

        # Testar com repositório
        user_repo = UserRepository.get_by_id(db, user_id)
        print(f"   Busca com Repository: {user_repo.email if user_repo else 'NÃO ENCONTRADO'}")

        # Listar todos os usuários
        all_users = db.query(User).all()
        print(f"\n[3] Todos os usuários no banco ({len(all_users)}):")
        for u in all_users:
            print(f"   - {u.id} : {u.email}")
            if str(u.id) == payload["sub"]:
                print("     ^^^ ESTE É O ID DO TOKEN!")

    finally:
        db.close()

except Exception as e:
    print(f"\n[ERRO] {type(e).__name__}: {e!s}")
    import traceback

    traceback.print_exc()
