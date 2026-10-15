"""Políticas GRC candidatas. PASS_LOCAL não autoriza e não muda estado."""
import hashlib
import importlib
import json
from pathlib import Path

from packages.cli.pep import RAIZ

ARQUIVO = RAIZ / "policies" / "grc.json"
PRIVILEGIADOS = {
    "REMOTE_WRITE",
    "WRITE_CANONICAL_STATE",
    "ALTER_CANONICAL_STATE",
    "ALTER_CANONICAL",
    "AUTHORIZE_WO",
    "CREATE_WO_AS_AUTHORITY",
    "CLOSE_FIND",
    "PUBLISH",
    "CHANGE_POLICY",
    "DELETE_SOURCE",
}
EVENTOS = {
    "FIND_TRIAGED",
    "RCA_DOCUMENTED",
    "CORRECTION_PROPOSED",
    "CORRECTION_RECORDED",
    "RETEST_RECORDED",
    "CLOSURE_PROPOSED",
}


def documento() -> dict:
    return json.loads(ARQUIVO.read_text(encoding="utf-8"))


def _digest(obj) -> str:
    corpo = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(corpo).hexdigest()


def _ler(relativo: str):
    return json.loads((RAIZ / relativo).read_text(encoding="utf-8"))


def val_agentes(agentes) -> list[str]:
    issues = []
    if not isinstance(agentes, list) or not agentes:
        return ["ERR_AGENTES_AUSENTES"]
    vistos = set()
    for agente in agentes:
        aid = agente.get("agent_id", "?")
        if aid in vistos:
            issues.append(f"ERR_AGENTE_DUPLICADO:{aid}")
        vistos.add(aid)
        efeitos = set(agente.get("allowed_effects", []))
        if efeitos & PRIVILEGIADOS:
            issues.append(f"ERR_AGENTE_EFEITO_PRIVILEGIADO:{aid}")
        if not {"READ_SNAPSHOT", "RETURN_DIAGNOSTIC"}.issuperset(efeitos):
            issues.append(f"ERR_AGENTE_EFEITO_DESCONHECIDO:{aid}")
        for campo in ("may_approve_work_order", "may_execute_correction", "may_change_status"):
            if agente.get(campo) is not False:
                issues.append(f"ERR_AGENTE_AUTORIDADE:{aid}:{campo}")
        if agente.get("enunciado_oficial_armazenado") is not False:
            issues.append(f"ERR_ENUNCIADO_OFICIAL:{aid}")
    return issues


def val_controle(controles) -> list[str]:
    issues = []
    if not isinstance(controles, list) or not controles:
        return ["ERR_CONTROLES_AUSENTES"]
    esperados = {
        "template_status": "MODEL_DRAFT_NOT_IMPLEMENTED",
        "implementation_status": "NOT_VERIFIED",
        "effectiveness_status": "NOT_ASSESSED",
        "evaluation_status": "NOT_TESTED",
    }
    for controle in controles:
        cid = controle.get("control_id", "?")
        for campo, valor in esperados.items():
            if controle.get(campo) != valor:
                issues.append(f"ERR_MODELO_EFICAZ_SEM_PROVA:{cid}:{campo}")
    return issues


def val_definicao_tarefa(tarefa) -> list[str]:
    if not isinstance(tarefa, dict):
        return ["ERR_DEFINICAO_AUSENTE"]
    issues = []
    if tarefa.get("status") != "CANDIDATE_NOT_HOMOLOGATED":
        issues.append("ERR_DEFINICAO_NAO_CANDIDATA")
    if tarefa.get("state") == "PREAUTHORIZED":
        issues.append("ERR_DEFINICAO_MISTURADA_COM_ORDEM")
    if "REMOTE_WRITE" in tarefa.get("allowed_effects", []):
        issues.append("ERR_DEFINICAO_ESCRITA_REMOTA")
    return issues


def val_pedido_wo(pedido) -> list[str]:
    if not isinstance(pedido, dict):
        return ["ERR_PEDIDO_AUSENTE"]
    issues = []
    if pedido.get("state") != "REQUESTED" or pedido.get("approval_reference") is not None:
        issues.append("ERR_PEDIDO_NAO_E_AUTORIZACAO")
    if not pedido.get("task_definition_id"):
        issues.append("ERR_PEDIDO_SEM_DEFINICAO")
    return issues


