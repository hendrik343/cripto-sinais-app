#!/bin/bash

# Define a porta padrão como 3000 se a variável PORT não estiver definida
export PORT=${PORT:-3000}
echo "Iniciando o servidor na porta: $PORT"

# Iniciar o Gunicorn utilizando a porta obtida
exec gunicorn --bind "0.0.0.0:$PORT" --log-level info --timeout 120 main:app