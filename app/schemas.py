"""
Sales Quest — Schemas Pydantic para validação de dados.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
# ─────────────────────────────────────────────
# Auth
# ─────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: str
    senha: str
class RegisterRequest(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=150)
    senha: str = Field(..., min_length=4, max_length=100)
    cargo: Optional[str] = "Vendedor"
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict
class UserResponse(BaseModel):
    id: int
    nome: str
    email: str
    avatar: str
    cargo: str
    xp_total: int
    nivel: int
    class Config:
        from_attributes = True
# ─────────────────────────────────────────────
# Client
# ─────────────────────────────────────────────
class ClientCreate(BaseModel):
    nome: str = Field(..., min_length=2, max_length=150)
    email: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    notas: Optional[str] = None
class ClientUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    notas: Optional[str] = None
class ClientResponse(BaseModel):
    id: int
    nome: str
    email: Optional[str]
    telefone: Optional[str]
    endereco: Optional[str]
    notas: Optional[str]
    ativo: bool
    created_at: datetime
    total_vendas: Optional[int] = 0
    valor_total: Optional[float] = 0.0
    class Config:
        from_attributes = True
# ─────────────────────────────────────────────
# Sale
# ─────────────────────────────────────────────
class SaleCreate(BaseModel):
    produto: str = Field(..., min_length=1, max_length=200)
    categoria: str = Field(..., min_length=1, max_length=100)
    valor: float = Field(..., gt=0)
    quantidade: int = Field(default=1, ge=1)
    client_id: Optional[int] = None
class SaleResponse(BaseModel):
    id: int
    produto: str
    categoria: str
    valor: float
    quantidade: int
    data_venda: datetime
    client_nome: Optional[str] = None
    xp_ganho: Optional[int] = 0
    class Config:
        from_attributes = True
# ─────────────────────────────────────────────
# Mission
# ─────────────────────────────────────────────
class MissionResponse(BaseModel):
    id: int
    titulo: str
    descricao: Optional[str]
    icone: str
    tipo: str
    meta_valor: float
    xp_recompensa: int
    progresso: float = 0
    completa: bool = False
    percentual: float = 0
    class Config:
        from_attributes = True
# ─────────────────────────────────────────────
# Achievement
# ─────────────────────────────────────────────
class AchievementResponse(BaseModel):
    id: int
    titulo: str
    descricao: Optional[str]
    icone: str
    xp_recompensa: int
    desbloqueada: bool = False
    data_desbloqueio: Optional[datetime] = None
    class Config:
        from_attributes = True
# ─────────────────────────────────────────────
# Ranking
# ─────────────────────────────────────────────
class RankingEntry(BaseModel):
    posicao: int
    user_id: int
    nome: str
    avatar: str
    cargo: str
    xp_total: int
    nivel: int
    total_vendas: int
# ─────────────────────────────────────────────
# AI Recommendation
# ─────────────────────────────────────────────
class AIRecommendation(BaseModel):
    icone: str
    titulo: str
    mensagem: str
    tipo: str  # "dica", "alerta", "motivacao", "meta"
