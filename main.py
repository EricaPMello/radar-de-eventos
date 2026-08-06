from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
import urllib.parse

app = FastAPI()

# Permite comunicação com o GitHub Pages
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
    
    # URL de busca em tempo real na web para eventos e shows
    termo_busca = f"{termo} {local}"
    url_pesquisa = f"https://www.clubedoingresso.com/busca?busca={urllib.parse.quote(termo_busca)}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url_pesquisa, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Raspagem dos cards de eventos reais encontrados na busca
            cards = soup.select('.card-evento') or soup.select('.event-item') or soup.find_all('article')
            
            for card in cards[:8]:  # Pega até 8 eventos reais por busca
                titulo_elem = card.select_one('.titulo, .event-title, h3, h2')
                local_elem = card.select_one('.local, .venue, .location')
                data_elem = card.select_one('.data, .date')
                link_elem = card.find('a', href=True)

                if titulo_elem:
                    titulo = titulo_elem.get_text(strip=True)
                    local_evento = local_elem.get_text(strip=True) if local_elem else f"Região de {local.capitalize()}"
                    data_evento = data_elem.get_text(strip=True) if data_elem else "Consultar no site"
                    link = link_elem['href'] if link_elem else "https://www.clubedoingresso.com"
                    
                    if not link.startswith('http'):
                        link = f"https://www.clubedoingresso.com{link}"

                    eventos.append({
                        "titulo": titulo,
                        "local": local_evento,
                        "data": data_evento,
                        "fonte": "Agenda de Divulgação Pública",
                        "link": link
                    })

    except Exception as e:
        print(f"Erro na busca: {e}")

    # Caso a raspagem direta não retorne resultados específicos, trazemos uma busca dinâmica filtrada
    if not eventos:
        link_busca_direta = f"https://www.google.com/search?q={urllib.parse.quote('shows de ' + termo + ' em ' + local + ' 2026')}"
        eventos.append({
            "titulo": f"Busca Ativa: Shows de {termo.capitalize()} em {local.capitalize()}",
            "local": f"Casas de show e bares em {local.capitalize()}",
            "data": "Próximas datas / Esta semana",
            "fonte": "Divulgações e Agendas Locais",
            "link": link_busca_direta
        })

    return {"termo": termo, "local": local, "resultados": eventos}
   
