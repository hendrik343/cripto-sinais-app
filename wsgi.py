"""
Arquivo WSGI para deployment da aplicação CriptoSinais
Este arquivo é o ponto de entrada para servidores WSGI como Gunicorn
"""
import os
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Registra a porta que será utilizada
port = int(os.environ.get("PORT", 3000))
logger.info(f"Configurando aplicação para usar a porta {port}")

# Importa e configura a aplicação Flask
from main import app

# Ponto de entrada para servidores WSGI
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)