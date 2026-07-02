"""
Sales Quest — Modelos do Banco de Dados (SQLAlchemy ORM).
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text,
    DateTime, ForeignKey,
)
from sqlalchemy.orm import relationship
from database import Base
def utc_now():
    return datetime.now(timezone.utc)
# ─────────────────────────────────────────────
# Usuário (Vendedor)
# ─────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)
    avatar = Column(String(255), default="🧑‍💼")  # Emoji ou URL da imagem
    cargo = Column(String(100), default="Vendedor")
    xp_total = Column(Integer, default=0)
    nivel = Column(Integer, default=1)
    created_at = Column(DateTime, default=utc_now)
    # Relacionamentos
    sales = relationship("Sale", back_populates="user", lazy="dynamic")
    clients = relationship("Client", back_populates="user", lazy="dynamic")
    missions = relationship("UserMission", back_populates="user", lazy="dynamic")
    achievements = relationship("UserAchievement", back_populates="user", lazy="dynamic")
    xp_logs = relationship("XPLog", back_populates="user", lazy="dynamic")
# ─────────────────────────────────────────────
# Cliente
# ─────────────────────────────────────────────
class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    nome = Column(String(150), nullable=False)
    email = Column(String(150), nullable=True)
    telefone = Column(String(30), nullable=True)
    endereco = Column(String(300), nullable=True)
    notas = Column(Text, nullable=True)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    # Relacionamentos
    user = relationship("User", back_populates="clients")
    sales = relationship("Sale", back_populates="client", lazy="dynamic")
# ─────────────────────────────────────────────
# Venda
# ─────────────────────────────────────────────
class Sale(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    produto = Column(String(200), nullable=False)
    categoria = Column(String(100), nullable=False)
    valor = Column(Float, nullable=False)
    quantidade = Column(Integer, default=1)
    data_venda = Column(DateTime, default=utc_now)
    # Relacionamentos
    user = relationship("User", back_populates="sales")
    client = relationship("Client", back_populates="sales")
# ─────────────────────────────────────────────
# Missão
# ─────────────────────────────────────────────
class Mission(Base):
    __tablename__ = "missions"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(150), nullable=False)
    descricao = Column(Text, nullable=True)
    icone = Column(String(10), default="🎯")
    tipo = Column(String(50), nullable=False)  # "vendas_count", "vendas_valor", "categorias", "streak"
    meta_valor = Column(Float, nullable=False)  # valor numérico da meta
    xp_recompensa = Column(Integer, nullable=False)
    ativa = Column(Boolean, default=True)
    prazo_dias = Column(Integer, nullable=True)  # NULL = sem prazo
# ─────────────────────────────────────────────
# Progresso do Usuário em Missões
# ─────────────────────────────────────────────
class UserMission(Base):
    __tablename__ = "user_missions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=False)
    progresso = Column(Float, default=0)
    completa = Column(Boolean, default=False)
    data_inicio = Column(DateTime, default=utc_now)
    data_conclusao = Column(DateTime, nullable=True)
    # Relacionamentos
    user = relationship("User", back_populates="missions")
    mission = relationship("Mission")
# ─────────────────────────────────────────────
# Conquista
# ─────────────────────────────────────────────
class Achievement(Base):
    __tablename__ = "achievements"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(150), nullable=False)
    descricao = Column(Text, nullable=True)
    icone = Column(String(10), default="🏅")
    xp_recompensa = Column(Integer, default=0)
    criterio_tipo = Column(String(50), nullable=False)  # "total_vendas", "xp_total", "nivel", "valor_venda", "streak"
    criterio_valor = Column(Float, nullable=False)
# ─────────────────────────────────────────────
# Conquistas Desbloqueadas pelo Usuário
# ─────────────────────────────────────────────
class UserAchievement(Base):
    __tablename__ = "user_achievements"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    achievement_id = Column(Integer, ForeignKey("achievements.id"), nullable=False)
    data_desbloqueio = Column(DateTime, default=utc_now)
    # Relacionamentos
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement")
# ─────────────────────────────────────────────
# Log de XP
# ─────────────────────────────────────────────
class XPLog(Base):
    __tablename__ = "xp_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quantidade = Column(Integer, nullable=False)
    fonte = Column(String(50), nullable=False)  # "venda", "missao", "conquista"
    descricao = Column(String(300), nullable=True)
    created_at = Column(DateTime, default=utc_now)
    # Relacionamentos
    user = relationship("User", back_populates="xp_logs")
