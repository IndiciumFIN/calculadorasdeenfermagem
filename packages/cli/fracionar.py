"""Parte arquivo grande em bytes, sem reescrever o conteúdo.

A integridade é o SHA-256 do arquivo original. A recomposição é a
concatenação das partes, na ordem, sem parsear JSON.
"""
import hashlib
import json
from pathlib import Path

ALGORITMO = "concatenacao-bytes-sha256"
LIMITE_PARTE = 40_000_000
LIMITE_REPOSITORIO = 50_000_000


def _sha_arquivo(caminho: Path) -> str:
    digest = hashlib.sha256()
    with caminho.open("rb") as entrada:
        while bloco := entrada.read(1024 * 1024):
            digest.update(bloco)
    return digest.hexdigest()


def _caminho_parte(pasta: Path, nome: str) -> Path:
    if not isinstance(nome, str) or nome != Path(nome).name or nome in {"", ".", "..", "manifesto.json"}:
        raise ValueError("nome de parte inválido")
    destino = (pasta / nome).resolve()
    if destino.parent != pasta.resolve():
        raise ValueError("parte fora da pasta da fração")
    return destino


def recomposto_confere(manifesto: Path, esperado: str) -> bool:
    """True só se a concatenação das partes repetir o SHA-256 esperado."""
    try:
        doc = json.loads(manifesto.read_text(encoding="utf-8"))
        partes = doc["partes"]
        if doc.get("algoritmo") != ALGORITMO or doc.get("sha256") != esperado:
            return False
        if not isinstance(partes, list) or not partes:
            return False
    except (OSError, json.JSONDecodeError, KeyError, TypeError):
        return False
    pasta = manifesto.parent
    digest = hashlib.sha256()
    offset = 0
    try:
        for indice, parte in enumerate(partes):
            if parte["ordem"] != indice or parte["offset"] != offset:
                return False
            caminho = _caminho_parte(pasta, parte["nome"])
            tamanho = caminho.stat().st_size
            if tamanho != parte["bytes"] or tamanho <= 0 or tamanho >= LIMITE_REPOSITORIO:
                return False
            parte_digest = hashlib.sha256()
            with caminho.open("rb") as entrada:
                while bloco := entrada.read(1024 * 1024):
                    parte_digest.update(bloco)
                    digest.update(bloco)
            if parte_digest.hexdigest() != parte["sha256"]:
                return False
            offset += tamanho
    except (OSError, KeyError, TypeError, ValueError):
        return False
    return offset == doc.get("bytes") and digest.hexdigest() == esperado


def fracionar(
    origem: Path,
    pasta: Path,
    *,
    tamanho_parte: int = LIMITE_PARTE,
    limite_repositorio: int = LIMITE_REPOSITORIO,
    id_origem: str = "",
    caminho_obter: str = "",
) -> dict:
    """Grava as partes e o manifesto. Não apaga o arquivo original."""
    if tamanho_parte <= 0 or tamanho_parte >= limite_repositorio:
        raise ValueError("tamanho da parte precisa ficar abaixo de 50 MB")
    if not origem.is_file():
        raise ValueError("arquivo ausente")
    total = origem.stat().st_size
    if total < limite_repositorio:
        raise ValueError("arquivo abaixo do limite não é fracionado")
    pasta.mkdir(parents=True, exist_ok=True)
    partes = []
    digest = hashlib.sha256()
    offset = 0
    ordem = 0
    with origem.open("rb") as entrada:
        while bloco := entrada.read(tamanho_parte):
            if len(bloco) >= limite_repositorio:
                raise ValueError("parte atingiu o limite do repositório")
            nome = f"part-{ordem:03d}"
            destino = _caminho_parte(pasta, nome)
            destino.write_bytes(bloco)
            partes.append(
                {
                    "nome": nome,
                    "ordem": ordem,
                    "offset": offset,
                    "bytes": len(bloco),
                    "sha256": hashlib.sha256(bloco).hexdigest(),
                }
            )
            digest.update(bloco)
            offset += len(bloco)
            ordem += 1
    doc = {
        "algoritmo": ALGORITMO,
        "id_origem": id_origem,
        "arquivo": origem.name,
        "caminho_obter": caminho_obter,
        "bytes": total,
        "sha256": digest.hexdigest(),
        "tamanho_parte": tamanho_parte,
        "partes": partes,
    }
    manifesto = pasta / "manifesto.json"
    manifesto.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    if not recomposto_confere(manifesto, doc["sha256"]):
        raise ValueError("re composição divergente")
    return doc
