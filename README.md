# Crypto Price Monitor Bot

Este é um bot para monitoramento de preços de criptomoedas que envia notificações via Telegram quando ocorrem variações significativas.

## Funcionalidades

- Monitoramento de múltiplas criptomoedas simultaneamente via API do CoinGecko
- Cálculo de variações percentuais entre verificações
- Envio de notificações pelo Telegram para variações significativas (configurável)
- Formatação de mensagens com dados detalhados e indicadores visuais
- Tratamento de erros e limites de taxa da API

## Requisitos

- Python 3.6+
- Pacote `requests`
- Token de um bot do Telegram
- Chat ID do Telegram para receber as notificações

## Configuração

### Variáveis de Ambiente

Configure as seguintes variáveis de ambiente:

- `TELEGRAM_TOKEN`: Token do seu bot do Telegram
- `TELEGRAM_CHAT_ID`: ID do chat/grupo onde as mensagens serão enviadas
- `CHECK_INTERVAL`: Intervalo em segundos entre verificações (padrão: 120)
- `ALERT_THRESHOLD`: Limiar de variação percentual que dispara alertas (padrão: 3.0)
- `CRYPTO_IDS`: (Opcional) Lista personalizada de criptomoedas no formato "id1:SYMBOL1,id2:SYMBOL2,..."

### Criando um Bot do Telegram

1. Fale com o [@BotFather](https://t.me/botfather) no Telegram
2. Use o comando `/newbot` e siga as instruções
3. Copie o token fornecido para a variável `TELEGRAM_TOKEN`

### Obtendo o Chat ID

1. Adicione o seu bot a um grupo ou inicie uma conversa com ele
2. Envie uma mensagem para o bot
3. Acesse `https://api.telegram.org/bot<TELEGRAM_TOKEN>/getUpdates`
4. Localize o campo `"chat":{"id":123456789}` na resposta JSON
5. Copie o valor do ID para a variável `TELEGRAM_CHAT_ID`

## Executando o Bot

```bash
python crypto_price_bot.py
# trigger
