"""
Adapter para diários oficiais.

- Federal: DOU (in.gov.br)
- Estadual e municipal: diários oficiais próprios (consulta obrigatória).

Este adapter cobre o DOU federal. Para outras esferas, usar o adapter genérico
ou criar adapter específico quando a fonte for conhecida.
"""
import requests
from bs4 import BeautifulSoup

from packages.cli.evidence import registrar_proveniencia


def fetch_dou_federal(url: str) -> dict:
    """Busca página do DOU federal (in.gov.br).

    Sem truncamento: cortar o texto geraria sucesso parcial silencioso
    (GOV-005). O original bruto é preservado com hash duplo (GAP-02).
    """
    resp = requests.get(url, timeout=30, headers={"User-Agent": "CE-CLI/1.2 (normative)"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    texto = soup.get_text(separator="\n", strip=True)
    evidencia = registrar_proveniencia(texto, origem=url)
    return {
        "origem": url,
        "esfera": "federal",
        "fonte_tipo": "DIARIO_OFICIAL_FEDERAL",
        "texto_sanitizado": evidencia["texto_sanitizado"],
        "hash": evidencia["sha256_transformado"],
        "sha256_original": evidencia["sha256_original"],
        "sha256_transformado": evidencia["sha256_transformado"],
        "mascara_diff": evidencia["mascara_diff"],
        "aviso": "Verificar anexos no órgão emissor. Divergência com fonte secundária exige revisão humana."
    }
