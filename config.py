import os

# Configurações da API CoinGecko
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"

# Configurações de logo
DEFAULT_LOGO = "/static/images/logo.svg"
EXTERNAL_LOGO = os.getenv("EXTERNAL_LOGO", "https://teu-servidor.com/logo-criptosinais.png")
USE_EXTERNAL_LOGO = os.getenv("USE_EXTERNAL_LOGO", "false").lower() == "true"

# Configuração de logo para templates
LOGO_CONFIG = {
    'logo_path': EXTERNAL_LOGO if USE_EXTERNAL_LOGO else DEFAULT_LOGO,
    'use_external_logo': USE_EXTERNAL_LOGO
}

# Configurações do Bot do Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "7773905776:AAEohw7-YUXf0RzpR7_QFfWK5_YZ_CATPi8")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "7556052789")

# Configurações de monitoramento
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "120"))  # Intervalo em segundos entre verificações (padrão: 2 minutos)
ALERT_THRESHOLD = float(os.getenv("ALERT_THRESHOLD", "3.0"))  # Variação percentual que dispara os alertas (padrão: 3%)

# Lista de moedas com IDs do CoinGecko e seus símbolos
# Formato: "id-coingecko": "SIMBOLO"
MOEDAS = {
    "shiba-inu": "SHIB",
    "floki": "FLOKI",
    "dogecoin": "DOGE",
    "bonk": "BONK",
    "solana": "SOL",
    "ripple": "XRP",
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
    "starknet": "STRK"
}

# Permitir configurar moedas via variáveis de ambiente
# Formato: CRYPTO_IDS=id1:SYMBOL1,id2:SYMBOL2,...
if os.getenv("CRYPTO_IDS"):
    MOEDAS = {}
    crypto_ids = os.getenv("CRYPTO_IDS").split(",")
    for item in crypto_ids:
        if ":" in item:
            id, symbol = item.strip().split(":")
            MOEDAS[id] = symbol
