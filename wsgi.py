"""
Arquivo WSGI para deployment da aplicação CriptoSinais
Este arquivo é o ponto de entrada para servidores WSGI como Gunicorn
"""

try:
    from app import app  # Tentar importar do app.py primeiro
except ImportError:
    try:
        from index import app  # Fallback para index.py
    except ImportError:
        from main import app  # Último fallback para main.py

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)