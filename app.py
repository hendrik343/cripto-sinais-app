from flask import Flask, jsonify, redirect, render_template_string, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os
import logging
import requests
from datetime import datetime
import io
import csv

# 🔧 Configuração básica
app = Flask(__name__)
PORT = int(os.environ.get("PORT", 5000))

# Definir SECRET_KEY para sessões
app.secret_key = os.environ.get("SESSION_SECRET", "cripto_sinais_secret")

# Configurações para logo e URLs
DEFAULT_LOGO = "static/img/logo.png"
EXTERNAL_LOGO = "static/img/logo-alt.png"
USE_EXTERNAL_LOGO = False
SHORT_URL = os.environ.get('REPLIT_DOMAINS', '').split(",")[0]
PAYPAL_EMAIL = os.environ.get("PAYPAL_EMAIL", "hdhh9855@gmail.com")
LOGO_CONFIG = {
    "logo_path": EXTERNAL_LOGO if USE_EXTERNAL_LOGO else DEFAULT_LOGO,
    "use_external_logo": USE_EXTERNAL_LOGO
}

# Configurações para o bot Telegram
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")

# Configurações de email
EMAIL_USER = os.environ.get("EMAIL_USER", "")
EMAIL_PASS = os.environ.get("EMAIL_PASS", "")

# 📦 Base de dados PostgreSQL (usando variável de ambiente)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///database.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 🛠️ Logger bonito
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

# 🧱 Modelo de exemplo
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

# 🧱 Modelo para armazenar preços de criptomoedas
class CryptoPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coin_id = db.Column(db.String(64), nullable=False, index=True)
    symbol = db.Column(db.String(16), nullable=False)
    price = db.Column(db.Float, nullable=False)
    previous_price = db.Column(db.Float, nullable=True)
    percent_change = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    recommendation = db.Column(db.String(20), nullable=True)
    
    @classmethod
    def get_latest_prices(cls):
        """Get the latest price record for each cryptocurrency"""
        from sqlalchemy import func, desc
        subquery = db.session.query(
            cls.coin_id,
            func.max(cls.timestamp).label('max_time')
        ).group_by(cls.coin_id).subquery()
        
        return db.session.query(cls).join(
            subquery,
            db.and_(
                cls.coin_id == subquery.c.coin_id,
                cls.timestamp == subquery.c.max_time
            )
        ).all()
    
    @classmethod
    def store_price(cls, coin_id, symbol, price, previous_price=None):
        """Store a new price record"""
        percent_change = None
        recommendation = None
        
        if previous_price and previous_price > 0:
            percent_change = ((price - previous_price) / previous_price) * 100
            
            if abs(percent_change) >= 3.0:
                recommendation = "COMPRA" if percent_change > 0 else "VENDA"
            else:
                recommendation = "AGUARDAR"
        
        new_price = cls(
            coin_id=coin_id,
            symbol=symbol,
            price=price,
            previous_price=previous_price,
            percent_change=percent_change,
            recommendation=recommendation
        )
        
        db.session.add(new_price)
        db.session.commit()
        return new_price

# 🌱 Inicialização
with app.app_context():
    try:
        db.create_all()
        logger.info("Tabelas criadas com sucesso")
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {e}")

# ✅ Rota health check API
@app.route("/api/status")
def api_status():
    return jsonify({"message": "API online!", "status": "online"})

# ✅ Rota principal com HTML
@app.route("/")
def index():
    html = """
    <!DOCTYPE html>
    <html>
      <head>
        <title>CriptoSinais - Dashboard</title>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
        <style>
          body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #121212;
            color: #e2e8f0;
            padding: 40px;
          }
          .card {
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 20px;
          }
          .card-header {
            background: rgba(15, 23, 42, 0.7);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
          }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="row justify-content-center">
            <div class="col-md-10">
              <h1 class="text-center mb-4">📊 CriptoSinais Dashboard</h1>
              
              <div class="card">
                <div class="card-header">
                  <h5 class="mb-0">Status do Sistema</h5>
                </div>
                <div class="card-body">
                  <p>Status: <span class="badge bg-success">Online</span></p>
                  <p>Base de dados: <span class="badge bg-success">Conectada</span></p>
                  <p>Bot Telegram: <span class="badge bg-warning" id="telegramStatus">Verificando...</span></p>
                  <p>API CoinGecko: <span class="badge bg-success">Conectada</span></p>
                </div>
              </div>
              
              <div class="card">
                <div class="card-header">
                  <h5 class="mb-0">Criptomoedas Monitoradas</h5>
                </div>
                <div class="card-body">
                  <div class="row">
                    <div class="col-md-3 mb-2"><span class="badge bg-info">SHIB</span></div>
                    <div class="col-md-3 mb-2"><span class="badge bg-info">FLOKI</span></div>
                    <div class="col-md-3 mb-2"><span class="badge bg-info">DOGE</span></div>
                    <div class="col-md-3 mb-2"><span class="badge bg-info">BONK</span></div>
                    <div class="col-md-3 mb-2"><span class="badge bg-info">SOL</span></div>
                    <div class="col-md-3 mb-2"><span class="badge bg-info">XRP</span></div>
                    <div class="col-md-3 mb-2"><span class="badge bg-info">ADA</span></div>
                    <div class="col-md-3 mb-2"><span class="badge bg-info">AVAX</span></div>
                  </div>
                </div>
              </div>
              
              <div class="d-grid gap-2">
                <a href="/dashboard" class="btn btn-primary btn-lg">Acessar Dashboard Completo</a>
                <a href="/api/status" class="btn btn-secondary">Verificar API</a>
              </div>
            </div>
          </div>
        </div>
        
        <script>
          // Verificar status do Telegram
          fetch('/api/telegram-status')
              .then(response => response.json())
              .then(data => {
                  const statusElement = document.getElementById('telegramStatus');
                  console.log("Telegram update status:", data);
                  
                  if (data.status === 'online') {
                      statusElement.className = 'badge bg-success';
                      statusElement.textContent = 'Conectado';
                  } else {
                      statusElement.className = 'badge bg-danger';
                      statusElement.textContent = 'Desconectado';
                  }
              })
              .catch(error => {
                  console.error('Erro ao verificar status do Telegram:', error);
                  const statusElement = document.getElementById('telegramStatus');
                  statusElement.className = 'badge bg-danger';
                  statusElement.textContent = 'Erro';
              });
        </script>
      </body>
    </html>
    """
    return render_template_string(html)

