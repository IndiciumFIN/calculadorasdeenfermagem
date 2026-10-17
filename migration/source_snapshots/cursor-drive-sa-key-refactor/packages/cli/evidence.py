"""
Cadeia de proveniência (GAP-02 / GAP-08).

Toda ingestão preserva o texto original bruto e registra hash duplo:
  - sha256_original: do texto exatamente como obtido da fonte;
  - sha256_transformado: do texto após máscara.
Sem o original preservado, a evidência não permite re-verificação contra a
fonte. O diff da máscara acompanha o manifesto para auditoria.
"""
import json
from datetime import date
from pathlib import Path

from packages.cli.utils import aplicar_mascara_com_diff, calcular_hash

SOURCES_DIR = Path("data/sources")


def registrar_proveniencia(texto_original: str, origem: str, sources_dir: Path = SOURCES_DIR) -> dict:
    """Preserva o original bruto e devolve o bloco de evidência com hash duplo."""
    sha_original = calcular_hash(texto_original)
    texto_limpo, mascara_diff = aplicar_mascara_com_diff(texto_original)
    sha_transformado = calcular_hash(texto_limpo)

    sources_dir.mkdir(parents=True, exist_ok=True)
    original_path = sources_dir / f"{sha_original}.txt"
    if not original_path.exists():
        original_path.write_text(texto_original, encoding="utf-8")
    manifest_path = sources_dir / f"{sha_original}.manifest.json"
    manifest = {
        "origem": origem,
        "sha256_original": sha_original,
        "sha256_transformado": sha_transformado,
        "mascara_diff": mascara_diff,
        "data_captura": str(date.today()),
        "original_path": str(original_path),
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "texto_sanitizado": texto_limpo,
        "sha256_original": sha_original,
        "sha256_transformado": sha_transformado,
        "mascara_diff": mascara_diff,
    }
