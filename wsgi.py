"""
Arquivo WSGI para deployment da aplicação CriptoSinais
Este arquivo é o ponto de entrada para servidores WSGI como Gunicorn
"""

import os
import logging
import sys

# Configurar logging básico
logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('main')

# Tentar importar a aplicação completa (app.py)
try:
    logger.info("Tentando importar a aplicação completa (app.py)...")
    from app import app
    logger.info("Aplicação principal (app.py) importada com sucesso")
except Exception as e:
    # Em caso de erro, importe a aplicação minimalista
    logger.warning(f"Erro ao importar aplicação completa: {e}")
    logger.info("Importando aplicação minimalista (minimal_app.py)...")
    from minimal_app import app
    logger.info("Aplicação minimalista importada com sucesso")

# Verificar a porta para o servidor
port = int(os.environ.get("PORT", 8080))
logger.info(f"Configurado para usar a porta {port}")

# Disponibiliza o objeto 'app' para servidores WSGI
if __name__ == "__main__":
    logger.info(f"Iniciando servidor na porta {port}")
    app.run(host="0.0.0.0", port=port)