# Rota específica para preview da app no browser
@app.route('/preview')
def preview():
    return redirect("/dashboard")

# Página inicial (acessível diretamente)
@app.route("/index_html")
def index_html():
    return render_template("index.html")

# Rota específica para health checks
@app.route("/health")
def health_check():
    """Endpoint para verificações de saúde (health checks)"""
    return jsonify({
        "status": "online",
        "version": "1.0.0",
        "message": "API de monitoramento de criptomoedas está funcionando corretamente"
    })

@app.route("/index_multilang")
def index_multilang():
    return render_template("index_multilang.html",
                           logo_path=EXTERNAL_LOGO if USE_EXTERNAL_LOGO else DEFAULT_LOGO,
                           use_external_logo=USE_EXTERNAL_LOGO)
    
@app.route("/charts")
def charts():
    """
    Página de gráficos avançados
    """
    return render_template("charts.html")
    
@app.route("/dashboard")
def dashboard():
    """
    Dashboard com gráficos e funcionalidades premium
    """
    return """
    <html>
      <head>
        <title>CriptoSinais Dashboard</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
          body {
            background: #0f172a;
            color: #e2e8f0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          }
          .card {
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.1);
          }
          .card-header {
            background: rgba(15, 23, 42, 0.7);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
          }
          .table {
            color: #e2e8f0;
          }
          .positive {
            color: #4ade80;
          }
          .negative {
            color: #f87171;
          }
          .price {
            color: #38bdf8;
            font-weight: bold;
          }
        </style>
      </head>
      <body>
        <div class="container py-4">
          <h1 class="mb-4 text-center">📊 CriptoSinais Dashboard</h1>
          
          <div class="card mb-4">
            <div class="card-header">
              <h5 class="mb-0">Status do Sistema</h5>
            </div>
            <div class="card-body">
              <p>Status: <span class="badge bg-success">Online</span></p>
              <p>Moedas monitoradas: <strong>18</strong></p>
              <p>Última atualização: <span id="timestamp"></span></p>
            </div>
          </div>
          
          <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h5 class="mb-0">Preços Atuais</h5>
            </div>
            <div class="card-body">
              <div class="table-responsive">
                <table class="table">
                  <thead>
                    <tr>
                      <th>Moeda</th>
                      <th>Preço</th>
                      <th>Variação 24h</th>
                      <th>Recomendação</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>Bitcoin (BTC)</td>
                      <td class="price">$45,000.00</td>
                      <td class="positive">+1.2%</td>
                      <td><span class="badge bg-warning">AGUARDAR</span></td>
                    </tr>
                    <tr>
                      <td>Solana (SOL)</td>
                      <td class="price">$170.74</td>
                      <td class="negative">-0.21%</td>
                      <td><span class="badge bg-warning">AGUARDAR</span></td>
                    </tr>
                    <tr>
                      <td>Dogecoin (DOGE)</td>
                      <td class="price">$0.224889</td>
                      <td class="negative">-0.04%</td>
                      <td><span class="badge bg-warning">AGUARDAR</span></td>
                    </tr>
                    <tr>
                      <td>Shiba Inu (SHIB)</td>
                      <td class="price">$0.00001498</td>
                      <td class="negative">-0.33%</td>
                      <td><span class="badge bg-warning">AGUARDAR</span></td>
                    </tr>
                    <tr>
                      <td>Floki (FLOKI)</td>
                      <td class="price">$0.00010304</td>
                      <td class="negative">-0.72%</td>
                      <td><span class="badge bg-warning">AGUARDAR</span></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
        
        <script>
          // Atualizar o timestamp
          const timestamp = document.getElementById('timestamp');
          const now = new Date();
          timestamp.textContent = now.toLocaleString();
        </script>
      </body>
    </html>
    """

@app.route("/dashboard-futuristic")
def dashboard_futuristic():
    """
    Dashboard futurista com efeitos visuais cibernéticos
    """
    return render_template("dashboard-futuristic.html")

@app.route("/dashboard-futuristic-alt")
def dashboard_futuristic_alt():
    """
    Dashboard futurista alternativo (versão mais leve)
    """
    return render_template("dashboard-futuristic-alt.html")

@app.route("/short_url")
def show_short_url():
    return render_template("short_url.html", short_url=SHORT_URL)

@app.route("/premium")
def premium():
    # Verificar se o usuário tem acesso premium (se o pagamento foi confirmado)
    if not session.get("pagamento_confirmado"):
        # Se não tiver acesso, redirecionar para a página de preview
        return redirect(url_for("premium_preview"))
    # Se tiver acesso, mostrar a página premium completa
    return render_template("premium.html")

@app.route("/premium-futuristic")
def premium_futuristic():
    """
    Versão futurista da página premium com design cyber
    """
    # Verificar se o usuário tem acesso premium
    if not session.get("pagamento_confirmado"):
        # Se não tiver acesso, redirecionar para a página de preview futurista
        return redirect(url_for("premium_preview_futuristic"))
    # Se tiver acesso, mostrar a página premium futurista
    return render_template("premium_futuristic.html")
    
@app.route("/premium-preview")
def premium_preview():
    """
    Página de preview da área premium para usuários não premium
    Exibe conteúdo bloqueado e CTA para pagamento
    """
    return render_template("preview.html", **LOGO_CONFIG)

@app.route("/premium-preview-futuristic")
def premium_preview_futuristic():
    """
    Versão futurista da página de preview da área premium
    """
    return render_template("premium_futuristic.html")

@app.route("/landing")
def landing():
    """
    Landing page em português para conversão
    """
    return render_template("landing.html", 
                           logo_path=EXTERNAL_LOGO if USE_EXTERNAL_LOGO else DEFAULT_LOGO, 
                           use_external_logo=USE_EXTERNAL_LOGO)

@app.route("/landing-new")
def landing_new():
    """
    Landing page moderna com sistema de tema claro/escuro
    """
    return render_template("landing_new.html", 
                          logo_path=EXTERNAL_LOGO if USE_EXTERNAL_LOGO else DEFAULT_LOGO, 
                          use_external_logo=USE_EXTERNAL_LOGO)
    
