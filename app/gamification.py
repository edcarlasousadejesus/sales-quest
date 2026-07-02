"""
Sales Quest — Motor de Gamificação (XP, Níveis, Missões, Conquistas).
"""
import math
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import User, Sale, Mission, UserMission, Achievement, UserAchievement, XPLog
# ─────────────────────────────────────────────
# Sistema de Níveis
# ─────────────────────────────────────────────
LEVEL_TITLES = {
    1: "Iniciante",
    5: "Vendedor Bronze",
    10: "Vendedor Prata",
    15: "Vendedor Ouro",
    20: "Vendedor Platina",
    25: "Vendedor Diamante",
    30: "Mestre de Vendas",
    40: "Grão-Mestre",
    50: "Lenda das Vendas",
}
def xp_for_level(level: int) -> int:
    """Calcula o XP necessário para atingir um nível (curva exponencial)."""
    return int(100 * (level ** 1.5))
def calculate_level(xp_total: int) -> int:
    """Calcula o nível baseado no XP total."""
    level = 1
    while xp_for_level(level + 1) <= xp_total:
        level += 1
    return level
def get_level_title(level: int) -> str:
    """Retorna o título do nível."""
    title = "Iniciante"
    for lvl, name in sorted(LEVEL_TITLES.items()):
        if level >= lvl:
            title = name
    return title
def get_level_progress(xp_total: int, level: int) -> dict:
    """Retorna informações de progresso do nível atual."""
    current_xp_req = xp_for_level(level)
    next_xp_req = xp_for_level(level + 1)
    xp_in_level = xp_total - current_xp_req
    xp_needed = next_xp_req - current_xp_req
    percentual = min(100, max(0, (xp_in_level / xp_needed) * 100)) if xp_needed > 0 else 100
    return {
        "nivel": level,
        "titulo": get_level_title(level),
        "xp_total": xp_total,
        "xp_nivel_atual": current_xp_req,
        "xp_proximo_nivel": next_xp_req,
        "xp_no_nivel": max(0, xp_in_level),
        "xp_necessario": xp_needed,
        "percentual": round(percentual, 1),
    }
# ─────────────────────────────────────────────
# Sistema de XP
# ─────────────────────────────────────────────
def calculate_sale_xp(valor: float, quantidade: int) -> int:
    """Calcula o XP ganho por uma venda."""
    base_xp = max(10, int(valor * 0.1))
    quantity_bonus = (quantidade - 1) * 5 if quantidade > 1 else 0
    return base_xp + quantity_bonus
def grant_xp(db: Session, user: User, quantidade: int, fonte: str, descricao: str) -> dict:
    """Concede XP ao usuário, atualiza nível e registra no log."""
    old_level = user.nivel
    # Registra no log
    xp_log = XPLog(
        user_id=user.id,
        quantidade=quantidade,
        fonte=fonte,
        descricao=descricao,
    )
    db.add(xp_log)
    # Atualiza XP e nível
    user.xp_total += quantidade
    new_level = calculate_level(user.xp_total)
    user.nivel = new_level
    db.commit()
    level_up = new_level > old_level
    return {
        "xp_ganho": quantidade,
        "xp_total": user.xp_total,
        "nivel_anterior": old_level,
        "nivel_atual": new_level,
        "level_up": level_up,
        "titulo": get_level_title(new_level),
    }
