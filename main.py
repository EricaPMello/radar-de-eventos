from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
import urllib.parse
import unicodedata

app = FastAPI(title="Radar de Eventos API")

# Permite comunicação entre o GitHub Pages e a API sem bloqueios de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def remover_acentos(texto: str) -> str:
    """Remove acentos e caracteres especiais para facilitar a busca"""
    nfkd = unicodedata.normalize('NFKD', texto)
    return "".join([c for c in nfkd if not unicodedata.combining(c)])

@app.get("/")
def home():
    return {"status": "Servidor do Radar de Eventos está online!"}

@app.get("/api/eventos")
def buscar_eventos(termo: str = "rock", local: str = "piracicaba", periodo: str = "proximos"):
    # Normalização dos termos (remove acentos, espaços extras e converte para minúsculos)
    termo_limpo = remover_acentos(termo.strip().lower())
    local_limpo = remover_acentos(local.strip().lower())
    
    # Define o sufixo temporal para focar em eventos futuros
    termo_data = "2026 agenda shows eventos"
    if periodo == "semana":
        termo_data = "esta semana 2026 agenda shows"
    elif periodo == "fim_semana":
        termo_data = "este fim de semana 2026 agenda"
    elif periodo == "mes":
        termo_data = "este mes 2026 agenda shows"

    eventos = []

    try:
        query_str = f"shows {termo_limpo} {local_limpo} {termo_data} instagram facebook sympla"
        url_busca = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query_str)}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        response = requests.get(url_busca, headers=headers, timeout=8)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            resultados = soup.select('.result')

            for item in resultados[:6]:
                titulo_elem = item.select_one('.result__title')
                snippet_elem = item.select_one('.result__snippet')
                url_elem = item.select_one('.result__url')

                if titulo_elem:
                    titulo = titulo_elem.get_text(strip=True)
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else "Divulgação pública de evento."
                    url_raw = url_elem['href'] if url_elem and 'href' in url_elem.attrs else "#"
                    
                    if 'uddg=' in url_raw:
                        url_real = urllib.parse.unquote(url_raw.split('uddg=')[1].split('&')[0])
                    else:
                        url_real = url_raw

                    eventos.append({
                        "titulo": titulo,
                        "local": f"Região de {local_limpo.title()}",
                        "data": snippet[:110] + "...",
                        "fonte": "Redes / Portais Culturais",
                        "link": url_real
                    })
    except Exception as e:
        print(f"Erro no processamento da busca: {e}")

    # Fallback garantido com links diretos
    if not eventos:
        link_sympla = f"https://www.sympla.com.br/eventos/{urllib.parse.quote(local_limpo)}?s={urllib.parse.quote(termo_limpo)}"
        link_instagram = f"https://www.instagram.com/explore/tags/{urllib.parse.quote(termo_limpo + local_limpo)}/"
        link_google = f"https://www.google.com/search?q={urllib.parse.quote('agenda de shows ' + termo_limpo + ' em ' + local_limpo + ' 2026')}"

        eventos = [
            {
                "titulo": f"Agenda no Sympla: {termo_limpo.title()} em {local_limpo.title()}",
                "local": f"Bares e Casas de Show em {local_limpo.title()}",
                "data": "Apresentações com ingressos e eventos abertos",
                "fonte": "Sympla Brasil",
                "link": link_sympla
            },
            {
                "titulo": f"Divulgações no Instagram (#{termo_limpo}{local_limpo})",
                "local": f"Publicações de bandas e bares locais",
                "data": "Confira os cartazes e flyers mais recentes",
                "fonte": "Instagram Public",
                "link": link_instagram
            },
            {
                "titulo": f"Radar Cultural: {termo_limpo.title()} em {local_limpo.title()}",
                "local": f"Locais diversos na região de {local_limpo.title()}",
                "data": "Resultados de programação na web",
                "fonte": "Busca Cultural Direta",
                "link": link_google
            }
        ]

    return {"termo": termo_limpo, "local": local_limpo, "resultados": eventos}
