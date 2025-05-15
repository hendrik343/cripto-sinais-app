from flask import Flask, redirect, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify({"message": "API online!", "status": "online"})

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
        </style>
      </head>
      <body>
        <div class="container">
          <h1>📊 CriptoSinais Dashboard</h1>
          <div class="status">Online</div>
          <p>Servidor de monitoramento de criptomoedas funcionando normalmente.</p>
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