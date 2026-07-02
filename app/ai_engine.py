"""
Sales Quest — Motor de IA para Recomendações Personalizadas.
Análise baseada em regras e estatísticas dos dados de vendas.
"""
import os
from openai import OpenAI
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from models import User, Sale, Client, UserMission
from gamification import get_level_title
def get_recommendations(db: Session, user: User) -> list:
    """Gera recomendações personalizadas baseadas nos dados do vendedor."""
    recommendations = []
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)
    two_weeks_ago = now - timedelta(days=14)
    month_ago = now - timedelta(days=30)
    # ─── Estatísticas básicas ───
    total_vendas = db.query(func.count(Sale.id)).filter(Sale.user_id == user.id).scalar() or 0
    total_clientes = db.query(func.count(Client.id)).filter(
        Client.user_id == user.id, Client.ativo == True
    ).scalar() or 0
    # ─── 1. Vendedor novo — dicas de boas-vindas ───
    if total_vendas == 0:
        recommendations.append({
            "icone": "🚀",
            "titulo": "Comece sua jornada!",
            "mensagem": "Cadastre seu primeiro cliente e registre sua primeira venda para começar a ganhar XP e subir no ranking!",
            "tipo": "motivacao",
        })
        return recommendations
    # ─── 2. Análise de tendência semanal ───
    vendas_semana_atual = db.query(func.sum(Sale.valor * Sale.quantidade)).filter(
        Sale.user_id == user.id,
        Sale.data_venda >= week_ago,
    ).scalar() or 0
    vendas_semana_anterior = db.query(func.sum(Sale.valor * Sale.quantidade)).filter(
        Sale.user_id == user.id,
        Sale.data_venda >= two_weeks_ago,
        Sale.data_venda < week_ago,
    ).scalar() or 0
    if vendas_semana_anterior > 0:
        variacao = ((vendas_semana_atual - vendas_semana_anterior) / vendas_semana_anterior) * 100
        if variacao > 10:
            recommendations.append({
                "icone": "📈",
                "titulo": "Tendência de alta!",
                "mensagem": f"Suas vendas cresceram {variacao:.0f}% esta semana comparado à semana anterior. Continue nesse ritmo!",
                "tipo": "motivacao",
            })
        elif variacao < -10:
            recommendations.append({
                "icone": "📉",
                "titulo": "Atenção com as vendas",
                "mensagem": f"Suas vendas caíram {abs(variacao):.0f}% esta semana. Tente entrar em contato com seus clientes e oferecer novos produtos!",
                "tipo": "alerta",
            })
    # ─── 3. Análise de ticket médio ───
    ticket_medio = db.query(func.avg(Sale.valor * Sale.quantidade)).filter(
        Sale.user_id == user.id,
    ).scalar() or 0
    if ticket_medio > 0:
        meta_ticket = ticket_medio * 1.3
        recommendations.append({
            "icone": "💰",
            "titulo": "Aumente seu ticket médio",
            "mensagem": f"Seu ticket médio é R${ticket_medio:,.2f}. Tente fechar vendas acima de R${meta_ticket:,.2f} para acelerar seus ganhos de XP!",
            "tipo": "dica",
        })
    # ─── 4. Análise de categorias ───
    categorias = (
        db.query(Sale.categoria, func.count(Sale.id).label("total"))
        .filter(Sale.user_id == user.id)
        .group_by(Sale.categoria)
        .order_by(func.count(Sale.id).desc())
        .all()
    )
    if len(categorias) >= 2:
        top_cat = categorias[0]
        percentual_top = (top_cat.total / total_vendas) * 100
        if percentual_top > 60:
            recommendations.append({
                "icone": "🎯",
                "titulo": "Diversifique suas categorias",
                "mensagem": f"'{top_cat.categoria}' representa {percentual_top:.0f}% das suas vendas. Tente explorar outras categorias para não depender de um único segmento!",
                "tipo": "dica",
            })
    elif len(categorias) == 1:
        recommendations.append({
            "icone": "🌈",
            "titulo": "Explore novas categorias",
            "mensagem": f"Todas as suas vendas são da categoria '{categorias[0].categoria}'. Diversifique para completar missões e ganhar mais XP!",
            "tipo": "dica",
        })
    # ─── 5. Clientes sem vendas recentes ───
    if total_clientes > 0:
        clientes_ativos_recentes = db.query(func.count(distinct(Sale.client_id))).filter(
            Sale.user_id == user.id,
            Sale.data_venda >= month_ago,
            Sale.client_id.isnot(None),
        ).scalar() or 0
        inativos = total_clientes - clientes_ativos_recentes
        if inativos > 0:
            recommendations.append({
                "icone": "📞",
                "titulo": "Reative seus clientes",
                "mensagem": f"Você tem {inativos} cliente(s) sem compras no último mês. Entre em contato e ofereça novidades!",
                "tipo": "dica",
            })
    # ─── 6. Progresso no ranking ───
    users_above = db.query(func.count(User.id)).filter(
        User.xp_total > user.xp_total,
        User.id != user.id,
    ).scalar() or 0
    posicao = users_above + 1
    if posicao > 1:
        user_acima = db.query(User).filter(
            User.xp_total > user.xp_total
        ).order_by(User.xp_total.asc()).first()
        if user_acima:
            diff = user_acima.xp_total - user.xp_total
            recommendations.append({
                "icone": "🏆",
                "titulo": f"Você está na {posicao}ª posição",
                "mensagem": f"Faltam apenas {diff} XP para ultrapassar {user_acima.nome} e subir no ranking!",
                "tipo": "meta",
            })
    # ─── 7. Missões quase completas ───
    quase_prontas = (
        db.query(UserMission)
        .filter(
            UserMission.user_id == user.id,
            UserMission.completa == False,
        )
        .all()
    )
    for um in quase_prontas:
        if um.mission and um.mission.meta_valor > 0:
            pct = (um.progresso / um.mission.meta_valor) * 100
            if 70 <= pct < 100:
                falta = um.mission.meta_valor - um.progresso
                recommendations.append({
                    "icone": "🔥",
                    "titulo": f"Missão quase concluída!",
                    "mensagem": f"'{um.mission.titulo}' está {pct:.0f}% completa. Faltam apenas {falta:.0f} para ganhar {um.mission.xp_recompensa} XP!",
                    "tipo": "meta",
                })
    # ─── 8. Motivação por nível ───
    from gamification import xp_for_level
    next_level_xp = xp_for_level(user.nivel + 1)
    xp_faltando = next_level_xp - user.xp_total
    if xp_faltando > 0 and xp_faltando < 100:
        recommendations.append({
            "icone": "⬆️",
            "titulo": "Próximo nível à vista!",
            "mensagem": f"Faltam apenas {xp_faltando} XP para você alcançar o nível {user.nivel + 1} ({get_level_title(user.nivel + 1)})!",
            "tipo": "motivacao",
        })
    # Limita a 5 recomendações
    return recommendations[:5]


def get_chatbot_ai_response(db: Session, user: User, message: str) -> dict:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    total_vendas = db.query(func.count(Sale.id)).filter(Sale.user_id == user.id).scalar() or 0
    total_clientes = db.query(func.count(Client.id)).filter(Client.user_id == user.id,
                                                            Client.ativo == True).scalar() or 0
    valor_total = db.query(func.sum(Sale.valor * Sale.quantidade)).filter(Sale.user_id == user.id).scalar() or 0

    contexto = f"""
    Usuário: {user.nome}
    Nível: {user.nivel}
    XP: {user.xp_total}
    Total de vendas: {total_vendas}
    Clientes ativos: {total_clientes}
    Valor total vendido: R$ {valor_total:.2f}
    """

    resposta = client.responses.create(
        model="gpt-4.1-mini",
        input=f"""
        Você é o Assistente IA do Sales Quest.
        Responda em português do Brasil.
        Seja breve, prático e focado em vendas.

        Dados do usuário:
        {contexto}

        Pergunta do usuário:
        {message}
        """
    )

    return {"resposta": resposta.output_text}
