"""
Adapter para fontes secundárias de apoio.

Fontes secundárias (Planalto, site do órgão emissor, COFEN etc.)
são usadas apenas para cruzamento e recuperação de anexos.
Nunca substituem o DOU como fonte primária.

Se houver divergência, registrar ambas e marcar para revisão humana.
"""
from packages.cli.utils import aplicar_mascara, calcular_hash
import requests
from bs4 import BeautifulSoup

def fetch_secundaria(url: str, orgao: str = "desconhecido") -> dict:
    resp = requests.get(url, timeout=30, headers={"User-Agent": "CE-CLI/1.1"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    texto = soup.get_text(separator="\n", strip=True)
    texto_limpo = aplicar_mascara(texto)
    return {
        "origem": url,
        "fonte_tipo": "SECUNDARIA",
        "orgao": orgao,
        "texto_sanitizado": texto_limpo[:40000],
        "hash": calcular_hash(texto_limpo),
        "aviso": "Fonte de apoio. Cruzar com DOU. Divergência exige revisão humana."
    }