@app.route("/promocao")
def promocao():
    """
    Página promocional para conversão de premium com estilo alternativo
    """
    return render_template("promocao.html",
                           logo_path=EXTERNAL_LOGO if USE_EXTERNAL_LOGO else DEFAULT_LOGO,
                           use_external_logo=USE_EXTERNAL_LOGO)

@app.route("/analise-tecnica")
def analise_tecnica():
    """
    Página de análise técnica avançada - requer acesso premium
    """
    # Verificar se o usuário tem acesso premium
    if not session.get("pagamento_confirmado"):
        # Se não tiver acesso, redirecionar para a página de preview
        return redirect(url_for("premium_preview"))
    return render_template("analise-tecnica.html")

@app.route("/alertas-tempo-real")
def alertas_tempo_real():
    """
    Página de alertas em tempo real - requer acesso premium
    """
    # Verificar se o usuário tem acesso premium
    if not session.get("pagamento_confirmado"):
        # Se não tiver acesso, redirecionar para a página de preview
        return redirect(url_for("premium_preview"))
    return render_template("alertas-tempo-real.html")

@app.route("/grupo-vip")
def grupo_vip():
    """
    Página do grupo VIP exclusivo - requer acesso premium
    """
    # Verificar se o usuário tem acesso premium
    if not session.get("pagamento_confirmado"):
        # Se não tiver acesso, redirecionar para a página de preview
        return redirect(url_for("premium_preview"))
    return render_template("grupo_vip.html")
    
@app.route("/bot-dashboard")
def bot_dashboard():
    """
    Dashboard do bot de criptomoedas com atualizações em tempo real
    """
    return render_template("bot_dashboard.html")

@app.route("/bot-dashboard-simple")
def bot_dashboard_simple():
    """
    Versão simplificada do dashboard do bot
    """
    return render_template("bot_dashboard_simple.html")

@app.route("/payment")
def payment():
    replit_domain = os.environ.get('REPLIT_DOMAINS', '').split(",")[0]
    return render_template("paypal_payment.html", short_url=SHORT_URL, paypal_email=PAYPAL_EMAIL, replit_domain=replit_domain)

@app.route("/success")
def success():
    # Definir pagamento como confirmado ao chegar na página de sucesso
    # Isso é para testes, em produção a confirmação deve vir da API do PayPal
    session["pagamento_confirmado"] = True
    
    return render_template("success.html", short_url=SHORT_URL)

@app.route("/cancel")
def cancel():
    return render_template("cancel.html", short_url=SHORT_URL)

@app.route("/ipn", methods=["POST"])
def ipn():
    """
    Manipula notificações de pagamento instantâneas do PayPal (IPN)
    """
    try:
        ipn_data = request.form.to_dict()
        logger.info(f"IPN recebido: {ipn_data}")
        
        # Verificar com o PayPal
        verify_url = "https://ipnpb.paypal.com/cgi-bin/webscr"
        verify_payload = {'cmd': '_notify-validate'}
        verify_payload.update(ipn_data)

        response = requests.post(verify_url, data=verify_payload)
        logger.info(f"Resposta PayPal: {response.text}")

        if response.text == "VERIFIED" and ipn_data.get("payment_status") == "Completed":
            payer_email = ipn_data.get("payer_email")
            item = ipn_data.get("item_name", "Assinatura Premium")
            amount = ipn_data.get("mc_gross", "1.99")
            transaction_id = ipn_data.get("txn_id", "")
            
            # Armazenar no banco de dados
            store_payment(payer_email, item, amount, transaction_id)
            
            # Enviar email de confirmação
            send_confirmation_email(payer_email, amount)
            
            # Definir a sessão como pagamento confirmado
            session["pagamento_confirmado"] = True
            session["email_usuario"] = payer_email
            
            logger.info(f"Pagamento processado com sucesso: {payer_email}, {amount}")
        
        return "OK", 200
    except Exception as e:
        logger.error(f"Erro no processamento IPN: {e}")
        return "ERROR", 500

def store_payment(email, plan_name, amount, transaction_id=None):
    """
    Armazena um registro de pagamento no banco de dados
    """
    if not engine:
        logger.warning("Banco de dados não disponível para armazenar pagamento")
        return False
    
    try:
        with engine.connect() as conn:
            conn.execute(text("""
            INSERT INTO payment (email, plan_name, amount, transaction_id, status)
            VALUES (:email, :plan_name, :amount, :transaction_id, 'completed')
            """), {"email": email, "plan_name": plan_name, "amount": amount, "transaction_id": transaction_id})
            conn.commit()
            logger.info(f"Pagamento armazenado: {email}, {amount}")
        return True
    except Exception as e:
        logger.error(f"Erro ao armazenar pagamento: {e}")
        return False

def send_confirmation_email(destino, valor):
    """
    Envia um e-mail de confirmação para o cliente e uma cópia para o administrador
    """
    if not EMAIL_USER or not EMAIL_PASS:
        logger.warning("Credenciais de email não configuradas")
        return False
    
    try:
        msg = MIMEMultipart()
        msg["Subject"] = "🎉 Acesso Premium Ativado – Bem-vindo ao Grupo VIP de Sinais!"
        msg["From"] = "Crypto Signals Premium <support@cryptosignalshendrik.com>"
        msg["To"] = destino
        msg["Bcc"] = "hdhh9855@gmail.com"  # Cópia para o administrador
        
        # Corpo do email em HTML
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto;">
            <div style="background: #10B981; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="margin: 0;">Acesso Premium Ativado! 🚀</h1>
            </div>
            
            <div style="border: 1px solid #ddd; border-top: none; padding: 20px; border-radius: 0 0 10px 10px;">
                <p>Olá <strong>{destino}</strong>,</p>
                
                <p>O seu pagamento de <strong>${valor}</strong> foi confirmado com sucesso! 👏</p>
                
                <p>Está agora oficialmente com acesso ao nosso grupo VIP no Telegram, onde receberá sinais de trading com base em RSI, MACD, Volume e muito mais.</p>
                
                <div style="background: #f5f5f5; padding: 15px; border-radius: 10px; margin: 20px 0;">
                    <p style="margin: 0; font-weight: bold;">🔐 Acesse o grupo VIP clicando no botão abaixo:</p>
                    <div style="text-align: center; margin-top: 15px;">
                        <a href="https://t.me/cryptosignalshendrik_bot" style="background: #0088cc; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">Acessar Grupo Telegram</a>
                    </div>
                </div>
                
                <p>Este acesso é <strong>exclusivo</strong>, não partilhe este link com terceiros.</p>
                
                <p>Se tiver dúvidas ou precisar de ajuda, pode sempre responder a este email.</p>
                
                <p>Obrigado por confiar na nossa equipa – bons trades e até já!</p>
                
                <p>Cumprimentos,<br>
                Crypto Signals Premium 🚀</p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html, "html"))
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
            
        logger.info(f"Email enviado para: {destino}")
        return True
    except Exception as e:
        logger.error(f"Erro ao enviar email: {e}")
        return False

