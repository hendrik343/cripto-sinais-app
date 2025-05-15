# CriptoSinais - Monitoramento e Alertas de Criptomoedas

Plataforma completa para monitoramento de preços de criptomoedas com alertas via Telegram, análise técnica, dashboard web e aplicativo móvel.

## Funcionalidades

- **Monitoramento em tempo real:** Acompanhamento de múltiplas criptomoedas (SHIB, FLOKI, DOGE, BONK, SOL, etc.)
- **Alertas inteligentes:** Notificações via Telegram para variações significativas (configurável)
- **Dashboard web:** Visualização de dados com interface futurista e responsiva
- **Análise técnica:** Indicadores avançados (RSI, MACD, Médias Móveis) na área premium
- **Aplicativo móvel:** Acesso às funcionalidades pelo smartphone (Flutter/Android)
- **Detector de pump:** Algoritmo para identificar potenciais movimentos de alta

## Arquitetura

- **Backend:** Python/Flask com PostgreSQL para armazenamento de dados
- **Frontend Web:** HTML/CSS/JavaScript com design futurista responsivo
- **Mobile:** Flutter/Dart com Firebase para autenticação e notificações
- **Integrações:** CoinGecko API, Telegram Bot API, Firebase Cloud Messaging

## Requisitos para Implantação

- Python 3.11+
- PostgreSQL
- Node.js (opcional, para desenvolvimento Next.js)
- Flutter/Dart (para desenvolvimento mobile)

## Configuração para Implantação

### Variáveis de Ambiente

Configure as seguintes variáveis de ambiente:

```
# Banco de dados
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Telegram
TELEGRAM_TOKEN=seu_token_do_telegram
TELEGRAM_CHAT_ID=id_do_chat

# Email (para confirmações de pagamento)
EMAIL_USER=seu_email@gmail.com
EMAIL_PASS=sua_senha_de_app

# PayPal (para pagamentos)
PAYPAL_EMAIL=seu_email_paypal

# Configuração do servidor
PORT=3000
```

### Implantação

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/criptosinais.git
   cd criptosinais
   ```

2. **Instale as dependências:**
   ```bash
   pip install -e .
   ```

3. **Configure o banco de dados:**
   ```bash
   # Certifique-se de que a variável DATABASE_URL está configurada
   # As tabelas serão criadas automaticamente na primeira execução
   ```

4. **Inicie o servidor:**
   ```bash
   ./run.sh
   ```

### Deploy com Docker (Recomendado)

1. **Construa a imagem:**
   ```bash
   docker build -t criptosinais:latest .
   ```

2. **Execute o contêiner:**
   ```bash
   docker run -p 3000:3000 --env-file .env criptosinais:latest
   ```

## Health Checks

A aplicação suporta health checks nas seguintes rotas:

- **/** - Endpoint raiz retorna status para ferramentas de monitoramento
- **/health** - Endpoint detalhado para verificações de saúde

## Áreas do Sistema

- **/dashboard** - Dashboard principal com informações em tempo real
- **/premium** - Área de assinantes com análises avançadas
- **/api/crypto-signals** - API de sinais para integrações externas

## Contato e Suporte

- **Telegram:** @cryptosignalshendrik_bot
- **Instagram:** @criptosinais77
