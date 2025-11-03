from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ..core.config import get_settings


settings = get_settings()

# Engine e fábrica de sessões para o SQLAlchemy.
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)


def get_db() -> Generator[Session, None, None]:
    """Dependência do FastAPI que fornece uma sessão do SQLAlchemy por requisição."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


