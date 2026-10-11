"""
Adapter para diários oficiais.

- Federal: DOU (in.gov.br)
- Estadual e municipal: diários oficiais próprios (consulta obrigatória).

Este adapter cobre o DOU federal. Para outras esferas, usar o adapter genérico
ou criar adapter específico quando a fonte for conhecida.
"""
import requests
from bs4 import BeautifulSoup
from packages.cli.utils import aplicar_mascara, calcular_hash

def fetch_dou_federal(url: str) -> dict:
    """Busca página do DOU federal (in.gov.br)."""
    resp = requests.get(url, timeout=30, headers={"User-Agent": "CE-CLI/1.1 (normative)"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    texto = soup.get_text(separator="\n", strip=True)
    texto_limpo = aplicar_mascara(texto)
    return {
        "origem": url,
        "esfera": "federal",
        "fonte_tipo": "DIARIO_OFICIAL_FEDERAL",
        "texto_sanitizado": texto_limpo[:40000],
        "hash": calcular_hash(texto_limpo),
        "aviso": "Verificar anexos no órgão emissor. Divergência com fonte secundária exige revisão humana."
    }
