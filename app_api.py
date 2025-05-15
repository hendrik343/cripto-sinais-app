from flask import Flask, redirect, jsonify

# Rotas da API para uso básico, com páginas HTML incorporadas para facilitar o preview

app = Flask(__name__)

@app.route("/")
def index():
    return """
    <html>
      <head>
        <title>CriptoSinais API</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
          body {
            font-family: sans-serif;
            background-color: #0f172a;
            color: white;
            margin: 0;
            padding: 20px;
            text-align: center;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
          }
          .container {
            max-width: 800px;
            width: 100%;
            background-color: rgba(30, 41, 59, 0.8);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
          }
          h1 {
            color: #fcd34d;
            font-size: 2.5rem;
            margin-bottom: 10px;
          }
          h2 {
            color: #a3e635;
            font-weight: normal;
            margin-top: 0;
          }
          .status {
            display: inline-block;
            background-color: #22c55e;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            margin: 20px 0;
            font-weight: bold;
          }
          .links {
            margin-top: 30px;
            display: flex;
            justify-content: center;
            gap: 15px;
          }
          .btn {
            display: inline-block;
            background-color: #3b82f6;
            color: white;
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 5px;
            font-weight: bold;
            transition: all 0.3s ease;
          }
          .btn:hover {
            background-color: #2563eb;
            transform: translateY(-2px);
          }
          .version {
            margin-top: 30px;
            color: #64748b;
            font-size: 0.8rem;
          }
          .api-json {
            background-color: rgba(15, 23, 42, 0.7);
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
            text-align: left;
            font-family: monospace;
            color: #a5f3fc;
          }
        </style>
      </head>
      <body>
        <div class="container">
          <h1>📊 CriptoSinais</h1>
          <h2>Monitoramento de Criptomoedas</h2>
          <div class="status">Online</div>
          
          <div class="api-json">
            {<br>
            &nbsp;&nbsp;"message": "API online!",<br>
            &nbsp;&nbsp;"status": "online"<br>
            }
          </div>
          
          <p>O servidor de monitoramento de criptomoedas está funcionando normalmente.</p>
          
          <div class="links">
            <a href="/dashboard" class="btn">Dashboard</a>
            <a href="/premium" class="btn">Área Premium</a>
          </div>
          
          <div class="version">
            Versão 1.0.0
          </div>
        </div>
      </body>
    </html>
    """

@app.route("/preview")
def preview():
    return redirect("/dashboard")

@app.route("/dashboard")
def dashboard():
    return """
    <html>
      <head>
        <title>CriptoSinais Dashboard</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
          body {
            font-family: sans-serif;
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
            font-weight: bold;
          }
          .crypto-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            text-align: left;
          }
          .crypto-table th {
            background-color: rgba(15, 23, 42, 0.7);
            padding: 10px;
            font-weight: bold;
            color: #a3e635;
          }
          .crypto-table td {
            padding: 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
          }
          .crypto-table tr:last-child td {
            border-bottom: none;
          }
          .price {
            color: #38bdf8;
            font-weight: bold;
          }
          .positive {
            color: #4ade80;
          }
          .negative {
            color: #f87171;
          }
          .badge {
            display: inline-block;
            background-color: #8b5cf6;
            color: white;
            padding: 2px 8px;
            border-radius: 20px;
            font-size: 12px;
            margin-left: 5px;
          }
          .updated {
            margin-top: 20px;
            color: #64748b;
            font-size: 0.8rem;
          }
          .links {
            margin-top: 30px;
            display: flex;
            justify-content: center;
            gap: 15px;
          }
          .btn {
            display: inline-block;
            background-color: #3b82f6;
            color: white;
            text-decoration: none;
            padding: 8px 15px;
            border-radius: 5px;
            font-weight: bold;
            transition: all 0.3s ease;
          }
          .btn:hover {
            background-color: #2563eb;
            transform: translateY(-2px);
          }
          .premium-btn {
            background-color: #8b5cf6;
          }
          .premium-btn:hover {
            background-color: #7c3aed;
          }
        </style>
      </head>
      <body>
        <div class="container">
          <h1>📊 CriptoSinais Dashboard</h1>
          <div class="status">Online</div>
          
          <table class="crypto-table">
            <thead>
              <tr>
                <th>Moeda</th>
                <th>Preço</th>
                <th>Variação</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Bitcoin (BTC)</td>
                <td class="price">$45,000.00</td>
                <td class="positive">+1.2%</td>
              </tr>
              <tr>
                <td>Solana (SOL)</td>
                <td class="price">$171.80</td>
                <td class="negative">-0.04%</td>
              </tr>
              <tr>
                <td>Dogecoin (DOGE)</td>
                <td class="price">$0.227310</td>
                <td class="negative">-0.04%</td>
              </tr>
              <tr>
                <td>Shiba Inu (SHIB)</td>
                <td class="price">$0.00001512</td>
                <td class="positive">+0.0%</td>
              </tr>
              <tr>
                <td>Floki (FLOKI) <span class="badge">HOT</span></td>
                <td class="price">$0.00010410</td>
                <td class="positive">+0.5%</td>
              </tr>
            </tbody>
          </table>
          
          <div class="updated">
            Última atualização: 09:45:00
          </div>
          
          <div class="links">
            <a href="/" class="btn">Início</a>
            <a href="/premium" class="btn premium-btn">Área Premium</a>
          </div>
        </div>
      </body>
    </html>
    """

# Para execução standalone
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    print(f"Iniciando servidor na porta {port}")
    app.run(host="0.0.0.0", port=port)