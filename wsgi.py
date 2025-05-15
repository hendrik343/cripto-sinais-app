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
try:
    # Tentar importar primeiro a aplicação simplificada
    logger.info("Tentando importar app_simples.py...")
    from app_simples import app
    logger.info("Aplicação app_simples.py importada com sucesso")
except Exception as e:
    logger.warning(f"Não foi possível importar app_simples.py: {e}")
    
    # Fallback para main.py
    logger.info("Tentando importar main.py...")
    from main import app
    logger.info("Aplicação main.py importada com sucesso")

# Ponto de entrada para servidores WSGI
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)