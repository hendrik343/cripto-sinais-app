import os
import pyshorteners
import json
import requests

# Obter a URL completa do Replit
replit_domain = os.environ.get('REPLIT_DOMAINS').split(',')[0]
full_url = f"https://{replit_domain}"

# Tentar diferentes serviços de encurtamento de URL
def generate_short_url():
    # Tentar com Tinyurl
    try:
        s = pyshorteners.Shortener()
        short_url = s.tinyurl.short(full_url)
        return short_url
    except Exception as e:
        print(f"Erro com TinyURL: {e}")
    
    # Backup: Cuttly
    try:
        s = pyshorteners.Shortener()
        short_url = s.cuttly.short(full_url)
        return short_url
    except Exception as e:
        print(f"Erro com Cuttly: {e}")
    
    # Último recurso: usar a URL original
    return full_url

# Criar URL curta
short_url = generate_short_url()

print(f"URL Original: {full_url}")
print(f"URL Encurtada: {short_url}")

# Salvar em um arquivo para uso futuro
with open('short_url.json', 'w') as f:
    json.dump({
        'original_url': full_url,
        'short_url': short_url
    }, f)

print("URL encurtada salva em short_url.json")