"""Reconciliação do pacote zero-trust. A determinação não homologa e não implanta."""
import hashlib
import inspect
import io
import json
import re
import zipfile
from collections import Counter

from packages.cli.pep import RAIZ, VALIDADORES_POR_PROCEDIMENTO

ZIP_REL = "data/candidato/zero_trust/CKO_KERNEL_ZERO_TRUST_WO_v0_1_0.zip"
ZIP_SHA = "9b9413a7ca7f6318a6f7126e0f0bb2df7cd1c48478e65e8b2f2fb06d45bb78b1"
ZIP_BYTES = 54261
DRIVE_ID = "1mL-ILSBH9NlPyQXp2Bg7d2yZ5hpW6O3z"
PREFIXO = "CKO_KERNEL_ZERO_TRUST_WO_v0_1_0/"
BASE_OBSERVADA = "7cea80c572b1a789aa45388ff2af6828c1ff82b4"
POLITICA = RAIZ / "policies" / "zero_trust.json"
VIGENTES = ("AGT-EXTRATOR-001", "AGT-AUDITOR-001")
DETERMINACOES = frozenset({
    "CONFERIDO",
    "CONFIRMADO_HOLD",
    "NAO_REVOGA",
    "NAO_IMPLANTAR",
    "SEM_PROMOCAO",
    "REFERENCIA",
    "AUSENTE_DO_KERNEL",
    "PRESERVADO_VIGENTE",
    "DIVERGENTE",
})
CENSO = {"arquivos": 32, "finds": 12, "identidades": 128, "portas": 7, "tarefas": 25, "validadores": 16}


def documento() -> dict:
    return json.loads(POLITICA.read_text(encoding="utf-8"))


def _ler(rel: str) -> dict:
    return json.loads((RAIZ / rel).read_text(encoding="utf-8"))


def _item(ident: str, classe: str, determinacao: str, motivo: str) -> dict:
    if determinacao not in DETERMINACOES:
        determinacao = "INDETERMINADO"
        motivo = "rótulo fora do vocabulário da determinação"
    return {
        "id": ident,
        "classe": classe,
        "determinacao": determinacao,
        "autorizacao": False,
        "motivo": motivo,
    }


def _zip():
    caminho = RAIZ / ZIP_REL
    bruto = caminho.read_bytes()
    digest = hashlib.sha256(bruto).hexdigest()
    if len(bruto) != ZIP_BYTES or digest != ZIP_SHA:
        raise ValueError("ERR_PACOTE_SHA")
    arquivo = zipfile.ZipFile(io.BytesIO(bruto))
    somas = json.loads(arquivo.read(PREFIXO + "SHA256SUMS.json"))
    divergencias = []
    for nome, esperado in somas["files"].items():
        if hashlib.sha256(arquivo.read(PREFIXO + nome)).hexdigest() != esperado:
            divergencias.append(nome)
    return arquivo, somas, divergencias


def _json_zip(arquivo, nome: str) -> dict:
    return json.loads(arquivo.read(PREFIXO + nome))


def _registro_agentes() -> dict:
    return _ler("agents/registry.json")["agentes"]


def _status_registro(item: dict | None) -> str | None:
    if not isinstance(item, dict):
        return None
    return (item.get("recertificacao") or {}).get("status")


def _qualificadas() -> dict:
    return {
        chave: item
        for chave, item in _ler("policies/definicoes_tarefa.json")["definicoes"].items()
        if item.get("qualificacao") == "QUALIFICADA"
    }


def _finds(texto: str) -> list[str]:
    return re.findall(r"AG-KER-\d{3}", texto)


def _fonte(rel: str) -> str:
    return (RAIZ / rel).read_text(encoding="utf-8")


def _corpo(func) -> str:
    return inspect.getsource(func)


def _gateway() -> str:
    return _fonte("supabase/functions/cko-deepseek-gateway/index.ts")


def _sql_aplicado(texto: str) -> bool:
    marca = "CANDIDATE / REVIEW ONLY. DO NOT EXECUTE WITHOUT DBA"
    return any(marca in path.read_text(encoding="utf-8") for path in (RAIZ / "supabase" / "migrations").glob("*.sql"))


