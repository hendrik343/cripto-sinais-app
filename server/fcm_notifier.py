"""
Serviço de notificações FCM para enviar alertas de pump e análises
"""

import os
import json
import firebase_admin
from firebase_admin import credentials, messaging, firestore
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicialização do Firebase Admin SDK
# Nota: O arquivo de credenciais deve ser fornecido como um secret ou variável de ambiente
if not firebase_admin._apps:
    try:
        # Verificar se temos credenciais como variável de ambiente
        if 'FIREBASE_CREDENTIALS' in os.environ:
            cred_dict = json.loads(os.environ.get('FIREBASE_CREDENTIALS', '{}'))
            cred = credentials.Certificate(cred_dict)
        else:
            # Usar credenciais de arquivo se variável de ambiente não estiver disponível
            cred = credentials.Certificate('firebase-credentials.json')
        
        firebase_admin.initialize_app(cred)
        logger.info("Firebase Admin SDK inicializado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao inicializar Firebase Admin SDK: {e}")

# Função para calcular RSI
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
    
    # Converter para numpy array
    prices_array = np.array(prices)
    
    # Calcular diferenças
    deltas = np.diff(prices_array)
    
    # Separar ganhos e perdas
    gains = deltas.copy()
    losses = deltas.copy()
    gains[gains < 0] = 0
    losses[losses > 0] = 0
    losses = abs(losses)
    
    # Calcular médias
    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])
    
    if avg_loss == 0:
        return 100.0
    
    # Calcular RS e RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

# Função para obter dados de mercado
def get_market_data(coin_id, days=1):
    """
    Obtém dados de mercado da API CoinGecko
    
    Args:
        coin_id (str): ID da moeda na API CoinGecko
        dias (int): Número de dias de histórico
        
    Returns:
        dict: Dados de preço e volume da moeda
    """
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        'vs_currency': 'usd',
        'days': days,
        'interval': 'hourly'
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            
            # Extrair preços e volumes
            prices = [item[1] for item in data.get('prices', [])]
            volumes = [item[1] for item in data.get('total_volumes', [])]
            
            return {
                'prices': prices,
                'volumes': volumes
            }
        else:
            logger.warning(f"Erro ao obter dados de mercado: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Exceção ao obter dados de mercado: {e}")
        return None

# Verificar aumento de volume
def check_volume_increase(volumes):
    """
    Verifica se houve aumento significativo no volume
    
    Args:
        volumes (list): Lista de volumes
        
    Returns:
        tuple: (bool, float) Se houve aumento e a porcentagem
    """
    if not volumes or len(volumes) < 24:
        return False, 0
    
    # Volume atual
    current_volume = volumes[-1]
    
    # Volume médio das últimas 24 horas (excluindo o atual)
    avg_volume = sum(volumes[-25:-1]) / min(24, len(volumes) - 1)
    
    # Aumento percentual
    percent_increase = ((current_volume / avg_volume) - 1) * 100
    
    # Consideramos aumento significativo se for maior que 75%
    is_significant = percent_increase > 75
    
    return is_significant, percent_increase

# Enviar notificação FCM
def send_fcm_notification(topic, title, body, data=None):
    """
    Envia uma notificação via Firebase Cloud Messaging
    
    Args:
        topic (str): Tópico para enviar a notificação (ex: 'pump_alerts')
        title (str): Título da notificação
        body (str): Corpo da notificação
        data (dict): Dados adicionais para a notificação
        
    Returns:
        bool: True se o envio foi bem-sucedido, False caso contrário
    """
    try:
        # Criar mensagem
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            topic=topic,
            android=messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    icon='ic_notification',
                    color='#4287f5',
                    channel_id='cripto_sinais_channel',
                    priority='max',
                ),
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        badge=1,
                        sound='default',
                        content_available=True,
                    ),
                ),
            ),
        )
        
        # Enviar mensagem
        response = messaging.send(message)
        logger.info(f"Notificação FCM enviada para o tópico '{topic}': {response}")
        return True
    except Exception as e:
        logger.error(f"Erro ao enviar notificação FCM: {e}")
        return False