def val_evidencia(evidencia) -> list[str]:
    if not isinstance(evidencia, dict):
        return ["ERR_EVIDENCIA_AUSENTE"]
    conteudo = evidencia.get("content_text")
    if conteudo is None:
        if evidencia.get("source_status") == "VERIFIED_LOCAL_BYTES":
            return ["ERR_EVIDENCIA_SEM_BYTES"]
        return ["HASH_DECLARED_UNVERIFIED"]
    real = hashlib.sha256(conteudo.encode("utf-8")).hexdigest()
    if real != evidencia.get("sha256"):
        return ["ERR_EVIDENCIA_SHA"]
    if evidencia.get("source_status") != "VERIFIED_LOCAL_BYTES":
        return ["ERR_EVIDENCIA_STATUS"]
    return []


def val_find(find) -> list[str]:
    if not isinstance(find, dict):
        return ["ERR_FIND_AUSENTE"]
    issues = []
    if find.get("state") != "FIND_CANDIDATE":
        issues.append("ERR_FIND_FECHAMENTO_AUTOMATICO")
    if find.get("state") in {"ABERTO", "FECHADO", "CLOSED"}:
        issues.append("ERR_FIND_ESTADO_CANONICO")
    return issues


def val_reteste(reteste) -> list[str]:
    if not isinstance(reteste, dict):
        return ["ERR_RETESTE_AUSENTE"]
    if not reteste.get("implementer_id") or not reteste.get("tester_id"):
        return ["ERR_RETESTE_SEM_IDENTIDADE"]
    issues = []
    if reteste["implementer_id"] == reteste["tester_id"]:
        issues.append("ERR_RETESTE_MESMO_AGENTE")
    if reteste.get("result") not in {"PASS", "FAIL", "INCONCLUSIVE"}:
        issues.append("ERR_RETESTE_RESULTADO")
    if not reteste.get("evidence_ids"):
        issues.append("ERR_RETESTE_SEM_EVIDENCIA")
    return issues


def _hash_evento(evento) -> str:
    return _digest({chave: valor for chave, valor in evento.items() if chave != "event_hash"})


def val_ciclo(ciclo) -> list[str]:
    if not isinstance(ciclo, dict) or not isinstance(ciclo.get("events"), list):
        return ["ERR_CICLO_AUSENTE"]
    issues = []
    anterior = "0" * 64
    implementador = None
    ultimo = None
    for indice, evento in enumerate(ciclo["events"], 1):
        if evento.get("seq") != indice or evento.get("kind") not in EVENTOS:
            issues.append(f"ERR_CICLO_ORDEM:{indice}")
        if evento.get("previous_hash") != anterior or evento.get("event_hash") != _hash_evento(evento):
            issues.append(f"ERR_CICLO_HASH:{indice}")
        if not evento.get("actor_id") or not isinstance(evento.get("payload"), dict):
            issues.append(f"ERR_CICLO_CAMPOS:{indice}")
        anterior = evento.get("event_hash")
        if evento.get("kind") == "CORRECTION_RECORDED":
            implementador = evento.get("actor_id")
            ultimo = None
        if evento.get("kind") == "RETEST_RECORDED":
            if implementador is None:
                issues.append("ERR_RETESTE_ANTES_DA_CORRECAO")
            else:
                reteste = dict(evento["payload"])
                reteste.setdefault("implementer_id", implementador)
                reteste.setdefault("tester_id", evento["actor_id"])
                issues.extend(val_reteste(reteste))
                ultimo = reteste
        if evento.get("kind") == "CLOSURE_PROPOSED":
            if ultimo is None or ultimo.get("result") != "PASS":
                issues.append("ERR_FECHAMENTO_SEM_RETESTE")
            if evento.get("actor_id") == implementador:
                issues.append("ERR_FECHAMENTO_PELO_IMPLEMENTADOR")
    if ciclo.get("state") == "CLOSED":
        issues.append("ERR_CICLO_FECHADO")
    return issues