def _guard_implantado() -> bool:
    gateway = _gateway()
    return "admitLLMInvocation" in gateway or "CKO_KERNEL_INTROSPECTION_URL" in gateway


def _cko_guard_implantado() -> bool:
    return (RAIZ / "packages" / "cli" / "cko_guard").exists()


def _validador_no_procedimento() -> list[str]:
    achados = []
    for procedimento, ids in VALIDADORES_POR_PROCEDIMENTO.items():
        for ident in ids:
            if ident.startswith("VAL-ZT-") or ident.startswith("V-"):
                achados.append(f"{procedimento}:{ident}")
    for definicao in _ler("policies/definicoes_tarefa.json")["definicoes"].values():
        for ident in definicao.get("validadores", []):
            if ident.startswith("VAL-ZT-") or ident.startswith("V-"):
                achados.append(f"{definicao['id']}:{ident}")
    return achados


def _integridade(somas: dict, divergencias: list[str]) -> dict:
    status = somas.get("status")
    contagem = somas.get("file_count")
    if divergencias or status != "CANDIDATE_NOT_DEPLOYED" or contagem != CENSO["arquivos"] or _cko_guard_implantado():
        return _item(
            "PACOTE-INTEGRIDADE",
            "PACOTE",
            "DIVERGENTE",
            "O zip deixa de conferir com o manifesto interno ou o protótipo aparece no kernel.",
        )
    return _item(
        "PACOTE-INTEGRIDADE",
        "PACOTE",
        "CONFERIDO",
        "SHA-256 externo e os 32 arquivos internos conferem. cko_guard permanece dentro do zip.",
    )


def _base(inventario: dict) -> dict:
    bases = {item.get("source_sha") for item in inventario["agents"]}
    lote = RAIZ / "contracts" / "work_orders" / "WO-2026_10_15_0036.json"
    if bases == {BASE_OBSERVADA} and lote.is_file():
        return _item(
            "PACOTE-BASE",
            "PACOTE",
            "CONFERIDO",
            "Todos os agentes do pacote declaram a base 7cea80c. O kernel local já contém WO-2026_10_15_0036.",
        )
    return _item("PACOTE-BASE", "PACOTE", "DIVERGENTE", "A base declarada no pacote não fecha com o kernel local.")


def _censo(observado: dict) -> dict:
    if observado == CENSO:
        return _item(
            "PACOTE-CENSO",
            "PACOTE",
            "CONFERIDO",
            "O pacote traz 128 identidades, 25 tarefas, 16 validadores, 7 portas e 12 FINDs.",
        )
    return _item("PACOTE-CENSO", "PACOTE", "DIVERGENTE", "A contagem lida no pacote difere do censo declarado.")


