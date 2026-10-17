"""Extrai zip e gzip em bytes, sem reescrever o conteúdo.

O arquivo compactado permanece. Membro com o mesmo SHA-256 de uma cópia
já implantada não é gravado de novo. Membro a partir de 50 MB vira fração.
"""
import gzip
import hashlib
import json
import zipfile
from pathlib import Path

from packages.cli.fracionar import LIMITE_PARTE, LIMITE_REPOSITORIO, fracionar

ALGORITMO = "extracao-bytes-sha256"


def _sha_bytes(bloco: bytes) -> str:
    return hashlib.sha256(bloco).hexdigest()


def _caminho_membro(raiz: Path, nome: str) -> Path:
    if not isinstance(nome, str) or nome == "" or nome.endswith("/"):
        raise ValueError("nome de membro inválido")
    puro = Path(nome)
    if puro.is_absolute() or ".." in puro.parts or "\\" in nome:
        raise ValueError("membro fora do arquivo")
    destino = (raiz / puro).resolve()
    if not str(destino).startswith(str(raiz.resolve())):
        raise ValueError("membro fora do arquivo")
    return destino


def _gravar_membro(
    raiz: Path,
    nome: str,
    corpo: bytes,
    *,
    indice: dict[str, str],
    tamanho_parte: int,
    limite_repositorio: int,
) -> dict:
    sha = _sha_bytes(corpo)
    if sha in indice:
        return {
            "nome": nome,
            "bytes": len(corpo),
            "sha256": sha,
            "disposicao": "IDENTICO_EXISTENTE",
            "copia_existente": indice[sha],
        }
    if len(corpo) >= limite_repositorio:
        inteiros = raiz / "inteiros"
        inteiros.mkdir(parents=True, exist_ok=True)
        bruto = inteiros / Path(nome).name
        bruto.write_bytes(corpo)
        pasta = raiz / "fracoes" / nome
        doc = fracionar(
            bruto,
            pasta,
            tamanho_parte=tamanho_parte,
            limite_repositorio=limite_repositorio,
            caminho_obter=nome,
        )
        bruto.unlink()
        return {
            "nome": nome,
            "bytes": len(corpo),
            "sha256": sha,
            "disposicao": "FRACIONADO",
            "caminho": str(pasta.relative_to(raiz)),
            "partes": len(doc["partes"]),
        }
    destino = _caminho_membro(raiz, nome)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(corpo)
    return {
        "nome": nome,
        "bytes": len(corpo),
        "sha256": sha,
        "disposicao": "GRAVADO",
        "caminho": str(destino.relative_to(raiz)),
    }


def _membros_zip(arquivo: Path) -> list[tuple[str, bytes]]:
    with zipfile.ZipFile(arquivo) as compactado:
        saida = []
        for info in compactado.infolist():
            if info.is_dir():
                continue
            saida.append((info.filename, compactado.read(info)))
        return saida


def _membro_gzip(arquivo: Path) -> tuple[str, bytes]:
    with gzip.open(arquivo, "rb") as entrada:
        corpo = entrada.read()
    nome = arquivo.name[: -len(".gz")] if arquivo.name.endswith(".gz") else arquivo.name
    return nome, corpo


def extrair_compactado(
    arquivo: Path,
    destino: Path,
    *,
    indice: dict[str, str] | None = None,
    tamanho_parte: int = LIMITE_PARTE,
    limite_repositorio: int = LIMITE_REPOSITORIO,
) -> dict:
    """Grava a análise e os membros novos. Não apaga o compactado."""
    if not arquivo.is_file():
        raise ValueError("arquivo ausente")
    arquivo = arquivo.resolve()
    destino = destino.resolve()
    indice = dict(indice or {})
    if arquivo.suffix == ".zip":
        membros_brutos = _membros_zip(arquivo)
    elif arquivo.suffix == ".gz":
        membros_brutos = [_membro_gzip(arquivo)]
    else:
        raise ValueError("compactado fora de zip ou gzip")
    destino.mkdir(parents=True, exist_ok=True)
    membros = [
        _gravar_membro(
            destino,
            nome,
            corpo,
            indice=indice,
            tamanho_parte=tamanho_parte,
            limite_repositorio=limite_repositorio,
        )
        for nome, corpo in membros_brutos
    ]
    doc = {
        "algoritmo": ALGORITMO,
        "arquivo": arquivo.name,
        "bytes": arquivo.stat().st_size,
        "sha256": hashlib.sha256(arquivo.read_bytes()).hexdigest(),
        "membros": membros,
    }
    (destino / "analise.json").write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return doc
