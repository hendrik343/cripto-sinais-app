import os
import json
import requests
import time
from datetime import datetime
from flask import Flask, request, redirect, jsonify

app = Flask(__name__)

# Configurações do Telegram
TELEGRAM_BOT_TOKEN = "7773905776:AAEohw7-YUXf0RzpR7_QFfWK5_YZ_CATPi8"
TELEGRAM_CHAT_ID = None  # Será definido quando o usuário enviar uma mensagem

# Lista de criptomoedas para monitorar
MOEDAS = ["bitcoin", "ethereum", "solana", "dogecoin", "shiba-inu", "floki", "bonk", "xrp", "cardano", "avalanche-2", "chainlink", "matic-network", "arbitrum", "optimism", "render-token", "the-graph", "aptos", "internet-computer", "sei-network", "starknet"]

# Cache de preços para evitar muitas chamadas à API
preco_cache = {}

def obter_preco_atual(coin_id):
    """Obtém o preço atual de uma criptomoeda da API CoinGecko"""
    # Verificar se temos um preço em cache recente (menos de 1 minuto)
    if coin_id in preco_cache and time.time() - preco_cache[coin_id]['timestamp'] < 60:
        return preco_cache[coin_id]['price']
        
    try:
        # URL da API do CoinGecko para obter o preço da moeda em USD
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true"
        
        # Fazemos uma requisição GET para a API
        response = requests.get(url, timeout=5)
        
        # Verificamos se a requisição foi bem-sucedida (código 200)
        if response.status_code == 200:
            data = response.json()
            if coin_id in data:
                price = data[coin_id]['usd']
                change_24h = data[coin_id].get('usd_24h_change', 0)
                
                # Armazenar no cache
                preco_cache[coin_id] = {
                    'price': price,
                    'change_24h': change_24h,
                    'timestamp': time.time()
                }
                
                return price
    except Exception as e:
        print(f"Erro ao obter preço de {coin_id}: {e}")
    
    return None

def obter_variacao_24h(coin_id):
    """Obtém a variação de preço em 24h"""
    if coin_id in preco_cache and 'change_24h' in preco_cache[coin_id]:
        return preco_cache[coin_id]['change_24h']
    
    # Se não estiver no cache, tenta obter novamente
    obter_preco_atual(coin_id)
    
    if coin_id in preco_cache and 'change_24h' in preco_cache[coin_id]:
        return preco_cache[coin_id]['change_24h']
    
    return 0

def enviar_mensagem_telegram(mensagem):
    """Envia uma mensagem para o chat do Telegram"""
    if not TELEGRAM_CHAT_ID:
        return False
        
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": mensagem,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, data=data, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"Erro ao enviar mensagem para o Telegram: {e}")
        return False

def formatar_preco(price):
    """Formata o preço para exibição de acordo com sua magnitude"""
    if price is None:
        return "N/A"
        
    if price < 0.0001:
        return f"${price:.8f}"
    elif price < 0.01:
        return f"${price:.6f}"
    elif price < 1:
        return f"${price:.4f}"
    elif price < 10:
        return f"${price:.2f}"
    else:
        return f"${price:.2f}"

def gerar_recomendacao(variacao):
    """Gera uma recomendação simples com base na variação de preço"""
    if variacao is None:
        return "AGUARDAR"
        
    if variacao > 5:
        return "VENDER"
    elif variacao < -5:
        return "COMPRAR"
    else:
        return "AGUARDAR"

@app.route('/api/prices')
def api_prices():
    """API para obter os preços atuais das criptomoedas"""
    precos = {}
    
    # Limitar as moedas para as primeiras 5 para não sobrecarregar a API
    moedas_para_consultar = MOEDAS[:8]
    
    for moeda in moedas_para_consultar:
        price = obter_preco_atual(moeda)
        variation = obter_variacao_24h(moeda)
        
        # Símbolos para exibição amigável
        symbols = {
            "bitcoin": "BTC",
            "ethereum": "ETH",
            "solana": "SOL",
            "dogecoin": "DOGE",
            "shiba-inu": "SHIB",
            "floki": "FLOKI",
            "bonk": "BONK",
            "xrp": "XRP",
            "cardano": "ADA",
            "avalanche-2": "AVAX",
            "chainlink": "LINK",
            "matic-network": "MATIC",
            "arbitrum": "ARB",
            "optimism": "OP",
            "render-token": "RNDR",
            "the-graph": "GRT",
            "aptos": "APT",
            "internet-computer": "ICP",
            "sei-network": "SEI",
            "starknet": "STRK",
        }
        
        symbol = symbols.get(moeda, moeda.upper())
        
        precos[moeda] = {
            "symbol": symbol,
            "price": price,
            "price_formatted": formatar_preco(price),
            "change_24h": variation,
            "recommendation": gerar_recomendacao(variation)
        }
    
    return jsonify(precos)

