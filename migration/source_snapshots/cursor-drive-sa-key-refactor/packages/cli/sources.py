"""
Política de fontes executável (deny-by-default).

Codifica docs/SOURCES_HIERARCHY.md e contracts/fonte_*.json como allowlist
verificável por máquina. A CLI não ingere conteúdo de domínio fora da lista:
a classificação REFERENCE_ONLY bloqueia a extração (decisão de 04/10/2026).
"""
from urllib.parse import urlparse

# Domínios oficiais autorizados para extração (sufixos; subdomínios incluídos).
DOMINIOS_OFICIAIS = {
    "in.gov.br": "DIARIO_OFICIAL_FEDERAL",
    "planalto.gov.br": "SECUNDARIA",
    "cofen.gov.br": "SECUNDARIA",
    "anvisa.gov.br": "SECUNDARIA",
    "saude.gov.br": "SECUNDARIA",
    "gov.br": "SECUNDARIA",
}

ALLOWED = "ALLOWED"
REFERENCE_ONLY = "REFERENCE_ONLY"
INVALID = "INVALID"


def classificar_url(url: str) -> tuple[str, str]:
    """Retorna (classificacao, fonte_tipo) para uma URL.

    - ALLOWED: domínio oficial; extração permitida.
    - REFERENCE_ONLY: URL válida fora da allowlist; extração proibida.
    - INVALID: não é URL http(s).
    """
    try:
        parsed = urlparse(url)
    except ValueError:
        return INVALID, ""
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return INVALID, ""
    host = parsed.hostname.lower()
    for dominio, fonte_tipo in DOMINIOS_OFICIAIS.items():
        if host == dominio or host.endswith("." + dominio):
            return ALLOWED, fonte_tipo
    return REFERENCE_ONLY, ""


def dominio_oficial(url: str) -> bool:
    classificacao, _ = classificar_url(url)
    return classificacao == ALLOWED
