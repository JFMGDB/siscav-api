"""
Script para cadastrar dados de demonstração no sistema SISCAV.

Uso:
    cd apps/api/src
    python seed_demo.py

Este script cria:
1. Um usuário administrador (admin@siscav.com / admin123) com is_admin=true
2. Placas de exemplo na whitelist

Após a primeira migração com a coluna is_admin, se o usuário já existir sem privilégios,
promova manualmente: UPDATE users SET is_admin = 1 WHERE email = 'admin@siscav.com';
(veja docs/api/README.md — seção Primeiro administrador).
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

# Adicionar diretório raiz ao PYTHONPATH
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from apps.api.src.api.v1.core.config import get_settings
from apps.api.src.api.v1.core.security import get_password_hash
from apps.api.src.api.v1.models.user import User
from apps.api.src.api.v1.models.authorized_plate import AuthorizedPlate
from apps.api.src.api.v1.utils.plate import normalize_plate

settings = get_settings()

# Criar engine e sessão
engine = create_engine(settings.database_url, echo=True)
SessionLocal = sessionmaker(bind=engine)

# Verificar se estamos usando SQLite
is_sqlite = "sqlite" in settings.database_url.lower()

# Dados de demonstração
DEMO_USER = {
    "email": "admin@siscav.com",
    "password": "admin123",
}

# Placas para cadastrar (formato: placa, descrição)
DEMO_PLATES = [
    ("ABC1234", "Veículo de teste 1 - Formato antigo"),
    ("XYZ5678", "Veículo de teste 2 - Formato antigo"),
    ("ABC1D23", "Veículo de teste 3 - Formato Mercosul"),
    ("BRA2E19", "Veículo de teste 4 - Formato Mercosul"),
]


def seed_user(db):
    """Cria usuário administrador se não existir."""
    existing = db.query(User).filter(User.email == DEMO_USER["email"]).first()
    if existing:
        print(f"[OK] Usuario ja existe: {DEMO_USER['email']}")
        return existing
    
    now = datetime.now(timezone.utc)
    user = User(
        email=DEMO_USER["email"],
        hashed_password=get_password_hash(DEMO_USER["password"]),
        is_admin=True,
    )
    # Para SQLite, definir timestamps manualmente
    if is_sqlite:
        user.created_at = now
        user.updated_at = now
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"[OK] Usuario criado: {DEMO_USER['email']} (senha: {DEMO_USER['password']})")
    return user


def seed_plates(db):
    """Cria placas de demonstração se não existirem."""
    now = datetime.now(timezone.utc)
    for plate, description in DEMO_PLATES:
        normalized = normalize_plate(plate)
        existing = db.query(AuthorizedPlate).filter(
            AuthorizedPlate.normalized_plate == normalized
        ).first()
        
        if existing:
            print(f"[OK] Placa ja existe: {plate} ({normalized})")
            continue
        
        plate_obj = AuthorizedPlate(
            plate=plate,
            normalized_plate=normalized,
            description=description,
        )
        # Para SQLite, definir timestamps manualmente
        if is_sqlite:
            plate_obj.created_at = now
            plate_obj.updated_at = now
        db.add(plate_obj)
        db.commit()
        print(f"[OK] Placa cadastrada: {plate} ({normalized}) - {description}")


def main():
    print("=" * 60)
    print("SISCAV - Script de Seed para Demonstração")
    print("=" * 60)
    print(f"\nDatabase: {settings.database_url}\n")
    
    db = SessionLocal()
    try:
        print("\n--- Criando usuário administrador ---")
        seed_user(db)
        
        print("\n--- Cadastrando placas autorizadas ---")
        seed_plates(db)
        
        print("\n" + "=" * 60)
        print("SEED CONCLUÍDO COM SUCESSO!")
        print("=" * 60)
        print("\nCredenciais de acesso:")
        print(f"  Email: {DEMO_USER['email']}")
        print(f"  Senha: {DEMO_USER['password']}")
        print("\nPlacas autorizadas para teste:")
        for plate, desc in DEMO_PLATES:
            print(f"  - {plate}: {desc}")
        print("\nPróximos passos:")
        print("  1. Inicie a API: uvicorn apps.api.src.main:app --reload")
        print("  2. Acesse: http://localhost:8000/docs")
        print("  3. Faça login e teste a whitelist")
        print("=" * 60)
    finally:
        db.close()


if __name__ == "__main__":
    main()