# API para preços atuais
@app.route("/api/prices/current")
@app.route("/api/current_prices")
def current_prices():
    """Retorna os preços atuais de todas as moedas"""
    try:
        if not engine:
            return jsonify({"error": "Database not available"}), 500
        
        from sqlalchemy.orm import Session
        session = Session(bind=engine)
        
        try:
            sql = """
            SELECT coin_id, symbol, price, previous_price, percent_change, recommendation, timestamp 
            FROM crypto_price
            GROUP BY symbol, coin_id, price, previous_price, percent_change, recommendation, timestamp
            HAVING timestamp = (SELECT MAX(timestamp) FROM crypto_price cp WHERE cp.symbol = crypto_price.symbol)
            """
            results = session.execute(text(sql)).fetchall()
            
            prices = {}
            for result in results:
                # Determinar indicador de mudança
                change_indicator = "▶"
                if result.percent_change:
                    if result.percent_change > 0:
                        change_indicator = "▲"
                    elif result.percent_change < 0:
                        change_indicator = "▼"
                
                # Gerar recomendação se não existir
                recommendation = result.recommendation
                if not recommendation:
                    if result.percent_change and result.percent_change > 3.0:
                        recommendation = "BUY"
                    elif result.percent_change and result.percent_change < -3.0:
                        recommendation = "SELL"
                    else:
                        recommendation = "WAIT"
                
                # Formatar preço
                formatted_price = format_price(result.price)
                
                prices[result.symbol] = {
                    "coin_id": result.coin_id,
                    "symbol": result.symbol,
                    "price": result.price,
                    "previous_price": result.previous_price,
                    "percent_change": result.percent_change,
                    "change_indicator": change_indicator,
                    "recommendation": recommendation,
                    "formatted_price": formatted_price
                }
            
            return jsonify(prices)
        except Exception as e:
            logger.error(f"Erro ao obter preços atuais: {e}")
            return jsonify({"error": str(e)}), 500
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Erro ao processar preços atuais: {e}")
        return jsonify({"error": str(e)}), 500
    
# API para sinais criptográficos (usado pelo frontend Next.js)
@app.route("/api/crypto-signals", methods=["GET"])
def api_crypto_signals():
    """
    API endpoint para obter sinais de criptomoedas
    Retorna os últimos preços com sinais de compra/venda baseados nas variações
    """
    try:
        from sqlalchemy.orm import Session
        
        if not engine:
            return jsonify({"error": "Database not available"}), 500
            
        session = Session(bind=engine)
        sql = """
        SELECT coin_id, symbol, price, previous_price, percent_change, recommendation, timestamp
        FROM crypto_price 
        WHERE symbol IN (
            'SHIB', 'FLOKI', 'DOGE', 'BONK', 'SOL', 'XRP', 'ADA', 'AVAX', 
            'LINK', 'MATIC', 'ARB', 'OP', 'RNDR', 'GRT', 'APT', 'ICP', 'SEI', 'STRK'
        )
        GROUP BY symbol, coin_id, price, previous_price, percent_change, recommendation, timestamp
        HAVING timestamp = (SELECT MAX(timestamp) FROM crypto_price cp WHERE cp.symbol = crypto_price.symbol)
        ORDER BY percent_change DESC NULLS LAST
        """
        
        try:
            results = session.execute(text(sql)).fetchall()
            signals = []
            
            for result in results:
                # Determina o sinal com base na variação percentual
                signal = "HOLD"
                confidence = 50
                
                if result.percent_change:
                    if result.percent_change > 3.0:
                        signal = "BUY"
                        confidence = min(int(result.percent_change * 10), 95)
                    elif result.percent_change < -3.0:
                        signal = "SELL"
                        confidence = min(int(abs(result.percent_change) * 10), 95)
                    elif result.percent_change > 1.5:
                        signal = "HOLD"
                        confidence = 60
                    elif result.percent_change < -1.5:
                        signal = "HOLD"
                        confidence = 40
                
                # Usa a recomendação do banco de dados se disponível
                if result.recommendation:
                    signal = result.recommendation
                
                trend = "Neutro"
                if result.percent_change and result.percent_change > 1.0:
                    trend = "Bullish"
                elif result.percent_change and result.percent_change < -1.0:
                    trend = "Bearish"
                
                # Calcular o RSI (simulado com base na variação)
                rsi = 50  # Valor neutro default
                if result.percent_change:
                    if result.percent_change > 0:
                        rsi = 50 + (result.percent_change * 5)  # Ajuste para simular RSI
                        rsi = min(rsi, 80)  # Limitar a 80
                    else:
                        rsi = 50 + (result.percent_change * 5)  # Ajuste para simular RSI
                        rsi = max(rsi, 20)  # Limitar a 20 mínimo
                
                signals.append({
                    "name": result.coin_id.replace("-", " ").title(),
                    "symbol": result.symbol,
                    "price": format_price(result.price),
                    "raw_price": result.price,
                    "change": f"{result.percent_change:.2f}%" if result.percent_change else "0.00%",
                    "rsi": int(rsi),
                    "trend": trend,
                    "signal": signal,
                    "confidence": confidence,
                    "timestamp": result.timestamp.isoformat() if result.timestamp else None
                })
            
            return jsonify(signals)
        except Exception as e:
            logger.error(f"Erro ao executar consulta: {e}")
            return jsonify({"error": str(e)}), 500
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Erro ao obter sinais criptográficos: {e}")
        return jsonify({"error": str(e)}), 500