# Detectar condições de pump e enviar notificação
def detect_pump_and_notify(coin_id, coin_symbol=None):
    """
    Detecta condições de pump para uma moeda e envia notificação se necessário
    
    Args:
        coin_id (str): ID da moeda na API CoinGecko
        coin_symbol (str): Símbolo da moeda (opcional)
        
    Returns:
        dict: Resultados da análise ou None em caso de erro
    """
    # Obter o símbolo da moeda, se não fornecido
    if not coin_symbol:
        coin_symbol = coin_id.upper()[:4]
    
    # Obter dados de mercado
    market_data = get_market_data(coin_id, days=2)
    if not market_data:
        logger.error(f"Não foi possível obter dados de mercado para {coin_id}")
        return None
    
    # Extrair preços e volumes
    prices = market_data.get('prices', [])
    volumes = market_data.get('volumes', [])
    
    # Calcular RSI
    rsi = calculate_rsi(prices)
    
    # Verificar aumento de volume
    volume_increase, volume_percent = check_volume_increase(volumes)
    
    # Determinar o atual preço
    current_price = prices[-1] if prices else 0
    
    # Determinar recomendação baseada no RSI e volume
    recommendation = "AGUARDAR"
    if rsi is not None:
        if rsi < 30 and volume_increase:
            recommendation = "COMPRA"
        elif rsi > 70 and volume_increase:
            recommendation = "VENDA"
        elif volume_increase:
            recommendation = "OBSERVAR"
    
    # Verificar se temos condições de pump
    pump_detected = volume_increase and (rsi is None or rsi < 40)
    
    # Preparar resultado da análise
    analysis = {
        'coin_id': coin_id,
        'symbol': coin_symbol,
        'rsi': rsi,
        'current_price': current_price,
        'volume_increase': volume_increase,
        'volume_percent': volume_percent,
        'current_volume': volumes[-1] if volumes else 0,
        'avg_volume': sum(volumes[-25:-1]) / min(24, len(volumes) - 1) if len(volumes) >= 25 else 0,
        'pump_detected': pump_detected,
        'recommendation': recommendation,
        'timestamp': datetime.now().isoformat()
    }
    
    # Enviar notificação se detectamos pump
    if pump_detected:
        # Título da notificação baseado no RSI
        if rsi is not None and rsi < 30:
            title = f"🚨 ALERTA DE COMPRA: {coin_symbol}"
            body = f"RSI em níveis de sobrevenda ({rsi:.1f}) com volume {volume_percent:.0f}% acima da média!"
        else:
            title = f"🚀 PUMP DETECTADO: {coin_symbol}"
            body = f"Volume aumentou {volume_percent:.0f}% acima da média. RSI: {rsi:.1f if rsi else 'N/A'}"
        
        # Dados adicionais para a notificação
        data = {
            'coin_id': coin_id,
            'symbol': coin_symbol,
            'alert_type': 'pump',
            'recommendation': recommendation,
            'price': str(current_price),
            'rsi': str(rsi) if rsi else 'N/A',
            'volume_percent': str(int(volume_percent))
        }
        
        # Enviar para o tópico geral de alertas de pump
        send_fcm_notification('pump_alerts', title, body, data)
        
        # Enviar também para o tópico específico da moeda
        send_fcm_notification(f'coin_{coin_id}', title, body, data)
        
        # Salvar alerta no Firestore
        try:
            db = firestore.client()
            db.collection('pump_alerts').add({
                'coinId': coin_id,
                'symbol': coin_symbol,
                'rsi': rsi,
                'volume': volumes[-1] if volumes else 0,
                'avgVolume': analysis['avg_volume'],
                'pumpDetected': pump_detected,
                'recommendation': recommendation,
                'timestamp': firestore.firestore.SERVER_TIMESTAMP,
                'price': current_price,
                'volumePercent': volume_percent
            })
            logger.info(f"Alerta de pump salvo no Firestore para {coin_symbol}")
        except Exception as e:
            logger.error(f"Erro ao salvar alerta no Firestore: {e}")
    
    return analysis

def check_all_coins():
    """
    Verifica todas as moedas monitoradas para alertas de pump
    """
    # Lista de moedas a monitorar
    coins = [
        {'id': 'bitcoin', 'symbol': 'BTC'},
        {'id': 'ethereum', 'symbol': 'ETH'},
        {'id': 'solana', 'symbol': 'SOL'},
        {'id': 'shiba-inu', 'symbol': 'SHIB'},
        {'id': 'floki', 'symbol': 'FLOKI'},
        {'id': 'dogecoin', 'symbol': 'DOGE'},
        {'id': 'bonk-token', 'symbol': 'BONK'},
        {'id': 'cardano', 'symbol': 'ADA'},
        {'id': 'chainlink', 'symbol': 'LINK'},
    ]
    
    results = []
    
    for coin in coins:
        logger.info(f"Verificando alertas para {coin['symbol']} ({coin['id']})")
        
        # Aguardar um pouco entre requisições para evitar rate limits
        import time
        time.sleep(2)
        
        # Detectar pump e enviar notificação
        analysis = detect_pump_and_notify(coin['id'], coin['symbol'])
        
        if analysis:
            results.append(analysis)
            pump = "DETECTADO" if analysis['pump_detected'] else "não detectado"
            logger.info(f"Análise para {coin['symbol']}: Pump {pump}, RSI: {analysis['rsi']:.2f if analysis['rsi'] else 'N/A'}, Volume: {analysis['volume_percent']:.2f}%")
    
    return results

# Função principal
def main():
    logger.info("Iniciando verificação de alertas de pump...")
    results = check_all_coins()
    logger.info(f"Verificação concluída. {len(results)} moedas analisadas.")
    # Exibir resumo dos resultados
    pump_coins = [r for r in results if r['pump_detected']]
    if pump_coins:
        logger.info(f"Pumps detectados em {len(pump_coins)} moedas:")
        for coin in pump_coins:
            logger.info(f"- {coin['symbol']}: RSI={coin['rsi']:.2f if coin['rsi'] else 'N/A'}, Volume +{coin['volume_percent']:.2f}%")
    else:
        logger.info("Nenhum pump detectado nesta verificação.")
    
    return results

if __name__ == "__main__":
    main()