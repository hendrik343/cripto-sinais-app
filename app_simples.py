from flask import Flask, redirect, jsonify, render_template, send_from_directory
import os

app = Flask(__name__)

# Health check simples na raiz
@app.route('/')
def health():
    return """
    <html>
    <head>
        <title>CriptoSinais API</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #0f172a;
                color: white;
                margin: 0;
                padding: 20px;
                text-align: center;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background-color: rgba(30, 41, 59, 0.8);
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            h1 {
                color: #fcd34d;
            }
            .status {
                display: inline-block;
                background-color: #22c55e;
                color: white;
                padding: 5px 15px;
                border-radius: 20px;
                margin: 20px 0;
            }
            .links {
                display: flex;
                justify-content: center;
                gap: 20px;
                margin-top: 30px;
            }
            a {
                display: inline-block;
                background-color: #38bdf8;
                color: white;
                text-decoration: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                transition: background-color 0.3s;
            }
            a:hover {
                background-color: #0284c7;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>CriptoSinais API</h1>
            <div class="status">Online</div>
            <p>API de monitoramento de criptomoedas está funcionando corretamente.</p>
            <div class="links">
                <a href="/dashboard">Dashboard</a>
                <a href="/health">Status</a>
            </div>
        </div>
    </body>
    </html>
    """

# Rota para o ícone do favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Rota específica para preview da app no browser
@app.route('/preview')
def preview():
    return redirect("/dashboard")

# Simulando o dashboard
@app.route('/dashboard')
def dashboard():
    try:
        return render_template("dashboard.html")
    except:
        return """
        <html>
        <head>
            <title>Dashboard CriptoSinais</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #0f172a;
                    color: white;
                    margin: 0;
                    padding: 20px;
                }
                .container {
                    max-width: 800px;
                    margin: 0 auto;
                    background-color: rgba(30, 41, 59, 0.8);
                    border-radius: 10px;
                    padding: 20px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }
                h1 {
                    color: #fcd34d;
                    text-align: center;
                }
                .card {
                    background-color: rgba(15, 23, 42, 0.7);
                    border-radius: 8px;
                    padding: 15px;
                    margin-bottom: 15px;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }
                .crypto-row {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                    padding: 10px 0;
                }
                .name {
                    font-weight: bold;
                }
                .price {
                    color: #38bdf8;
                }
                .change.positive {
                    color: #4ade80;
                }
                .change.negative {
                    color: #f87171;
                }
                .badge {
                    background-color: #22c55e;
                    color: white;
                    border-radius: 20px;
                    padding: 5px 10px;
                    font-size: 12px;
                    margin-left: 10px;
                }
                .header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 20px;
                }
                .updated {
                    font-size: 12px;
                    color: #94a3b8;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>CriptoSinais Dashboard</h1>
                    <div class="updated">Última atualização: 09:42:10</div>
                </div>
                
                <div class="card">
                    <h3>Top Cryptocurrencies</h3>
                    <div class="crypto-row">
                        <div class="name">Bitcoin (BTC)</div>
                        <div class="price">$45,000.00</div>
                        <div class="change positive">+1.2%</div>
                    </div>
                    <div class="crypto-row">
                        <div class="name">Solana (SOL)</div>
                        <div class="price">$171.80</div>
                        <div class="change negative">-0.04%</div>
                    </div>
                    <div class="crypto-row">
                        <div class="name">Dogecoin (DOGE)</div>
                        <div class="price">$0.227310</div>
                        <div class="change negative">-0.04%</div>
                    </div>
                    <div class="crypto-row">
                        <div class="name">Shiba Inu (SHIB)</div>
                        <div class="price">$0.00001512</div>
                        <div class="change positive">+0.0%</div>
                    </div>
                    <div class="crypto-row">
                        <div class="name">Floki (FLOKI)</div>
                        <div class="price">$0.00010410</div>
                        <div class="badge">HOT</div>
                        <div class="change positive">+0.5%</div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    print(f"Iniciando servidor na porta {port}")
    app.run(host="0.0.0.0", port=port)