def _julgar_find(ident: str, exclusividade: dict) -> dict:
    from packages.cli.finds import encerrar
    from packages.cli.kernel import _fail
    from packages.cli.pep import WorkOrderTarefa

    gateway = _gateway()
    agentes = _registro_agentes()
    vigentes = sorted(chave for chave, item in agentes.items() if _status_registro(item) == "vigente")
    candidatos = [chave for chave, item in agentes.items() if _status_registro(item) == "candidato"]
    campos = set(WorkOrderTarefa.model_fields)
    falha = _corpo(_fail)
    fechamento = _corpo(encerrar)
    schema = _fonte("contracts/work_order.schema.json")
    pep = _fonte("packages/cli/pep.py")
    runner = _fonte("packages/cli/llm_runner.py")
    gate = _fonte(".github/workflows/gate.yml")
    registry = _fonte("packages/cli/registry.py")
    qualificadas = _qualificadas()
    checks = {
        "AG-KER-001": (
            campos >= {"authorized_by"} and "assinatura" not in campos and "signature" not in campos,
            "CONFIRMADO_HOLD",
            "authorized_by permanece texto com tamanho mínimo 3.",
        ),
        "AG-KER-002": (
            "def add(" in registry and "def set_status(" in registry,
            "CONFIRMADO_HOLD",
            "add e set_status gravam o registry sem Work Order.",
        ),
        "AG-KER-003": (
            "work_order" not in gateway and "WO-" not in gateway,
            "CONFIRMADO_HOLD",
            "O gateway vigente não contém work_order.",
        ),
        "AG-KER-004": (
            len(agentes) == 110 and set(vigentes) == set(VIGENTES) and len(candidatos) == 108 and exclusividade.get("enforcement_state") == "HOLD_CANDIDATE",
            "CONFIRMADO_HOLD",
            "O registro tem 110 agentes: 2 vigentes e 108 candidatos. A exclusividade do pacote está em HOLD_CANDIDATE.",
        ),
        "AG-KER-005": (
            exclusividade.get("no_claim_of_existing_technical_exclusivity") is True and "AGT-ORCH-001" not in agentes,
            "CONFIRMADO_HOLD",
            "Os superagentes do pacote têm execução negada. AGT-ORCH-001 continua fora do registro.",
        ),
        "AG-KER-006": (
            all(ident in qualificadas for ident in (
                "TAREFA-OBTER", "TAREFA-ATOMIZAR", "TAREFA-VALIDAR", "TAREFA-RETIRAR",
                "TAREFA-FIND-REGISTRAR", "TAREFA-FIND-VINCULAR", "TAREFA-FIND-ENCERRAR",
                "TAREFA-FIND-ANALISAR", "TAREFA-FIND-CORRIGIR",
            )),
            "NAO_REVOGA",
            "As 9 tarefas qualificadas permanecem qualificadas. O overlay marca homologação independente como falsa.",
        ),
        "AG-KER-007": (
            "typer.Exit(2)" in falha and "registrar" not in falha,
            "CONFIRMADO_HOLD",
            "_fail encerra com exit 2. O registro de FIND continua um procedimento explícito.",
        ),
        "AG-KER-008": (
            "evidencia_sha256" in fechamento and "reteste" not in fechamento and 'find["status"] = "FECHADO"' in fechamento,
            "CONFIRMADO_HOLD",
            "O encerramento exige SHA-256 da evidência e mantém o histórico. O reteste independente não é parâmetro.",
        ),
        "AG-KER-009": (
            "gates/aggregate.sh" in gate and "work_order" not in gate,
            "CONFIRMADO_HOLD",
            "O gate agregador executa os scripts de verificação. Ele não amarra cada escrita a uma Work Order.",
        ),
        "AG-KER-010": (
            '"^WO-[A-Z0-9-]+$"' in schema and 'r"^WO-\\d{4}_\\d{2}_\\d{2}_\\d{4}$"' in pep,
            "CONFIRMADO_HOLD",
            "O schema de LLM usa WO-[A-Z0-9-]+. A Work Order de tarefa usa WO-AAAA_MM_DD_0000.",
        ),
        "AG-KER-011": (
            '"homologacao_juridica": False' in runner and "work_order" not in gateway,
            "CONFIRMADO_HOLD",
            "O runner local grava homologacao_juridica falsa. O gateway segue sem essa checagem.",
        ),
        "AG-KER-012": (
            "save_registry" in registry and "ledger" not in registry,
            "CONFIRMADO_HOLD",
            "O registry local é um arquivo JSON regravável. add e set_status não exigem ledger assinado.",
        ),
    }
    if ident not in checks:
        return _item(ident, "FIND", "DIVERGENTE", "O FIND não pertence ao conjunto AG-KER-001..012.")
    ok, determinacao, texto = checks[ident]
    if not ok:
        return _item(ident, "FIND", "DIVERGENTE", f"A leitura atual do kernel deixa de sustentar {ident}.")
    return _item(ident, "FIND", determinacao, texto)


def _julgar_identidade(agente: dict, registro: dict) -> dict:
    ident = agente["agent_id"]
    live = registro.get(ident)
    origem = agente.get("status_source")
    if agente.get("may_issue_wo") is not False or agente.get("target_state") != "HOLD_RECONCILE":
        return _item(ident, "IDENTIDADE", "DIVERGENTE", "O pacote declara emissão de Work Order ou estado diferente de HOLD_RECONCILE.")
    if origem == "vigente" and _status_registro(live) == "vigente" and ident in VIGENTES:
        return _item(ident, "IDENTIDADE", "PRESERVADO_VIGENTE", "Permanece vigente no registro executável.")
    if origem == "candidato" and _status_registro(live) == "candidato":
        return _item(ident, "IDENTIDADE", "SEM_PROMOCAO", "Permanece candidato no registro executável.")
    if origem == "NOT_PRESENT_IN_REPO_CANDIDATE" and live is None:
        return _item(ident, "IDENTIDADE", "NAO_IMPLANTAR", "Continua ausente do registro executável.")
    return _item(ident, "IDENTIDADE", "DIVERGENTE", "O estado local do agente difere do inventário do pacote.")


