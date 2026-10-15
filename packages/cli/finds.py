"""Registro de FIND. Registrar não corrige. O histórico não é reescrito."""
import hashlib
import json
from pathlib import Path

from packages.cli import pep

REGISTRO = pep.RAIZ / "data" / "finds" / "registro.json"
BASE = pep.RAIZ


def politica() -> dict:
    return json.loads((pep.RAIZ / "policies" / "finds.json").read_text(encoding="utf-8"))


def carregar(caminho: Path | None = None) -> dict:
    path = caminho or REGISTRO
    if not path.is_file():
        return {"versao": "1.0.0", "finds": [], "eventos": []}
    return json.loads(path.read_text(encoding="utf-8"))


def gravar(doc: dict, caminho: Path | None = None) -> None:
    path = caminho or REGISTRO
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def caminho_interno(relativo: str) -> Path:
    puro = Path(relativo)
    if puro.is_absolute() or ".." in puro.parts:
        raise ValueError("caminho precisa ser relativo e sem '..'")
    dest = (BASE / puro).resolve()
    if not str(dest).startswith(str(BASE.resolve())):
        raise ValueError("caminho fora do repositório")
    return dest


def _foto(find: dict | None) -> dict:
    if find is None:
        return {"status": None, "ciclos": 0, "deteccoes": 0}
    return {
        "status": find["status"],
        "ciclos": find["ciclos"],
        "deteccoes": find["deteccoes"],
    }


def _anexar(doc: dict, tipo: str, find: dict, quando: str, work_order: str, antes: dict, extra: dict | None = None) -> None:
    evento = {
        "seq": len(doc["eventos"]) + 1,
        "tipo": tipo,
        "find_id": find["id"],
        "quando": quando,
        "work_order": work_order,
        "antes": antes,
        "depois": _foto(find),
    }
    if extra:
        evento["extra"] = extra
    doc["eventos"].append(evento)


def _novo_id(doc: dict) -> str:
    nums = [int(item["id"].rsplit("-", 1)[1]) for item in doc["finds"]]
    return f"FIND-{max(nums, default=0) + 1:04d}"


def _por_chave(doc: dict, codigo: str, objeto: str, status: str) -> dict | None:
    for item in doc["finds"]:
        if item["codigo"] == codigo and item["objeto"] == objeto and item["status"] == status:
            return item
    return None


def _exigir_texto(valor: str, nome: str) -> None:
    if len(valor.strip()) < 10:
        raise ValueError(f"{nome} precisa de pelo menos 10 caracteres")


def registrar(parametros: dict, work_order: str, caminho: Path | None = None) -> dict:
    regra = politica()
    if parametros["severidade"] not in regra["severidades"]:
        raise ValueError(f"severidade fora da política: {parametros['severidade']}")
    _exigir_texto(parametros["descricao"], "descricao")
    _exigir_texto(parametros["impacto"], "impacto")
    doc = carregar(caminho)
    antes_eventos = len(doc["eventos"])
    aberto = _por_chave(doc, parametros["codigo"], parametros["objeto"], "ABERTO")
    if aberto is not None:
        antes = _foto(aberto)
        aberto["deteccoes"] += 1
        _anexar(doc, "REINCIDENCIA", aberto, parametros["quando"], work_order, antes)
    else:
        fechado = _por_chave(doc, parametros["codigo"], parametros["objeto"], "FECHADO")
        if fechado is not None:
            antes = _foto(fechado)
            fechado["status"] = "ABERTO"
            fechado["deteccoes"] += 1
            fechado["correcao_autorizada"] = False
            _anexar(doc, "REABERTO", fechado, parametros["quando"], work_order, antes)
        else:
            novo = {
                "id": _novo_id(doc),
                "codigo": parametros["codigo"],
                "objeto": parametros["objeto"],
                "severidade": parametros["severidade"],
                "status": "ABERTO",
                "descricao": parametros["descricao"],
                "impacto": parametros["impacto"],
                "detector": parametros["detector"],
                "deteccoes": 1,
                "ciclos": 0,
                "correcao_autorizada": False,
            }
            doc["finds"].append(novo)
            _anexar(doc, "REGISTRADO", novo, parametros["quando"], work_order, _foto(None))
    if len(doc["eventos"]) != antes_eventos + 1:
        raise ValueError("histórico do FIND não pode ser reescrito")
    gravar(doc, caminho)
    return doc


def _aberto_por_id(doc: dict, find_id: str) -> dict:
    for item in doc["finds"]:
        if item["id"] == find_id:
            if item["status"] != "ABERTO":
                raise ValueError(f"FIND não está aberto: {find_id}")
            return item
    raise ValueError(f"FIND ausente: {find_id}")


def vincular(parametros: dict, work_order: str, caminho: Path | None = None) -> dict:
    destino = caminho_interno(parametros["run_caminho"])
    if not destino.is_file():
        raise ValueError("run_caminho ausente")
    digest = hashlib.sha256(destino.read_bytes()).hexdigest()
    doc = carregar(caminho)
    antes_eventos = len(doc["eventos"])
    find = _aberto_por_id(doc, parametros["find_id"])
    antes = _foto(find)
    find["ciclos"] += 1
    find["correcao_autorizada"] = False
    _anexar(
        doc,
        "VINCULADO",
        find,
        parametros["quando"],
        work_order,
        antes,
        {"work_order_ref": parametros["work_order_ref"], "run_sha256": digest},
    )
    if len(doc["eventos"]) != antes_eventos + 1 or find["status"] != "ABERTO":
        raise ValueError("vínculo não pode fechar nem reescrever o FIND")
    gravar(doc, caminho)
    return doc


def encerrar(parametros: dict, work_order: str, caminho: Path | None = None) -> dict:
    esperado = parametros["evidencia_sha256"]
    if len(esperado) != 64 or any(c not in "0123456789abcdef" for c in esperado):
        raise ValueError("evidencia_sha256 inválido")
    destino = caminho_interno(parametros["evidencia_caminho"])
    if not destino.is_file():
        raise ValueError("evidência ausente")
    digest = hashlib.sha256(destino.read_bytes()).hexdigest()
    if digest != esperado:
        raise ValueError("SHA-256 da evidência divergente")
    doc = carregar(caminho)
    antes_eventos = len(doc["eventos"])
    find = _aberto_por_id(doc, parametros["find_id"])
    antes = _foto(find)
    find["status"] = "FECHADO"
    find["correcao_autorizada"] = False
    _anexar(
        doc,
        "FECHADO",
        find,
        parametros["quando"],
        work_order,
        antes,
        {"evidencia_sha256": digest, "evidencia_caminho": parametros["evidencia_caminho"]},
    )
    if len(doc["eventos"]) != antes_eventos + 1:
        raise ValueError("fechamento não pode apagar o histórico")
    gravar(doc, caminho)
    return doc


def promocao_bloqueada(status: str, find_ids: list[str], caminho: Path | None = None) -> list[str]:
    regra = politica()
    if status not in regra["status_promocao"]:
        return []
    if not find_ids:
        return []
    doc = carregar(caminho)
    por_id = {item["id"]: item for item in doc["finds"]}
    bloqueiam = set(regra["promocao_bloqueada_por"])
    achados = []
    for find_id in find_ids:
        item = por_id.get(find_id)
        if item is None or (item["status"] == "ABERTO" and item["severidade"] in bloqueiam):
            achados.append(find_id)
    return achados
