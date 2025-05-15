#!/bin/bash

# Define a porta como 3000 para garantir compatibilidade com o deploy
export PORT=3000
echo "Iniciando servidor na porta $PORT..."

# Inicia o Gunicorn na porta definida
exec gunicorn --bind "0.0.0.0:$PORT" --log-level info --timeout 120 main:app