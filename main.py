import os
from flask import Flask, redirect, render_template, jsonify
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cria a aplicação Flask
app = Flask(__name__)

# Configuração do app
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Rota básica para health checks
@app.route('/')
def health_check_root():
    """Endpoint para verificações de saúde (health checks)"""
    return jsonify({
        "status": "online",
        "message": "API online!"
    })

# Rota específica para o preview do browser
@app.route('/preview')
def preview():
    """Rota especial para acessar a interface via browser"""
    return redirect('/dashboard')

# Rota alternativa para o dashboard
@app.route('/dashboard')
def dashboard_redirect():
    """Redireciona para o dashboard completo"""
    try:
        from app import dashboard
        return dashboard()
    except ImportError:
        return redirect('/health')

# Endpoint de status da API
@app.route('/health')
def health():
    """Endpoint para verificação de saúde da API"""
    return jsonify({
        "status": "online",
        "version": "1.0.0",
        "message": "API de monitoramento de criptomoedas está funcionando corretamente"
    })

# Tentativa de importar as rotas da aplicação principal
try:
    logger.info("Tentando importar a aplicação completa (app.py)...")
    # Importar usando um módulo auxiliar para evitar conflitos
    import app as app_module
    # Registrar blueprint ou adicionar rotas se necessário
    logger.info("Aplicação principal (app.py) importada com sucesso")
except Exception as e:
    logger.error(f"Erro ao importar app.py: {e}")
    # Continua com a aplicação mínima definida acima

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    logger.info(f"Iniciando aplicação na porta {port}")
    app.run(host='0.0.0.0', port=port)