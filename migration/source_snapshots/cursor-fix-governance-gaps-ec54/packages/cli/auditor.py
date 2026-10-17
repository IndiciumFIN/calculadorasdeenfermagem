from packages.cli.utils import extrair_numeros_criticos

def auditar_omissao(texto_original: str, texto_atomo: str) -> dict:
    """Camada 1 de auditoria: verifica se números/prazos críticos foram omitidos."""
    nums_orig = extrair_numeros_criticos(texto_original)
    nums_atomo = extrair_numeros_criticos(texto_atomo)
    omitidos = nums_orig - nums_atomo
    return {
        "omissao_critica": len(omitidos) > 0,
        "numeros_omitidos": list(omitidos),
        "numeros_originais": list(nums_orig),
        "numeros_no_atomo": list(nums_atomo)
    }
