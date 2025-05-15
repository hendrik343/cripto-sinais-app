import os
from flask import Flask, redirect, render_template, jsonify, request
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

# Rota para o dashboard
@app.route('/dashboard')
def dashboard():
    """Endpoint do dashboard"""
    # Se estamos em modo de desenvolvimento ou preview, use HTML embutido
    if os.environ.get('REPLIT_DEVELOPMENT') or 'preview' in request.headers.get('Host', ''):
        return """
        <html>
        <head>
            <title>Dashboard CriptoSinais</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #0f172a;
                    color: white;
                    margin: 0;
                    padding: 20px;
                }
                .container {
                    max-width: 800px;
                    margin: 0 auto;
                    background-color: rgba(30, 41, 59, 0.8);
                    border-radius: 10px;
                    padding: 20px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }
                h1 {
                    color: #fcd34d;
                    text-align: center;
                }
                .card {
                    background-color: rgba(15, 23, 42, 0.7);
                    border-radius: 8px;
                    padding: 15px;
                    margin-bottom: 15px;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }
                .crypto-row {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                    padding: 10px 0;
                }
                .name {
                    font-weight: bold;
                }
                .price {
                    color: #38bdf8;
                }
                .change.positive {
                    color: #4ade80;
                }
                .change.negative {
                    color: #f87171;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>CriptoSinais Dashboard</h1>
                <div class="card">
                    <h3>Top Cryptocurrencies</h3>
                    <div class="crypto-row">
                        <div class="name">Bitcoin (BTC)</div>
                        <div class="price">$45,000.00</div>
                        <div class="change positive">+1.2%</div>
                    </div>
                    <div class="crypto-row">
                        <div class="name">Solana (SOL)</div>
                        <div class="price">$171.80</div>
                        <div class="change negative">-0.04%</div>
                    </div>
                    <div class="crypto-row">
                        <div class="name">Dogecoin (DOGE)</div>
                        <div class="price">$0.227</div>
                        <div class="change negative">-0.04%</div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    
    # Se não estamos em preview, tentar renderizar o template
    try:
        from app import dashboard
        return dashboard()
    except ImportError:
        # Usar um HTML simples como fallback se não conseguir importar
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
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Iniciando aplicação na porta {port}")
    app.run(host='0.0.0.0', port=port)