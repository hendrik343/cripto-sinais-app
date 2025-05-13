from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
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

# Garante que o Flask está a correr
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)