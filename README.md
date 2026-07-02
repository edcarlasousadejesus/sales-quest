# 🚀 Sales Quest

Sistema web desenvolvido para gerenciamento de vendas com gamificação e Inteligência Artificial, criado como projeto acadêmico do curso de Tecnologia em Inteligência Artificial.

## 📖 Sobre o Projeto

O **Sales Quest** é uma plataforma que auxilia vendedores no gerenciamento de clientes, vendas, ranking e metas, utilizando técnicas de gamificação para incentivar o desempenho.

Além disso, o sistema possui um módulo de Inteligência Artificial baseado em análise de dados, capaz de gerar recomendações personalizadas para auxiliar o vendedor na tomada de decisões.

---

## 🎯 Objetivos

- Gerenciar clientes
- Registrar vendas
- Acompanhar indicadores de desempenho
- Incentivar usuários através de gamificação
- Gerar recomendações inteligentes utilizando IA
- Disponibilizar a aplicação na web

---

## ✨ Funcionalidades

✅ Cadastro de usuários

✅ Login com autenticação

✅ Cadastro de clientes

✅ Cadastro de vendas

✅ Dashboard com indicadores

✅ Sistema de níveis (XP)

✅ Ranking de vendedores

✅ Missões

✅ Conquistas

✅ Recomendações inteligentes baseadas em IA

✅ Interface moderna e responsiva

---

## 🤖 Inteligência Artificial

O projeto possui um módulo de IA responsável por analisar os dados do vendedor e gerar recomendações personalizadas.

A IA é capaz de analisar:

- Evolução das vendas
- Ticket médio
- Categorias mais vendidas
- Clientes inativos
- Ranking
- Missões quase concluídas
- Evolução de nível (XP)

Com essas informações, o sistema gera sugestões para melhorar o desempenho do vendedor.

---

## 🛠 Tecnologias Utilizadas

### Backend

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Jinja2

### Front-end

- HTML5
- CSS3
- JavaScript

### Banco de Dados

- SQLite

### Ferramentas

- Git
- GitHub
- Render
- PyCharm

---

## 📂 Estrutura do Projeto

```
Sales Quest
│
├── app/
│   ├── app.py
│   ├── ai_engine.py
│   ├── auth.py
│   ├── database.py
│   ├── gamification.py
│   ├── models.py
│   ├── schemas.py
│   ├── templates/
│   ├── static/
│   └── sales_quest.db
│
├── requirements.txt
└── README.md
```

---

## 🚀 Como Executar

### Clone o projeto

```bash
git clone https://github.com/edcarlasousadejesus/sales-quest.git
```

### Entre na pasta

```bash
cd sales-quest
```

### Crie o ambiente virtual

```bash
python -m venv .venv
```

### Ative o ambiente virtual

Windows

```bash
.venv\Scripts\activate
```

Linux/Mac

```bash
source .venv/bin/activate
```

### Instale as dependências

```bash
pip install -r requirements.txt
```

### Execute

```bash
uvicorn app.app:app
```

Abra no navegador:

```
http://127.0.0.1:8000
```

---

## 🌐 Projeto Publicado

A aplicação encontra-se publicada na plataforma Render.

---

## 📷 Telas do Sistema

- Login
- Cadastro
- Dashboard
- Clientes
- Vendas
- Ranking
- Missões
- Conquistas

*(Em breve serão adicionadas capturas de tela do sistema.)*

---

## 💡 Melhorias Futuras

- Chatbot com Inteligência Artificial
- Dashboard com gráficos avançados
- Notificações em tempo real
- Banco de dados PostgreSQL
- API REST completa
- Aplicativo Mobile
- Relatórios em PDF
- Exportação para Excel

---

## 👩‍💻 Desenvolvido por

**Edcarla Sousa de Jesus**

Curso Superior de Tecnologia em Inteligência Artificial

GitHub:
https://github.com/edcarlasousadejesus

---

## 📄 Licença

Projeto desenvolvido para fins acadêmicos.