"""
Arquivo WSGI para deployment da aplicação CriptoSinais
Este arquivo é o ponto de entrada para servidores WSGI como Gunicorn
"""

from index import app  # Pegar app diretamente do index.py

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)