import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CriptoSinais</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #0f172a;
                color: white;
                margin: 0;
                padding: 20px;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .container {
                background-color: rgba(30, 41, 59, 0.8);
                border-radius: 10px;
                padding: 40px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
                max-width: 800px;
                width: 100%;
                text-align: center;
            }
            h1 {
                color: #fcd34d;
                margin-bottom: 20px;
            }
            .status {
                display: inline-block;
                background-color: #22c55e;
                color: white;
                padding: 8px 20px;
                border-radius: 50px;
                font-weight: bold;
                margin: 20px 0;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            th {
                background-color: rgba(15, 23, 42, 0.7);
                padding: 12px;
                text-align: left;
                color: #a3e635;
            }
            td {
                padding: 12px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                text-align: left;
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
            .hot {
                background-color: #8b5cf6;
                color: white;
                padding: 2px 8px;
                border-radius: 20px;
                font-size: 12px;
                margin-left: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>CriptoSinais Dashboard</h1>
            <div class="status">Servidor Online</div>
            <table>
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
                        <td class="price">$170.74</td>
                        <td class="negative">-0.21%</td>
                    </tr>
                    <tr>
                        <td>Dogecoin (DOGE)</td>
                        <td class="price">$0.224889</td>
                        <td class="negative">-0.04%</td>
                    </tr>
                    <tr>
                        <td>Shiba Inu (SHIB)</td>
                        <td class="price">$0.00001498</td>
                        <td class="negative">-0.33%</td>
                    </tr>
                    <tr>
                        <td>Floki <span class="hot">HOT</span></td>
                        <td class="price">$0.00010304</td>
                        <td class="negative">-0.72%</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)