"""Work Order da tarefa. O kernel só executa o que esta política autoriza."""
import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, model_validator

RAIZ = Path(__file__).resolve().parents[2]
SHA = r"^[0-9a-f]{64}$"


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
    task_type: str = Field(min_length=3)
    policy_version: str = Field(min_length=1)
    state: str = Field(pattern=r"^PREAUTHORIZED$")
    entradas: list[Entrada] = Field(min_length=1)
    parametros: dict[str, str] = Field(default_factory=dict)


def politica() -> dict:
    return json.loads((RAIZ / "policies" / "tarefas.json").read_text(encoding="utf-8"))


def carregar_wo(caminho: Path) -> WorkOrderTarefa:
    bruto = json.loads(caminho.read_text(encoding="utf-8"))
    wo = WorkOrderTarefa.model_validate(bruto)
    doc = politica()
    if wo.policy_version != doc["versao"]:
        raise ValueError("policy_version não confere com policies/tarefas.json")
    tarefa = doc["tarefas"].get(wo.task_type)
    if tarefa is None:
        raise ValueError(f"task_type fora da política: {wo.task_type}")
    classes = doc["classes"]
    for entrada in wo.entradas:
        if entrada.classe not in classes:
            raise ValueError(f"classe fora da política: {entrada.classe}")
    if tarefa["exige_checker"]:
        if not wo.checker_id or wo.checker_id == wo.authorized_by:
            raise ValueError("checker_id obrigatório e diferente de authorized_by")
    if wo.task_type == "obter":
        for entrada in wo.entradas:
            if entrada.sha256:
                raise ValueError("obter não aceita sha256 declarado")
    else:
        for entrada in wo.entradas:
            if not entrada.sha256:
                raise ValueError(f"{wo.task_type} exige sha256 de cada entrada")
    return wo


def decidir_atomizacao(classe: str) -> str:
    return politica()["classes"][classe]["atomizar"]
