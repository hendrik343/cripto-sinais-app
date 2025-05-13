from flask import Flask, jsonify, render_template
import requests

app = Flask(__name__)

@app.route("/")
def index():
    """Página principal de teste da API"""
    return render_template("test_api.html")

@app.route("/test-api")
def test_api():
    """Endpoint para testar a conexão com a API do CoinGecko"""
    try:
        response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd")
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": f"API CoinGecko não está a responder. Status code: {response.status_code}"}), 500
    except Exception as e:
        return jsonify({"error": f"Erro ao conectar à API: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)