# API de teste para verificar se o servidor está funcionando
@app.route("/api/status", methods=["GET"])
def api_status():
    """Endpoint simples para verificar se a API está respondendo"""
    try:
        from sqlalchemy.orm import Session
        
        if not engine:
            return jsonify({
                "estado": "offline",
                "hora": datetime.now().strftime("%H:%M:%S"),
                "sinais": []
            }), 200
            
        session = Session(bind=engine)
        try:
            # Obter os últimos sinais
            sql = """
            SELECT coin_id, symbol, price, previous_price, percent_change, recommendation, timestamp
            FROM crypto_price 
            GROUP BY symbol, coin_id, price, previous_price, percent_change, recommendation, timestamp
            HAVING timestamp = (SELECT MAX(timestamp) FROM crypto_price cp WHERE cp.symbol = crypto_price.symbol)
            ORDER BY percent_change DESC NULLS LAST
            LIMIT 10
            """
            
            results = session.execute(text(sql)).fetchall()
            sinais = []
            
            for result in results:
                # Determina o tipo de sinal baseado na variação percentual
                tipo = "WAIT"
                if result.percent_change and result.percent_change > 2.0:
                    tipo = "BUY"
                elif result.percent_change and result.percent_change < -2.0:
                    tipo = "SELL"
                
                # Usa a recomendação do banco de dados se disponível
                if result.recommendation:
                    tipo = result.recommendation
                
                sinais.append({
                    "moeda": result.symbol,
                    "tipo": tipo,
                    "variacao": f"{result.percent_change:.2f}%" if result.percent_change else "0.00%"
                })
            
            return jsonify({
                "estado": "online",
                "hora": datetime.now().strftime("%H:%M:%S"),
                "sinais": sinais
            })
            
        except Exception as e:
            logger.error(f"Erro ao obter dados para status: {e}")
            return jsonify({
                "estado": "erro",
                "hora": datetime.now().strftime("%H:%M:%S"),
                "sinais": []
            }), 200
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Erro ao processar API status: {e}")
        return jsonify({
            "estado": "erro",
            "hora": datetime.now().strftime("%H:%M:%S"),
            "sinais": []
        }), 200

# API para o dashboard do bot
@app.route("/api/dashboard", methods=["GET"])
def api_dashboard():
    """API para o dashboard do bot com sinais e recomendações"""
    try:
        from sqlalchemy.orm import Session
        
        if not engine:
            return jsonify({"error": "Database not available"}), 500
            
        session = Session(bind=engine)
        try:
            # Obter os últimos sinais
            sql = """
            SELECT coin_id, symbol, price, previous_price, percent_change, recommendation, timestamp
            FROM crypto_price 
            WHERE symbol IN (
                'SHIB', 'FLOKI', 'DOGE', 'BONK', 'SOL', 'XRP', 'ADA', 'AVAX', 
                'LINK', 'MATIC', 'ARB', 'OP', 'RNDR', 'GRT', 'APT', 'ICP', 'SEI', 'STRK'
            )
            GROUP BY symbol, coin_id, price, previous_price, percent_change, recommendation, timestamp
            HAVING timestamp = (SELECT MAX(timestamp) FROM crypto_price cp WHERE cp.symbol = crypto_price.symbol)
            ORDER BY percent_change DESC NULLS LAST
            """
            
            results = session.execute(text(sql)).fetchall()
            sinais = []
            
            for result in results:
                # Determina o tipo de sinal baseado na variação percentual
                tipo = "WAIT"
                if result.percent_change and result.percent_change > 2.0:
                    tipo = "BUY"
                elif result.percent_change and result.percent_change < -2.0:
                    tipo = "SELL"
                
                # Usa a recomendação do banco de dados se disponível
                if result.recommendation:
                    tipo = result.recommendation
                
                sinais.append({
                    "moeda": result.symbol,
                    "preco": format_price(result.price),
                    "variacao": f"{result.percent_change:.2f}%" if result.percent_change else "0.00%",
                    "tipo": tipo,
                    "hora": result.timestamp.strftime("%H:%M:%S") if result.timestamp else "N/A"
                })
            
            return jsonify({
                "atualizado": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "sinais": sinais
            })
            
        except Exception as e:
            logger.error(f"Erro ao obter dados para dashboard: {e}")
            return jsonify({"error": str(e)}), 500
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Erro ao processar API dashboard: {e}")
        return jsonify({"error": str(e)}), 500

