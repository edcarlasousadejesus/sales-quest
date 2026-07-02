"""
Sales Quest — Configuração do Banco de Dados SQLite com SQLAlchemy.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
# Caminho do banco SQLite (na mesma pasta do projeto)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'sales_quest.db')}"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Necessário para SQLite com FastAPI
    echo=False,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
def get_db():
    """Dependency que fornece uma sessão do banco para cada request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
def init_db():
    """Cria todas as tabelas no banco de dados."""
    from models import (  # noqa: F401
        User, Client, Sale, Mission,
        UserMission, Achievement, UserAchievement, XPLog,
    )
    Base.metadata.create_all(bind=engine)
    print("✅ Banco de dados inicializado com sucesso!")
