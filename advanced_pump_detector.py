#!/usr/bin/env python3
"""
Detector de pump avançado para criptomoedas com alertas para Telegram
Este script monitora moedas e envia alertas quando detecta condições de pump
baseadas em RSI, médias móveis e volume
"""
import time
import requests
import logging
import os
from statistics import mean
from datetime import datetime
from config import TELEGRAM_TOKEN, CHAT_ID

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lista de moedas a monitorar (ID do CoinGecko)
MOEDAS = [
    "shiba-inu", "pepe", "floki", "dogecoin", "solana", "ripple", "cardano",
    "avalanche-2", "chainlink", "bitcoin", "ethereum", "aptos", "arbitrum",
    "optimism", "sei-network", "the-graph", "internet-computer", "strike"
]

# Mapeamento de IDs para símbolos/nomes legíveis
COIN_SYMBOLS = {
    "shiba-inu": "SHIB", "pepe": "PEPE", "floki": "FLOKI", "dogecoin": "DOGE",
    "solana": "SOL", "ripple": "XRP", "cardano": "ADA", "avalanche-2": "AVAX",
    "chainlink": "LINK", "bitcoin": "BTC", "ethereum": "ETH", "aptos": "APT",
    "arbitrum": "ARB", "optimism": "OP", "sei-network": "SEI", "the-graph": "GRT",
    "internet-computer": "ICP", "strike": "STRK"
}

# API CoinGecko
COIN_GECKO_URL = "https://api.coingecko.com/api/v3"

def get_market_data(coin_id, dias=1):
    """
    Obtém dados de mercado da API CoinGecko
    
    Args:
        coin_id (str): ID da moeda na API CoinGecko
        dias (int): Número de dias de histórico
        
    Returns:
        dict: Dados de preço e volume da moeda
    """
    logger.info(f"Obtendo dados de mercado para {coin_id}")
    url = f"{COIN_GECKO_URL}/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": str(dias),
        "interval": "hourly"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            logger.error(f"Erro na API CoinGecko: {response.status_code} - {response.text}")
            return None
            
        data = response.json()
        return data
    except Exception as e:
        logger.error(f"Erro ao buscar dados para {coin_id}: {e}")
        return None

def calculate_rsi(prices, period=14):
    """
    Calcula o RSI (Relative Strength Index) para uma série de preços
    
    Args:
        prices (list): Lista de preços
        period (int): Período do RSI
        
    Returns:
        float: Valor do RSI ou None se não houver dados suficientes
    """
    if len(prices) < period + 1:
        return None
        
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    
    try:
        avg_gain = mean(gains[:period]) if gains[:period] else 0
        avg_loss = mean(losses[:period]) if losses[:period] else 0
        
        rsi_values = []
        
        for i in range(period, len(prices)):
            if i > period:
                avg_gain = (avg_gain * (period - 1) + gains[i-1]) / period
                avg_loss = (avg_loss * (period - 1) + losses[i-1]) / period
                
            rs = avg_gain / avg_loss if avg_loss != 0 else float('inf')
            rsi_values.append(100 - (100 / (1 + rs)))
            
        return rsi_values[-1] if rsi_values else None
    except Exception as e:
        logger.error(f"Erro ao calcular RSI: {e}")
        return None

def calculate_moving_averages(prices):
    """
    Calcula médias móveis para uma série de preços
    
    Args:
        prices (list): Lista de preços
        
    Returns:
        tuple: (MA7, MA25) médias móveis de 7 e 25 períodos
    """
    if len(prices) < 25:
        return None, None
        
    try:
        ma7 = mean(prices[-7:])
        ma25 = mean(prices[-25:])
        return ma7, ma25
    except Exception as e:
        logger.error(f"Erro ao calcular médias móveis: {e}")
        return None, None

