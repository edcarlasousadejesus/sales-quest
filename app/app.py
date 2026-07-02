"""
Sales Quest — Aplicação Principal FastAPI.
Rotas de API (auth, vendas, clientes, gamificação, IA) + páginas Jinja2.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastapi import FastAPI, Depends, HTTPException, status, Request, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from datetime import datetime, timedelta, timezone
from contextlib import asynccontextmanager
import uuid
import shutil
from database import get_db, init_db
from models import User, Client, Sale, Mission, UserMission, Achievement, UserAchievement, XPLog
from schemas import (
    LoginRequest, RegisterRequest, TokenResponse, UserResponse,
    ClientCreate, ClientUpdate, ClientResponse,
    SaleCreate, SaleResponse,
    MissionResponse, AchievementResponse, RankingEntry,
)
from auth import (
    hash_password, verify_password,
    create_access_token, get_current_user,
)
from gamification import (
    calculate_level, get_level_progress, calculate_sale_xp,
    grant_xp, update_missions_progress, check_achievements,
    assign_missions, get_level_title,
)
from ai_engine import get_recommendations, get_chatbot_ai_response
# ─────────────────────────────────────────────
# App Setup
# ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
app = FastAPI(
    title="Sales Quest",
    description="Plataforma Gamificada de Vendas",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
# ═════════════════════════════════════════════
# ROTAS DE PÁGINAS (HTML)
# ═════════════════════════════════════════════
@app.get("/login", response_class=HTMLResponse)
async def page_login(request: Request):
    return templates.TemplateResponse(request, "login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def page_register(request: Request):
    return templates.TemplateResponse(request, "register.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def page_dashboard(request: Request):
    return templates.TemplateResponse(request, "dashboard.html", {"request": request})
@app.get("/sales", response_class=HTMLResponse)
async def page_sales(request: Request):
    return templates.TemplateResponse(request, "sales.html", {"request": request})

@app.get("/clients", response_class=HTMLResponse)
async def page_clients(request: Request):
    return templates.TemplateResponse(request, "clients.html", {"request": request})

@app.get("/ranking", response_class=HTMLResponse)
async def page_ranking(request: Request):
    return templates.TemplateResponse(request, "ranking.html", {"request": request})

@app.get("/missions", response_class=HTMLResponse)
async def page_missions(request: Request):
    return templates.TemplateResponse(request, "missions.html", {"request": request})

@app.get("/achievements", response_class=HTMLResponse)
async def page_achievements(request: Request):
    return templates.TemplateResponse(request, "achievements.html", {"request": request})
# ═════════════════════════════════════════════
# API: AUTENTICAÇÃO
# ═════════════════════════════════════════════
@app.get("/")
async def page_root():
    return RedirectResponse(url="/login")
@app.post("/api/login", response_model=TokenResponse)
def api_login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.senha, user.senha_hash):
        raise HTTPException(status_code=401, detail="Email ou senha inválidos.")
    token = create_access_token(user.id, user.email)
    # Atribui missões que ainda não foram atribuídas
    assign_missions(db, user)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "nome": user.nome,
            "email": user.email,
            "avatar": user.avatar,
            "cargo": user.cargo,
            "xp_total": user.xp_total,
            "nivel": user.nivel,
        },
    }
@app.post("/api/register", response_model=TokenResponse)
def api_register(data: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Este email já está cadastrado.")
    user = User(
        nome=data.nome,
        email=data.email,
        senha_hash=hash_password(data.senha),
        cargo=data.cargo or "Vendedor",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    # Atribui missões
    assign_missions(db, user)
    token = create_access_token(user.id, user.email)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "nome": user.nome,
            "email": user.email,
            "avatar": user.avatar,
            "cargo": user.cargo,
            "xp_total": user.xp_total,
            "nivel": user.nivel,
        },
    }
@app.get("/api/me")
def api_me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    level_info = get_level_progress(user.xp_total, user.nivel)
    # Posição no ranking
    above = db.query(func.count(User.id)).filter(User.xp_total > user.xp_total).scalar() or 0
    posicao = above + 1
    # Totais
    total_vendas = db.query(func.count(Sale.id)).filter(Sale.user_id == user.id).scalar() or 0
    total_clientes = db.query(func.count(Client.id)).filter(
        Client.user_id == user.id, Client.ativo == True
    ).scalar() or 0
    valor_vendas = db.query(func.sum(Sale.valor * Sale.quantidade)).filter(
        Sale.user_id == user.id
    ).scalar() or 0
    return {
        "id": user.id,
        "nome": user.nome,
        "email": user.email,
        "avatar": user.avatar,
        "cargo": user.cargo,
        "xp_total": user.xp_total,
        "nivel": user.nivel,
        "level_info": level_info,
        "posicao_ranking": posicao,
        "total_vendas": total_vendas,
        "total_clientes": total_clientes,
        "valor_vendas": round(valor_vendas, 2),
    }


@app.post("/api/upload-avatar")
async def api_upload_avatar(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="O arquivo deve ser uma imagem.")

    # Cria nome de arquivo único
    ext = file.filename.split(".")[-1]
    filename = f"{user.id}_{uuid.uuid4().hex[:8]}.{ext}"
    upload_dir = os.path.join(BASE_DIR, "static", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, filename)

    # Remove avatar antigo se for um arquivo local
    if user.avatar and user.avatar.startswith("/static/uploads/"):
        old_file = os.path.join(BASE_DIR, user.avatar.lstrip("/"))
        if os.path.exists(old_file):
            os.remove(old_file)

    # Salva o novo arquivo
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Atualiza banco
    url_path = f"/static/uploads/{filename}"
    user.avatar = url_path
    db.commit()

    return {"message": "Foto atualizada com sucesso.", "avatar": url_path}
# ═════════════════════════════════════════════
# API: CLIENTES
# ═════════════════════════════════════════════
@app.post("/api/clients")
def api_create_client(
    data: ClientCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    client = Client(
        user_id=user.id,
        nome=data.nome,
        email=data.email,
        telefone=data.telefone,
        endereco=data.endereco,
        notas=data.notas,
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    # Verifica conquistas e missões
    update_missions_progress(db, user)
    new_achievements = check_achievements(db, user)
    return {
        "client": {
            "id": client.id,
            "nome": client.nome,
            "email": client.email,
            "telefone": client.telefone,
            "endereco": client.endereco,
            "notas": client.notas,
            "ativo": client.ativo,
        },
        "conquistas": new_achievements,
    }
@app.get("/api/clients")
def api_list_clients(
    search: str = Query(default="", description="Busca por nome, email ou telefone"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Client).filter(Client.user_id == user.id, Client.ativo == True)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Client.nome.ilike(search_term)) |
            (Client.email.ilike(search_term)) |
            (Client.telefone.ilike(search_term))
        )
    clients = query.order_by(Client.nome).all()
    result = []
    for c in clients:
        total_vendas = db.query(func.count(Sale.id)).filter(Sale.client_id == c.id).scalar() or 0
        valor_total = db.query(func.sum(Sale.valor * Sale.quantidade)).filter(
            Sale.client_id == c.id
        ).scalar() or 0
        result.append({
            "id": c.id,
            "nome": c.nome,
            "email": c.email or "",
            "telefone": c.telefone or "",
            "endereco": c.endereco or "",
            "notas": c.notas or "",
            "ativo": c.ativo,
            "created_at": c.created_at.isoformat() if c.created_at else "",
            "total_vendas": total_vendas,
            "valor_total": round(valor_total, 2),
        })
    return {"clients": result, "total": len(result)}
@app.get("/api/clients/{client_id}")
def api_get_client(
    client_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    client = db.query(Client).filter(
        Client.id == client_id, Client.user_id == user.id
    ).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    total_vendas = db.query(func.count(Sale.id)).filter(Sale.client_id == client.id).scalar() or 0
    valor_total = db.query(func.sum(Sale.valor * Sale.quantidade)).filter(
        Sale.client_id == client.id
    ).scalar() or 0
    return {
        "id": client.id,
        "nome": client.nome,
        "email": client.email,
        "telefone": client.telefone,
        "endereco": client.endereco,
        "notas": client.notas,
        "ativo": client.ativo,
        "total_vendas": total_vendas,
        "valor_total": round(valor_total, 2),
    }
@app.put("/api/clients/{client_id}")
def api_update_client(
    client_id: int,
    data: ClientUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    client = db.query(Client).filter(
        Client.id == client_id, Client.user_id == user.id
    ).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    if data.nome is not None:
        client.nome = data.nome
    if data.email is not None:
        client.email = data.email
    if data.telefone is not None:
        client.telefone = data.telefone
    if data.endereco is not None:
        client.endereco = data.endereco
    if data.notas is not None:
        client.notas = data.notas
    db.commit()
    return {"message": "Cliente atualizado com sucesso.", "id": client.id}
@app.delete("/api/clients/{client_id}")
def api_delete_client(
    client_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    client = db.query(Client).filter(
        Client.id == client_id, Client.user_id == user.id
    ).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    client.ativo = False  # Soft delete
    db.commit()
    return {"message": "Cliente desativado com sucesso."}
# ═════════════════════════════════════════════
# API: VENDAS
# ═════════════════════════════════════════════
@app.post("/api/sales")
def api_create_sale(
    data: SaleCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Verifica se o cliente existe (se informado)
    if data.client_id:
        client = db.query(Client).filter(
            Client.id == data.client_id, Client.user_id == user.id
        ).first()
        if not client:
            raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    sale = Sale(
        user_id=user.id,
        client_id=data.client_id,
        produto=data.produto,
        categoria=data.categoria,
        valor=data.valor,
        quantidade=data.quantidade,
    )
    db.add(sale)
    db.commit()
    # Calcula e concede XP
    xp_amount = calculate_sale_xp(data.valor, data.quantidade)
    xp_result = grant_xp(
        db, user, xp_amount, "venda",
        f"Venda: {data.produto} — R${data.valor * data.quantidade:,.2f}"
    )
    # Atualiza missões e conquistas
    completed_missions = update_missions_progress(db, user)
    new_achievements = check_achievements(db, user)
    client_nome = ""
    if data.client_id:
        c = db.query(Client).filter(Client.id == data.client_id).first()
        client_nome = c.nome if c else ""
    return {
        "sale": {
            "id": sale.id,
            "produto": sale.produto,
            "categoria": sale.categoria,
            "valor": sale.valor,
            "quantidade": sale.quantidade,
            "client_nome": client_nome,
        },
        "xp": xp_result,
        "missoes_completas": completed_missions,
        "conquistas": new_achievements,
    }
@app.get("/api/sales")
def api_list_sales(
    search: str = Query(default=""),
    categoria: str = Query(default=""),
    client_id: int = Query(default=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Sale).filter(Sale.user_id == user.id)
    if search:
        query = query.filter(Sale.produto.ilike(f"%{search}%"))
    if categoria:
        query = query.filter(Sale.categoria == categoria)
    if client_id > 0:
        query = query.filter(Sale.client_id == client_id)
    sales = query.order_by(Sale.data_venda.desc()).limit(100).all()
    result = []
    for s in sales:
        client_nome = ""
        if s.client_id:
            c = db.query(Client).filter(Client.id == s.client_id).first()
            client_nome = c.nome if c else ""
        result.append({
            "id": s.id,
            "produto": s.produto,
            "categoria": s.categoria,
            "valor": s.valor,
            "quantidade": s.quantidade,
            "data_venda": s.data_venda.isoformat() if s.data_venda else "",
            "client_nome": client_nome,
            "client_id": s.client_id,
        })
    return {"sales": result, "total": len(result)}
@app.get("/api/sales/stats")
def api_sales_stats(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    # Vendas dos últimos 7 dias (por dia)
    daily_sales = []
    for i in range(6, -1, -1):
        day = now - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        total = db.query(func.sum(Sale.valor * Sale.quantidade)).filter(
            Sale.user_id == user.id,
            Sale.data_venda >= day_start,
            Sale.data_venda < day_end,
        ).scalar() or 0
        count = db.query(func.count(Sale.id)).filter(
            Sale.user_id == user.id,
            Sale.data_venda >= day_start,
            Sale.data_venda < day_end,
        ).scalar() or 0
        daily_sales.append({
            "data": day_start.strftime("%d/%m"),
            "dia_semana": ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"][day_start.weekday()],
            "valor": round(total, 2),
            "quantidade": count,
        })
    # Vendas por categoria
    by_category = (
        db.query(
            Sale.categoria,
            func.count(Sale.id).label("count"),
            func.sum(Sale.valor * Sale.quantidade).label("total"),
        )
        .filter(Sale.user_id == user.id)
        .group_by(Sale.categoria)
        .order_by(func.sum(Sale.valor * Sale.quantidade).desc())
        .all()
    )
    categories = [
        {"categoria": c.categoria, "count": c.count, "total": round(c.total, 2)}
        for c in by_category
    ]
    # Categorias disponíveis (para filtro)
    all_categories = [c.categoria for c in by_category]
    return {
        "daily_sales": daily_sales,
        "categories": categories,
        "all_categories": all_categories,
    }
# ═════════════════════════════════════════════
# API: GAMIFICAÇÃO
# ═════════════════════════════════════════════
@app.get("/api/ranking")
def api_ranking(db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.xp_total.desc()).all()
    ranking = []
    for i, u in enumerate(users):
        total_vendas = db.query(func.count(Sale.id)).filter(Sale.user_id == u.id).scalar() or 0
        ranking.append({
            "posicao": i + 1,
            "user_id": u.id,
            "nome": u.nome,
            "avatar": u.avatar,
            "cargo": u.cargo,
            "xp_total": u.xp_total,
            "nivel": u.nivel,
            "titulo": get_level_title(u.nivel),
            "total_vendas": total_vendas,
        })
    return {"ranking": ranking}
@app.get("/api/missions")
def api_missions(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Atualiza progresso antes de retornar
    update_missions_progress(db, user)
    user_missions = (
        db.query(UserMission)
        .filter(UserMission.user_id == user.id)
        .all()
    )
    result = []
    for um in user_missions:
        m = um.mission
        if not m:
            continue
        pct = min(100, (um.progresso / m.meta_valor * 100)) if m.meta_valor > 0 else 0
        result.append({
            "id": m.id,
            "titulo": m.titulo,
            "descricao": m.descricao,
            "icone": m.icone,
            "tipo": m.tipo,
            "meta_valor": m.meta_valor,
            "xp_recompensa": m.xp_recompensa,
            "progresso": um.progresso,
            "completa": um.completa,
            "percentual": round(pct, 1),
        })
    # Ordena: incompletas primeiro, depois completas
    result.sort(key=lambda x: (x["completa"], -x["percentual"]))
    return {"missions": result}
@app.get("/api/achievements")
def api_achievements(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    all_ach = db.query(Achievement).all()
    unlocked = {
        ua.achievement_id: ua.data_desbloqueio
        for ua in db.query(UserAchievement).filter(UserAchievement.user_id == user.id).all()
    }
    result = []
    for a in all_ach:
        result.append({
            "id": a.id,
            "titulo": a.titulo,
            "descricao": a.descricao,
            "icone": a.icone,
            "xp_recompensa": a.xp_recompensa,
            "desbloqueada": a.id in unlocked,
            "data_desbloqueio": unlocked[a.id].isoformat() if a.id in unlocked else None,
        })
    # Desbloqueadas primeiro
    result.sort(key=lambda x: (not x["desbloqueada"], x["titulo"]))
    return {"achievements": result}
@app.get("/api/xp/history")
def api_xp_history(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logs = (
        db.query(XPLog)
        .filter(XPLog.user_id == user.id)
        .order_by(XPLog.created_at.desc())
        .limit(50)
        .all()
    )
    return {
        "logs": [
            {
                "quantidade": log.quantidade,
                "fonte": log.fonte,
                "descricao": log.descricao,
                "created_at": log.created_at.isoformat() if log.created_at else "",
            }
            for log in logs
        ]
    }
# ═════════════════════════════════════════════
# API: IA / RECOMENDAÇÕES
# ═════════════════════════════════════════════
@app.get("/api/ai/recommendations")
def api_ai_recommendations(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    recs = get_recommendations(db, user)
    return {"recommendations": recs}
@app.post("/api/ai/chat")
def api_ai_chat(
    data: dict,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    message = data.get("message", "")
    return get_chatbot_ai_response(db, user, message)
# ─────────────────────────────────────────────
# Run
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.app:app", host="0.0.0.0", port=8000, reload=True)