@app.route('/telegram-webhook', methods=['POST'])
def telegram_webhook():
    """Webhook para receber mensagens do Telegram"""
    global TELEGRAM_CHAT_ID
    
    try:
        data = request.get_json()
        if 'message' in data and 'chat' in data['message']:
            TELEGRAM_CHAT_ID = data['message']['chat']['id']
            
            # Enviar mensagem de boas-vindas
            mensagem = (
                "🚀 *CriptoSinais Bot* 🚀\n\n"
                "Olá! Você agora está conectado ao bot CriptoSinais.\n"
                "Você receberá alertas sobre movimentações significativas de criptomoedas.\n\n"
                "Para ver os preços atuais, digite /precos\n"
                "Para configurar alertas, digite /alertas"
            )
            enviar_mensagem_telegram(mensagem)
            
            # Se a mensagem contém texto, verificar comandos
            if 'text' in data['message']:
                texto = data['message']['text']
                
                if texto == '/precos':
                    # Buscar preços e enviar resposta
                    moedas_principais = ["bitcoin", "ethereum", "solana", "dogecoin", "shiba-inu"]
                    mensagem = "💰 *Preços Atuais* 💰\n\n"
                    
                    for moeda in moedas_principais:
                        preco = obter_preco_atual(moeda)
                        variacao = obter_variacao_24h(moeda)
                        
                        if preco:
                            preco_formatado = formatar_preco(preco)
                            simbolo = moeda.upper()
                            if moeda == 'shiba-inu':
                                simbolo = 'SHIB'
                            
                            emoji = "🟢" if variacao > 0 else "🔴"
                            mensagem += f"{emoji} *{simbolo}*: {preco_formatado} ({variacao:.2f}%)\n"
                    
                    mensagem += "\nÚltima atualização: " + datetime.now().strftime("%H:%M:%S")
                    enviar_mensagem_telegram(mensagem)
        
        return jsonify({"status": "success"})
    
    except Exception as e:
        print(f"Erro no webhook do Telegram: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/send-telegram-update', methods=['GET'])
def send_telegram_update():
    """Endpoint para forçar o envio de uma atualização para o Telegram"""
    if not TELEGRAM_CHAT_ID:
        return jsonify({"status": "error", "message": "TELEGRAM_CHAT_ID não definido"})
    
    try:
        moedas_principals = ["bitcoin", "ethereum", "solana", "dogecoin", "shiba-inu", "floki"]
        
        mensagem = "📊 *Atualização de Preços* 📊\n\n"
        
        for moeda in moedas_principals:
            preco = obter_preco_atual(moeda)
            variacao = obter_variacao_24h(moeda)
            
            if preco:
                preco_formatado = formatar_preco(preco)
                simbolo = moeda.upper()
                if moeda == 'shiba-inu':
                    simbolo = 'SHIB'
                
                recomendacao = gerar_recomendacao(variacao)
                emoji_variacao = "🟢" if variacao > 0 else "🔴"
                emoji_recomendacao = "⏳" if recomendacao == "AGUARDAR" else "💰" if recomendacao == "COMPRAR" else "💵"
                
                mensagem += f"{emoji_variacao} *{simbolo}*: {preco_formatado} ({variacao:.2f}%)\n"
                mensagem += f"   {emoji_recomendacao} *{recomendacao}*\n\n"
        
        mensagem += f"⏰ _Atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}_"
        
        success = enviar_mensagem_telegram(mensagem)
        
        if success:
            return jsonify({"status": "success", "message": "Mensagem enviada com sucesso"})
        else:
            return jsonify({"status": "error", "message": "Erro ao enviar mensagem"})
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/')
def index():
    # Pré-carregar dados da API
    try:
        for moeda in MOEDAS[:5]:
            obter_preco_atual(moeda)
    except Exception as e:
        print(f"Erro ao pré-carregar dados: {e}")
    
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CriptoSinais Futuristic Dashboard</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');
            
            :root {
                --neon-purple: #8b5cf6;
                --neon-blue: #3b82f6;
                --neon-green: #10b981;
                --neon-pink: #ec4899;
                --neon-text: #f0abfc;
                --bg-dark: #030712;
                --bg-panel: rgba(15, 23, 42, 0.7);
                --border-glow: 0 0 10px var(--neon-purple), 0 0 20px rgba(139, 92, 246, 0.3);
            }
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Rajdhani', sans-serif;
                background-color: var(--bg-dark);
                color: #e2e8f0;
                background-image: 
                    linear-gradient(rgba(3, 7, 18, 0.7), rgba(3, 7, 18, 0.9)),
                    url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiB2aWV3Qm94PSIwIDAgMjAwIDIwMCI+CiAgPGcgZmlsbD0iIzFhMWQyZCIgZmlsbC1vcGFjaXR5PSIwLjEiPgogICAgPHBhdGggZD0iTTQwIDEwMHMxIDAgMSAxdjEwMHMwIDEtMSAxaC00MHMtMS0xLTEtdi0xMDBzMC0xIDEtMXoiLz4KICAgIDxwYXRoIGQ9Ik0xNDAgMTAwczEgMCAxIDF2MTAwczAgMS0xIDFoLTQwcy0xLTEtMS0xdi0xMDBzMC0xIDEtMXoiLz4KICAgIDxwYXRoIGQ9Ik04MCAyMDBzMSAwIDEgMXYxMDBzMCAxLTEgMWgtNDBzLTEtMS0xLTF2LTEwMHMwLTEgMS0xeiIvPgogICAgPHBhdGggZD0iTTE4MCAyMDBzMSAwIDEgMXYxMDBzMCAxLTEgMWgtNDBzLTEtMS0xLTF2LTEwMHMwLTEgMS0xeiIvPgogIDwvZz4KPC9zdmc+');
                min-height: 100vh;
            }
            
            .page-wrapper {
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                overflow-x: hidden;
            }
            
            header {
                background: rgba(15, 23, 42, 0.9);
                padding: 1rem 2rem;
                backdrop-filter: blur(10px);
                border-bottom: 1px solid rgba(139, 92, 246, 0.3);
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
                position: relative;
                z-index: 100;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .logo {
                font-family: 'Orbitron', sans-serif;
                font-weight: 700;
                font-size: 1.8rem;
                color: white;
                text-transform: uppercase;
                letter-spacing: 2px;
                position: relative;
                text-shadow: 0 0 10px rgba(139, 92, 246, 0.7);
            }
            
            .logo::before {
                content: '';
                position: absolute;
                width: 100%;
                height: 4px;
                background: linear-gradient(90deg, var(--neon-purple), var(--neon-pink));
                bottom: -8px;
                left: 0;
                border-radius: 2px;
            }
            
            .main-container {
                flex: 1;
                padding: 2rem;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            
            .dashboard {
                max-width: 1200px;
                width: 100%;
                background: rgba(15, 23, 42, 0.6);
                backdrop-filter: blur(10px);
                border-radius: 12px;
                padding: 2rem;
                border: 1px solid rgba(139, 92, 246, 0.2);
                box-shadow: var(--border-glow);
                display: grid;
                grid-template-columns: 1fr;
                gap: 2rem;
                position: relative;
                overflow: hidden;
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 1.5rem;
                margin-bottom: 1rem;
            }
            
            .stat-card {
                background: var(--bg-panel);
                border-radius: 10px;
                padding: 1.5rem;
                border: 1px solid rgba(255, 255, 255, 0.1);
                position: relative;
                overflow: hidden;
                transition: all 0.3s ease;
            }
            
            .stat-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 0 15px rgba(139, 92, 246, 0.5);
            }
            
            .stat-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 4px;
                height: 100%;
                background: linear-gradient(0deg, var(--neon-purple), var(--neon-blue));
                border-radius: 4px 0 0 4px;
            }
            
            .stat-title {
                font-size: 0.9rem;
                color: var(--neon-text);
                margin-bottom: 0.5rem;
                font-weight: 500;
                letter-spacing: 1px;
                text-transform: uppercase;
            }
            
            .stat-value {
                font-size: 1.8rem;
                font-weight: 700;
                margin-bottom: 0.25rem;
                font-family: 'Orbitron', sans-serif;
            }
            
            .stat-subtitle {
                font-size: 0.9rem;
                color: #94a3b8;
            }
            
            .crypto-table-container {
                background: var(--bg-panel);
                border-radius: 10px;
                padding: 1.5rem;
                border: 1px solid rgba(255, 255, 255, 0.1);
                overflow: hidden;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
                position: relative;
            }
            
            .crypto-table-container::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 4px;
                background: linear-gradient(90deg, var(--neon-blue), var(--neon-purple), var(--neon-pink));
                border-radius: 4px 4px 0 0;
            }
            
            .table-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1.5rem;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .table-title {
                font-family: 'Orbitron', sans-serif;
                font-size: 1.2rem;
                font-weight: 700;
                color: white;
                letter-spacing: 1px;
            }
            
            .crypto-table {
                width: 100%;
                border-collapse: collapse;
            }
            
            .crypto-table th {
                text-align: left;
                padding: 1rem 0.5rem;
                color: var(--neon-text);
                font-weight: 600;
                letter-spacing: 1px;
                font-size: 0.9rem;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .crypto-table td {
                padding: 1rem 0.5rem;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }
            
            .crypto-table tr:last-child td {
                border-bottom: none;
            }
            
            .crypto-table tr {
                transition: background-color 0.3s ease;
            }
            
            .crypto-table tr:hover {
                background-color: rgba(255, 255, 255, 0.05);
            }
            
            .coin-cell {
                display: flex;
                align-items: center;
                gap: 0.75rem;
            }
            
            .coin-name {
                font-weight: 600;
            }
            
            .coin-symbol {
                color: #94a3b8;
                font-size: 0.9rem;
            }
            
            .price {
                font-family: 'Orbitron', sans-serif;
                font-weight: 700;
                color: var(--neon-blue);
            }
            
            .positive {
                color: var(--neon-green);
                display: flex;
                align-items: center;
                gap: 0.25rem;
                font-weight: 600;
            }
            
            .negative {
                color: var(--neon-pink);
                display: flex;
                align-items: center;
                gap: 0.25rem;
                font-weight: 600;
            }
            
            .badge {
                background-color: var(--neon-purple);
                color: white;
                padding: 0.25rem 0.5rem;
                border-radius: 4px;
                font-size: 0.75rem;
                font-weight: 600;
                box-shadow: 0 0 8px rgba(139, 92, 246, 0.5);
                margin-left: 0.5rem;
            }
            
            .action-btn {
                background: linear-gradient(135deg, var(--neon-blue), var(--neon-purple));
                color: white;
                border: none;
                padding: 0.5rem 1rem;
                border-radius: 6px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                font-family: 'Rajdhani', sans-serif;
                text-transform: uppercase;
                letter-spacing: 1px;
                font-size: 0.9rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
                box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
            }
            
            .action-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 0 15px rgba(59, 130, 246, 0.7);
            }
            
            .updated-time {
                margin-top: 2rem;
                font-size: 0.9rem;
                color: #94a3b8;
                text-align: center;
                font-family: 'Orbitron', sans-serif;
                letter-spacing: 1px;
            }
            
            .neon-glow {
                position: absolute;
                width: 300px;
                height: 300px;
                border-radius: 50%;
                background: radial-gradient(circle, rgba(139, 92, 246, 0.2) 0%, rgba(59, 130, 246, 0.1) 40%, transparent 70%);
                pointer-events: none;
                z-index: -1;
            }
            
            .glow-1 {
                top: -100px;
                right: -100px;
            }
            
            .glow-2 {
                bottom: -150px;
                left: -100px;
                background: radial-gradient(circle, rgba(236, 72, 153, 0.2) 0%, rgba(236, 72, 153, 0.1) 40%, transparent 70%);
            }
            
            .cyber-circuit {
                position: absolute;
                width: 100%;
                height: 100%;
                top: 0;
                left: 0;
                pointer-events: none;
                z-index: -1;
                opacity: 0.1;
                background-image: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiPgogIDxwYXR0ZXJuIGlkPSJwYXR0ZXJuIiB4PSIwIiB5PSIwIiB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHBhdHRlcm5Vbml0cz0idXNlclNwYWNlT25Vc2UiIHBhdHRlcm5UcmFuc2Zvcm09InJvdGF0ZSgzMCkiPgogICAgPGxpbmUgeDE9IjAiIHkxPSIwIiB4Mj0iNDAiIHkyPSI0MCIgc3Ryb2tlPSIjOGI1Y2Y2IiBzdHJva2Utd2lkdGg9IjEiLz4KICAgIDxsaW5lIHgxPSIwIiB5MT0iNDAiIHgyPSI0MCIgeTI9IjAiIHN0cm9rZT0iIzNiODJmNiIgc3Ryb2tlLXdpZHRoPSIwLjUiLz4KICA8L3BhdHRlcm4+CiAgPHJlY3QgeD0iMCIgeT0iMCIgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0idXJsKCNwYXR0ZXJuKSIvPgo8L3N2Zz4=');
            }
            
            .menu {
                display: flex;
                gap: 1.5rem;
            }
            
            .menu-item {
                color: white;
                text-decoration: none;
                font-weight: 600;
                font-size: 1rem;
                letter-spacing: 1px;
                transition: all 0.3s ease;
                padding: 0.5rem 1rem;
                border-radius: 4px;
                text-transform: uppercase;
            }
            
            .menu-item:hover {
                color: var(--neon-purple);
                background: rgba(139, 92, 246, 0.1);
            }
            
            .premium-btn {
                background: linear-gradient(135deg, var(--neon-purple), var(--neon-pink));
                color: white;
                padding: 0.5rem 1.25rem;
                border-radius: 6px;
                font-weight: 600;
                box-shadow: 0 0 10px rgba(139, 92, 246, 0.5);
            }
            
            .premium-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 0 15px rgba(139, 92, 246, 0.7);
                color: white;
                background: linear-gradient(135deg, var(--neon-pink), var(--neon-purple));
            }
            
            @keyframes pulse {
                0% { opacity: 0.8; }
                50% { opacity: 1; }
                100% { opacity: 0.8; }
            }
            
            .status-indicator {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                font-size: 0.9rem;
                color: #94a3b8;
                font-family: 'Orbitron', sans-serif;
            }
            
            .status-dot {
                width: 10px;
                height: 10px;
                border-radius: 50%;
                background-color: var(--neon-green);
                animation: pulse 2s infinite;
            }
            
            @media (max-width: 768px) {
                .stats-grid {
                    grid-template-columns: 1fr;
                }
                
                .dashboard {
                    padding: 1.5rem;
                }
                
                .menu {
                    display: none;
                }
            }
        </style>
    </head>
    <body>
        <div class="page-wrapper">
            <header>
                <div class="logo">CriptoSinais</div>
                <div class="menu">
                    <a href="/" class="menu-item">Dashboard</a>
                    <a href="/dashboard" class="menu-item">Análise</a>
                    <a href="/premium" class="menu-item premium-btn">Premium</a>
                </div>
            </header>
            
            <div class="main-container">
                <div class="dashboard">
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-title">Total monitorado</div>
                            <div class="stat-value">18</div>
                            <div class="stat-subtitle">Criptomoedas</div>
                        </div>
                        
                        <div class="stat-card">
                            <div class="stat-title">Maior alta 24h</div>
                            <div class="stat-value">+1.2%</div>
                            <div class="stat-subtitle">Bitcoin (BTC)</div>
                        </div>
                        
                        <div class="stat-card">
                            <div class="stat-title">Maior queda 24h</div>
                            <div class="stat-value">-0.72%</div>
                            <div class="stat-subtitle">Floki (FLOKI)</div>
                        </div>
                        
                        <div class="stat-card">
                            <div class="stat-title">Status</div>
                            <div class="stat-value">
                                <div class="status-indicator">
                                    <div class="status-dot"></div> 
                                    Online
                                </div>
                            </div>
                            <div class="stat-subtitle">Monitoramento em tempo real</div>
                        </div>
                    </div>
                    
                    <div class="crypto-table-container">
                        <div class="table-header">
                            <div class="table-title">TOP CRIPTOMOEDAS</div>
                            <button class="action-btn">
                                <i class="fas fa-sync-alt"></i> Atualizar
                            </button>
                        </div>
                        
                        <table class="crypto-table">
                            <thead>
                                <tr>
                                    <th>Moeda</th>
                                    <th>Preço</th>
                                    <th>Variação 24h</th>
                                    <th>Ação</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>
                                        <div class="coin-cell">
                                            <div>
                                                <div class="coin-name">Bitcoin</div>
                                                <div class="coin-symbol">BTC</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td class="price">$45,000.00</td>
                                    <td class="positive">
                                        <i class="fas fa-caret-up"></i> +1.2%
                                    </td>
                                    <td>
                                        <button class="action-btn">
                                            <i class="fas fa-chart-line"></i>
                                        </button>
                                    </td>
                                </tr>
                                <tr>
                                    <td>
                                        <div class="coin-cell">
                                            <div>
                                                <div class="coin-name">Solana</div>
                                                <div class="coin-symbol">SOL</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td class="price">$170.74</td>
                                    <td class="negative">
                                        <i class="fas fa-caret-down"></i> -0.21%
                                    </td>
                                    <td>
                                        <button class="action-btn">
                                            <i class="fas fa-chart-line"></i>
                                        </button>
                                    </td>
                                </tr>
                                <tr>
                                    <td>
                                        <div class="coin-cell">
                                            <div>
                                                <div class="coin-name">Dogecoin</div>
                                                <div class="coin-symbol">DOGE</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td class="price">$0.224889</td>
                                    <td class="negative">
                                        <i class="fas fa-caret-down"></i> -0.04%
                                    </td>
                                    <td>
                                        <button class="action-btn">
                                            <i class="fas fa-chart-line"></i>
                                        </button>
                                    </td>
                                </tr>
                                <tr>
                                    <td>
                                        <div class="coin-cell">
                                            <div>
                                                <div class="coin-name">Shiba Inu</div>
                                                <div class="coin-symbol">SHIB</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td class="price">$0.00001498</td>
                                    <td class="negative">
                                        <i class="fas fa-caret-down"></i> -0.33%
                                    </td>
                                    <td>
                                        <button class="action-btn">
                                            <i class="fas fa-chart-line"></i>
                                        </button>
                                    </td>
                                </tr>
                                <tr>
                                    <td>
                                        <div class="coin-cell">
                                            <div>
                                                <div class="coin-name">Floki <span class="badge">HOT</span></div>
                                                <div class="coin-symbol">FLOKI</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td class="price">$0.00010304</td>
                                    <td class="negative">
                                        <i class="fas fa-caret-down"></i> -0.72%
                                    </td>
                                    <td>
                                        <button class="action-btn">
                                            <i class="fas fa-chart-line"></i>
                                        </button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    
                    <div class="updated-time">
                        ÚLTIMA ATUALIZAÇÃO: 09:45:00
                    </div>
                    
                    <div class="neon-glow glow-1"></div>
                    <div class="neon-glow glow-2"></div>
                    <div class="cyber-circuit"></div>
                </div>
            </div>
        </div>
        
        <script>
            // Função para atualizar os preços das criptomoedas em tempo real
            function atualizarPrecos() {
                fetch('/api/prices')
                    .then(response => response.json())
                    .then(data => {
                        // Atualizar os preços na tabela
                        const tableBody = document.querySelector('.crypto-table tbody');
                        tableBody.innerHTML = ''; // Limpar a tabela
                        
                        // Dicionário para mapear moedas com nomes para exibição
                        const coinDisplayNames = {
                            'bitcoin': 'Bitcoin',
                            'ethereum': 'Ethereum',
                            'solana': 'Solana',
                            'dogecoin': 'Dogecoin',
                            'shiba-inu': 'Shiba Inu',
                            'floki': 'Floki',
                            'bonk': 'Bonk',
                            'xrp': 'XRP'
                        };
                        
                        // Lista ordenada de moedas para exibir
                        const moedas = ['bitcoin', 'ethereum', 'solana', 'dogecoin', 'shiba-inu', 'floki', 'bonk', 'xrp'];
                        moedas.forEach(moeda => {
                            if (data[moeda]) {
                                const info = data[moeda];
                                
                                // Criar a linha da tabela
                                const row = document.createElement('tr');
                                
                                // Célula com o nome da moeda
                                const nameCell = document.createElement('td');
                                nameCell.innerHTML = `
                                    <div class="coin-cell">
                                        <div>
                                            <div class="coin-name">${coinDisplayNames[moeda] || moeda}</div>
                                            <div class="coin-symbol">${info.symbol}</div>
                                        </div>
                                        ${moeda === 'floki' ? '<span class="badge">HOT</span>' : ''}
                                    </div>
                                `;
                                row.appendChild(nameCell);
                                
                                // Célula com o preço
                                const priceCell = document.createElement('td');
                                priceCell.className = 'price';
                                priceCell.textContent = info.price_formatted;
                                row.appendChild(priceCell);
                                
                                // Célula com a variação
                                const changeCell = document.createElement('td');
                                changeCell.className = info.change_24h > 0 ? 'positive' : 'negative';
                                changeCell.innerHTML = `
                                    <i class="fas fa-caret-${info.change_24h > 0 ? 'up' : 'down'}"></i>
                                    ${info.change_24h ? info.change_24h.toFixed(2) + '%' : '0.00%'}
                                `;
                                row.appendChild(changeCell);
                                
                                // Célula com o botão de ação
                                const actionCell = document.createElement('td');
                                actionCell.innerHTML = `
                                    <button class="action-btn">
                                        <i class="fas fa-chart-line"></i>
                                    </button>
                                `;
                                row.appendChild(actionCell);
                                
                                // Adicionar a linha à tabela
                                tableBody.appendChild(row);
                            }
                        });
                        
                        // Atualizar o horário da última atualização
                        const updatedTimeElement = document.querySelector('.updated-time');
                        if (updatedTimeElement) {
                            const now = new Date();
                            const hours = now.getHours().toString().padStart(2, '0');
                            const minutes = now.getMinutes().toString().padStart(2, '0');
                            const seconds = now.getSeconds().toString().padStart(2, '0');
                            updatedTimeElement.textContent = `ÚLTIMA ATUALIZAÇÃO: ${hours}:${minutes}:${seconds}`;
                        }
                        
                        // Atualizar a maior alta e a maior baixa
                        let maiorAlta = { valor: -100, moeda: null };
                        let maiorBaixa = { valor: 100, moeda: null };
                        
                        Object.keys(data).forEach(moeda => {
                            const variacao = data[moeda].change_24h;
                            if (variacao !== null) {
                                if (variacao > maiorAlta.valor) {
                                    maiorAlta = { valor: variacao, moeda: moeda };
                                }
                                if (variacao < maiorBaixa.valor) {
                                    maiorBaixa = { valor: variacao, moeda: moeda };
                                }
                            }
                        });
                        
                        // Atualizar os cards de estatísticas
                        const estatisticas = document.querySelectorAll('.stat-card');
                        if (estatisticas && estatisticas.length >= 3) {
                            // Maior alta
                            if (maiorAlta.moeda) {
                                const info = data[maiorAlta.moeda];
                                estatisticas[1].querySelector('.stat-value').textContent = `+${maiorAlta.valor.toFixed(2)}%`;
                                estatisticas[1].querySelector('.stat-subtitle').textContent = coinDisplayNames[maiorAlta.moeda] || maiorAlta.moeda;
                            }
                            
                            // Maior baixa
                            if (maiorBaixa.moeda) {
                                const info = data[maiorBaixa.moeda];
                                estatisticas[2].querySelector('.stat-value').textContent = `${maiorBaixa.valor.toFixed(2)}%`;
                                estatisticas[2].querySelector('.stat-subtitle').textContent = coinDisplayNames[maiorBaixa.moeda] || maiorBaixa.moeda;
                            }
                        }
                    })
                    .catch(error => {
                        console.error('Erro ao atualizar preços:', error);
                    });
            }
            
            // Atualizar os preços a cada 30 segundos
            atualizarPrecos(); // Atualização inicial
            setInterval(atualizarPrecos, 30000); // Atualização a cada 30 segundos
            
            // Adicionar evento ao botão de atualizar
            const updateButton = document.querySelector('.action-btn');
            if (updateButton) {
                updateButton.addEventListener('click', () => {
                    atualizarPrecos();
                });
            }
            
            // Enviar atualização para o Telegram a cada 2 minutos
            function enviarAtualizacaoTelegram() {
                fetch('/send-telegram-update')
                    .then(response => response.json())
                    .then(data => {
                        console.log('Telegram update status:', data);
                    })
                    .catch(error => {
                        console.error('Erro ao enviar atualização para o Telegram:', error);
                    });
            }
            
            // Tentar enviar uma atualização para o Telegram após 5 segundos
            // e depois continuar enviando a cada 2 minutos
            setTimeout(() => {
                enviarAtualizacaoTelegram();
                setInterval(enviarAtualizacaoTelegram, 120000);
            }, 5000);
        </script>
    </body>
    </html>
    """
    
@app.route('/dashboard')
def dashboard():
    return redirect('/')
    
@app.route('/premium')
def premium():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CriptoSinais Premium</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');
            
            :root {
                --neon-purple: #8b5cf6;
                --neon-blue: #3b82f6;
                --neon-green: #10b981;
                --neon-pink: #ec4899;
                --neon-yellow: #fcd34d;
                --neon-text: #f0abfc;
                --bg-dark: #030712;
                --bg-panel: rgba(15, 23, 42, 0.7);
                --border-glow: 0 0 10px var(--neon-purple), 0 0 20px rgba(139, 92, 246, 0.3);
            }
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Rajdhani', sans-serif;
                background-color: var(--bg-dark);
                color: #e2e8f0;
                background-image: 
                    linear-gradient(rgba(3, 7, 18, 0.7), rgba(3, 7, 18, 0.9)),
                    url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiB2aWV3Qm94PSIwIDAgMjAwIDIwMCI+CiAgPGcgZmlsbD0iIzFhMWQyZCIgZmlsbC1vcGFjaXR5PSIwLjEiPgogICAgPHBhdGggZD0iTTQwIDEwMHMxIDAgMSAxdjEwMHMwIDEtMSAxaC00MHMtMS0xLTEtdi0xMDBzMC0xIDEtMXoiLz4KICAgIDxwYXRoIGQ9Ik0xNDAgMTAwczEgMCAxIDF2MTAwczAgMS0xIDFoLTQwcy0xLTEtMS0xdi0xMDBzMC0xIDEtMXoiLz4KICAgIDxwYXRoIGQ9Ik04MCAyMDBzMSAwIDEgMXYxMDBzMCAxLTEgMWgtNDBzLTEtMS0xLTF2LTEwMHMwLTEgMS0xeiIvPgogICAgPHBhdGggZD0iTTE4MCAyMDBzMSAwIDEgMXYxMDBzMCAxLTEgMWgtNDBzLTEtMS0xLTF2LTEwMHMwLTEgMS0xeiIvPgogIDwvZz4KPC9zdmc+');
                min-height: 100vh;
            }
            
            .page-wrapper {
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                overflow-x: hidden;
            }
            
            header {
                background: rgba(15, 23, 42, 0.9);
                padding: 1rem 2rem;
                backdrop-filter: blur(10px);
                border-bottom: 1px solid rgba(139, 92, 246, 0.3);
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
                position: relative;
                z-index: 100;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .logo {
                font-family: 'Orbitron', sans-serif;
                font-weight: 700;
                font-size: 1.8rem;
                color: white;
                text-transform: uppercase;
                letter-spacing: 2px;
                position: relative;
                text-shadow: 0 0 10px rgba(139, 92, 246, 0.7);
            }
            
            .logo::before {
                content: '';
                position: absolute;
                width: 100%;
                height: 4px;
                background: linear-gradient(90deg, var(--neon-purple), var(--neon-pink));
                bottom: -8px;
                left: 0;
                border-radius: 2px;
            }
            
            .main-container {
                flex: 1;
                padding: 2rem;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            
            .premium-container {
                max-width: 1000px;
                width: 100%;
                background: rgba(15, 23, 42, 0.6);
                backdrop-filter: blur(10px);
                border-radius: 12px;
                padding: 3rem;
                border: 1px solid rgba(139, 92, 246, 0.2);
                box-shadow: var(--border-glow);
                position: relative;
                overflow: hidden;
                text-align: center;
            }
            
            .premium-title {
                font-family: 'Orbitron', sans-serif;
                font-size: 2.5rem;
                font-weight: 900;
                color: white;
                text-transform: uppercase;
                margin-bottom: 1rem;
                text-shadow: 0 0 10px rgba(139, 92, 246, 0.7);
                letter-spacing: 2px;
            }
            
            .premium-subtitle {
                color: var(--neon-text);
                font-size: 1.2rem;
                margin-bottom: 2rem;
                font-weight: 500;
            }
            
            .premium-badge {
                display: inline-block;
                background: linear-gradient(135deg, var(--neon-purple), var(--neon-pink));
                color: white;
                padding: 0.5rem 1.5rem;
                border-radius: 50px;
                font-weight: 700;
                letter-spacing: 1px;
                text-transform: uppercase;
                margin-bottom: 2rem;
                font-family: 'Orbitron', sans-serif;
                box-shadow: 0 0 15px rgba(139, 92, 246, 0.7);
            }
            
            .features-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 2rem;
                margin: 2rem 0;
            }
            
            .feature-card {
                background: rgba(15, 23, 42, 0.7);
                border-radius: 10px;
                padding: 1.5rem;
                border: 1px solid rgba(255, 255, 255, 0.1);
                text-align: left;
                transition: all 0.3s ease;
            }
            
            .feature-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 0 15px rgba(139, 92, 246, 0.3);
            }
            
            .feature-icon {
                color: var(--neon-purple);
                font-size: 2rem;
                margin-bottom: 1rem;
            }
            
            .feature-title {
                font-family: 'Orbitron', sans-serif;
                font-size: 1.2rem;
                font-weight: 700;
                margin-bottom: 0.5rem;
                color: white;
            }
            
            .feature-desc {
                color: #94a3b8;
                font-size: 0.95rem;
                line-height: 1.5;
            }
            
            .price-section {
                background: rgba(15, 23, 42, 0.8);
                border-radius: 10px;
                padding: 2rem;
                margin: 3rem 0;
                border: 1px solid rgba(255, 255, 255, 0.1);
                position: relative;
                overflow: hidden;
            }
            
            .price-box {
                display: inline-block;
                padding: 2rem;
                position: relative;
                z-index: 1;
            }
            
            .price-title {
                font-family: 'Orbitron', sans-serif;
                font-size: 1.1rem;
                font-weight: 700;
                text-transform: uppercase;
                color: var(--neon-text);
                margin-bottom: 0.5rem;
                letter-spacing: 1px;
            }
            
            .price-amount {
                font-family: 'Orbitron', sans-serif;
                font-size: 3.5rem;
                font-weight: 900;
                color: var(--neon-yellow);
                text-shadow: 0 0 10px rgba(252, 211, 77, 0.5);
                margin-bottom: 1rem;
            }
            
            .price-period {
                color: #94a3b8;
                font-size: 1rem;
                font-weight: 500;
                margin-top: -0.5rem;
                display: block;
            }
            
            .price-description {
                color: white;
                margin-bottom: 2rem;
                font-size: 1.1rem;
            }
            
            .cta-button {
                display: inline-block;
                background: linear-gradient(135deg, var(--neon-yellow), var(--neon-pink));
                color: white;
                padding: 1rem 3rem;
                border-radius: 50px;
                font-family: 'Orbitron', sans-serif;
                font-weight: 700;
                font-size: 1.2rem;
                text-transform: uppercase;
                border: none;
                cursor: pointer;
                letter-spacing: 2px;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
                box-shadow: 0 0 20px rgba(252, 211, 77, 0.5);
                text-decoration: none;
            }
            
            .cta-button:hover {
                transform: translateY(-5px);
                box-shadow: 0 0 30px rgba(252, 211, 77, 0.7);
            }
            
            .cta-button::before {
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: linear-gradient(
                    to bottom right,
                    rgba(255, 255, 255, 0) 0%,
                    rgba(255, 255, 255, 0.3) 100%
                );
                transform: rotate(45deg);
                z-index: 1;
                animation: shine 3s infinite;
            }
            
            @keyframes shine {
                0% {
                    left: -100%;
                    top: -100%;
                }
                100% {
                    left: 100%;
                    top: 100%;
                }
            }
            
            .cta-button span {
                position: relative;
                z-index: 2;
            }
            
            .menu {
                display: flex;
                gap: 1.5rem;
            }
            
            .menu-item {
                color: white;
                text-decoration: none;
                font-weight: 600;
                font-size: 1rem;
                letter-spacing: 1px;
                transition: all 0.3s ease;
                padding: 0.5rem 1rem;
                border-radius: 4px;
                text-transform: uppercase;
            }
            
            .menu-item:hover {
                color: var(--neon-purple);
                background: rgba(139, 92, 246, 0.1);
            }
            
            .premium-btn {
                background: linear-gradient(135deg, var(--neon-purple), var(--neon-pink));
                color: white;
                padding: 0.5rem 1.25rem;
                border-radius: 6px;
                font-weight: 600;
                box-shadow: 0 0 10px rgba(139, 92, 246, 0.5);
            }
            
            .premium-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 0 15px rgba(139, 92, 246, 0.7);
                color: white;
                background: linear-gradient(135deg, var(--neon-pink), var(--neon-purple));
            }
            
            .neon-glow {
                position: absolute;
                width: 300px;
                height: 300px;
                border-radius: 50%;
                background: radial-gradient(circle, rgba(252, 211, 77, 0.2) 0%, rgba(252, 211, 77, 0.1) 40%, transparent 70%);
                pointer-events: none;
                z-index: -1;
            }
            
            .glow-1 {
                top: -100px;
                right: -100px;
            }
            
            .glow-2 {
                bottom: -150px;
                left: -100px;
                background: radial-gradient(circle, rgba(236, 72, 153, 0.2) 0%, rgba(236, 72, 153, 0.1) 40%, transparent 70%);
            }
            
            @media (max-width: 768px) {
                .features-grid {
                    grid-template-columns: 1fr;
                }
                
                .premium-container {
                    padding: 2rem 1.5rem;
                }
                
                .menu {
                    display: none;
                }
                
                .price-amount {
                    font-size: 2.5rem;
                }
            }
        </style>
    </head>
    <body>
        <div class="page-wrapper">
            <header>
                <div class="logo">CriptoSinais</div>
                <div class="menu">
                    <a href="/" class="menu-item">Dashboard</a>
                    <a href="/dashboard" class="menu-item">Análise</a>
                    <a href="/premium" class="menu-item premium-btn">Premium</a>
                </div>
            </header>
            
            <div class="main-container">
                <div class="premium-container">
                    <div class="premium-badge">Acesso VIP</div>
                    <h1 class="premium-title">CriptoSinais Premium</h1>
                    <p class="premium-subtitle">Desbloqueie recursos exclusivos e aumente suas chances de sucesso com criptomoedas</p>
                    
                    <div class="features-grid">
                        <div class="feature-card">
                            <div class="feature-icon">
                                <i class="fas fa-bell"></i>
                            </div>
                            <h3 class="feature-title">Alertas Antecipados</h3>
                            <p class="feature-desc">Receba alertas antes que as movimentações significativas aconteçam no mercado, possibilitando tempo de reação.</p>
                        </div>
                        
                        <div class="feature-card">
                            <div class="feature-icon">
                                <i class="fas fa-chart-line"></i>
                            </div>
                            <h3 class="feature-title">Análise Técnica Avançada</h3>
                            <p class="feature-desc">Acesso a gráficos profissionais com indicadores RSI, MACD e Bandas de Bollinger em tempo real.</p>
                        </div>
                        
                        <div class="feature-card">
                            <div class="feature-icon">
                                <i class="fas fa-users"></i>
                            </div>
                            <h3 class="feature-title">Grupo VIP no Telegram</h3>
                            <p class="feature-desc">Entre no grupo exclusivo com outros traders e receba sinais de compra e venda 24/7.</p>
                        </div>
                        
                        <div class="feature-card">
                            <div class="feature-icon">
                                <i class="fas fa-headset"></i>
                            </div>
                            <h3 class="feature-title">Suporte Prioritário</h3>
                            <p class="feature-desc">Receba atendimento diferenciado com respostas às suas dúvidas em tempo recorde.</p>
                        </div>
                    </div>
                    
                    <div class="price-section">
                        <div class="price-box">
                            <div class="price-title">Oferta Exclusiva</div>
                            <div class="price-amount">$1.99<span class="price-period">pagamento único</span></div>
                            <p class="price-description">Acesso vitalício a todos os recursos premium</p>
                            <a href="/payment" class="cta-button"><span>QUERO SER PREMIUM</span></a>
                        </div>
                    </div>
                    
                    <div class="neon-glow glow-1"></div>
                    <div class="neon-glow glow-2"></div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)