def _julgar_tarefa(tarefa: dict, locais: dict) -> dict:
    ident = tarefa["task_id"]
    local = locais.get(ident)
    if tarefa.get("independently_homologated") is not False:
        return _item(ident, "TAREFA", "DIVERGENTE", "O pacote marca a tarefa como homologada de forma independente.")
    if tarefa.get("origin") == "EXISTING_REPO_TASK_REGISTRY":
        if local is None or local.get("qualificacao") != tarefa.get("source_qualification"):
            return _item(ident, "TAREFA", "DIVERGENTE", "A qualificação local difere da qualificação declarada no pacote.")
        if tarefa.get("source_qualification") == "QUALIFICADA":
            return _item(ident, "TAREFA", "NAO_REVOGA", "A qualificação local permanece QUALIFICADA.")
        return _item(ident, "TAREFA", "CONFIRMADO_HOLD", "A definição local permanece NAO_QUALIFICADA.")
    if tarefa.get("origin") == "NEW_PROPOSED_CANDIDATE" and tarefa.get("state") == "CANDIDATE_NOT_HOMOLOGATED" and local is None:
        return _item(ident, "TAREFA", "NAO_IMPLANTAR", "A tarefa proposta continua fora de policies/definicoes_tarefa.json.")
    return _item(ident, "TAREFA", "DIVERGENTE", "A origem da tarefa no pacote não fecha com o registro local.")


def _julgar_validador(ident: str, registro: dict, status: str) -> dict:
    if status == "CANDIDATE_REFERENCE_IMPLEMENTATION" and ident not in registro:
        return _item(ident, "VALIDADOR", "AUSENTE_DO_KERNEL", "O validador V-* continua fora de policies/validadores.json.")
    return _item(ident, "VALIDADOR", "DIVERGENTE", "O validador de referência aparece no kernel ou muda de estado.")


def _julgar_porta(porta: dict) -> dict:
    ident = porta["port"]
    if porta.get("verified") == "NOT_DEPLOYED":
        return _item(ident, "PORTA", "CONFIRMADO_HOLD", "A porta permanece NOT_DEPLOYED.")
    return _item(ident, "PORTA", "DIVERGENTE", "A matriz deixa de declarar a porta como NOT_DEPLOYED.")


def _referencias(arquivo) -> list[dict]:
    sql = arquivo.read(PREFIXO + "integration/db_acl_REFERENCE_ONLY.sql").decode("utf-8")
    guard = arquivo.read(PREFIXO + "integration/gateway_guard_REFERENCE_ONLY.ts").decode("utf-8")
    sql_ok = "DO NOT EXECUTE" in sql and sql.strip().endswith("ROLLBACK;") and not _sql_aplicado(sql)
    gateway_ok = "NOT DEPLOYED" in guard and not _guard_implantado() and "work_order" not in _gateway()
    return [
        _item(
            "REFERENCIA-SQL",
            "REFERENCIA",
            "REFERENCIA" if sql_ok else "DIVERGENTE",
            "O script declara DO NOT EXECUTE e termina em ROLLBACK. Nenhuma migration o contém."
            if sql_ok
            else "O SQL de referência deixou de permanecer só no zip.",
        ),
        _item(
            "REFERENCIA-GATEWAY",
            "REFERENCIA",
            "REFERENCIA" if gateway_ok else "DIVERGENTE",
            "O arquivo de referência permanece no zip. O gateway vigente não o incorpora."
            if gateway_ok
            else "O gateway vigente passou a incorporar a referência do pacote.",
        ),
    ]