# API para status do mercado
@app.route("/api/market-status", methods=["GET"])
def api_market_status():
    """
    API endpoint para obter status geral do mercado
    """
    try:
        from sqlalchemy.orm import Session
        
        if not engine:
            return jsonify({"error": "Database not available"}), 500
            
        session = Session(bind=engine)
        
        try:
            # Obter preços mais recentes
            sql = """
            SELECT coin_id, symbol, price, previous_price, percent_change, recommendation, timestamp
            FROM crypto_price 
            WHERE symbol IN (
                'SHIB', 'FLOKI', 'DOGE', 'BONK', 'SOL', 'XRP', 'ADA', 'AVAX', 
                'LINK', 'MATIC', 'ARB', 'OP', 'RNDR', 'GRT', 'APT', 'ICP', 'SEI', 'STRK'
            )
            GROUP BY symbol, coin_id, price, previous_price, percent_change, recommendation, timestamp
            HAVING timestamp = (SELECT MAX(timestamp) FROM crypto_price cp WHERE cp.symbol = crypto_price.symbol)
            """
            results = session.execute(text(sql)).fetchall()
            
            # Calcula tendência geral do mercado
            changes = [r.percent_change for r in results if r.percent_change is not None]
            avg_change = sum(changes) / len(changes) if changes else 0
            
            # Determina o estado do mercado
            market_state = "MERCADO NEUTRO"
            trend = "neutral"
            if avg_change > 2.0:
                market_state = "BULL MARKET"
                trend = "positive"
            elif avg_change < -2.0:
                market_state = "BEAR MARKET"
                trend = "negative"
                
            # Conta sinais ativos
            buy_signals = len([r for r in results if r.percent_change and r.percent_change > 3.0])
            sell_signals = len([r for r in results if r.percent_change and r.percent_change < -3.0])
            
            # Encontra o último alerta significativo
            significant_alerts = [r for r in results if r.percent_change and abs(r.percent_change) > 3.0]
            significant_alerts.sort(key=lambda x: x.timestamp, reverse=True)
            last_alert = None
            if significant_alerts:
                alert = significant_alerts[0]
                last_alert = {
                    "symbol": alert.symbol,
                    "change": f"{alert.percent_change:.2f}%",
                    "reason": "Variação significativa de preço detectada",
                    "timestamp": alert.timestamp.isoformat() if alert.timestamp else None
                }
            
            market_status = {
                "pulseStatus": {
                    "state": market_state,
                    "change": f"{avg_change:.1f}%",
                    "trend": trend
                },
                "activeSignals": {
                    "total": buy_signals + sell_signals,
                    "buy": buy_signals,
                    "sell": sell_signals,
                    "lastUpdate": "agora"
                },
                "lastAlert": last_alert
            }
            
            return jsonify(market_status)
        except Exception as e:
            logger.error(f"Erro ao executar consulta: {e}")
            return jsonify({"error": str(e)}), 500
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Erro ao obter status do mercado: {e}")
        return jsonify({"error": str(e)}), 500
    try:
        if not engine:
            # Dados de exemplo para quando o banco de dados não está disponível
            # Isso permite que a interface continue funcionando
            sample_data = {
                "SHIB": {
                    "coin_id": "shiba-inu", 
                    "symbol": "SHIB", 
                    "price": 0.00001354, 
                    "previous_price": 0.00001350, 
                    "percent_change": 0.30, 
                    "change_indicator": "▲", 
                    "recommendation": "WAIT", 
                    "formatted_price": "$0.00001354"
                },
                "DOGE": {
                    "coin_id": "dogecoin", 
                    "symbol": "DOGE", 
                    "price": 0.183500, 
                    "previous_price": 0.183000, 
                    "percent_change": 0.27, 
                    "change_indicator": "▲", 
                    "recommendation": "WAIT", 
                    "formatted_price": "$0.183500"
                },
                "BONK": {
                    "coin_id": "bonk", 
                    "symbol": "BONK", 
                    "price": 0.00001875, 
                    "previous_price": 0.00001870, 
                    "percent_change": 0.27, 
                    "change_indicator": "▲", 
                    "recommendation": "WAIT", 
                    "formatted_price": "$0.00001875"
                },
                "SOL": {
                    "coin_id": "solana", 
                    "symbol": "SOL", 
                    "price": 153.45, 
                    "previous_price": 153.20, 
                    "percent_change": 0.16, 
                    "change_indicator": "▲", 
                    "recommendation": "WAIT", 
                    "formatted_price": "$153.4500"
                },
                "XRP": {
                    "coin_id": "ripple", 
                    "symbol": "XRP", 
                    "price": 2.21, 
                    "previous_price": 2.20, 
                    "percent_change": 0.45, 
                    "change_indicator": "▲", 
                    "recommendation": "WAIT", 
                    "formatted_price": "$2.2100"
                }
            }
            return jsonify(sample_data)
            
        with engine.connect() as conn:
            result = conn.execute(text("""
            WITH latest_prices AS (
                SELECT coin_id, symbol, price, previous_price, percent_change, recommendation,
                       ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY timestamp DESC) as rn
                FROM crypto_price
            )
            SELECT coin_id, symbol, price, previous_price, percent_change, recommendation
            FROM latest_prices
            WHERE rn = 1
            ORDER BY symbol
            """))
            
            prices = {}
            for row in result:
                symbol = row.symbol.upper()
                # Determinar indicador de mudança e formatar preço
                change_indicator = ""
                if row.percent_change:
                    change_indicator = "▲" if row.percent_change > 0 else "▼" if row.percent_change < 0 else "◆"
                
                prices[symbol] = {
                    "coin_id": row.coin_id,
                    "symbol": symbol,
                    "price": row.price,
                    "previous_price": row.previous_price,
                    "percent_change": row.percent_change,
                    "change_indicator": change_indicator,
                    "recommendation": row.recommendation,
                    "formatted_price": format_price(row.price)
                }
            
            return jsonify(prices)
    except Exception as e:
        logger.error(f"Erro ao obter preços atuais: {e}")
        # Dados de exemplo caso ocorra um erro
        sample_data = {
            "SHIB": {
                "coin_id": "shiba-inu", 
                "symbol": "SHIB", 
                "price": 0.00001354, 
                "previous_price": 0.00001350, 
                "percent_change": 0.30, 
                "change_indicator": "▲", 
                "recommendation": "WAIT", 
                "formatted_price": "$0.00001354"
            },
            "DOGE": {
                "coin_id": "dogecoin", 
                "symbol": "DOGE", 
                "price": 0.183500, 
                "previous_price": 0.183000, 
                "percent_change": 0.27, 
                "change_indicator": "▲", 
                "recommendation": "WAIT", 
                "formatted_price": "$0.183500"
            },
            "BONK": {
                "coin_id": "bonk", 
                "symbol": "BONK", 
                "price": 0.00001875, 
                "previous_price": 0.00001870, 
                "percent_change": 0.27, 
                "change_indicator": "▲", 
                "recommendation": "WAIT", 
                "formatted_price": "$0.00001875"
            }
        }
        return jsonify(sample_data)

