from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
import urllib.parse

app = FastAPI(title="Radar de Eventos API")

# Permite que o GitHub Pages acesse a API sem bloqueios de CORS
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
    termo_limpo = termo.strip() if termo else "Rock"
    local_limpo = local.strip() if local else "Piracicaba"
    
    eventos = []

    # Busca em tempo real por divulgações públicas e agendas culturais
    try:
        query_str = f"shows {termo_limpo} {local_limpo} 2026 instagram facebook sympla"
        url_busca = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query_str)}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        response = requests.get(url_busca, headers=headers, timeout=8)
        
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
                    
                    if 'uddg=' in url_raw:
                        url_real = urllib.parse.unquote(url_raw.split('uddg=')[1].split('&')[0])
                    else:
                        url_real = url_raw

                    eventos.append({
                        "titulo": titulo,
                        "local": f"Região de {local_limpo.capitalize()}",
                        "data": snippet[:110] + "...",
                        "fonte": "Redes / Portais Culturais",
                        "link": url_real
                    })
    except Exception as e:
        print(f"Erro no processamento da busca: {e}")

    # Fallback contextualizado para garantir retorno de links diretos e atualizados
    if not eventos:
        link_sympla = f"https://www.sympla.com.br/eventos/{urllib.parse.quote(local_limpo.lower())}?s={urllib.parse.quote(termo_limpo)}"
        link_instagram = f"https://www.instagram.com/explore/tags/{urllib.parse.quote(termo_limpo.lower() + local_limpo.lower())}/"
        link_google = f"https://www.google.com/search?q={urllib.parse.quote('shows de ' + termo_limpo + ' em ' + local_limpo + ' 2026')}"

        eventos = [
            {
                "titulo": f"Agenda de {termo_limpo.capitalize()} no Sympla ({local_limpo.capitalize()})",
                "local": f"Bares, Teatros e Casas de Show em {local_limpo.capitalize()}",
                "data": "Lista completa de apresentações e vendas de ingresso",
                "fonte": "Sympla Brasil",
                "link": link_sympla
            },
            {
                "titulo": f"Publicações do Instagram (#{termo_limpo.lower()}{local_limpo.lower()})",
                "local": f"Divulgações de bandas e bares locais",
                "data": "Confira os cartazes e flyers mais recentes",
                "fonte": "Instagram Public",
                "link": link_instagram
            },
            {
                "titulo": f"Pesquisa Aberta: Eventos de {termo_limpo.capitalize()} em {local_limpo.capitalize()}",
                "local": f"Locais diversos na região de {local_limpo.capitalize()}",
                "data": "Resultados gerais e notícias de shows",
                "fonte": "Radar Cultural",
                "link": link_google
            }
        ]

    return {"termo": termo_limpo, "local": local_limpo, "resultados": eventos}