def _contrato() -> dict:
    """Preserva os nove procedimentos originais e valida extensões por contrato."""
    versao = _ler("policies/tarefas.json")["versao"]
    antigos = {
        "obter": "TAREFA-OBTER", "atomizar": "TAREFA-ATOMIZAR",
        "validar": "TAREFA-VALIDAR", "retirar": "TAREFA-RETIRAR",
        "registrar-find": "TAREFA-FIND-REGISTRAR",
        "vincular-find": "TAREFA-FIND-VINCULAR",
        "analisar-find": "TAREFA-FIND-ANALISAR",
        "corrigir-find": "TAREFA-FIND-CORRIGIR",
        "encerrar-find": "TAREFA-FIND-ENCERRAR",
    }
    extensoes = {
        "auditar-inventario": "TAREFA-AUDITAR-INVENTARIO",
        "auditar-zip": "TAREFA-AUDITAR-ZIP",
        "importar-drive": "TAREFA-IMPORTAR-DRIVE",
    }
    opcionais = {"auditar-duplicatas": "TAREFA-AUDITAR-DUPLICATAS"}
    definicoes = _ler("policies/definicoes_tarefa.json")["definicoes"]
    if "TAREFA-AUDITAR-DUPLICATAS" in definicoes:
        extensoes.update(opcionais)
    procedimentos = set(VALIDADORES_POR_PROCEDIMENTO)
    esperado = antigos | extensoes
    validadores = _ler("policies/validadores.json")["validadores"]
    protegido = (
        versao == "1.0.0"
        and procedimentos == set(esperado)
        and not _validador_no_procedimento()
    )
    if protegido:
        for nome, task_id in esperado.items():
            d = definicoes.get(task_id, {})
            exigidos = VALIDADORES_POR_PROCEDIMENTO[nome]
            if (
                d.get("versao") != "1.0.0"
                or d.get("qualificacao") != "QUALIFICADA"
                or d.get("procedimento") != nome
                or d.get("validadores") != exigidos
                or any(v not in validadores for v in exigidos)
            ):
                protegido = False
                break
    if protegido:
        return _item(
            "CONTRATO-TAREFA", "CONTRATO", "NAO_REVOGA",
            "Nove procedimentos originais preservados; extensões auditadas por allowlist exata, Work Order e validadores.",
        )
    return _item(
        "CONTRATO-TAREFA", "CONTRATO", "DIVERGENTE",
        "Conjunto de procedimentos ou qualificação/validadores divergentes; revisão humana necessária.",
    )


def _registro_find() -> dict:
    texto = _fonte("data/finds/registro.json")
    if "AG-KER-" not in texto:
        return _item("REGISTRO-FIND", "FIND", "NAO_IMPLANTAR", "AG-KER-001..012 permanecem fora de data/finds/registro.json.")
    return _item("REGISTRO-FIND", "FIND", "DIVERGENTE", "Um FIND AG-KER entrou no registro executável.")


def _superagentes(inventario: dict, exclusividade: dict, registro: dict) -> bool:
    ids = set(exclusividade.get("superagent_ids") or [])
    if "AGT-ORCH-001" not in ids:
        return False
    por_id = {item["agent_id"]: item for item in inventario["agents"]}
    if set(por_id) & set(ids) != ids:
        return False
    for ident in ids:
        agente = por_id[ident]
        if agente.get("may_execute_wo") is not False:
            return False
        live = registro.get(ident)
        if ident == "AGT-ORCH-001":
            if live is not None or agente.get("status_source") != "NOT_PRESENT_IN_REPO_CANDIDATE":
                return False
        elif _status_registro(live) != "candidato":
            return False
    return True


