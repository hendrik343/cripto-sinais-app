import requests
import time
import logging
import os
import sys
from datetime import datetime
from config import TELEGRAM_TOKEN, CHAT_ID, MOEDAS, CHECK_INTERVAL, ALERT_THRESHOLD, COINGECKO_API_URL

# Add parent directory to path for importing from web application
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize database connection (will be set if web app is running)
db_enabled = False
CryptoPrice = None

def init_db_connection():
    """Initialize database connection for storing price data"""
    global db_enabled, CryptoPrice
    
    try:
        # Try to directly use the database from app.py
        from sqlalchemy import create_engine, text
        from app import engine
        from models import CryptoPrice as CryptoPriceModel
        
        if engine is not None:
            CryptoPrice = CryptoPriceModel
            db_enabled = True
            logger.info("Conexão com o banco de dados inicializada com sucesso.")
            return True
        else:
            raise Exception("Engine not initialized")
    except Exception as e:
        logger.warning(f"Não foi possível inicializar a conexão com o banco de dados: {e}")
        logger.warning("Os dados não serão armazenados no banco de dados.")
        db_enabled = False
        return False
        
def store_price_in_db(coin_id, symbol, price, previous_price=None):
    """Store cryptocurrency price in database if database connection is available"""
    if not db_enabled:
        logger.warning("Database connection not enabled, skipping data storage")
        return None
        
    try:
        # Calculate percent change
        percent_change = None
        if previous_price is not None and previous_price > 0:
            percent_change = ((price - previous_price) / previous_price) * 100
            
        # Store the data using the app's engine
        from app import engine
        
        if engine:
            logger.info(f"Storing price for {symbol}: ${price}")
            
            # Directly use SQL to insert the record with text()
            from sqlalchemy import text
            
            with engine.connect() as conn:
                sql = text("""
                INSERT INTO crypto_price (coin_id, symbol, price, previous_price, percent_change, timestamp)
                VALUES (:coin_id, :symbol, :price, :previous_price, :percent_change, NOW())
                """)
                
                conn.execute(sql, {
                    'coin_id': coin_id,
                    'symbol': symbol,
                    'price': price,
                    'previous_price': previous_price,
                    'percent_change': percent_change
                })
                
                conn.commit()
                
                logger.info(f"Price for {symbol} stored in database: ${price:.8f}")
                return True
        else:
            raise Exception("Engine not available")
    except Exception as e:
        logger.error(f"Error storing price in database: {e}")
        return None

# Histórico de preços para comparação
historico_precos = {}

def get_preco_atual(moeda_id):
    """
    Obtém o preço atual de uma criptomoeda a partir da API do CoinGecko
    
    Args:
        moeda_id (str): ID da moeda na API do CoinGecko
    
    Returns:
        float: Preço atual da moeda em USD ou None em caso de erro
    """
    # Mapeamento de símbolos alternativos para os IDs oficiais do CoinGecko
    COIN_MAP = {
        "shib": "shiba-inu",
        "pepe": "pepe",
        "btc": "bitcoin",
        "eth": "ethereum",
        "floki": "floki",
        "doge": "dogecoin",
        "sol": "solana",
        "xrp": "ripple",
        "ada": "cardano",
        "avax": "avalanche-2",
        "link": "chainlink",
        "matic": "matic-network",
        "arb": "arbitrum",
        "op": "optimism",
        "rndr": "render-token",
        "grt": "the-graph",
        "apt": "aptos",
        "icp": "internet-computer",
        "sei": "sei-network",
        "strk": "starknet"
    }
    
    # Se a moeda estiver no mapa como símbolo, use o ID correspondente
    # Isso ajuda quando um símbolo é passado em vez do ID completo do CoinGecko
    if moeda_id.lower() in COIN_MAP:
        moeda_id = COIN_MAP[moeda_id.lower()]
    
    url = f"{COINGECKO_API_URL}/simple/price"
    params = {
        "ids": moeda_id,
        "vs_currencies": "usd"
    }
    try:
        response = requests.get(url, params=params, timeout=30)
        
        # Verificar se a resposta foi bem-sucedida
        if response.status_code == 429:
            logger.warning(f"Rate limit atingido na API do CoinGecko. Aguardando para nova tentativa.")
            time.sleep(60)  # Espera 1 minuto em caso de rate limit
            return None
            
        if response.status_code != 200:
            logger.error(f"Erro na API do CoinGecko: {response.status_code} - {response.text}")
            return None
            
        data = response.json()
        if moeda_id in data:
            return data[moeda_id]["usd"]
        else:
            logger.error(f"{moeda_id} não encontrado na resposta.")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro de conexão ao obter preço de {moeda_id}: {e}")
        return None
    except Exception as e:
        logger.error(f"Erro ao obter preço de {moeda_id}: {e}")
        return None

