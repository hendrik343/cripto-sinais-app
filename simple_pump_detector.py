#!/usr/bin/env python3
"""
Detector de pump simplificado para criptomoedas com alertas para Telegram
Este script monitoriza moedas e envia alertas quando detecta condições de pump
"""
import requests
import pandas as pd
import numpy as np
import schedule
import time
import os
import logging
from datetime import datetime
from config import TELEGRAM_TOKEN, CHAT_ID

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lista de moedas a monitorar (ID do CoinGecko)
# Reduzindo para apenas 4 moedas principais para evitar rate limit
COINS = [
    {"id": "bitcoin", "name": "Bitcoin", "symbol": "BTC"},
    {"id": "solana", "name": "Solana", "symbol": "SOL"},
    {"id": "shiba-inu", "name": "Shiba Inu", "symbol": "SHIB"},
    {"id": "dogecoin", "name": "Dogecoin", "symbol": "DOGE"}
]

def fetch_candles(coin_id="bitcoin", days=7):
    """
    Obtém os dados de velas (OHLCV) de uma criptomoeda da API CoinGecko
    
    Args:
        coin_id (str): ID da moeda no CoinGecko
        days (int): Número de dias de histórico a obter
        
    Returns:
        DataFrame: DataFrame com timestamp, preço e volume
    """
    logger.info(f"Buscando dados de {coin_id} para os últimos {days} dias")
    
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        params = {
            "vs_currency": "usd",
            "days": days,
            "interval": "hourly"
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            logger.error(f"Erro ao obter dados: {response.status_code} - {response.text}")
            return None
            
        data = response.json()
        
        prices = [p[1] for p in data["prices"]]
        volumes = [v[1] for v in data["total_volumes"]]
        timestamps = [pd.to_datetime(p[0], unit='ms') for p in data["prices"]]
        
        df = pd.DataFrame({
            "timestamp": timestamps, 
            "close": prices, 
            "volume": volumes
        })
        
        return df
    except Exception as e:
        logger.error(f"Erro ao buscar dados de {coin_id}: {e}")
        return None

def calculate_indicators(df):
    """
    Calcula indicadores técnicos manualmente (RSI, MACD) para um DataFrame
    
    Args:
        df (DataFrame): DataFrame com dados de preço
        
    Returns:
        DataFrame: DataFrame com indicadores calculados
    """
    if df is None or len(df) < 30:  # Precisamos de pelo menos 30 registros para cálculos confiáveis
        return None
        
    try:
        # Calcular mudanças de preço
        df['price_change'] = df['close'].diff()
        
        # Calcular RSI (14 períodos)
        window_length = 14
        # Separe ganhos e perdas
        df['gain'] = np.where(df['price_change'] > 0, df['price_change'], 0)
        df['loss'] = np.where(df['price_change'] < 0, -df['price_change'], 0)
        
        # Calcule a média móvel dos ganhos e perdas
        avg_gain = df['gain'].rolling(window=window_length).mean()
        avg_loss = df['loss'].rolling(window=window_length).mean()
        
        # Calcule o RS (Relative Strength) e o RSI
        rs = avg_gain / avg_loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Calcular médias móveis para MACD
        df['ema12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema26'] = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = df['ema12'] - df['ema26']
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']
        
        # Calcular média de volume
        df['volume_ma5'] = df['volume'].rolling(window=5).mean()
        
        return df
    except Exception as e:
        logger.error(f"Erro ao calcular indicadores: {e}")
        return None

def analyze_for_pump(df, coin):
    """
    Analisa os indicadores técnicos para identificar condições de pump
    
    Args:
        df (DataFrame): DataFrame com indicadores
        coin (dict): Dicionário com informações da moeda
        
    Returns:
        dict: Resultados da análise com recomendação e explicação
    """
    if df is None or 'rsi' not in df.columns:
        return None
        
    try:
        # Pegar o último registro
        latest = df.iloc[-1]
        previous = df.iloc[-2]
        
        # Verificar sinais de RSI
        rsi_value = latest["rsi"]
        rsi_oversold = rsi_value < 30
        rsi_rising = latest["rsi"] > previous["rsi"]
        
        # Verificar sinais de MACD
        macd_crossover = (previous["macd"] < previous["macd_signal"]) and (latest["macd"] > latest["macd_signal"])
        macd_positive_momentum = latest["macd_hist"] > previous["macd_hist"]
        
        # Verificar sinais de volume
        volume_increasing = latest["volume"] > latest["volume_ma5"]
        volume_spike = latest["volume"] > 1.5 * latest["volume_ma5"]
        
        # Contar pontos para determinar a força do sinal
        signal_strength = 0
        explanation = []
        
        if rsi_oversold:
            signal_strength += 2
            explanation.append(f"RSI em condição de sobrevenda ({rsi_value:.2f} < 30)")
        elif rsi_rising and rsi_value < 50:
            signal_strength += 1
            explanation.append(f"RSI subindo ({rsi_value:.2f}) a partir de níveis baixos")
            
        if macd_crossover:
            signal_strength += 2
            explanation.append("MACD cruzou acima da linha de sinal")
        elif macd_positive_momentum:
            signal_strength += 1
            explanation.append("MACD mostrando momentum positivo")
            
        if volume_spike:
            signal_strength += 2
            explanation.append("Volume com pico significativo (+50%)")
        elif volume_increasing:
            signal_strength += 1
            explanation.append("Volume acima da média")
            
        # Determinar recomendação com base na força do sinal
        recommendation = "WAIT"
        emoji = "⏳"
        
        if signal_strength >= 4:
            recommendation = "COMPRA"
            emoji = "🟢"
        elif signal_strength >= 2:
            recommendation = "OBSERVAR"
            emoji = "👀"
            
        result = {
            "coin_id": coin["id"],
            "symbol": coin["symbol"],
            "name": coin["name"],
            "price": latest["close"],
            "rsi": rsi_value,
            "macd": latest["macd"],
            "macd_signal": latest["macd_signal"],
            "volume": latest["volume"],
            "volume_change": (latest["volume"] / latest["volume_ma5"] - 1) * 100,
            "recommendation": recommendation,
            "signal_strength": signal_strength,
            "explanation": explanation,
            "emoji": emoji
        }
        
        logger.info(f"{coin['symbol']}: Força do sinal = {signal_strength}, Recomendação = {recommendation}")
        return result
        
    except Exception as e:
        logger.error(f"Erro ao analisar {coin['symbol']}: {e}")
        return None

def send_telegram(message):
    """
    Envia uma mensagem para o grupo/canal do Telegram
    
    Args:
        message (str): Mensagem a ser enviada
        
    Returns:
        bool: True se o envio foi bem-sucedido, False caso contrário
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
            logger.info("Mensagem enviada para o Telegram com sucesso")
            return True
        else:
            logger.error(f"Erro ao enviar mensagem para o Telegram: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem para o Telegram: {e}")
        return False

def format_signal_message(analysis):
    """
    Formata uma mensagem de sinal para o Telegram
    
    Args:
        analysis (dict): Resultados da análise
        
    Returns:
        str: Mensagem formatada em Markdown
    """
    # Timestamp no formato que você usa
    timestamp = datetime.now().strftime("%d/%m %H:%M")
    
    # Título/cabeçalho com emojis
    if analysis['recommendation'] == "COMPRA":
        message = f"🚀 *POSSÍVEL PUMP DETETADO* — {analysis['name'].upper()} ({analysis['symbol']})\n\n"
    else:
        message = f"{analysis['emoji']} *SINAL DE {analysis['recommendation']}* — {analysis['name'].upper()} ({analysis['symbol']})\n\n"
    
    # Indicadores com formatação code
    message += f"• Preço: `${analysis['price']:.6f}`\n"
    message += f"• RSI: `{analysis['rsi']:.2f}`"
    
    # Adicionar detalhes do RSI
    if analysis['rsi'] < 30:
        message += " (abaixo de 30)\n"
    else:
        message += "\n"
        
    # MACD e volume com bullet points
    if analysis['macd'] > analysis['macd_signal']:
        message += f"• MACD cruzado para cima\n"
    else:
        message += f"• MACD: `{analysis['macd']:.6f}`\n"
    
    if analysis['volume_change'] > 0:
        message += f"• Volume crescente detectado (+{analysis['volume_change']:.2f}%)\n"
    else:
        message += f"• Volume: `{analysis['volume_change']:.2f}%`\n"
    
    # Hora e recomendação
    message += f"\n_Hora:_ {timestamp}\n"
    
    if analysis['recommendation'] == "COMPRA":
        message += f"_Ação recomendada:_ monitorar para entrada antecipada 📈"
    elif analysis['recommendation'] == "OBSERVAR":
        message += f"_Ação recomendada:_ monitorar de perto 👀"
    else:
        message += f"_Ação recomendada:_ aguardar melhores condições ⏳"
    
    return message

def check_for_pumps():
    """
    Verifica todas as moedas monitoradas em busca de sinais de pump
    Envia sinais fortes diretamente para o Telegram
    """
    logger.info("Iniciando verificação de pumps...")
    results = []
    
    for coin in COINS:
        try:
            # Buscar dados
            df = fetch_candles(coin["id"], days=7)
            
            if df is not None and len(df) > 0:
                # Calcular indicadores
                df_with_indicators = calculate_indicators(df)
                
                # Analisar para identificar condições de pump
                analysis = analyze_for_pump(df_with_indicators, coin)
                
                if analysis and analysis["signal_strength"] >= 2:
                    results.append(analysis)
                    
                    # Enviar sinais fortes diretamente para o Telegram
                    if analysis["signal_strength"] >= 4:
                        message = format_signal_message(analysis)
                        send_telegram(message)
                        
            # Pausa para evitar rate limit da API
            time.sleep(5)
            
        except Exception as e:
            logger.error(f"Erro ao processar {coin['id']}: {e}")
    
    # Resumo dos sinais potenciais
    if results:
        logger.info(f"Encontrados {len(results)} sinais potenciais")
        
        # Enviar resumo para o Telegram se houver pelo menos 1 sinal
        if len(results) > 0:
            summary = "🔍 *RESUMO DOS SINAIS*\n\n"
            
            for r in results:
                summary += f"{r['emoji']} *{r['symbol']}:* {r['recommendation']} (`${r['price']:.6f}`, RSI: `{r['rsi']:.2f}`)\n"
                
            current_time = datetime.now().strftime("%d/%m %H:%M")
            summary += f"\n_Atualizado em {current_time}_"
            
            send_telegram(summary)
    else:
        logger.info("Nenhum sinal potencial encontrado")

def main():
    """Função principal do script"""
    logger.info("Iniciando detector simplificado de pump para criptomoedas...")
    
    # Verificar imediatamente ao iniciar
    check_for_pumps()
    
    # Agendar verificações a cada 5 minutos
    schedule.every(5).minutes.do(check_for_pumps)
    
    logger.info("Detector de pump iniciado. Verificações agendadas a cada 5 minutos.")
    
    # Loop principal
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Verifica a cada minuto se há tarefas pendentes
        except KeyboardInterrupt:
            logger.info("Programa interrompido pelo usuário")
            break
        except Exception as e:
            logger.error(f"Erro no loop principal: {e}")
            time.sleep(300)  # Pausa maior em caso de erro

if __name__ == "__main__":
    main()