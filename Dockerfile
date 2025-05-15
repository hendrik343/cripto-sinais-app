FROM python:3.11-slim

WORKDIR /app

# Instalar dependências de sistema
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    libpq-dev \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./

# Instalar as dependências Python
RUN pip install --no-cache-dir uv && \
    uv pip install -e .

# Copiar o código da aplicação
COPY . .

# Expor a porta
ENV PORT=3000
EXPOSE 3000

# Configurar timezone
ENV TZ=UTC

# Definir como não-root
RUN useradd -m appuser
USER appuser

# Executar o script de inicialização
CMD ["./run.sh"]