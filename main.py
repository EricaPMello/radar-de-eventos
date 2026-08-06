from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
import re

app = FastAPI()

# Permite que o GitHub Pages converse com este servidor sem ser bloqueado
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
    
    # Exemplo de busca simulada de eventos públicos estruturados
    # Na prática, este bloco faz requisições Web Scraping em portais e redes
    eventos_encontrados = [
        {
            "titulo": f"Festival de {termo.capitalize()} Local",
            "local": f"Centro Cultural de {local.capitalize()}",
            "data": "Próximo Fim de Semana - 19:00",
            "fonte": "Divulgação Pública Local",
            "link": "https://instagram.com"
        },
        {
            "titulo": f"Encontro de Bandas de {termo.capitalize()}",
            "local": f"Praça Principal - {local.capitalize()}",
            "data": "Sábado - 16:00",
            "fonte": "Agenda da Prefeitura / Guias CULT",
            "link": "https://facebook.com"
        }
    ]
    
    return {"termo": termo, "local": local, "resultados": eventos_encontrados}