def send_telegram(mensagem):
    """
    Envia uma mensagem para o chat configurado no Telegram
    
    Args:
        mensagem (str): Mensagem a ser enviada
    
    Returns:
        bool: True se a mensagem foi enviada com sucesso, False caso contrário
    """
    if not TELEGRAM_TOKEN or not CHAT_ID:
        logger.error("Token do Telegram ou Chat ID não configurados!")
        return False
        
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "HTML"}
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            logger.info(f"Mensagem enviada para o Telegram com sucesso")
            return True
        else:
            logger.error(f"Erro ao enviar para o Telegram: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Erro ao enviar para o Telegram: {e}")
        return False

def verificar_variacao(moeda_id, simbolo):
    """
    Verifica a variação de preço de uma moeda e envia alerta se necessário
    
    Args:
        moeda_id (str): ID da moeda na API do CoinGecko
        simbolo (str): Símbolo da moeda para exibição
    """
    preco = get_preco_atual(moeda_id)
    if preco is None:
        logger.warning(f"Não foi possível obter o preço atual para {simbolo} ({moeda_id})")
        return

    anterior = historico_precos.get(moeda_id)
    
    # Se for a primeira vez que estamos obtendo este preço, apenas registramos
    if anterior is None:
        logger.info(f"Primeiro registro de {simbolo}: ${preco:.8f}")
        historico_precos[moeda_id] = preco
        
        # Armazenar no banco de dados se disponível
        store_price_in_db(moeda_id, simbolo, preco)
        return
    
    # Calcula a variação e atualiza o histórico
    variacao = ((preco - anterior) / anterior) * 100
    historico_precos[moeda_id] = preco
    
    # Armazenar no banco de dados se disponível
    store_price_in_db(moeda_id, simbolo, preco, anterior)
    
    # Formata números para exibição
    if preco < 0.01:
        formato_preco = f"${preco:.8f}"
    elif preco < 1:
        formato_preco = f"${preco:.6f}"
    elif preco < 1000:
        formato_preco = f"${preco:.4f}"
    else:
        formato_preco = f"${preco:.2f}"
    
    # Registra a variação no log
    logger.info(f"{simbolo}: {formato_preco} | Variação: {variacao:.2f}%")
    
    # Envia alerta se a variação for significativa
    if abs(variacao) >= ALERT_THRESHOLD:
        data_hora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
        # Determina o emoji, a mensagem e a recomendação com base na direção da variação
        if variacao > 0:
            emoji = "🚀 📈"
            msg_variacao = f"<b>ALTA de {variacao:.2f}%</b>"
            recomendacao = "📈 ALTA forte! <b>RECOMENDADO: COMPRA ✅</b>"
        else:
            emoji = "📉 ⚠️"
            msg_variacao = f"<b>QUEDA de {variacao:.2f}%</b>"
            recomendacao = "📉 QUEDA forte! <b>RECOMENDADO: VENDA ⚠️</b>"
        
        # Monta a mensagem
        mensagem = f"{emoji} <b>{simbolo}</b> {emoji}\n"
        mensagem += f"<i>{data_hora}</i>\n\n"
        mensagem += f"Preço atual: <b>{formato_preco}</b>\n"
        mensagem += f"Variação: {msg_variacao}\n"
        mensagem += f"Anterior: ${anterior:.8f}\n\n"
        mensagem += f"SINAL: {recomendacao}"
        
        # Armazena a recomendação para o web dashboard
        try:
            # Use the engine directly
            from app import engine
            from sqlalchemy import text
            
            if engine:
                with engine.connect() as conn:
                    sql = text("""
                        UPDATE crypto_price 
                        SET recommendation = :recommendation 
                        WHERE coin_id = :coin_id 
                        AND timestamp = (
                            SELECT MAX(timestamp) FROM crypto_price WHERE coin_id = :coin_id
                        )
                    """)
                    
                    conn.execute(sql, {
                        'recommendation': "COMPRA" if variacao > 0 else "VENDA",
                        'coin_id': moeda_id
                    })
                    
                    conn.commit()
                    logger.info(f"Recomendação para {simbolo} atualizada: {'COMPRA' if variacao > 0 else 'VENDA'}")
            else:
                raise Exception("Engine not available")
        except Exception as e:
            logger.error(f"Erro ao atualizar recomendação: {e}")
        
        # Envia para o Telegram
        send_telegram(mensagem)