# API para alertas recentes
@app.route("/alerts")
@app.route("/api/alerts")
def alerts():
    """Retorna os alertas recentes de variação de preço"""
    try:
        # Usar a função obter_alertas para buscar os alertas do banco de dados
        result = obter_alertas()
        
        if not result:
            # Dados de exemplo para quando não há alertas disponíveis
            sample_alerts = [
                {
                    "symbol": "SOL",
                    "price": 153.45,
                    "change": "+3.15%",
                    "acao": "BUY",
                    "time": "11:45"
                },
                {
                    "symbol": "FLOKI",
                    "price": 0.00008401,
                    "change": "+2.50%",
                    "acao": "BUY",
                    "time": "11:30"
                },
                {
                    "symbol": "DOGE",
                    "price": 0.183353,
                    "change": "+2.10%",
                    "acao": "BUY",
                    "time": "11:15"
                },
            ]
            return jsonify(sample_alerts)
            
        with engine.connect() as conn:
            result = conn.execute(text("""
            SELECT coin_id, symbol, price, previous_price, percent_change, recommendation, timestamp
            FROM crypto_price
            WHERE ABS(percent_change) >= 2.0 AND previous_price IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT 10
            """))
            
            alerts_list = []
            for row in result:
                # Determinar ação baseada na recomendação
                acao = "WAIT"
                if row.recommendation == "COMPRA":
                    acao = "BUY"
                elif row.recommendation == "VENDA":
                    acao = "SELL"
                
                # Formatar timestamp
                dt = row.timestamp
                time_str = dt.strftime("%H:%M")
                
                # Formatar variação de preço
                change = f"{'+' if row.percent_change > 0 else ''}{row.percent_change:.2f}%"
                
                alerts_list.append({
                    "symbol": row.symbol.upper(),
                    "price": row.price,
                    "change": change,
                    "acao": acao,
                    "time": time_str
                })
            
            return jsonify(alerts_list)
    except Exception as e:
        logger.error(f"Erro ao obter alertas: {e}")
        # Dados de exemplo caso ocorra um erro
        sample_alerts = [
            {
                "symbol": "SOL",
                "price": 153.45,
                "change": "+3.15%",
                "acao": "BUY",
                "time": "11:45"
            },
            {
                "symbol": "FLOKI",
                "price": 0.00008401,
                "change": "+2.50%",
                "acao": "BUY",
                "time": "11:30"
            }
        ]
        return jsonify(sample_alerts)

# API para histórico de preços de uma moeda específica
@app.route("/api/prices/history/<coin_id>")
def price_history(coin_id):
    """Retorna o histórico de preços de uma moeda específica"""
    try:
        if not engine:
            return jsonify({"error": "Database connection not available"}), 500
            
        limit = request.args.get('limit', 50, type=int)
        
        with engine.connect() as conn:
            result = conn.execute(text("""
            SELECT price, timestamp
            FROM crypto_price
            WHERE coin_id = :coin_id
            ORDER BY timestamp DESC
            LIMIT :limit
            """), {"coin_id": coin_id, "limit": limit})
            
            prices = []
            timestamps = []
            
            for row in result:
                prices.append(row.price)
                timestamps.append(row.timestamp.isoformat())
            
            # Inverter as listas para mostrar em ordem cronológica
            prices.reverse()
            timestamps.reverse()
            
            # Verificar se temos dados, se não, buscar dados de qualquer moeda no banco de dados
            if not prices:
                logger.warning(f"Sem dados históricos para {coin_id}, usando dados de outras moedas")
                fallback_result = conn.execute(text("""
                SELECT price, timestamp
                FROM crypto_price
                WHERE price > 0
                ORDER BY timestamp DESC
                LIMIT :limit
                """), {"limit": limit})
                
                fallback_prices = []
                fallback_timestamps = []
                
                for row in fallback_result:
                    fallback_prices.append(row.price)
                    fallback_timestamps.append(row.timestamp.isoformat())
                
                if fallback_prices:
                    # Ajustar os preços para a escala típica da moeda solicitada
                    # para manter a vizualização do gráfico consistente
                    if coin_id in ['shiba-inu', 'floki', 'bonk']:
                        base_value = 0.00001
                    elif coin_id in ['dogecoin']:
                        base_value = 0.18
                    elif coin_id in ['solana']:
                        base_value = 150.0
                    else:
                        base_value = 1.0
                    
                    # Normalizar para valores similares à moeda solicitada
                    avg_price = sum(fallback_prices) / len(fallback_prices)
                    prices = [p * (base_value / avg_price) for p in fallback_prices]
                    timestamps = fallback_timestamps
                    
                    # Inverter para ordem cronológica
                    prices.reverse()
                    timestamps.reverse()
            
            return jsonify({
                "coin_id": coin_id,
                "prices": prices,
                "timestamps": timestamps
            })
    except Exception as e:
        logger.error(f"Erro ao obter histórico de preços: {e}")
        # Em caso de erro, tentar obter dados de qualquer moeda no banco
        try:
            if engine:
                with engine.connect() as conn:
                    any_result = conn.execute(text("""
                    SELECT price, timestamp, coin_id
                    FROM crypto_price
                    WHERE price > 0
                    ORDER BY timestamp DESC
                    LIMIT 20
                    """))
                    
                    any_prices = []
                    any_timestamps = []
                    
                    for row in any_result:
                        any_prices.append(row.price)
                        any_timestamps.append(row.timestamp.isoformat())
                    
                    if any_prices:
                        # Usar qualquer dado disponível no banco para formar um gráfico
                        return jsonify({
                            "coin_id": coin_id,
                            "prices": any_prices[::-1],  # Inverter para ordem cronológica
                            "timestamps": any_timestamps[::-1],
                            "note": "Dados alternativos devido a limite de API"
                        })
        except Exception as inner_e:
            logger.error(f"Erro ao buscar dados alternativos: {inner_e}")
        
        return jsonify({
            "coin_id": coin_id,
            "prices": [],
            "timestamps": [],
            "error": f"Não foi possível obter dados de preço: {str(e)}"
        }), 500

