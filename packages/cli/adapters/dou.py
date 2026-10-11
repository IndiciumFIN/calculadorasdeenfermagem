"""
Adapter para Diário Oficial da União (DOU) — fonte primária oficial.

DOU é a fonte da verdade para legislação normativa no Brasil
(esferas federal, estadual e municipal quando publicadas).

Limitações conhecidas:
- Pode não conter anexos completos.
- Pode haver divergência entre a publicação no DOU e o texto consolidado
  em portais secundários (Planalto, órgão emissor).
- Sempre registrar a origem e o hash. Nunca sobrescrever sem evidência.
"""
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from packages.cli.utils import aplicar_mascara, calcular_hash

def fetch_dou_page(url: str) -> dict:
    """Busca página do DOU / in.gov.br e retorna texto sanitizado + metadados."""
    resp = requests.get(url, timeout=30, headers={"User-Agent": "CE-CLI/1.1 (normative)"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    # Seletores amplos — DOU muda layout com frequência
    texto = soup.get_text(separator="\n", strip=True)
    texto_limpo = aplicar_mascara(texto)
    return {
        "origem": url,
        "fonte_tipo": "DOU_PRIMARIA",
        "texto_sanitizado": texto_limpo[:40000],
        "hash": calcular_hash(texto_limpo),
        "aviso": "Verificar anexos e possível divergência com fonte secundária do órgão emissor."
    }
