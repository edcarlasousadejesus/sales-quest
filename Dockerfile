FROM python:3.11-slim

# Impede que o Python grave arquivos .pyc no disco
ENV PYTHONDONTWRITEBYTECODE 1
# Garante que a saída do Python seja enviada diretamente para o terminal (logs)
ENV PYTHONUNBUFFERED 1

# Diretório de trabalho
WORKDIR /project

# Instala dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências do Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia a aplicação
COPY app/ ./app/

# Expõe a porta 8000
EXPOSE 8000

# Variáveis de ambiente padrão
ENV PORT=8000

# Executa o servidor Uvicorn
CMD ["sh", "-c", "uvicorn app.app:app --host 0.0.0.0 --port ${PORT}"]
