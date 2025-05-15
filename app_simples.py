from flask import Flask, redirect, jsonify, render_template
import os

app = Flask(__name__)

# Health check simples na raiz
@app.route('/')
def health():
    return jsonify({"message": "API online!", "status": "online"})

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
        return "<h1>Bem-vindo ao CriptoSinais!</h1><p>Painel de controlo a funcionar.</p>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    print(f"Iniciando servidor na porta {port}")
    app.run(host="0.0.0.0", port=port)