def determinar() -> dict:
    try:
        arquivo, somas, divergencias = _zip()
    except (OSError, ValueError, KeyError, zipfile.BadZipFile, json.JSONDecodeError):
        return _fecho([], "INCOMPLETA", 1)
    if divergencias:
        return _fecho([_integridade(somas, divergencias)], "INCOMPLETA", 1)
    inventario = _json_zip(arquivo, "registries/agent_identity_inventory.json")
    tarefas = _json_zip(arquivo, "registries/task_definition_registry.json")
    validadores = _json_zip(arquivo, "registries/validator_registry.json")
    portas = _json_zip(arquivo, "integration/enforcement_matrix.json")
    exclusividade = _json_zip(arquivo, "registries/role_exclusivity.json")
    finds = _finds(arquivo.read(PREFIXO + "SECURITY_FINDINGS.md").decode("utf-8"))
    registro = _registro_agentes()
    locais = _ler("policies/definicoes_tarefa.json")["definicoes"]
    kernel_validadores = _ler("policies/validadores.json")["validadores"]
    itens = [
        _integridade(somas, divergencias),
        _base(inventario),
        _censo({
            "arquivos": somas.get("file_count"),
            "finds": len(set(finds)),
            "identidades": len(inventario["agents"]),
            "portas": len(portas["required_ports"]),
            "tarefas": len(tarefas["tasks"]),
            "validadores": len(validadores["validators"]),
        }),
    ]
    for ident in sorted(set(finds)):
        item = _julgar_find(ident, exclusividade)
        if ident == "AG-KER-005" and not _superagentes(inventario, exclusividade, registro):
            item = _item(ident, "FIND", "DIVERGENTE", "A execução dos superagentes ou a ausência de AGT-ORCH-001 deixa de conferir.")
        itens.append(item)
    for agente in sorted(inventario["agents"], key=lambda item: item["agent_id"]):
        itens.append(_julgar_identidade(agente, registro))
    for tarefa in sorted(tarefas["tasks"].values(), key=lambda item: item["task_id"]):
        itens.append(_julgar_tarefa(tarefa, locais))
    for ident in sorted(validadores["validators"]):
        itens.append(_julgar_validador(ident, kernel_validadores, validadores.get("validator_status")))
    for porta in portas["required_ports"]:
        itens.append(_julgar_porta(porta))
    itens.extend(_referencias(arquivo))
    itens.append(_contrato())
    itens.append(_registro_find())
    indeterminados = sum(1 for item in itens if item["determinacao"] == "INDETERMINADO")
    return _fecho(itens, "TOTAL" if indeterminados == 0 else "INCOMPLETA", indeterminados)


def _fecho(itens: list[dict], cobertura: str, indeterminados: int) -> dict:
    contagem = Counter(item["determinacao"] for item in itens)
    return {
        "versao": "0.1.0",
        "efeito": "DETERMINACAO",
        "homologacao_juridica": False,
        "autorizacao": False,
        "cobertura": cobertura,
        "indeterminados": indeterminados,
        "drive_id": DRIVE_ID,
        "arquivo": ZIP_REL,
        "bytes": ZIP_BYTES,
        "sha256": ZIP_SHA,
        "acesso": "somente_dono",
        "metodo": "conector_autenticado",
        "status_pacote": "CANDIDATE_NOT_HOMOLOGATED",
        "base_observada": BASE_OBSERVADA,
        "nao_substitui": "CKO-TAREFA-1.0.0",
        "contagens": dict(sorted(contagem.items())),
        "itens": itens,
    }


def _por_id(det: dict) -> dict:
    return {item["id"]: item for item in det.get("itens", [])}


def val_pacote(determinacao=None) -> list[str]:
    det = determinar() if determinacao is None else determinacao
    item = _por_id(det).get("PACOTE-INTEGRIDADE")
    issues = []
    if det.get("sha256") != ZIP_SHA or det.get("bytes") != ZIP_BYTES:
        issues.append("ERR_PACOTE_SHA")
    if det.get("status_pacote") != "CANDIDATE_NOT_HOMOLOGATED":
        issues.append("ERR_PACOTE_STATUS")
    if item is None or item.get("determinacao") != "CONFERIDO":
        issues.append("ERR_PACOTE_DIVERGENTE")
    if det.get("autorizacao") is not False or (item or {}).get("autorizacao") is not False:
        issues.append("ERR_AUTORIZACAO")
    return issues


def val_sem_promocao(determinacao=None) -> list[str]:
    det = determinar() if determinacao is None else determinacao
    identidades = [item for item in det.get("itens", []) if item.get("classe") == "IDENTIDADE"]
    issues = []
    preservados = [item["id"] for item in identidades if item.get("determinacao") == "PRESERVADO_VIGENTE"]
    if sorted(preservados) != sorted(VIGENTES):
        issues.append("ERR_VIGENTES")
    if sum(item.get("determinacao") == "SEM_PROMOCAO" for item in identidades) != 108:
        issues.append("ERR_CANDIDATOS")
    if sum(item.get("determinacao") == "NAO_IMPLANTAR" for item in identidades) != 18:
        issues.append("ERR_AUSENTES")
    if any(item.get("determinacao") == "DIVERGENTE" for item in identidades):
        issues.append("ERR_IDENTIDADE_DIVERGENTE")
    return issues