def val_crosswalk(doc) -> list[str]:
    if not isinstance(doc, dict):
        return ["ERR_CROSSWALK_AUSENTE"]
    issues = []
    if doc.get("is_official_crosswalk") is not False:
        issues.append("ERR_CROSSWALK_OFICIAL")
    for item in doc.get("items", []):
        if item.get("mapping_status") != "HYPOTHESIS_ONLY_NOT_OFFICIAL" or item.get("source_verified") is not False:
            issues.append("ERR_CROSSWALK_ITEM:" + str(item.get("source_control_id", "?")))
    return issues


def val_politica(politica) -> list[str]:
    if not isinstance(politica, dict):
        return ["ERR_POLITICA_AUSENTE"]
    issues = []
    if politica.get("effect_on_violation") != "HOLD":
        issues.append("ERR_POLITICA_ABERTA")
    if not politica.get("version"):
        issues.append("ERR_POLITICA_SEM_VERSAO")
    return issues


def val_hash_arquivo(pedido) -> list[str]:
    if not isinstance(pedido, dict) or not pedido.get("caminho") or not pedido.get("sha256"):
        return ["ERR_HASH_SEM_CONTEXTO"]
    relativo = Path(pedido["caminho"])
    if relativo.is_absolute() or ".." in relativo.parts:
        return ["ERR_HASH_CAMINHO"]
    arquivo = RAIZ / relativo
    if not arquivo.is_file():
        return ["ERR_HASH_ARQUIVO_AUSENTE"]
    if hashlib.sha256(arquivo.read_bytes()).hexdigest() != pedido["sha256"]:
        return ["ERR_HASH_DIVERGENTE"]
    return []


def val_relato_legado(relato) -> list[str]:
    if not isinstance(relato, dict):
        return ["ERR_RELATO_AUSENTE"]
    controles = {item["control_id"] for item in _ler("data/grc/controles.json")}
    issues = []
    modelos = relato.get("controls", {}).get("model_controls", [])
    if not isinstance(modelos, list):
        return ["ERR_RELATO_FORMATO"]
    for modelo in modelos:
        status = str(modelo.get("status", "")).upper()
        if modelo.get("control_id") in controles and status in {"TESTADO", "EFICAZ", "EFFECTIVE", "TESTED", "PASS", "IMPLEMENTADO"}:
            issues.append("ERR_RELATO_EFICAZ:" + modelo["control_id"])
    return issues


def val_sem_escrita_remota(efeitos) -> list[str]:
    if not isinstance(efeitos, list):
        return ["ERR_EFEITOS_AUSENTES"]
    if set(efeitos) & PRIVILEGIADOS:
        return ["ERR_ESCRITA_REMOTA"]
    return []


def val_sem_promocao(saida) -> list[str]:
    if not isinstance(saida, dict):
        return ["ERR_SAIDA_AUSENTE"]
    if saida.get("no_canonical_write") is True and saida.get("qualification") == "NOT_APPROVED" and saida.get("effectiveness") == "NOT_ASSESSED":
        return []
    return ["ERR_SAIDA_PROMOVIDA"]


def val_registro_validadores() -> list[str]:
    doc = documento()
    registro = _ler("policies/validadores.json")["validadores"]
    issues = []
    vistos = set()
    for politica in doc["politicas"] + doc["adicionais"]:
        pid = politica["policy_id"]
        if pid in vistos:
            issues.append(f"ERR_POLITICA_DUPLICADA:{pid}")
        vistos.add(pid)
        val = doc["validadores"].get(politica["validador"])
        if val is None:
            issues.append(f"ERR_VALIDADOR_AUSENTE:{pid}")
            continue
        if val["implementado"]:
            alvo = registro.get(politica["validador"])
            if alvo != val["funcao"] or _carregar(alvo) is None:
                issues.append(f"ERR_VALIDADOR_SEM_CODIGO:{politica['validador']}")
        elif politica["validador"] in registro:
            issues.append(f"ERR_VALIDADOR_IDENTIFICADO_NO_KERNEL:{politica['validador']}")
    return issues


def val_candidato_nao_executa(registro=None) -> list[str]:
    bruto = registro if registro is not None else _ler("agents/registry.json")
    issues = []
    for aid, item in bruto.get("agentes", {}).items():
        status = (item.get("recertificacao") or {}).get("status")
        if aid.startswith("AG-") and status != "candidato":
            issues.append(f"ERR_AGENTE_GRC_EXECUTA:{aid}")
        if aid.startswith("AGT-") and status != "vigente":
            issues.append(f"ERR_AGENTE_VIGENTE_AUSENTE:{aid}")
    return issues


