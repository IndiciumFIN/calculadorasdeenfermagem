"""Revisão regulatória. PASS_LOCAL não homologa e não publica."""
import json
from urllib.parse import urlparse

from packages.cli.pep import RAIZ
from packages.cli.sources import dominio_oficial
from packages.schemas.invariantes import CONDICAO_DETERMINADA

ARQUIVO = RAIZ / "policies" / "regulatorio.json"
RESUMO = RAIZ / "data" / "legado" / "resumo.json"
PARECER_PILOTO = RAIZ / "data" / "legado" / "piloto" / "auditoria_res800_manifest.json"


def documento() -> dict:
    return json.loads(ARQUIVO.read_text(encoding="utf-8"))


def _ler(caminho) -> dict:
    return json.loads(caminho.read_text(encoding="utf-8"))


def _planilha(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return host == "docs.google.com" or host.endswith(".docs.google.com") or host == "drive.google.com" or host.endswith(".drive.google.com")


def val_corpus(resumo=None) -> list[str]:
    doc = resumo if resumo is not None else _ler(RESUMO)
    if not isinstance(doc, dict):
        return ["ERR_CORPUS_AUSENTE"]
    issues = []
    if doc.get("status_distintos") != ["Não verificado"]:
        issues.append("ERR_CORPUS_STATUS")
    if doc.get("candidatos", 0) < 1:
        issues.append("ERR_CORPUS_VAZIO")
    for nome, fonte in doc.get("fontes", {}).items():
        link = str(fonte.get("link_fonte") or "")
        if not _planilha(link) or dominio_oficial(link):
            issues.append(f"ERR_CORPUS_LINK:{nome}")
    return issues


def val_fonte_oficial(atomo) -> list[str]:
    if not isinstance(atomo, dict):
        return ["ERR_ATOMO_AUSENTE"]
    link = str(atomo.get("link_fonte") or "")
    issues = []
    if atomo.get("fonte_oficial") not in (None, False, "AUSENTE") and _planilha(link):
        issues.append("ERR_PLANILHA_COMO_FONTE_OFICIAL")
    if atomo.get("status") in CONDICAO_DETERMINADA:
        if not atomo.get("data_verificacao"):
            issues.append("ERR_SEM_DATA_VERIFICACAO")
        if _planilha(link) or not dominio_oficial(link):
            issues.append("ERR_FONTE_NAO_OFICIAL")
    return issues


def val_parecer_llm(manifest=None) -> list[str]:
    doc = manifest if manifest is not None else _ler(PARECER_PILOTO)
    if not isinstance(doc, dict):
        return ["ERR_PARECER_AUSENTE"]
    issues = []
    if doc.get("homologacao_juridica") is not False:
        issues.append("ERR_PARECER_HOMOLOGA")
    if doc.get("estagio") != "raw":
        issues.append("ERR_PARECER_FORA_DO_RAW")
    if doc.get("efeito") not in (None, "CANDIDATE_ONLY"):
        issues.append("ERR_PARECER_EFEITO")
    if doc.get("promotable") is True and doc.get("homologacao_juridica") is not False:
        issues.append("ERR_PROMOVEL_COMO_HOMOLOGACAO")
    return issues


def val_publicacao(registro=None) -> list[str]:
    doc = registro if isinstance(registro, dict) else {
        "autorizacao_publicacao": "NAO_AUTORIZADA",
        "publica_por_status": False,
    }
    issues = []
    if doc.get("publica_por_status") is True:
        issues.append("ERR_PUBLICACAO_POR_STATUS")
    if doc.get("autorizacao_publicacao") == "AUTORIZADA" and doc.get("fonte_oficial") != "PRESENTE":
        issues.append("ERR_PUBLICACAO_SEM_FONTE")
    if doc.get("status") in CONDICAO_DETERMINADA and doc.get("autorizacao_publicacao") not in {
        "AUTORIZADA",
        "NAO_AUTORIZADA",
    }:
        issues.append("ERR_PUBLICACAO_AUSENTE")
    return issues


def val_sem_truncamento(par) -> list[str]:
    if not isinstance(par, dict):
        return ["ERR_TEXTO_AUSENTE"]
    origem = par.get("linha")
    texto = par.get("texto_regra")
    if not isinstance(origem, str) or not isinstance(texto, str) or texto != origem:
        return ["ERR_TEXTO_TRUNCADO"]
    return []


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
    regra = politica["rule_key"]
    if regra == "corpus_permanece_candidato":
        issues = val_corpus(ctx.get("resumo"))
    elif regra == "condicao_exige_fonte_oficial":
        issues = val_fonte_oficial(ctx.get("atomo")) if "atomo" in ctx else ["ERR_ATOMO_AUSENTE"]
    elif regra == "parecer_nao_homologa":
        issues = val_parecer_llm(ctx.get("manifest"))
    elif regra == "publicacao_nao_e_status":
        issues = val_publicacao(ctx.get("registro"))
    elif regra == "texto_integral":
        issues = val_sem_truncamento(ctx.get("par")) if "par" in ctx else ["ERR_TEXTO_AUSENTE"]
    else:
        issues = ["ERR_REGRA_DESCONHECIDA"]
    return {
        "policy_id": policy_id,
        "result": "HOLD" if issues else "PASS_LOCAL",
        "reason": "; ".join(issues) if issues else "LOCAL_CHECK_PASSED_NOT_AUTHORIZATION",
        "authorization": False,
    }