def enviar_resumo_precos():
    """
    Envia um resumo com os preços atuais de todas as moedas monitoradas
    a cada ciclo de verificação, incluindo recomendações
    """
    if not historico_precos:
        logger.warning("Ainda não temos dados de preços para enviar um resumo")
        return
        
    data_hora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    mensagem = f"🔄 <b>ATUALIZAÇÃO DE PREÇOS</b> 🔄\n"
    mensagem += f"<i>{data_hora}</i>\n\n"
    
    # Criar lista ordenada por símbolo para melhor visualização
    moedas_ordenadas = sorted([(simbolo, moeda_id) for moeda_id, simbolo in MOEDAS.items()])
    
    # Obter dados históricos para calcular variações percentuais e recomendações
    try:
        # Use the engine directly
        from app import engine
        from sqlalchemy import text
        
        if engine:
            precos_anteriores = {}
            recomendacoes = {}
            
            with engine.connect() as conn:
                for simbolo, moeda_id in moedas_ordenadas:
                    # Get the last two price records for this coin
                    query = text("""
                    SELECT price, timestamp 
                    FROM crypto_price 
                    WHERE coin_id = :coin_id 
                    ORDER BY timestamp DESC 
                    LIMIT 2
                    """)
                    
                    result = conn.execute(query, {"coin_id": moeda_id})
                    records = result.fetchall()
                    
                    if len(records) >= 2:
                        preco_atual = records[0].price
                        preco_anterior = records[1].price
                        variacao = ((preco_atual - preco_anterior) / preco_anterior) * 100
                        
                        # Determinar recomendação com base na variação
                        if variacao > ALERT_THRESHOLD:
                            recomendacao = "BUY ✅"
                        elif variacao < -ALERT_THRESHOLD:
                            recomendacao = "SELL ❌"
                        else:
                            recomendacao = "WAIT ⏳"
                            
                        precos_anteriores[moeda_id] = preco_anterior
                        recomendacoes[moeda_id] = recomendacao
        else:
            raise Exception("Engine not available")
    except Exception as e:
        logger.error(f"Erro ao obter dados históricos para recomendações: {e}")
        precos_anteriores = {}
        recomendacoes = {}
    
    for simbolo, moeda_id in moedas_ordenadas:
        if moeda_id in historico_precos:
            preco = historico_precos[moeda_id]
            
            # Formata preços para exibição
            if preco < 0.01:
                formato_preco = f"${preco:.8f}"
            elif preco < 1:
                formato_preco = f"${preco:.6f}"
            elif preco < 1000:
                formato_preco = f"${preco:.4f}"
            else:
                formato_preco = f"${preco:.2f}"
            
            # Adicionar recomendação se disponível
            if moeda_id in recomendacoes:
                mensagem += f"<b>{simbolo}</b>: {formato_preco} | <b>{recomendacoes[moeda_id]}</b>\n"
            else:
                mensagem += f"<b>{simbolo}</b>: {formato_preco}\n"
    
    # Adiciona mensagem de rodapé
    mensagem += "\n<i>Você receberá atualizações a cada 2 minutos</i>"
    
    # Envia para o Telegram
    send_telegram(mensagem)

def iniciar_monitoramento():
    """
    Inicia o loop principal de monitoramento
    """
    logger.info("Iniciando monitoramento de criptomoedas...")
    logger.info(f"Moedas monitoradas: {', '.join(MOEDAS.values())}")
    logger.info(f"Limiar de alerta: {ALERT_THRESHOLD}%")
    logger.info(f"Intervalo de verificação: {CHECK_INTERVAL} segundos")
    
    # Tenta inicializar conexão com o banco de dados
    init_db_connection()
    
    # Insert initial test data to validate database connection
    try:
        logger.info("Inserting test data to validate database connection")
        store_price_in_db("bitcoin", "BTC", 45000.0)
        logger.info("Test data successfully inserted")
    except Exception as e:
        logger.error(f"Failed to insert test data: {e}")
    
    # Collect initial prices with increased delays to avoid rate limiting
    logger.info("Coletando preços iniciais...")
    
    # Only get initial prices for a few coins to avoid rate limiting
    initial_coins = list(MOEDAS.items())[:5]  # Just get the first 5 coins initially
    
    for moeda_id, simbolo in initial_coins:
        logger.info(f"Requesting price for {simbolo} ({moeda_id})...")
        preco = get_preco_atual(moeda_id)
        if preco:
            historico_precos[moeda_id] = preco
            logger.info(f"Preço inicial de {simbolo}: ${preco:.8f}")
            
            # Store in database
            logger.info(f"Storing initial price for {simbolo} in database")
            store_price_in_db(moeda_id, simbolo, preco)
        else:
            logger.warning(f"Não foi possível obter o preço inicial de {simbolo}")
        time.sleep(5)  # Increased pause to avoid rate limit
    
    # Envia mensagem de início
    mensagem_inicio = "🤖 <b>Bot de Monitoramento de Criptomoedas</b> 🤖\n\n"
    mensagem_inicio += "Monitoramento iniciado!\n\n"
    mensagem_inicio += f"Moedas: {', '.join(MOEDAS.values())}\n"
    mensagem_inicio += f"Você receberá atualizações a cada {CHECK_INTERVAL//60} minutos"
    send_telegram(mensagem_inicio)
    
    # Loop principal
    try:
        while True:
            logger.info("Iniciando ciclo de verificação...")
            for moeda_id, simbolo in MOEDAS.items():
                verificar_variacao(moeda_id, simbolo)
                time.sleep(3)  # Pausa entre moedas para respeitar rate limit
            
            # Enviar resumo de preços após cada ciclo
            enviar_resumo_precos()
            
            logger.info(f"Aguardando {CHECK_INTERVAL} segundos para próximo ciclo...")
            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        logger.info("Monitoramento interrompido pelo usuário.")
        send_telegram("🛑 <b>Monitoramento interrompido</b> 🛑")
    except Exception as e:
        logger.error(f"Erro no loop principal: {e}")
        send_telegram(f"❌ <b>Erro no monitoramento</b>: {str(e)}")
        raise

if __name__ == "__main__":
    iniciar_monitoramento()
