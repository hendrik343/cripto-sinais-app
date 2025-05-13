"""
Rotas de API para comunicação entre o aplicativo Flutter e o servidor
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from fcm_notifier import detect_pump_and_notify, calculate_rsi
import requests
import logging
import json
from models import CryptoPrice

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Criar blueprint para as rotas de API
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/status', methods=['GET'])
def api_status():
    """Endpoint simples para verificar se a API está respondendo"""
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@api_bp.route('/crypto-signals', methods=['GET'])
def api_crypto_signals():
    """
    API endpoint para obter sinais de criptomoedas
    Retorna os últimos preços com sinais de compra/venda baseados nas variações
    """
    try:
        # Obter os preços mais recentes do banco de dados
        latest_prices = CryptoPrice.get_latest_prices()
        
        signals = []
        for price_record in latest_prices:
            recommendation = "AGUARDA"
            
            # Aplicar lógica simples de recomendação
            if price_record.percent_change and price_record.percent_change >= 3.0:
                recommendation = "COMPRA"
            elif price_record.percent_change and price_record.percent_change <= -3.0:
                recommendation = "VENDA"
            
            # Formatação do preço
            formatted_price = price_record.price
            
            signals.append({
                'coin_id': price_record.coin_id,
                'symbol': price_record.symbol,
                'price': formatted_price,
                'percent_change': price_record.percent_change if price_record.percent_change else 0,
                'recommendation': recommendation
            })
        
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'signals': signals
        })
    except Exception as e:
        logger.error(f"Erro ao obter sinais: {e}")
        return jsonify({
            'error': 'Não foi possível obter os sinais',
            'timestamp': datetime.now().isoformat()
        }), 500

@api_bp.route('/pump-signals', methods=['GET'])
def api_pump_signals():
    """
    API endpoint para obter alertas de pump
    Retorna dados de moedas com potencial de pump baseados em RSI e volume
    """
    try:
        # Lista de moedas para analisar
        coins = [
            {'id': 'bitcoin', 'symbol': 'BTC'},
            {'id': 'ethereum', 'symbol': 'ETH'},
            {'id': 'solana', 'symbol': 'SOL'},
            {'id': 'shiba-inu', 'symbol': 'SHIB'},
            {'id': 'floki', 'symbol': 'FLOKI'},
            {'id': 'dogecoin', 'symbol': 'DOGE'},
            {'id': 'bonk-token', 'symbol': 'BONK'}
        ]
        
        # Para cada moeda, verificar se há potencial de pump
        pump_alerts = []
        for coin in coins:
            # Verificar se há dados em cache para esta moeda
            analysis = detect_pump_and_notify(coin['id'], coin['symbol'])
            
            if analysis and analysis.get('pump_detected'):
                pump_alerts.append({
                    'coin': analysis['coin_id'],
                    'symbol': analysis['symbol'],
                    'rsi': analysis['rsi'],
                    'volume': analysis['current_volume'],
                    'avg_volume': analysis['avg_volume'],
                    'volume_percent': analysis['volume_percent'],
                    'pump_detected': analysis['pump_detected'],
                    'recommendation': analysis['recommendation'],
                    'price': analysis['current_price']
                })
        
        return jsonify(pump_alerts)
    except Exception as e:
        logger.error(f"Erro ao obter sinais de pump: {e}")
        return jsonify({
            'error': 'Não foi possível obter os sinais de pump',
            'timestamp': datetime.now().isoformat()
        }), 500

@api_bp.route('/price-history/<coin_id>', methods=['GET'])
def price_history(coin_id):
    """
    Retorna o histórico de preços de uma moeda específica
    Parâmetros opcionais: 
    - limit: número de registros (padrão: 50)
    - days: alternativa para limit, número de dias de histórico
    """
    try:
        # Verificar parâmetros
        limit = request.args.get('limit', default=50, type=int)
        days = request.args.get('days', default=None, type=int)
        
        # Se days for especificado, calcular a data limite
        if days:
            start_date = datetime.now() - timedelta(days=days)
            history = CryptoPrice.query.filter(
                CryptoPrice.coin_id == coin_id,
                CryptoPrice.timestamp >= start_date
            ).order_by(CryptoPrice.timestamp.desc()).all()
        else:
            # Caso contrário, usar limit
            history = CryptoPrice.get_price_history(coin_id, limit)
        
        # Formatar resposta
        history_data = []
        for record in history:
            history_data.append({
                'timestamp': record.timestamp.isoformat(),
                'price': record.price,
                'percent_change': record.percent_change
            })
        
        return jsonify({
            'coin_id': coin_id,
            'history': history_data
        })
    except Exception as e:
        logger.error(f"Erro ao obter histórico de preços: {e}")
        return jsonify({
            'error': 'Não foi possível obter o histórico de preços',
            'timestamp': datetime.now().isoformat()
        }), 500

@api_bp.route('/market-status', methods=['GET'])
def api_market_status():
    """
    API endpoint para obter status geral do mercado
    """
    try:
        # Usar a API do CoinGecko para obter dados globais
        response = requests.get('https://api.coingecko.com/api/v3/global')
        if response.status_code == 200:
            data = response.json()
            global_data = data.get('data', {})
            
            # Extrair métricas relevantes
            market_cap_change = global_data.get('market_cap_change_percentage_24h_usd', 0)
            btc_dominance = global_data.get('market_cap_percentage', {}).get('btc', 0)
            eth_dominance = global_data.get('market_cap_percentage', {}).get('eth', 0)
            
            # Determinar sentimento do mercado com base na variação do market cap
            market_sentiment = "NEUTRO"
            if market_cap_change >= 3.0:
                market_sentiment = "BULLISH"
            elif market_cap_change <= -3.0:
                market_sentiment = "BEARISH"
            
            return jsonify({
                'timestamp': datetime.now().isoformat(),
                'market_cap_change_24h': market_cap_change,
                'btc_dominance': btc_dominance,
                'eth_dominance': eth_dominance,
                'market_sentiment': market_sentiment,
                'active_cryptocurrencies': global_data.get('active_cryptocurrencies', 0),
                'total_market_cap': global_data.get('total_market_cap', {}).get('usd', 0),
                'total_volume': global_data.get('total_volume', {}).get('usd', 0)
            })
        else:
            raise Exception(f"API do CoinGecko retornou código {response.status_code}")
    except Exception as e:
        logger.error(f"Erro ao obter status do mercado: {e}")
        return jsonify({
            'error': 'Não foi possível obter o status do mercado',
            'timestamp': datetime.now().isoformat(),
            'market_sentiment': "NEUTRO",  # Default fallback
            'market_cap_change_24h': 0,
            'btc_dominance': 0,
            'eth_dominance': 0
        })