from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
import urllib.parse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "Servidor do Radar de Eventos está online!"}

@app.get("/api/eventos")
def buscar_eventos(termo: str = "Rock", local: str = "Piracicaba"):
    eventos = []
    
    # 1. Busca em agregadores de eventos e divulgações públicas via DuckDuckGo
    termo_limpo = urllib.parse.quote(f"shows {termo} {local} 2026 instagram facebook sympla")
    url_ddg = f"https://html.duckduckgo.com/html/?q={termo_limpo}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url_ddg, headers=headers, timeout=8)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            resultados = soup.select('.result')

            for item in resultados[:5]:
                titulo_elem = item.select_one('.result__title')
                snippet_elem = item.select_one('.result__snippet')
                url_elem = item.select_one('.result__url')

                if titulo_elem:
                    titulo = titulo_elem.get_text(strip=True)
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else "Divulgação pública de evento."
                    url_raw = url_elem['href'] if url_elem and 'href' in url_elem.attrs else "#"
                    
                    # Decodifica links de redirecionamento
                    if 'uddg=' in url_raw:
                        url_real = urllib.parse.unquote(url_raw.split('uddg=')[1].split('&')[0])
                    else:
                        url_real = url_raw

                    eventos.append({
                        "titulo": titulo,
                        "local": f"Região de {local.capitalize()}",
                        "data": snippet[:90] + "...",
                        "fonte": "Redes / Portais de Eventos",
                        "link": url_real
                    })

    except Exception as e:
        print(f"Erro na raspagem: {e}")

    # 2. Garante retorno de resultados com busca contextualizada em portais e redes
    if not eventos:
        link_instagram = f"https://www.instagram.com/explore/tags/{urllib.parse.quote(termo.lower() + local.lower())}/"
        link_sympla = f"https://www.sympla.com.br/eventos/{urllib.parse.quote(local.lower())}?s={urllib.parse.quote(termo)}"
        
        eventos = [
            {
                "titulo": f"Divulgações de {termo.capitalize()} no Sympla - {local.capitalize()}",
                "local": f"Casas de Show em {local.capitalize()}",
                "data": "Confira a agenda de ingressos e apresentações abertas",
                "fonte": "Sympla Eventos",
                "link": link_sympla
            },
            {
                "titulo": f"Publicações no Instagram (#{termo.lower()}{local.lower()})",
                "local": f"Postagens públicas na região de {local.capitalize()}",
                "data": "Últimas publicações de bandas e bares",
                "fonte": "Instagram Public",
                "link": link_instagram
            }
        ]

    return {"termo": termo, "local": local, "resultados": eventos}