def check_volume_increase(volumes):
    """
    Verifica se houve aumento significativo no volume
    
    Args:
        volumes (list): Lista de volumes
        
    Returns:
        tuple: (bool, float) Se houve aumento e a porcentagem
    """
    if len(volumes) < 6:
        return False, 0
        
    try:
        volume_medio = mean(volumes[-6:-1])
        volume_atual = volumes[-1]
        
        aumento = (volume_atual / volume_medio) if volume_medio > 0 else 1
        return volume_atual > 1.3 * volume_medio, aumento
    except Exception as e:
        logger.error(f"Erro ao verificar volume: {e}")
        return False, 0

def send_telegram_alert(coin_id, rsi, ma_cruzado, volume_aumento, price):
    """
    Envia alerta de pump para o Telegram
    
    Args:
        coin_id (str): ID da moeda
        rsi (float): Valor do RSI
        ma_cruzado (bool): Se houve cruzamento de médias móveis
        volume_aumento (float): Aumento percentual do volume
        price (float): Preço atual
    """
    symbol = COIN_SYMBOLS.get(coin_id, coin_id.upper())
    now = datetime.now().strftime("%d/%m %H:%M")
    
    message = f"""🚀 *PUMP DETECTADO EM {symbol}*

📊 RSI: `{rsi:.2f}`
📈 {'' if ma_cruzado else 'Sem '}Cruzamento MA7 > MA25
💰 Volume: `+{(volume_aumento-1)*100:.2f}%` acima da média
💵 Preço: `${price:.8f}`
📅 Hora: {now}

⚡ _Tendência de valorização em preparação!_
"""
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"Alerta enviado para {symbol}")
            return True
        else:
            logger.error(f"Erro ao enviar alerta: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Erro ao enviar alerta para Telegram: {e}")
        return False

def monitorar_moedas():
    """
    Função principal que monitora as moedas e detecta condições de pump
    """
    logger.info("Iniciando monitoramento de moedas para detecção de pump")
    
    while True:
        for moeda in MOEDAS:
            try:
                # Obter dados de mercado
                data = get_market_data(moeda, dias=1)
                
                if not data or "prices" not in data or "total_volumes" not in data:
                    logger.warning(f"Sem dados para {moeda}")
                    continue
                    
                # Extrair preços e volumes
                prices = [x[1] for x in data["prices"]][-30:] if data["prices"] else []
                volumes = [x[1] for x in data["total_volumes"]][-30:] if data["total_volumes"] else []
                
                if len(prices) < 25 or len(volumes) < 6:
                    logger.warning(f"Dados insuficientes para análise de {moeda}")
                    continue
                    
                # Calcular indicadores
                rsi = calculate_rsi(prices)
                ma7, ma25 = calculate_moving_averages(prices)
                volume_aumentou, volume_aumento = check_volume_increase(volumes)
                
                # Verificar condições de pump
                ma_cruzado = ma7 > ma25 if ma7 is not None and ma25 is not None else False
                
                # Registrar dados calculados
                logger.info(f"{moeda}: RSI={rsi:.2f if rsi else 'N/A'}, MA7={ma7:.6f if ma7 else 'N/A'}, MA25={ma25:.6f if ma25 else 'N/A'}, Volume+={volume_aumento:.2f}x")
                
                # Decisão de envio de alerta
                if (
                    rsi is not None and rsi < 35 and
                    ma_cruzado and
                    volume_aumentou
                ):
                    logger.info(f"Condições de pump detectadas para {moeda}")
                    send_telegram_alert(moeda, rsi, ma_cruzado, volume_aumento, prices[-1])
                    
                # Pausa para evitar rate limit
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Erro ao processar {moeda}: {e}")
                
        logger.info("Ciclo de verificação completo. Aguardando próximo ciclo...")
        time.sleep(300)  # Espera 5 minutos entre os ciclos

if __name__ == "__main__":
    try:
        monitorar_moedas()
    except KeyboardInterrupt:
        logger.info("Monitoramento interrompido pelo usuário")
    except Exception as e:
        logger.critical(f"Erro fatal: {e}")