def val_enunciado_ausente(texto=None) -> list[str]:
    if texto is None:
        texto = (RAIZ / "data" / "grc" / "agentes.json").read_text(encoding="utf-8")
        texto += (RAIZ / "data" / "grc" / "normas.json").read_text(encoding="utf-8")
    issues = []
    if "· Princípio" in texto or "· Componente" in texto:
        issues.append("ERR_ENUNCIADO_OFICIAL")
    return issues


def val_estados(doc) -> list[str]:
    if not isinstance(doc, dict):
        return ["ERR_ESTADO_AUSENTE"]
    issues = []
    if doc.get("find_state") == "FIND_CANDIDATE" and doc.get("canonico") in {"ABERTO", "FECHADO"}:
        issues.append("ERR_FIND_CANDIDATO_COMO_CANONICO")
    if doc.get("cycle_state") == "CLOSURE_CANDIDATE" and doc.get("canonico") == "FECHADO":
        issues.append("ERR_CICLO_CANDIDATO_COMO_FECHADO")
    if doc.get("find_state") not in {None, "FIND_CANDIDATE"}:
        issues.append("ERR_FIND_ESTADO")
    return issues


def _carregar(caminho: str):
    modulo, _, nome = caminho.rpartition(".")
    try:
        return getattr(importlib.import_module(modulo), nome)
    except (ImportError, AttributeError):
        return None


def _contexto(contexto, chave, leitor):
    if contexto is not None and chave in contexto:
        return contexto[chave]
    return leitor()


def avaliar(policy_id: str, contexto: dict | None = None) -> dict:
    doc = documento()
    politicas = {item["policy_id"]: item for item in doc["politicas"] + doc["adicionais"]}
    politica = politicas.get(policy_id)
    if politica is None:
        issues = ["ERR_POLITICA_DESCONHECIDA"]
    elif politica["enforcement"] == "EXTERNAL_HOLD" or not doc["validadores"][politica["validador"]]["implementado"]:
        issues = ["EXTERNAL_HOLD"]
    else:
        issues = _aplicar(politica["rule_key"], contexto)
    return {
        "policy_id": policy_id,
        "result": "HOLD" if issues else "PASS_LOCAL",
        "reason": "; ".join(issues) if issues else "LOCAL_CHECK_PASSED_NOT_AUTHORIZATION",
        "authorization": False,
    }


def _aplicar(regra: str, contexto: dict | None) -> list[str]:
    ctx = contexto or {}
    if regra == "agent_no_authority":
        return val_agentes(_contexto(contexto, "agentes", lambda: _ler("data/grc/agentes.json")))
    if regra == "task_wo_separation":
        return val_pedido_wo(ctx.get("pedido")) + val_definicao_tarefa(ctx.get("definicao"))
    if regra == "find_not_closed":
        return val_find(ctx.get("find"))
    if regra == "cycle_independent_retest":
        return val_ciclo(ctx.get("ciclo"))
    if regra == "models_are_not_effective":
        return val_controle(_contexto(contexto, "controles", lambda: _ler("data/grc/controles.json")))
    if regra == "version_hash":
        return val_hash_arquivo(ctx.get("hash"))
    if regra == "no_remote_writes":
        return val_sem_escrita_remota(ctx.get("efeitos"))
    if regra == "evidence_truth":
        return val_evidencia(ctx.get("evidencia"))
    if regra == "validator_registry":
        return val_registro_validadores()
    if regra == "separation_of_duties":
        return val_reteste(ctx.get("reteste"))
    if regra == "no_promotion":
        return val_sem_promocao(ctx.get("saida"))
    if regra == "append_only":
        return val_ciclo(ctx.get("ciclo"))
    if regra == "crosswalk_hypothesis":
        return val_crosswalk(ctx.get("crosswalk"))
    if regra == "legacy_not_effective":
        return val_relato_legado(ctx.get("relato"))
    if regra == "candidate_cannot_execute":
        return val_candidato_nao_executa(ctx.get("registro"))
    if regra == "official_text_absent":
        return val_enunciado_ausente(ctx.get("texto"))
    if regra == "state_names_distinct":
        return val_estados(ctx.get("estados"))
    return ["ERR_REGRA_SEM_CODIGO:" + regra]
