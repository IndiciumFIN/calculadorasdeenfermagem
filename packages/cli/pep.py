"""Work Order pede permissão. A definição da tarefa é outro objeto e não vem na ordem."""
import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, model_validator

RAIZ = Path(__file__).resolve().parents[2]
SHA = r"^[0-9a-f]{64}$"

VALIDADORES_POR_PROCEDIMENTO = {
    "obter": [
        "VAL-WO-ESTRUTURA",
        "VAL-DEFINICAO",
        "VAL-CAMINHO",
        "VAL-CLASSE",
        "VAL-SHA-ENTRADA",
        "VAL-HTML",
    ],
    "atomizar": [
        "VAL-WO-ESTRUTURA",
        "VAL-DEFINICAO",
        "VAL-CAMINHO",
        "VAL-CLASSE",
        "VAL-SHA-ENTRADA",
        "VAL-HASH-ARQUIVO",
        "VAL-CLASSE-ATOMO",
    ],
    "validar": [
        "VAL-WO-ESTRUTURA",
        "VAL-DEFINICAO",
        "VAL-CAMINHO",
        "VAL-CLASSE",
        "VAL-SHA-ENTRADA",
        "VAL-CHECKER-TEXTUAL",
        "VAL-HASH-ARQUIVO",
        "VAL-CLASSE-ATOMO",
    ],
    "retirar": [
        "VAL-WO-ESTRUTURA",
        "VAL-DEFINICAO",
        "VAL-CAMINHO",
        "VAL-CLASSE",
        "VAL-SHA-ENTRADA",
        "VAL-CHECKER-TEXTUAL",
        "VAL-HASH-ARQUIVO",
        "VAL-PARECER",
    ],
}


class Entrada(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id_origem: str = Field(min_length=3)
    caminho: str = Field(min_length=1)
    classe: str = Field(min_length=3)
    sha256: str | None = Field(default=None, pattern=SHA)

    @model_validator(mode="after")
    def caminho_interno(self):
        puro = Path(self.caminho)
        if puro.is_absolute() or ".." in puro.parts:
            raise ValueError("caminho precisa ser relativo e sem '..'")
        return self


class WorkOrderTarefa(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^WO-[A-Z0-9-]+$")
    contract_version: str = Field(min_length=1)
    authorized_by: str = Field(min_length=3)
    checker_id: str | None = None
    task_id: str = Field(pattern=r"^TAREFA-[A-Z0-9-]+$")
    task_version: str = Field(min_length=1)
    task_type: str = Field(min_length=3)
    policy_version: str = Field(min_length=1)
    state: str = Field(pattern=r"^PREAUTHORIZED$")
    entradas: list[Entrada] = Field(min_length=1)
    parametros: dict[str, str] = Field(default_factory=dict)


def politica() -> dict:
    return json.loads((RAIZ / "policies" / "tarefas.json").read_text(encoding="utf-8"))


def definicoes() -> dict:
    return json.loads((RAIZ / "policies" / "definicoes_tarefa.json").read_text(encoding="utf-8"))


def validadores() -> dict:
    return json.loads((RAIZ / "policies" / "validadores.json").read_text(encoding="utf-8"))


def resolver_definicao(task_id: str, task_version: str) -> dict:
    bruto = definicoes()["definicoes"].get(task_id)
    if bruto is None:
        raise ValueError(f"definição ausente: {task_id}")
    if bruto["versao"] != task_version:
        raise ValueError(f"task_version não confere com a definição {task_id}")
    if bruto["qualificacao"] != "QUALIFICADA":
        raise ValueError(f"tarefa não qualificada: {task_id}")
    registro = validadores()["validadores"]
    declarados = bruto["validadores"]
    if any(item not in registro for item in declarados):
        raise ValueError(f"validador fora do registro: {task_id}")
    esperados = VALIDADORES_POR_PROCEDIMENTO.get(bruto["procedimento"])
    if esperados is None or set(declarados) != set(esperados) or len(declarados) != len(esperados):
        raise ValueError(f"validadores da definição não são os implementados: {task_id}")
    return bruto


def carregar_wo(caminho: Path) -> WorkOrderTarefa:
    bruto = json.loads(caminho.read_text(encoding="utf-8"))
    wo = WorkOrderTarefa.model_validate(bruto)
    doc = politica()
    if wo.policy_version != doc["versao"]:
        raise ValueError("policy_version não confere com policies/tarefas.json")
    definicao = resolver_definicao(wo.task_id, wo.task_version)
    if wo.task_type != definicao["procedimento"]:
        raise ValueError("Work Order não redefine o procedimento")
    classes = doc["classes"]
    for entrada in wo.entradas:
        if entrada.classe not in classes:
            raise ValueError(f"classe fora da política: {entrada.classe}")
    if definicao["exige_checker"]:
        if not wo.checker_id or wo.checker_id == wo.authorized_by:
            raise ValueError("checker_id obrigatório e diferente de authorized_by")
    if definicao["sha256_entrada"] == "proibido":
        for entrada in wo.entradas:
            if entrada.sha256:
                raise ValueError("obter não aceita sha256 declarado")
    elif definicao["sha256_entrada"] == "obrigatorio":
        for entrada in wo.entradas:
            if not entrada.sha256:
                raise ValueError(f"{wo.task_type} exige sha256 de cada entrada")
    else:
        raise ValueError("sha256_entrada fora da definição")
    return wo


def decidir_atomizacao(classe: str) -> str:
    return politica()["classes"][classe]["atomizar"]
