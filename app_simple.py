from flask import Flask, render_template, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "segredo"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/dashboard-futuristic")
def dashboard_futuristic():
    return render_template("dashboard_futuristic.html")

@app.route("/dashboard-futuristic-alt")
def dashboard_futuristic_alt():
    return render_template("dashboard_futuristic_alt.html")

@app.route("/premium")
def premium():
    if session.get("pagamento_confirmado"):
        return render_template("premium.html")
    else:
        return redirect("/premium-preview")

@app.route("/premium-preview")
def premium_preview():
    return render_template("preview.html")

@app.route("/premium-futuristic")
def premium_futuristic():
    if session.get("pagamento_confirmado"):
        return render_template("premium_futuristic.html")
    else:
        return redirect("/premium-preview-futuristic")

@app.route("/premium-preview-futuristic")
def premium_preview_futuristic():
    return render_template("premium_futuristic.html")

@app.route("/payment", methods=["GET", "POST"])
def payment():
    # Simulação de processamento de pagamento
    if session.get("pagamento_confirmado"):
        return redirect("/premium")
    
    # Em uma situação real, aqui seria o código para processar o pagamento
    # Após o pagamento bem-sucedido, definiríamos a sessão
    
    return render_template("payment.html")

@app.route("/success")
def success():
    # Simulando pagamento bem-sucedido
    session["pagamento_confirmado"] = True
    return render_template("success.html")

@app.route("/cancel")
def cancel():
    return render_template("cancel.html")

# Rota para simular o login (para fins de teste)
@app.route("/simulate-login")
def simulate_login():
    session["pagamento_confirmado"] = True
    return redirect("/premium")

# Rota para simular o logout (para fins de teste)
@app.route("/simulate-logout")
def simulate_logout():
    session.pop("pagamento_confirmado", None)
    return redirect("/premium-preview")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)