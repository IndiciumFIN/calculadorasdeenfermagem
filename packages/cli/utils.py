import re
import hashlib

# Padrões de máscara nomeados para que o diff da máscara seja auditável (GAP-08).
PADROES_MASCARA = [
    ("CPF", re.compile(r'\d{3}\.\d{3}\.\d{3}-\d{2}'), '[CPF_REDACT]'),
    ("TELEFONE", re.compile(r'(?<!\d)\(?\d{2}\)?\s?\d{4,5}-?\d{4}(?!\d)'), '[TEL_REDACT]'),
    ("ASSINATURA_DIGITAL", re.compile(r'Documento assinado digitalmente.*', re.IGNORECASE), ''),
    ("VERIFICACAO", re.compile(r'Este documento pode ser verificado.*', re.IGNORECASE), ''),
]


def aplicar_mascara(texto: str) -> str:
    """Remove dados sensíveis e ruído comum de diários oficiais."""
    resultado, _ = aplicar_mascara_com_diff(texto)
    return resultado


def aplicar_mascara_com_diff(texto: str) -> tuple[str, list[dict]]:
    """Aplica a máscara e retorna também o diff auditável de cada substituição.

    O diff permite verificar que a máscara não corrompeu conteúdo normativo
    (números de processo, prazos, dispositivos) e integra a evidência da
    ingestão (GAP-02 / GAP-08).
    """
    diff: list[dict] = []
    resultado = texto
    for nome, padrao, substituto in PADROES_MASCARA:
        ocorrencias = padrao.findall(resultado)
        if ocorrencias:
            diff.append({
                "padrao": nome,
                "ocorrencias": len(ocorrencias),
                "amostra": str(ocorrencias[0])[:80],
            })
            resultado = padrao.sub(substituto, resultado)
    return resultado.strip(), diff


def calcular_hash(texto: str) -> str:
    return hashlib.sha256(texto.encode('utf-8')).hexdigest()


def extrair_numeros_criticos(texto: str) -> set[str]:
    """Extrai números, prazos e valores para checagem de omissão.

    Grupos são não-capturantes: com grupo de captura, re.findall devolvia só
    a unidade ('dias') e perdia o número — '30 dias' e '60 dias' viravam
    ambos 'dias', mascarando omissões (defeito confirmado no teste T9).
    """
    padroes = [
        r'\d+\s*(?:dias|meses|anos)',
        r'R\$\s*[\d.,]+',
        r'\d+%',
        r'\d{1,3}(?:\.\d{3})*(?:,\d{2})?'
    ]
    encontrados = set()
    for p in padroes:
        encontrados.update(re.findall(p, texto, re.IGNORECASE))
    return encontrados
