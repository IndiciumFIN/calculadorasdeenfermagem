"""O pacote zero-trust recebe determinação total e permanece sem autorização."""
import hashlib
import json

from packages.cli.pep import RAIZ, VALIDADORES_POR_PROCEDIMENTO
from packages.cli.zero_trust import ZIP_BYTES, ZIP_REL, ZIP_SHA, avaliar, determinar

POLITICA = json.loads((RAIZ / "policies" / "zero_trust.json").read_text(encoding="utf-8"))
REGISTRO = json.loads((RAIZ / "agents" / "registry.json").read_text(encoding="utf-8"))["agentes"]
DETERMINACAO = json.loads((RAIZ / "data" / "zero_trust" / "determinacao.json").read_text(encoding="utf-8"))
ORIGEM = json.loads((RAIZ / "data" / "zero_trust" / "origem.json").read_text(encoding="utf-8"))


def test_politicas_zero_trust_nao_entram_na_tarefa_qualificada():
    assert [item["policy_id"] for item in POLITICA["politicas"]] == [f"POL-ZT-{n:03d}" for n in range(1, 6)]
    assert all(item["authorization"] is False for item in POLITICA["politicas"])
    assert all(item["status"] == "CANDIDATE_NOT_HOMOLOGATED" for item in POLITICA["politicas"])
    definicoes = (RAIZ / "policies" / "definicoes_tarefa.json").read_text(encoding="utf-8")
    assert "POL-ZT-" not in definicoes
    assert "VAL-ZT-" not in definicoes
    usados = {ident for ids in VALIDADORES_POR_PROCEDIMENTO.values() for ident in ids}
    assert not any(ident.startswith("VAL-ZT-") or ident.startswith("V-") for ident in usados)
    kernel = json.loads((RAIZ / "policies" / "validadores.json").read_text(encoding="utf-8"))
    assert kernel["versao"] == "1.3.0"
    for numero in range(1, 6):
        assert kernel["validadores"][f"VAL-ZT-{numero:03d}"] == POLITICA["validadores"][f"VAL-ZT-{numero:03d}"]["funcao"]


def test_determinacao_total_nao_autoriza_e_repete_o_arquivo():
    fresco = determinar()
    assert fresco["cobertura"] == "TOTAL"
    assert fresco["indeterminados"] == 0
    assert fresco["autorizacao"] is False
    assert fresco["homologacao_juridica"] is False
    assert fresco["efeito"] == "DETERMINACAO"
    assert all(item["autorizacao"] is False for item in fresco["itens"])
    assert [(item["id"], item["determinacao"]) for item in DETERMINACAO["itens"]] == [
        (item["id"], item["determinacao"]) for item in fresco["itens"]
    ]
    assert "DIVERGENTE" not in fresco["contagens"]
    for numero in range(1, 6):
        decisao = avaliar(f"POL-ZT-{numero:03d}")
        assert decisao["result"] == "PASS_LOCAL"
        assert decisao["authorization"] is False


def test_pass_local_nao_autoriza_quando_a_determinacao_e_trocada():
    vazia = {
        "sha256": ZIP_SHA,
        "bytes": ZIP_BYTES,
        "status_pacote": "CANDIDATE_NOT_HOMOLOGATED",
        "autorizacao": True,
        "homologacao_juridica": False,
        "efeito": "DETERMINACAO",
        "cobertura": "TOTAL",
        "indeterminados": 0,
        "itens": [],
    }
    decisao = avaliar("POL-ZT-005", {"determinacao": vazia})
    assert decisao["result"] == "HOLD"
    assert decisao["authorization"] is False
    assert avaliar("POL-ZT-999")["reason"] == "ERR_POLITICA_DESCONHECIDA"


def test_agentes_vigentes_permanecem_e_os_dezoito_continuam_fora():
    vigentes = sorted(ident for ident, item in REGISTRO.items() if item["recertificacao"]["status"] == "vigente")
    assert vigentes == ["AGT-AUDITOR-001", "AGT-EXTRATOR-001"]
    identidades = [item for item in DETERMINACAO["itens"] if item["classe"] == "IDENTIDADE"]
    assert len(identidades) == 128
    assert sum(item["determinacao"] == "SEM_PROMOCAO" for item in identidades) == 108
    assert sum(item["determinacao"] == "PRESERVADO_VIGENTE" for item in identidades) == 2
    ausentes = [item["id"] for item in identidades if item["determinacao"] == "NAO_IMPLANTAR"]
    assert len(ausentes) == 18
    assert all(ident not in REGISTRO for ident in ausentes)
    assert "AGT-ORCH-001" in ausentes


def test_zip_conferido_nao_vira_kernel_nem_migration():
    caminho = RAIZ / ZIP_REL
    bruto = caminho.read_bytes()
    assert len(bruto) == ZIP_BYTES == ORIGEM["bytes"]
    assert hashlib.sha256(bruto).hexdigest() == ZIP_SHA == ORIGEM["sha256"]
    assert ORIGEM["acesso"] == "somente_dono"
    assert ORIGEM["metodo"] == "conector_autenticado"
    assert ORIGEM["drive_id"] == "1mL-ILSBH9NlPyQXp2Bg7d2yZ5hpW6O3z"
    assert not (RAIZ / "packages" / "cli" / "cko_guard").exists()
    assert "AG-KER-" not in (RAIZ / "data" / "finds" / "registro.json").read_text(encoding="utf-8")
    migrations = "\n".join(path.read_text(encoding="utf-8") for path in (RAIZ / "supabase" / "migrations").glob("*.sql"))
    assert "DO NOT EXECUTE WITHOUT DBA" not in migrations
    gateway = (RAIZ / "supabase" / "functions" / "cko-deepseek-gateway" / "index.ts").read_text(encoding="utf-8")
    assert "admitLLMInvocation" not in gateway
    qualificadas = [
        item["id"]
        for item in DETERMINACAO["itens"]
        if item["classe"] == "TAREFA" and item["determinacao"] == "NAO_REVOGA"
    ]
    assert len(qualificadas) == 9