# ─────────────────────────────────────────────
# Sistema de Missões
# ─────────────────────────────────────────────
def update_missions_progress(db: Session, user: User):
    """Atualiza o progresso de todas as missões ativas do usuário."""
    user_missions = (
        db.query(UserMission)
        .filter(UserMission.user_id == user.id, UserMission.completa == False)
        .all()
    )
    completed_missions = []
    for um in user_missions:
        mission = um.mission
        progress = 0
        if mission.tipo == "vendas_count":
            # Total de vendas do usuário
            progress = db.query(func.count(Sale.id)).filter(Sale.user_id == user.id).scalar() or 0
        elif mission.tipo == "vendas_valor":
            # Valor total de vendas do usuário
            progress = db.query(func.sum(Sale.valor * Sale.quantidade)).filter(
                Sale.user_id == user.id
            ).scalar() or 0
        elif mission.tipo == "vendas_semana":
            # Vendas na última semana
            week_ago = datetime.now(timezone.utc) - timedelta(days=7)
            progress = db.query(func.count(Sale.id)).filter(
                Sale.user_id == user.id,
                Sale.data_venda >= week_ago,
            ).scalar() or 0
        elif mission.tipo == "vendas_dia":
            # Vendas no dia atual
            today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            progress = db.query(func.count(Sale.id)).filter(
                Sale.user_id == user.id,
                Sale.data_venda >= today,
            ).scalar() or 0
        elif mission.tipo == "categorias":
            # Número de categorias diferentes
            progress = db.query(func.count(func.distinct(Sale.categoria))).filter(
                Sale.user_id == user.id
            ).scalar() or 0
        elif mission.tipo == "clientes":
            # Número de clientes cadastrados
            from models import Client
            progress = db.query(func.count(Client.id)).filter(
                Client.user_id == user.id, Client.ativo == True
            ).scalar() or 0
        um.progresso = progress
        # Verifica se completou
        if progress >= mission.meta_valor and not um.completa:
            um.completa = True
            um.data_conclusao = datetime.now(timezone.utc)
            # Concede XP da missão
            grant_xp(db, user, mission.xp_recompensa, "missao", f"Missão concluída: {mission.titulo}")
            completed_missions.append({
                "titulo": mission.titulo,
                "icone": mission.icone,
                "xp": mission.xp_recompensa,
            })
    db.commit()
    return completed_missions
def assign_missions(db: Session, user: User):
    """Atribui missões ativas ao usuário que ainda não foram atribuídas."""
    active_missions = db.query(Mission).filter(Mission.ativa == True).all()
    existing = {
        um.mission_id
        for um in db.query(UserMission).filter(UserMission.user_id == user.id).all()
    }
    for mission in active_missions:
        if mission.id not in existing:
            um = UserMission(
                user_id=user.id,
                mission_id=mission.id,
                progresso=0,
                completa=False,
            )
            db.add(um)
    db.commit()
# ─────────────────────────────────────────────
# Sistema de Conquistas
# ─────────────────────────────────────────────
def check_achievements(db: Session, user: User) -> list:
    """Verifica e desbloqueia conquistas elegíveis."""
    all_achievements = db.query(Achievement).all()
    unlocked_ids = {
        ua.achievement_id
        for ua in db.query(UserAchievement).filter(UserAchievement.user_id == user.id).all()
    }
    new_achievements = []
    for ach in all_achievements:
        if ach.id in unlocked_ids:
            continue
        earned = False
        if ach.criterio_tipo == "total_vendas":
            count = db.query(func.count(Sale.id)).filter(Sale.user_id == user.id).scalar() or 0
            earned = count >= ach.criterio_valor
        elif ach.criterio_tipo == "xp_total":
            earned = user.xp_total >= ach.criterio_valor
        elif ach.criterio_tipo == "nivel":
            earned = user.nivel >= ach.criterio_valor
        elif ach.criterio_tipo == "valor_venda":
            max_val = db.query(func.max(Sale.valor * Sale.quantidade)).filter(
                Sale.user_id == user.id
            ).scalar() or 0
            earned = max_val >= ach.criterio_valor
        elif ach.criterio_tipo == "total_clientes":
            from models import Client
            count = db.query(func.count(Client.id)).filter(
                Client.user_id == user.id, Client.ativo == True
            ).scalar() or 0
            earned = count >= ach.criterio_valor
        elif ach.criterio_tipo == "valor_total":
            total = db.query(func.sum(Sale.valor * Sale.quantidade)).filter(
                Sale.user_id == user.id
            ).scalar() or 0
            earned = total >= ach.criterio_valor
        if earned:
            ua = UserAchievement(
                user_id=user.id,
                achievement_id=ach.id,
            )
            db.add(ua)
            # XP bônus pela conquista
            if ach.xp_recompensa > 0:
                grant_xp(db, user, ach.xp_recompensa, "conquista", f"Conquista: {ach.titulo}")
            new_achievements.append({
                "titulo": ach.titulo,
                "icone": ach.icone,
                "descricao": ach.descricao,
                "xp": ach.xp_recompensa,
            })
    db.commit()
    return new_achievements
