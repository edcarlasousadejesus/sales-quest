"""
Sales Quest — Dados Iniciais de Demonstração (Seed).
Popula o banco com vendedores, clientes, vendas, missões e conquistas.
"""
import os
import sys
import random
from datetime import datetime, timedelta, timezone
# Ajusta path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import init_db, SessionLocal
from models import User, Client, Sale, Mission, Achievement, UserMission
from auth import hash_password
from gamification import calculate_level, grant_xp, assign_missions
def seed():
    """Popula o banco com dados de demonstração."""
    init_db()
    db = SessionLocal()
    # Limpa dados existentes (para re-seed)
    for table in [UserMission, Sale, Client, User, Mission, Achievement]:
        db.query(table).delete()
    db.commit()
    print("🌱 Populando banco de dados...")
    # ─── Usuários (Vendedores) ───
    users_data = [
        {"nome": "Admin Sales", "email": "admin@salesquest.com", "senha": "admin123", "avatar": "👑", "cargo": "Gerente de Vendas", "xp": 5200},
        {"nome": "Maria Silva", "email": "maria@salesquest.com", "senha": "maria123", "avatar": "👩‍💼", "cargo": "Vendedora Sênior", "xp": 3100},
        {"nome": "João Santos", "email": "joao@salesquest.com", "senha": "joao123", "avatar": "👨‍💼", "cargo": "Vendedor", "xp": 1400},
    ]
    users = []
    for u in users_data:
        user = User(
            nome=u["nome"],
            email=u["email"],
            senha_hash=hash_password(u["senha"]),
            avatar=u["avatar"],
            cargo=u["cargo"],
            xp_total=u["xp"],
            nivel=calculate_level(u["xp"]),
        )
        db.add(user)
        db.flush()
        users.append(user)
        print(f"  ✅ Usuário: {u['nome']} ({u['email']}) — Nível {user.nivel}")
    # ─── Clientes ───
    clients_data = [
        {"nome": "TechCorp Ltda", "email": "contato@techcorp.com", "telefone": "(11) 99999-1234", "endereco": "Rua das Flores, 100 - São Paulo/SP"},
        {"nome": "Supermercado Bom Preço", "email": "compras@bompreco.com", "telefone": "(21) 98888-5678", "endereco": "Av. Brasil, 500 - Rio de Janeiro/RJ"},
        {"nome": "Farmácia Saúde+", "email": "farmacia@saudemais.com", "telefone": "(31) 97777-9012", "endereco": "Rua da Saúde, 200 - Belo Horizonte/MG"},
        {"nome": "Loja Mix Digital", "email": "vendas@mixdigital.com", "telefone": "(41) 96666-3456", "endereco": "Av. Tecnologia, 300 - Curitiba/PR"},
        {"nome": "Restaurante Sabor Real", "email": "gerencia@saborreal.com", "telefone": "(51) 95555-7890", "endereco": "Rua da Gastronomia, 50 - Porto Alegre/RS"},
        {"nome": "Auto Peças Express", "email": "pedidos@autoexpress.com", "telefone": "(85) 94444-1234", "endereco": "Av. Automotiva, 800 - Fortaleza/CE"},
        {"nome": "Construtora Horizonte", "email": "obras@horizonte.com", "telefone": "(71) 93333-5678", "endereco": "Rua dos Engenheiros, 120 - Salvador/BA"},
        {"nome": "Pet Shop Amigo Fiel", "email": "contato@amigofiel.com", "telefone": "(62) 92222-9012", "endereco": "Rua dos Animais, 75 - Goiânia/GO"},
        {"nome": "Escritório Advocacia Souza", "email": "admin@souzaadv.com", "telefone": "(61) 91111-3456", "endereco": "SQN 308, Bloco A - Brasília/DF"},
        {"nome": "Padaria Pão Quente", "email": "paoquente@email.com", "telefone": "(27) 90000-7890", "endereco": "Rua do Trigo, 30 - Vitória/ES"},
        {"nome": "Clínica Vida Nova", "email": "agendamento@vidanova.com", "telefone": "(48) 98765-4321", "endereco": "Av. Saúde, 400 - Florianópolis/SC"},
        {"nome": "Studio Beleza & Estilo", "email": "contato@belezaestilo.com", "telefone": "(92) 97654-3210", "endereco": "Rua da Moda, 55 - Manaus/AM"},
        {"nome": "Escola Futuro Brilhante", "email": "secretaria@futurobrilhante.edu", "telefone": "(91) 96543-2109", "endereco": "Av. Educação, 1000 - Belém/PA"},
        {"nome": "Distribuidora Norte Sul", "email": "vendas@nortesul.com", "telefone": "(84) 95432-1098", "endereco": "Rod. BR-101, KM 5 - Natal/RN"},
        {"nome": "Gráfica Print Master", "email": "orcamento@printmaster.com", "telefone": "(82) 94321-0987", "endereco": "Rua Gutenberg, 200 - Maceió/AL"},
    ]
    clients = []
    for i, c in enumerate(clients_data):
        # Distribui clientes entre os vendedores
        owner = users[i % len(users)]
        client = Client(
            user_id=owner.id,
            nome=c["nome"],
            email=c["email"],
            telefone=c["telefone"],
            endereco=c["endereco"],
            notas=f"Cliente cadastrado automaticamente (demo).",
        )
        db.add(client)
        db.flush()
        clients.append(client)
    print(f"  ✅ {len(clients)} clientes cadastrados")
    # ─── Vendas ───
    categorias = ["Eletrônicos", "Software", "Serviços", "Consultoria", "Hardware", "Suprimentos"]
    produtos = {
        "Eletrônicos": ["Notebook Dell", "Monitor LG 27\"", "Teclado Mecânico", "Mouse Gamer", "Webcam HD"],
        "Software": ["Licença Office 365", "Antivírus Kaspersky", "ERP Módulo Fiscal", "CRM Pro", "Backup Cloud"],
        "Serviços": ["Manutenção Mensal", "Suporte Técnico VIP", "Instalação de Rede", "Treinamento TI", "Consultoria SEO"],
        "Consultoria": ["Análise de Processos", "Planejamento Estratégico", "Auditoria Financeira", "Marketing Digital", "Gestão de Projetos"],
        "Hardware": ["Servidor Dell PowerEdge", "Switch 48 Portas", "Roteador WiFi 6", "No-Break 3KVA", "HD Externo 2TB"],
        "Suprimentos": ["Toner HP", "Papel A4 (cx)", "Cabo de Rede Cat6", "Pen Drive 64GB", "Pilhas Duracell"],
    }
    vendas_count = 0
    now = datetime.now(timezone.utc)
    for user in users:
        user_clients = [c for c in clients if c.user_id == user.id]
        num_vendas = random.randint(12, 25)
        for _ in range(num_vendas):
            cat = random.choice(categorias)
            prod = random.choice(produtos[cat])
            valor = round(random.uniform(50, 5000), 2)
            qtd = random.randint(1, 5)
            days_ago = random.randint(0, 30)
            data = now - timedelta(days=days_ago, hours=random.randint(0, 23))
            client = random.choice(user_clients) if user_clients else None
            sale = Sale(
                user_id=user.id,
                client_id=client.id if client else None,
                produto=prod,
                categoria=cat,
                valor=valor,
                quantidade=qtd,
                data_venda=data,
            )
            db.add(sale)
            vendas_count += 1
    db.commit()
    print(f"  ✅ {vendas_count} vendas registradas")
    # ─── Missões ───
    missions_data = [
        {"titulo": "Primeira Venda", "descricao": "Cadastre sua primeira venda no sistema", "icone": "⭐", "tipo": "vendas_count", "meta": 1, "xp": 50},
        {"titulo": "Vendedor Iniciante", "descricao": "Realize 5 vendas no total", "icone": "🎯", "tipo": "vendas_count", "meta": 5, "xp": 100},
        {"titulo": "Semana Forte", "descricao": "Faça 10 vendas em uma semana", "icone": "💪", "tipo": "vendas_semana", "meta": 10, "xp": 200},
        {"titulo": "Meta de R$5.000", "descricao": "Alcance R$5.000 em vendas totais", "icone": "💰", "tipo": "vendas_valor", "meta": 5000, "xp": 300},
        {"titulo": "Meta de R$20.000", "descricao": "Alcance R$20.000 em vendas totais", "icone": "💎", "tipo": "vendas_valor", "meta": 20000, "xp": 500},
        {"titulo": "Diversidade", "descricao": "Venda em 4 categorias diferentes", "icone": "🌈", "tipo": "categorias", "meta": 4, "xp": 150},
        {"titulo": "Carteira de Clientes", "descricao": "Cadastre 5 clientes", "icone": "📋", "tipo": "clientes", "meta": 5, "xp": 120},
        {"titulo": "Rede de Contatos", "descricao": "Cadastre 10 clientes", "icone": "🤝", "tipo": "clientes", "meta": 10, "xp": 250},
        {"titulo": "Vendedor Voraz", "descricao": "Realize 50 vendas no total", "icone": "🔥", "tipo": "vendas_count", "meta": 50, "xp": 400},
        {"titulo": "Centurião", "descricao": "Realize 100 vendas no total", "icone": "🏛️", "tipo": "vendas_count", "meta": 100, "xp": 800},
    ]
    for m in missions_data:
        mission = Mission(
            titulo=m["titulo"],
            descricao=m["descricao"],
            icone=m["icone"],
            tipo=m["tipo"],
            meta_valor=m["meta"],
            xp_recompensa=m["xp"],
            ativa=True,
        )
        db.add(mission)
    db.commit()
    print(f"  ✅ {len(missions_data)} missões criadas")
    # ─── Conquistas ───
    achievements_data = [
        {"titulo": "Primeira Estrela", "descricao": "Cadastrou sua primeira venda", "icone": "⭐", "tipo": "total_vendas", "valor": 1, "xp": 30},
        {"titulo": "Vendedor de Elite", "descricao": "25 vendas realizadas", "icone": "🏅", "tipo": "total_vendas", "valor": 25, "xp": 100},
        {"titulo": "Centurião", "descricao": "100 vendas realizadas", "icone": "💯", "tipo": "total_vendas", "valor": 100, "xp": 300},
        {"titulo": "Venda Diamante", "descricao": "Uma venda acima de R$5.000", "icone": "💎", "tipo": "valor_venda", "valor": 5000, "xp": 200},
        {"titulo": "Nível Bronze", "descricao": "Alcançou nível 5", "icone": "🥉", "tipo": "nivel", "valor": 5, "xp": 50},
        {"titulo": "Nível Prata", "descricao": "Alcançou nível 10", "icone": "🥈", "tipo": "nivel", "valor": 10, "xp": 100},
        {"titulo": "Nível Ouro", "descricao": "Alcançou nível 20", "icone": "🥇", "tipo": "nivel", "valor": 20, "xp": 200},
        {"titulo": "Milionário", "descricao": "R$50.000 em vendas totais", "icone": "🤑", "tipo": "valor_total", "valor": 50000, "xp": 500},
        {"titulo": "Rei dos Clientes", "descricao": "10 clientes cadastrados", "icone": "👑", "tipo": "total_clientes", "valor": 10, "xp": 150},
        {"titulo": "Mestre XP", "descricao": "Acumulou 5.000 XP", "icone": "🚀", "tipo": "xp_total", "valor": 5000, "xp": 100},
    ]
    for a in achievements_data:
        ach = Achievement(
            titulo=a["titulo"],
            descricao=a["descricao"],
            icone=a["icone"],
            criterio_tipo=a["tipo"],
            criterio_valor=a["valor"],
            xp_recompensa=a["xp"],
        )
        db.add(ach)
    db.commit()
    print(f"  ✅ {len(achievements_data)} conquistas criadas")
    # ─── Atribui missões aos usuários ───
    for user in users:
        assign_missions(db, user)
    print("  ✅ Missões atribuídas aos usuários")
    db.close()
    print("\n🎉 Banco de dados populado com sucesso!")
    print("─" * 40)
    print("📧 Login de demonstração:")
    print("   Email: admin@salesquest.com")
    print("   Senha: admin123")
    print("─" * 40)
if __name__ == "__main__":
    seed()
