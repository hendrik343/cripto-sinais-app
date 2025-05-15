#!/bin/bash

# Usa a porta definida pela plataforma ou 3000 como fallback
if [ -z "$PORT" ]; then
    export PORT=3000
fi

echo "Iniciando servidor na porta $PORT..."

# Inicia o Gunicorn na porta definida usando wsgi.py que escolherá a aplicação apropriada
exec gunicorn --bind "0.0.0.0:$PORT" --log-level info --timeout 120 wsgi:app