def val_nao_revoga(determinacao=None) -> list[str]:
    det = determinar() if determinacao is None else determinacao
    por_id = _por_id(det)
    issues = []
    qualificadas = _qualificadas()
    if len(qualificadas) != 9:
        issues.append("ERR_QUALIFICADAS")
    for ident in qualificadas:
        item = por_id.get(ident)
        if item is None or item.get("determinacao") != "NAO_REVOGA":
            issues.append(f"ERR_REVOGA:{ident}")
    if (por_id.get("CONTRATO-TAREFA") or {}).get("determinacao") != "NAO_REVOGA":
        issues.append("ERR_CONTRATO")
    if (por_id.get("AG-KER-006") or {}).get("determinacao") != "NAO_REVOGA":
        issues.append("ERR_OVERLAY")
    if _validador_no_procedimento():
        issues.append("ERR_VALIDADOR_NO_PROCEDIMENTO")
    return issues


def val_portas(determinacao=None) -> list[str]:
    det = determinar() if determinacao is None else determinacao
    por_id = _por_id(det)
    issues = []
    portas = [item for item in det.get("itens", []) if item.get("classe") == "PORTA"]
    if len(portas) != 7 or any(item.get("determinacao") != "CONFIRMADO_HOLD" for item in portas):
        issues.append("ERR_PORTA")
    if (por_id.get("REFERENCIA-SQL") or {}).get("determinacao") != "REFERENCIA":
        issues.append("ERR_SQL")
    if (por_id.get("REFERENCIA-GATEWAY") or {}).get("determinacao") != "REFERENCIA":
        issues.append("ERR_GATEWAY")
    if _cko_guard_implantado() or _guard_implantado() or _sql_aplicado(""):
        issues.append("ERR_IMPLANTADO")
    return issues


def val_cobertura(determinacao=None) -> list[str]:
    det = determinar() if determinacao is None else determinacao
    issues = []
    if det.get("cobertura") != "TOTAL" or det.get("indeterminados") != 0:
        issues.append("ERR_COBERTURA")
    if det.get("autorizacao") is not False or det.get("homologacao_juridica") is not False or det.get("efeito") != "DETERMINACAO":
        issues.append("ERR_EFEITO")
    for item in det.get("itens", []):
        if item.get("autorizacao") is not False:
            issues.append(f"ERR_AUTORIZACAO:{item.get('id')}")
        if item.get("determinacao") not in DETERMINACOES:
            issues.append(f"ERR_INDETERMINADO:{item.get('id')}")
    if not det.get("itens"):
        issues.append("ERR_VAZIO")
    return issues


def avaliar(policy_id: str, contexto: dict | None = None) -> dict:
    doc = documento()
    politica = next((item for item in doc["politicas"] if item["policy_id"] == policy_id), None)
    if politica is None:
        return {
            "policy_id": policy_id,
            "result": "HOLD",
            "reason": "ERR_POLITICA_DESCONHECIDA",
            "authorization": False,
        }
    ctx = contexto or {}
    det = ctx.get("determinacao")
    regra = politica["rule_key"]
    if regra == "pacote_conferido":
        issues = val_pacote(det)
    elif regra == "sem_promocao":
        issues = val_sem_promocao(det)
    elif regra == "overlay_nao_revoga":
        issues = val_nao_revoga(det)
    elif regra == "portas_nao_implantadas":
        issues = val_portas(det)
    elif regra == "determinacao_total":
        issues = val_cobertura(det)
    else:
        issues = ["ERR_REGRA_DESCONHECIDA"]
    return {
        "policy_id": policy_id,
        "result": "HOLD" if issues else "PASS_LOCAL",
        "reason": "; ".join(issues) if issues else "LOCAL_CHECK_PASSED_NOT_AUTHORIZATION",
        "authorization": False,
    }
