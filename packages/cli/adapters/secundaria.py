"""
Adapter para fontes secundárias de apoio.

Fontes secundárias (Planalto, site do órgão emissor, COFEN etc.)
são usadas apenas para cruzamento e recuperação de anexos.
Nunca substituem o DOU como fonte primária.

Se houver divergência, registrar ambas e marcar para revisão humana.
"""
import requests
from bs4 import BeautifulSoup

from packages.cli.evidence import registrar_proveniencia


def fetch_secundaria(url: str, orgao: str = "desconhecido") -> dict:
    resp = requests.get(url, timeout=30, headers={"User-Agent": "CE-CLI/1.2"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    texto = soup.get_text(separator="\n", strip=True)
    evidencia = registrar_proveniencia(texto, origem=url)
    return {
        "origem": url,
        "fonte_tipo": "SECUNDARIA",
        "orgao": orgao,
        "texto_sanitizado": evidencia["texto_sanitizado"],
        "hash": evidencia["sha256_transformado"],
        "sha256_original": evidencia["sha256_original"],
        "sha256_transformado": evidencia["sha256_transformado"],
        "mascara_diff": evidencia["mascara_diff"],
        "aviso": "Fonte de apoio. Cruzar com DOU. Divergência exige revisão humana."
    }
