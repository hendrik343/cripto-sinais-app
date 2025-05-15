// Servidor Node.js simples para funcionar como ponto de entrada
const express = require('express');
const { exec } = require('child_process');
const app = express();
const PORT = process.env.PORT || 3000;

// Inicia o servidor Flask em segundo plano
const startFlaskServer = () => {
  console.log('Iniciando servidor Flask em segundo plano...');
  const flaskServer = exec('python main.py');
  
  flaskServer.stdout.on('data', (data) => {
    console.log(`Flask stdout: ${data}`);
  });
  
  flaskServer.stderr.on('data', (data) => {
    console.error(`Flask stderr: ${data}`);
  });
  
  flaskServer.on('close', (code) => {
    console.log(`Servidor Flask encerrado com código ${code}`);
  });
};

// Iniciar o servidor Flask quando o Node.js iniciar
startFlaskServer();

// Rota principal
app.get('/', (req, res) => {
  res.send(`
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
        <h1>CriptoSinais</h1>
        <p>Bem-vindo ao monitor de criptomoedas</p>
        <div class="links">
          <a href="/dashboard">Dashboard</a>
          <a href="/api/status">Status da API</a>
        </div>
      </div>
    </body>
    </html>
  `);
});

// Redirecionamento para o dashboard
app.get('/dashboard', (req, res) => {
  res.redirect('http://localhost:5000/dashboard');
});

// Redirecionamento para a API
app.get('/api/status', (req, res) => {
  res.redirect('http://localhost:5000/health');
});

// Iniciar o servidor
app.listen(PORT, () => {
  console.log(`Servidor Node.js rodando na porta ${PORT}`);
});