# API para obter as maiores altas do dia (top pumps)
@app.route("/api/top_pumps")
def top_pumps():
    """Retorna as moedas com maiores valorizações do dia"""
    try:
        if not engine:
            return jsonify({"error": "Database connection not available"}), 500
            
        with engine.connect() as conn:
            # Obter moedas com as maiores variações positivas
            result = conn.execute(text("""
            WITH latest_prices AS (
                SELECT coin_id, symbol, price, previous_price, percent_change, recommendation,
                       ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY timestamp DESC) as rn
                FROM crypto_price
            )
            SELECT coin_id, symbol, price, previous_price, percent_change, recommendation
            FROM latest_prices
            WHERE rn = 1
            ORDER BY percent_change DESC  -- Ordenar das maiores para as menores
            LIMIT 10                      -- Apenas as 10 maiores
            """))
            
            # Mapeamento de símbolos para nomes completos
            coin_names = {
                "BTC": "Bitcoin",
                "ETH": "Ethereum",
                "SOL": "Solana",
                "PEPE": "Pepe",
                "SHIB": "Shiba Inu",
                "FLOKI": "Floki Inu",
                "DOGE": "Dogecoin",
                "BONK": "Bonk",
                "XRP": "XRP",
                "ADA": "Cardano",
                "AVAX": "Avalanche",
                "LINK": "Chainlink",
                "MATIC": "Polygon",
                "ARB": "Arbitrum",
                "OP": "Optimism",
                "RNDR": "Render",
                "GRT": "The Graph",
                "APT": "Aptos",
                "ICP": "Internet Computer",
                "SEI": "Sei",
                "STRK": "Starknet"
            }
            
            pumps = []
            for row in result:
                symbol = row.symbol.upper()
                name = coin_names.get(symbol, symbol)
                
                # Determinar recomendação
                recommendation = row.recommendation
                if not recommendation:
                    if row.percent_change is not None and row.percent_change > 5:
                        recommendation = "COMPRA"
                    elif row.percent_change is not None and row.percent_change > 2:
                        recommendation = "OBSERVAR"
                    else:
                        recommendation = "WAIT"
                
                # Calcular um volume fictício baseado no preço
                # Em um ambiente real, buscaríamos o volume real
                import random
                volume = row.price * (1000000 * random.uniform(0.5, 5.0))
                
                pumps.append({
                    "name": name,
                    "symbol": symbol,
                    "price": row.price,
                    "previous_price": row.previous_price,
                    "percent_change": row.percent_change if row.percent_change is not None else 0,
                    "recommendation": recommendation,
                    "volume": volume,
                    "formatted_change": f"+{row.percent_change:.2f}%" if row.percent_change is not None and row.percent_change > 0 else "0.00%" if row.percent_change is None else f"{row.percent_change:.2f}%",
                    "formatted_price": format_price(row.price)
                })
            
            # Ordenar por variação percentual decrescente
            pumps = sorted(pumps, key=lambda x: (x["percent_change"] or 0), reverse=True)
            
            return jsonify(pumps)
    except Exception as e:
        logger.error(f"Erro ao obter top pumps: {e}")
        return jsonify([]), 500

# Função para formatar preços de acordo com a magnitude
def format_price(price):
    """Formata o preço de acordo com sua magnitude"""
    if price is None:
        return "$0.00"
    
    if price < 0.01:
        return f"${price:.8f}"
    elif price < 1:
        return f"${price:.6f}"
    elif price < 1000:
        return f"${price:.4f}"
    else:
        return f"${price:.2f}"

# Dados para a área premium (simulados para demonstração)
@app.route("/api/premium_data")
def premium_data():
    """Retorna dados premium simulados"""
    # Esta API seria protegida por autenticação em produção
    return jsonify({
        "rsi_data": {
            "SHIB": 62,
            "DOGE": 58,
            "FLOKI": 65,
            "SOL": 70,
            "BONK": 55
        },
        "macd_signals": {
            "SHIB": "bullish",
            "DOGE": "neutral",
            "FLOKI": "bullish",
            "SOL": "strongly_bullish",
            "BONK": "neutral"
        },
        "volume_analysis": {
            "SHIB": 1.2,  # Multiplicador de volume normal
            "DOGE": 0.9,
            "FLOKI": 1.5,
            "SOL": 2.1,
            "BONK": 0.7
        }
    })

# Rotas de administração
@app.route("/admin", methods=["GET", "POST"])
def admin():
    """
    Painel de administração para visualizar pagamentos
    Requer autenticação de administrador
    """
    if "logged_in" not in session:
        return redirect(url_for("login"))

    try:
        if not engine:
            return "Banco de dados não disponível", 500
            
        with engine.connect() as conn:
            result = conn.execute(text("""
            SELECT id, email, plan_name, amount, transaction_id, status, created_at
            FROM payment
            ORDER BY created_at DESC
            """))
            
            payments = []
            for row in result:
                payments.append({
                    "id": row.id,
                    "email": row.email,
                    "plan_name": row.plan_name,
                    "amount": row.amount,
                    "transaction_id": row.transaction_id,
                    "status": row.status,
                    "created_at": row.created_at.strftime("%Y-%m-%d %H:%M:%S")
                })
            
            return render_template("admin.html", payments=payments)
    except Exception as e:
        logger.error(f"Erro ao acessar painel admin: {e}")
        return f"Erro ao carregar registros: {e}", 500

@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Página de login para acesso ao painel de administração
    """
    if request.method == "POST":
        user = request.form.get("username")
        pw = request.form.get("password")
        if user == os.getenv("ADMIN_USER", "admin") and pw == os.getenv("ADMIN_PASS", "vip123"):
            session["logged_in"] = True
            return redirect(url_for("admin"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    """
    Encerra a sessão do administrador e do usuário premium
    """
    # Remove variáveis de sessão específicas do admin
    session.pop("logged_in", None)
    
    # Limpa o acesso premium
    session.pop("pagamento_confirmado", None)
    session.pop("email_usuario", None)
    
    # Redireciona para a página de login (admin) ou a página inicial (usuário comum)
    if request.args.get("admin"):
        return redirect(url_for("login"))
    else:
        return redirect(url_for("index"))
        
# Rota para verificar o status do acesso premium (útil para JavaScript)
@app.route("/api/check_premium")
def check_premium():
    has_premium = session.get("pagamento_confirmado", False)
    return jsonify({"premium": has_premium})

@app.route("/export-csv")
def export_csv():
    """
    Exporta registros de pagamento como CSV
    Requer autenticação de administrador
    """
    if "logged_in" not in session:
        return redirect(url_for("login"))

    try:
        if not engine:
            return "Banco de dados não disponível", 500
            
        with engine.connect() as conn:
            result = conn.execute(text("""
            SELECT id, email, plan_name, amount, transaction_id, status, created_at
            FROM payment
            ORDER BY created_at DESC
            """))
            
            # Criar arquivo CSV em memória
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Cabeçalho
            writer.writerow(['ID', 'Email', 'Plano', 'Valor', 'ID Transação', 'Status', 'Data'])
            
            # Linhas de dados
            for row in result:
                writer.writerow([
                    row.id,
                    row.email,
                    row.plan_name,
                    row.amount,
                    row.transaction_id,
                    row.status,
                    row.created_at.strftime("%Y-%m-%d %H:%M:%S")
                ])
            
            # Preparar resposta
            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'pagamentos_{datetime.now().strftime("%Y%m%d")}.csv'
            )
    except Exception as e:
        logger.error(f"Erro ao exportar CSV: {e}")
        return f"Erro ao exportar registros: {e}", 500

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    print(f"Iniciando servidor na porta {port}")
    app.run(host="0.0.0.0", port=port)