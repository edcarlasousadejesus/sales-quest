"""
Sales Quest — Sistema de Autenticação (JWT + bcrypt).
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import get_db
from models import User
# ─────────────────────────────────────────────
# Configurações
# ─────────────────────────────────────────────
SECRET_KEY = "sales-quest-secret-key-2024-mude-em-producao"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)
# ─────────────────────────────────────────────
# Funções de Senha
# ─────────────────────────────────────────────
def hash_password(password: str) -> str:
    """Gera hash bcrypt da senha."""
    return pwd_context.hash(password)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica senha contra o hash."""
    return pwd_context.verify(plain_password, hashed_password)
# ─────────────────────────────────────────────
# Funções de Token JWT
# ─────────────────────────────────────────────
def create_access_token(user_id: int, email: str) -> str:
    """Cria token JWT com expiração."""
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
def decode_token(token: str) -> Optional[dict]:
    """Decodifica e valida token JWT."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
# ─────────────────────────────────────────────
# Dependency de Autenticação
# ─────────────────────────────────────────────
def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Dependency que retorna o usuário autenticado ou lança 401."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acesso não fornecido.",
        )
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado.",
        )
    user_id = int(payload.get("sub", 0))
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado.",
        )
    return user
