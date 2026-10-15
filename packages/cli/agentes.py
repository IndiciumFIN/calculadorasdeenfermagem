"""Registro determinístico de agentes (somente leitura).

Não contém estado. Serve para consulta de papéis e regras
conforme docs/AGENTES_GROK.md e docs/AGENTS.md.
"""
from typing import Final

AGENTES: Final[dict[str, dict[str, str]]] = {
    "arquiteto": {
        "papel": "Implementação de controles via branch+PR",
        "escreve": "sim (via PR)",
        "reporta": "Grok Bot / Leivis",
    },
    "auditor": {
        "papel": "Verificação de integridade e precisão",
        "escreve": "não",
        "reporta": "Grok Bot",
    },
    "extrator": {
        "papel": "Captura literal de fontes oficiais",
        "escreve": "staging",
        "reporta": "Grok Bot",
    },
    "atomizador": {
        "papel": "Transformação em átomos",
        "escreve": "staging",
        "reporta": "Grok Bot",
    },
}

def papel(agente: str) -> str:
    """Retorna o papel canônico ou 'desconhecido'."""
    return AGENTES.get(agente.lower(), {}).get("papel", "desconhecido")

def pode_escrever(agente: str) -> bool:
    """True somente se o agente tiver permissão de escrita controlada."""
    return AGENTES.get(agente.lower(), {}).get("escreve", "não").startswith("sim")
