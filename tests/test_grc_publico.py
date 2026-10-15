"""Recorte público do pacote GRC: controles permanecem; a norma fica em metadados."""
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GRC = REPO / "data" / "grc"
CODIGO = re.compile(r"^(EDM|APO|BAI|DSS|MEA)\d{2}$")


def _json(nome):
    return json.loads((GRC / nome).read_text(encoding="utf-8"))


def test_recorte_tem_so_os_tres_arquivos():
    assert sorted(p.name for p in GRC.iterdir()) == ["controles.json", "normas.json", "origem.json"]


def test_controles_conservam_o_modelo_e_omitem_o_enunciado_da_norma():
    controles = _json("controles.json")
    assert len(controles) == 105
    coso = [c for c in controles if c["origin"] == "USER_SUPPLIED_COSO_CONTROL_TEMPLATE"]
    cko = [c for c in controles if c["origin"] == "NEW_INTERNAL_CONTROL_PROPOSAL"]
    assert len(coso) == 75
    assert len(cko) == 30
    for item in coso:
        assert "test_design_template" not in item
        assert item["norma"]["nivel"] == "METADADOS"
        assert set(item["norma"]) == {"framework", "codigo", "checkpoints", "nivel"}
        assert item["norma"]["framework"] in {"COSO_ICIF2013", "COSO_ERM2017"}
        assert item["template_status"] == "MODEL_DRAFT_NOT_IMPLEMENTED"
        assert item["implementation_status"] == "NOT_VERIFIED"
        assert item["effectiveness_status"] == "NOT_ASSESSED"
        assert item["evaluation_status"] == "NOT_TESTED"
    for item in cko:
        assert item["norma"]["framework"] == "CKO_ORIGINAL_CONTROL"
        assert item["test_design_template"].startswith("Inspecionar definição formal")
    texto = json.dumps(controles, ensure_ascii=False)
    assert "endereça:" not in texto


def test_norma_publica_so_tem_metadados():
    doc = _json("normas.json")
    assert doc["versao"] == "0.2.0"
    por_id = {item["id"]: item for item in doc["itens"]}
    assert set(por_id) == {
        "COSO_ICIF2013",
        "COSO_ERM2017",
        "IT_GOVERNANCE_PUBLIC_COBIT_IDS",
    }
    assert por_id["COSO_ICIF2013"]["principios"] == 17
    assert por_id["COSO_ICIF2013"]["controles"] == 35
    assert por_id["COSO_ERM2017"]["principios"] == 20
    assert por_id["COSO_ERM2017"]["controles"] == 40
    objetivos = por_id["IT_GOVERNANCE_PUBLIC_COBIT_IDS"]["objetivos"]
    assert len(objetivos) == 40
    assert all(CODIGO.fullmatch(codigo) for codigo in objetivos)
    assert por_id["IT_GOVERNANCE_PUBLIC_COBIT_IDS"]["controles"] == 0
    texto = json.dumps(doc, ensure_ascii=False)
    assert "description" not in texto
    assert "practice" not in texto


def test_origem_aponta_para_o_zip_e_deixa_o_drive_no_lugar():
    origem = _json("origem.json")
    assert origem["estado"] == "CANDIDATE_NOT_HOMOLOGATED"
    assert origem["controles"] == 105
    assert origem["fonte"]["sha256"] == "f6bb4f7ae382e260233846571427abf69d0ccda8ac278b4ba64fc83dd2babb65"
    assert origem["fonte"]["bytes"] == 289541
    assert origem["fonte"]["id_origem"] == "1wBohCXFLZbRIk9mhMBCMWFQq50Q1NWLv"
