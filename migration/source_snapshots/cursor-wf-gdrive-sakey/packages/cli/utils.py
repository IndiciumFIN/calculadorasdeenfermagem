import re
import hashlib
from typing import Any

def aplicar_mascara(texto: str) -> str:
    """Remove dados sensíveis e ruído comum de diários oficiais."""
    # CPF
    texto = re.sub(r'\d{3}\.\d{3}\.\d{3}-\d{2}', '[CPF_REDACT]', texto)
    # Telefones simples
    texto = re.sub(r'\(?\d{2}\)?\s?\d{4,5}-?\d{4}', '[TEL_REDACT]', texto)
    # Marcas d'água comuns
    texto = re.sub(r'Documento assinado digitalmente.*', '', texto, flags=re.IGNORECASE)
    texto = re.sub(r'Este documento pode ser verificado.*', '', texto, flags=re.IGNORECASE)
    return texto.strip()

def calcular_hash(texto: str) -> str:
    return hashlib.sha256(texto.encode('utf-8')).hexdigest()

def extrair_numeros_criticos(texto: str) -> set[str]:
    """Extrai números, prazos e valores para checagem de omissão."""
    padroes = [
        r'\d+\s*(dias|meses|anos)',
        r'R\$\s*[\d.,]+',
        r'\d+%',
        r'\d{1,3}(?:\.\d{3})*(?:,\d{2})?'
    ]
    encontrados = set()
    for p in padroes:
        encontrados.update(re.findall(p, texto, re.IGNORECASE))
    return encontrados
