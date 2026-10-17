#!/usr/bin/env python3
"""
atomizar.py - transforma a biblioteca /workspace/doencas em "átomos" JSONL determinísticos.

Uso:  python3 atomizar.py [--entrada /workspace/doencas] [--saida /workspace/doencas_atomizado] [tema ...]
Fase 1 (temas únicos): cid10 icd11 medlineplus dispositivos medicamentos nutricao suprimentos epidemiologico

Regras (ver MANIFESTO.json de cada tema e README_ATOMIZADO.md):
- 1 átomo por entidade; chaves fixas em pt-BR:
  atom_id, tema, tipo_entidade, codigo, titulo, sinonimos, descricao_literal, fonte_nome, fonte_url,
  fonte_versao, data_extracao, referencias_cruzadas{cid10,cid11,mesh,medlineplus}, sha256
- atom_id = "<tema>:<codigo>"; "codigo" é a chave local (com prefixo de subfonte quando o tema tem mais de uma).
- descricao_literal = renderização literal ("campo: valor", uma linha por campo, na ordem da fonte; campos vazios
  omitidos; listas unidas por "; ") de TODOS os registros de origem da entidade. Nada é resumido nem reescrito.
  Entidades com vários registros de origem: blocos separados por linha em branco, ordenados pelo JSON canônico.
  Tabelas-filhas (nutrientes USDA, ácidos graxos/aminoácidos TACO): cabeçalho "## <arquivo>" e uma linha por registro
  no formato "campo: valor | campo: valor".
- referencias_cruzadas: sempre com as 4 chaves (listas possivelmente vazias); só preenchidas por regra determinística
  a partir dos próprios dados (ex.: campo mesh do MedlinePlus; códigos CID-10 em SIM/SINAN conferidos contra a
  tabela CID-10 da biblioteca). Nada é inferido.
- sha256 = SHA-256 do JSON canônico do átomo sem o campo sha256.
- Saída: JSON canônico (sort_keys, ensure_ascii=False, separators=(',',':')), UTF-8, LF, linhas ordenadas por atom_id,
  um arquivo por tipo_entidade, dividido em partes <= 90.000.000 bytes quando necessário.
"""
import csv, hashlib, json, sys, collections
from pathlib import Path

VERSAO_GERADOR = "atomizar.py 1.0.0"
MAX_BYTES = 90_000_000   # bytes; margem abaixo do limite de 100 MB de upload
DATA = "2026-10-10"   # data de extração de todas as fontes da biblioteca (download feito em 10/10/2026)
MS_API = "https://apidadosabertos.saude.gov.br"

FONTES = {
    "cid10": dict(nome="DATASUS - CID-10 em português (CID10CSV.zip, cópia do Internet Archive)",
                  url="http://www2.datasus.gov.br/cid10/V2008/downloads/CID10CSV.zip", versao="CID-10 DATASUS V2008"),
    "icd11": dict(nome="OMS - CID-11 MMS Simple Tabulation (pt)",
                  url="https://icdcdn.who.int/static/releasefiles/2026-01/SimpleTabulation-ICD-11-MMS-pt.zip", versao="ICD-11 MMS release 2026-01"),
    "medlineplus": dict(nome="NLM/NIH - MedlinePlus Health Topics XML",
                        url="https://medlineplus.gov/xml/mplus_topics_2026-10-10.xml", versao="mplus_topics_2026-10-10.xml"),
    "anvisa_dispositivos": dict(nome="Anvisa - Produtos para saúde registrados (TA_PRODUTO_SAUDE_SITE.csv)",
                                url="https://dados.anvisa.gov.br/dados/TA_PRODUTO_SAUDE_SITE.csv", versao="arquivo baixado em 2026-10-10 (sem número de versão na fonte)"),
    "fda_dispositivos": dict(nome="FDA/openFDA - Device classification",
                             url="https://download.open.fda.gov/device/classification/device-classification-0001-of-0001.json.zip", versao="openFDA last_updated 2026-10-05"),
    "anvisa_medicamentos": dict(nome="Anvisa - Medicamentos registrados (DADOS_ABERTOS_MEDICAMENTOS.csv)",
                                url="https://dados.anvisa.gov.br/dados/DADOS_ABERTOS_MEDICAMENTOS.csv", versao="arquivo baixado em 2026-10-10 (sem número de versão na fonte)"),
    "cmed": dict(nome="Anvisa/CMED - Lista de preços de medicamentos (TA_PRECO_MEDICAMENTO.csv)",
                 url="https://dados.anvisa.gov.br/dados/TA_PRECO_MEDICAMENTO.csv", versao="arquivo baixado em 2026-10-10 (sem número de versão na fonte)"),
    "fda_ndc": dict(nome="FDA/openFDA - NDC Directory (produtos)",
                    url="https://download.open.fda.gov/drug/ndc/drug-ndc-0001-of-0001.json.zip", versao="openFDA last_updated 2026-10-09"),
    "fda_shortages": dict(nome="FDA/openFDA - Drug shortages",
                          url="https://download.open.fda.gov/drug/shortages/drug-shortages-0001-of-0001.json.zip", versao="openFDA last_updated 2026-10-09"),
    "taco": dict(nome="TACO 4ª ed. (NEPA/UNICAMP), CSV processado por github.com/brolesi/taco",
                 url="https://raw.githubusercontent.com/brolesi/taco/main/data/processed/taco/taco_composicao.csv", versao="TACO 4ª edição (repositório brolesi/taco, branch main)"),
    "pof": dict(nome="IBGE POF - Medidas caseiras (CSV processado por github.com/brolesi/taco)",
                url="https://raw.githubusercontent.com/brolesi/taco/main/data/processed/pof/pof_medidas_caseiras.csv", versao="POF/IBGE (repositório brolesi/taco, branch main)"),
    "usda_sr": dict(nome="USDA FoodData Central - SR Legacy",
                    url="https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_sr_legacy_food_csv_2018-04.zip", versao="SR Legacy 2018-04"),
    "usda_foundation": dict(nome="USDA FoodData Central - Foundation Foods",
                            url="https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_foundation_food_csv_2026-04-30.zip", versao="Foundation Foods 2026-04-30"),
    "catmat": dict(nome="Compras.gov.br - CATMAT (API dados abertos, módulo material), classes 6510/6515/6530/6532",
                   url="https://dadosabertos.compras.gov.br/modulo-material/4_consultarItemMaterial", versao="consulta à API em 2026-10-10"),
    "notificacao": dict(nome="Ministério da Saúde - Portaria GM/MS nº 11.211/2026, Anexo I (lista nacional de notificação compulsória)",
                        url="https://bvsms.saude.gov.br/bvs/saudelegis/gm/2026/prt11211_14_05_2026.html", versao="Portaria GM/MS nº 11.211, de 13/05/2026"),
}
EPI = [  # arquivo, prefixo, tipo_entidade, rótulo, endpoint, campo-id (None = hash do conteúdo), campo CID-10
    ("sinan_dengue_2026_amostra", "sinan-dengue", "notificacao_sinan_dengue", "Notificação SINAN dengue 2026", "arboviroses/dengue?nu_ano=2026", None, "id_agravo"),
    ("sinan_chikungunya_2026_amostra", "sinan-chikungunya", "notificacao_sinan_chikungunya", "Notificação SINAN chikungunya 2026", "arboviroses/chikungunya?nu_ano=2026", None, "id_agravo"),
    ("sinan_zika_2026_amostra", "sinan-zika", "notificacao_sinan_zika", "Notificação SINAN zika 2026", "arboviroses/zikavirus?nu_ano=2026", None, "id_agravo"),
    ("sim_mortalidade_amostra", "sim", "obito_sim", "Declaração de óbito SIM", "vigilancia-e-meio-ambiente/sistema-de-informacao-sobre-mortalidade", "contador", "causabas"),
    ("srag_2019_2026_amostra", "srag", "notificacao_srag", "Notificação SRAG", "vigilancia-e-meio-ambiente/srag-2019-2026", "nu_notific", None),
    ("mpox_amostra", "mpox", "notificacao_mpox", "Notificação mpox", "vigilancia-e-meio-ambiente/mpox", None, None),
    ("febre_amarela_epizootias", "febre-amarela-epizootia", "epizootia_febre_amarela", "Epizootia de febre amarela", "arboviroses/febre-amarela-epzootias", None, None),
    ("febre_amarela_humanos_primatas", "febre-amarela-humano-primata", "caso_febre_amarela_humano_primata", "Registro de febre amarela (humanos/primatas não humanos)", "arboviroses/febre-amarela-humanos-primatas-nao-humanos", None, None),
]

def canon(o):
    return json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"))

def sha(b):
    return hashlib.sha256(b).hexdigest()

def val(v):
    if v is None: return ""
    if isinstance(v, str): return v
    if isinstance(v, list): return "; ".join(val(x) for x in v if val(x) != "")
    if isinstance(v, bool): return "true" if v else "false"
    return json.dumps(v, ensure_ascii=False)

def render(rec):
    return "\n".join(f"{k}: {val(v)}" for k, v in rec.items() if val(v) != "")

def render_line(rec):
    return " | ".join(f"{k}: {val(v)}" for k, v in rec.items() if val(v) != "")

def render_many(recs):
    uniq = sorted({canon(r): r for r in recs}.items())
    return "\n\n".join(render(r) for _, r in uniq), [r for _, r in uniq]

def refs(cid10=(), cid11=(), mesh=(), medlineplus=()):
    s = lambda x: sorted(set(x))
    return {"cid10": s(cid10), "cid11": s(cid11), "mesh": s(mesh), "medlineplus": s(medlineplus)}

def atom(tema, tipo, codigo, titulo, sinonimos, descricao, fonte, url=None, ref=None):
    f = FONTES[fonte]
    sin = []
    for x in sinonimos:
        x = (x or "").strip()
        if x and x != titulo and x not in sin: sin.append(x)
    a = {"atom_id": f"{tema}:{codigo}", "tema": tema, "tipo_entidade": tipo, "codigo": codigo,
         "titulo": titulo or "", "sinonimos": sorted(sin), "descricao_literal": descricao,
         "fonte_nome": f["nome"], "fonte_url": url or f["url"], "fonte_versao": f["versao"],
         "data_extracao": DATA, "referencias_cruzadas": ref or refs()}
    a["sha256"] = sha(canon(a).encode("utf-8"))
    return a

class Ctx:
    def __init__(self, base):
        self.base = base; self.entradas = []; self.conferencia = []
    def load(self, rel):
        p = self.base / rel
        d = json.loads(p.read_text(encoding="utf-8"))
        c = p.with_suffix(".csv")
        with open(c, encoding="utf-8", newline="") as fh:
            ncsv = sum(1 for _ in csv.reader(fh)) - 1
        self.entradas.append({"arquivo": rel, "registros_json": len(d), "linhas_csv": ncsv,
                              "sha256_json": sha(p.read_bytes()), "sha256_csv": sha(c.read_bytes())})
        return d
    def conf(self, rel, linhas, atomos, explicacao=""):
        self.conferencia.append({"arquivo_entrada": rel, "linhas_csv": linhas, "atomos": atomos,
                                 "confere": linhas == atomos, "explicacao": explicacao})

# ---------------------------------------------------------------- CID-10 helpers (referências cruzadas)
_CID = None
def cid10_index(base):
    global _CID
    if _CID is None:
        sub = json.loads((base / "cid10/subcategorias.json").read_text(encoding="utf-8"))
        cat = json.loads((base / "cid10/categorias.json").read_text(encoding="utf-8"))
        _CID = ({r["codigo_sem_ponto"]: r["codigo"] for r in sub}, {r["codigo"] for r in cat})
    return _CID

def cid10_norm(base, code):
    """Converte 'A920', 'A92.0', 'A90' no código CID-10 da biblioteca. Retorna [] se não existir (não chuta)."""
    if not code: return []
    sub, cat = cid10_index(base)
    c = str(code).upper().replace(".", "").strip()
    if len(c) == 4 and c in sub: return [sub[c]]
    if len(c) == 3 and c in cat: return [c]
    return []

# ---------------------------------------------------------------- temas
def t_cid10(cx):
    T, out = "cid10", []
    d = cx.load("cid10/capitulos.json")
    for r in d:
        out.append(atom(T, "capitulo", f"cap:{int(r['numero']):02d}", r["descricao"], [r["descricao_abrev"]], render(r), "cid10"))
    cx.conf("cid10/capitulos.csv", len(d), len(d))
    d = cx.load("cid10/grupos.json")
    for r in d:
        out.append(atom(T, "grupo", f"grupo:{r['cat_inicio']}-{r['cat_fim']}", r["descricao"], [r["descricao_abrev"]], render(r), "cid10"))
    cx.conf("cid10/grupos.csv", len(d), len(d))
    cats = cx.load("cid10/categorias.json")
    subs = cx.load("cid10/subcategorias.json")
    catset = {r["codigo"] for r in cats}
    sub3 = {r["codigo"]: r for r in subs if r["codigo"] in catset}
    for r in cats:
        desc, sins = render(r), [r["descricao_abrev"]]
        if r["codigo"] in sub3:
            s3 = sub3[r["codigo"]]
            desc += "\n\n## subcategorias\n" + render(s3); sins += [s3["descricao"], s3["descricao_abrev"]]
        out.append(atom(T, "categoria", r["codigo"], r["descricao"], sins, desc, "cid10"))
    cx.conf("cid10/categorias.csv", len(cats), len(cats))
    n = 0
    for r in subs:
        if r["codigo"] in sub3: continue
        out.append(atom(T, "subcategoria", r["codigo"], r["descricao"], [r["descricao_abrev"]], render(r), "cid10")); n += 1
    cx.conf("cid10/subcategorias.csv", len(subs), n,
            f"{len(sub3)} linhas do arquivo de subcategorias do DATASUS são categorias sem subdivisão (código de 3 caracteres, ex.: A09), idênticas à categoria; "
            "foram anexadas ao átomo 'categoria' correspondente (seção '## subcategorias' em descricao_literal) em vez de gerar átomo duplicado.")
    d = cx.load("cid10/cid_o_categorias.json")
    for r in d:
        out.append(atom(T, "cido_categoria", f"cido:{r['cat']}", r["descricao"], [], render(r), "cid10"))
    cx.conf("cid10/cid_o_categorias.csv", len(d), len(d))
    d = cx.load("cid10/cid_o_grupos.json")
    g = collections.OrderedDict()
    for r in d: g.setdefault(f"{r['catinic']}-{r['catfim']}", []).append(r)
    for k, rs in g.items():
        desc, _ = render_many(rs)
        out.append(atom(T, "cido_grupo", f"cidogrupo:{k}", rs[0]["descricao"], [x["descricao"] for x in rs[1:]], desc, "cid10"))
    cx.conf("cid10/cid_o_grupos.csv", len(d), len(g),
            "Na fonte, as faixas M959-M959 e M980-M980 aparecem duas vezes cada, com descrições diferentes; cada faixa virou 1 átomo (título = 1ª descrição na ordem da fonte, a outra em sinonimos, os dois registros em descricao_literal).")
    return out

def t_icd11(cx):
    T, out = "icd11", []
    d = cx.load("icd11/cid11_mms_completa.json")
    for r in d:
        ent = r["uri_linearizacao"].rsplit("/", 1)[-1]
        if r["tipo"] == "chapter": tipo, cod = "capitulo", f"cap:{r['capitulo']}"
        elif r["tipo"] == "block": tipo, cod = "bloco", f"bloco:{ent}"
        else: tipo, cod = "categoria", r["codigo"]
        tit = r["titulo_pt"] or r["titulo_en"]
        out.append(atom(T, tipo, cod, tit, [r["titulo_en"]], render(r), "icd11", url=r["link_navegador"]))
    cx.conf("icd11/cid11_mms_completa.csv", len(d), len(d))
    sub = cx.load("icd11/cid11_mms_categorias_com_codigo.json")
    codes = {r["codigo"] for r in d if r["codigo"]}
    assert all(r["codigo"] in codes for r in sub)
    cx.conf("icd11/cid11_mms_categorias_com_codigo.csv", len(sub), 0,
            f"Subconjunto de cid11_mms_completa (as {len(sub)} linhas com código); todas já estão nos átomos tipo 'categoria'. Não gera átomos novos para não duplicar.")
    return out

def t_medlineplus(cx):
    T, out = "medlineplus", []
    rows = []
    for lang in ("en", "es"):
        d = cx.load(f"medlineplus/health_topics_{lang}.json")
        rows += [(lang, r) for r in d]
        cx.conf(f"medlineplus/health_topics_{lang}.csv", len(d), len(d))
    by_url = {r["url"]: f"{T}:{lang}:{r['id']}" for lang, r in rows}
    for lang, r in rows:
        mesh = [m.split(":", 1)[0] for m in r["mesh"] if m]
        cp = [by_url[r["topico_outro_idioma_url"]]] if r["topico_outro_idioma_url"] in by_url else []
        out.append(atom(T, f"topico_saude_{lang}", f"{lang}:{r['id']}", r["titulo"],
                        list(r["tambem_chamado"]) + list(r["ver_tambem_termos"]), render(r), "medlineplus",
                        url=r["url"], ref=refs(mesh=mesh, medlineplus=cp)))
    t = cx.load("medlineplus/health_topics_todos.json")
    cx.conf("medlineplus/health_topics_todos.csv", len(t), 0,
            f"União de health_topics_en + health_topics_es ({len(t)} = soma dos dois); não gera átomos novos para não duplicar.")
    return out

def _anvisa_disp(T, rows, fonte, tipo, prefixo):
    g = collections.OrderedDict()
    for r in rows: g.setdefault(r["numero_registro_cadastro"], []).append(r)
    out = []
    for k, rs in g.items():
        desc, srt = render_many(rs)
        out.append(atom(T, tipo, f"{prefixo}:{k}", srt[0]["nome_comercial"], [], desc, fonte))
    return out

def t_dispositivos(cx):
    T = "dispositivos"
    d = cx.load("dispositivos/anvisa_produtos_saude_registrados.json")
    out = _anvisa_disp(T, d, "anvisa_dispositivos", "registro_anvisa_produto_saude", "anvisa")
    cx.conf("dispositivos/anvisa_produtos_saude_registrados.csv", len(d), len(out),
            "Entidade = número de registro/cadastro Anvisa. A fonte repete o registro numa linha por fabricante/país de fabricação; essas linhas foram agrupadas num átomo (todas as linhas literais em descricao_literal).")
    f = cx.load("dispositivos/fda_classificacao_dispositivos.json")
    for r in f:
        out.append(atom(T, "classificacao_fda_dispositivo", f"fda:{r['product_code']}", r["device_name"], [], render(r), "fda_dispositivos"))
    cx.conf("dispositivos/fda_classificacao_dispositivos.csv", len(f), len(f))
    return out

def t_medicamentos(cx):
    T, out = "medicamentos", []
    d = cx.load("medicamentos/anvisa_medicamentos_registrados.json")
    g = collections.OrderedDict(); sem = collections.OrderedDict()
    for r in d:
        if r["numero_registro_produto"]: g.setdefault(r["numero_registro_produto"], []).append(r)
        else: sem.setdefault(sha(canon(r).encode())[:16], r)
    for k, rs in g.items():
        desc, srt = render_many(rs)
        out.append(atom(T, "registro_anvisa_medicamento", f"anvisa:{k}", srt[0]["nome_produto"], [], desc, "anvisa_medicamentos"))
    for h, r in sem.items():
        out.append(atom(T, "produto_anvisa_sem_numero_registro", f"anvisa-sem-registro:{h}", r["nome_produto"], [], render(r), "anvisa_medicamentos"))
    cx.conf("medicamentos/anvisa_medicamentos_registrados.csv", len(d), len(g) + len(sem),
            f"Entidade = número de registro do produto ({len(g)} registros). O arquivo da Anvisa repete a mesma linha muitas vezes (só {len({canon(r) for r in d})} linhas distintas em {len(d)}); "
            f"linhas idênticas viram 1 átomo, e as variantes de um mesmo registro (situação Ativo/Inativo) ficam todas em descricao_literal. "
            f"{sum(1 for r in d if not r['numero_registro_produto'])} linhas sem número de registro (notificados de baixo risco, dinamizados etc.) viraram {len(sem)} átomos distintos, com código = 16 primeiros hex do SHA-256 do registro canônico.")
    c = cx.load("medicamentos/anvisa_cmed_precos_medicamentos.json")
    for r in c:
        tit = " - ".join(x for x in (r["produto"], r["apresentação"]) if x)
        out.append(atom(T, "apresentacao_cmed", f"cmed:{r['código ggrem']}", tit, [], render(r), "cmed"))
    cx.conf("medicamentos/anvisa_cmed_precos_medicamentos.csv", len(c), len(c))
    n = cx.load("medicamentos/fda_ndc_produtos.json")
    g = collections.OrderedDict()
    for r in n: g.setdefault(r["product_ndc"], []).append(r)
    for k, rs in g.items():
        desc, srt = render_many(rs)
        out.append(atom(T, "produto_fda_ndc", f"fda-ndc:{k}", srt[0]["brand_name"] or srt[0]["generic_name"],
                        [x["generic_name"] for x in srt] + [x["brand_name"] for x in srt[1:]], desc, "fda_ndc"))
    cx.conf("medicamentos/fda_ndc_produtos.csv", len(n), len(g),
            "Entidade = product_ndc. O openFDA traz alguns product_ndc em mais de um registro (listagens diferentes do mesmo NDC); foram agrupados num átomo com todos os registros literais.")
    s = cx.load("medicamentos/fda_desabastecimento.json")
    g = collections.OrderedDict()
    for r in s: g.setdefault(r["package_ndc"], []).append(r)
    for k, rs in g.items():
        desc, srt = render_many(rs)
        out.append(atom(T, "desabastecimento_fda", f"fda-desabastecimento:{k}", srt[0]["presentation"],
                        [x["generic_name"] for x in srt], desc, "fda_shortages"))
    cx.conf("medicamentos/fda_desabastecimento.csv", len(s), len(g),
            "Entidade = package_ndc em desabastecimento. Alguns NDC aparecem em mais de um registro (inclusive 1 linha duplicada idêntica); agrupados num átomo.")
    return out

def t_nutricao(cx):
    T, out = "nutricao", []
    comp = cx.load("nutricao/taco_composicao.json")
    ag = cx.load("nutricao/taco_acidos_graxos.json")
    am = cx.load("nutricao/taco_aminoacidos.json")
    ids = {r["numero_alimento"] for r in comp}
    assert all(r["numero_alimento"] in ids for r in ag + am)
    agm = {r["numero_alimento"]: r for r in ag}; amm = {r["numero_alimento"]: r for r in am}
    for r in comp:
        k = r["numero_alimento"]; desc = render(r)
        if k in agm: desc += "\n\n## taco_acidos_graxos\n" + render(agm[k])
        if k in amm: desc += "\n\n## taco_aminoacidos\n" + render(amm[k])
        out.append(atom(T, "alimento_taco", f"taco:{k}", r["descricao"], [], desc, "taco"))
    cx.conf("nutricao/taco_composicao.csv", len(comp), len(comp))
    cx.conf("nutricao/taco_acidos_graxos.csv", len(ag), 0, "Atributos do mesmo alimento TACO (mesmo numero_alimento): anexados ao átomo alimento_taco, seção '## taco_acidos_graxos'.")
    cx.conf("nutricao/taco_aminoacidos.csv", len(am), 0, "Atributos do mesmo alimento TACO: anexados ao átomo alimento_taco, seção '## taco_aminoacidos'.")
    p = cx.load("nutricao/pof_medidas_caseiras.json")
    for r in p:
        tit = " - ".join(x for x in (r["descricao_alimento"], r["descricao_preparacao"], r["descricao_medida"]) if x)
        out.append(atom(T, "medida_caseira_pof", f"pof:{r['codigo_alimento']}-{r['codigo_preparacao']}-{r['codigo_medida']}", tit, [], render(r), "pof"))
    cx.conf("nutricao/pof_medidas_caseiras.csv", len(p), len(p))
    for nome, tipo, fonte in (("sr_legacy", "alimento_usda_sr_legacy", "usda_sr"), ("foundation", "alimento_usda_foundation", "usda_foundation")):
        al = cx.load(f"nutricao/usda_{nome}_alimentos.json")
        nu = cx.load(f"nutricao/usda_{nome}_nutrientes.json")
        ids = {r["fdc_id"] for r in al}
        assert all(r["fdc_id"] in ids for r in nu)
        g = collections.defaultdict(list)
        for r in nu: g[r["fdc_id"]].append(r)
        for r in al:
            desc = render(r)
            if g[r["fdc_id"]]:
                desc += f"\n\n## usda_{nome}_nutrientes\n" + "\n".join(render_line(x) for x in g[r["fdc_id"]])
            out.append(atom(T, tipo, f"usda:{r['fdc_id']}", r["descricao"], [], desc, fonte))
        cx.conf(f"nutricao/usda_{nome}_alimentos.csv", len(al), len(al))
        cx.conf(f"nutricao/usda_{nome}_nutrientes.csv", len(nu), 0,
                f"Formato longo (1 linha por alimento x nutriente): as linhas foram anexadas ao átomo do alimento (fdc_id), seção '## usda_{nome}_nutrientes'.")
    return out

def t_suprimentos(cx):
    T, out = "suprimentos", []
    full = cx.load("suprimentos/catmat_itens_classes_6510_6515_6530_6532.json")
    filt = cx.load("suprimentos/catmat_seringas_agulhas_luvas_curativos.json")
    fset = {r["codigoItem"] for r in filt}
    assert fset <= {r["codigoItem"] for r in full}
    for r in full:
        tipo = "item_catmat_seringa_agulha_luva_curativo" if r["codigoItem"] in fset else "item_catmat"
        out.append(atom(T, tipo, f"catmat:{r['codigoItem']}", r["nomePdm"] or r["descricaoItem"], [], render(r), "catmat"))
    cx.conf("suprimentos/catmat_itens_classes_6510_6515_6530_6532.csv", len(full), len(full))
    cx.conf("suprimentos/catmat_seringas_agulhas_luvas_curativos.csv", len(filt), 0,
            f"Subconjunto filtrado do arquivo completo: os {len(filt)} itens já estão nos átomos e recebem tipo_entidade 'item_catmat_seringa_agulha_luva_curativo' (os demais: 'item_catmat').")
    a = cx.load("suprimentos/anvisa_registros_seringas_agulhas_luvas_curativos.json")
    x = _anvisa_disp(T, a, "anvisa_dispositivos", "registro_anvisa_seringa_agulha_luva_curativo", "anvisa")
    out += x
    cx.conf("suprimentos/anvisa_registros_seringas_agulhas_luvas_curativos.csv", len(a), len(x),
            "Entidade = número de registro Anvisa; linhas repetidas por fabricante/país foram agrupadas (mesma regra de dispositivos).")
    f = cx.load("suprimentos/fda_classificacao_seringas_agulhas_luvas_curativos.json")
    for r in f:
        out.append(atom(T, "classificacao_fda_seringa_agulha_luva_curativo", f"fda:{r['product_code']}", r["device_name"], [], render(r), "fda_dispositivos"))
    cx.conf("suprimentos/fda_classificacao_seringas_agulhas_luvas_curativos.csv", len(f), len(f))
    return out

def t_epidemiologico(cx):
    T, out = "epidemiologico", []
    lst = cx.load("epidemiologico/lista_notificacao_compulsoria_2026.json")
    import re
    for r in lst:
        m = re.match(r"^([a-z])\.\s+(.*)$", r["doenca_ou_agravo"])
        cod = r["numero"] + (m.group(1) if m else "")
        tit = m.group(2) if m else r["doenca_ou_agravo"]
        out.append(atom(T, "agravo_notificacao_compulsoria", f"notificacao-compulsoria:{cod}", tit, [], render(r), "notificacao"))
    cx.conf("epidemiologico/lista_notificacao_compulsoria_2026.csv", len(lst), len(lst))
    for arq, pre, tipo, rot, ep, idf, cidf in EPI:
        d = cx.load(f"epidemiologico/{arq}.json")
        FONTES[pre] = dict(nome=f"Ministério da Saúde - API de Dados Abertos ({ep.split('?')[0]})", url=f"{MS_API}/{ep}",
                           versao=f"amostra: primeiros {len(d)} registros devolvidos pela API em 2026-10-10" if "amostra" in arq else "todos os registros devolvidos pela API em 2026-10-10")
        seen = collections.Counter()
        for r in d:
            if idf: k = str(r[idf])
            else:
                h = sha(canon(r).encode())[:16]; seen[h] += 1
                k = h if seen[h] == 1 else f"{h}-{seen[h]}"
            ref = refs(cid10=cid10_norm(cx.base, r.get(cidf))) if cidf else refs()
            out.append(atom(T, tipo, f"{pre}:{k}", f"{rot} - {k}", [], render(r), pre, ref=ref))
        expl = ""
        if not idf:
            dup = len(d) - len({canon(r) for r in d})
            expl = ("Sem identificador de notificação na fonte: código = 16 primeiros hex do SHA-256 do registro canônico"
                    + (f"; {dup} linhas idênticas a outra receberam sufixo -2, -3... (ordem de ocorrência) para não perder registros" if dup else "") + ".")
        cx.conf(f"epidemiologico/{arq}.csv", len(d), len(d), expl)
    return out

TEMAS = {"cid10": t_cid10, "icd11": t_icd11, "medlineplus": t_medlineplus, "dispositivos": t_dispositivos,
         "medicamentos": t_medicamentos, "nutricao": t_nutricao, "suprimentos": t_suprimentos, "epidemiologico": t_epidemiologico}

def escrever(tema, atoms, cx, saida):
    d = saida / tema; d.mkdir(parents=True, exist_ok=True)
    for old in list(d.glob("*.jsonl")) + [d / "MANIFESTO.json"]:
        if old.exists(): old.unlink()
    ids = collections.Counter(a["atom_id"] for a in atoms)
    dups = [k for k, v in ids.items() if v > 1]
    if dups: raise SystemExit(f"{tema}: atom_id duplicado: {dups[:5]}")
    if any(not a["fonte_url"] for a in atoms): raise SystemExit(f"{tema}: átomo sem fonte_url")
    por_tipo = collections.defaultdict(list)
    for a in atoms: por_tipo[a["tipo_entidade"]].append(a)
    arquivos = []
    for tipo in sorted(por_tipo):
        lines = [canon(a) + "\n" for a in sorted(por_tipo[tipo], key=lambda a: a["atom_id"])]
        parts, cur, size = [], [], 0
        for ln in lines:
            b = len(ln.encode("utf-8"))
            if cur and size + b > MAX_BYTES: parts.append(cur); cur, size = [], 0
            cur.append(ln); size += b
        if cur: parts.append(cur)
        for i, p in enumerate(parts, 1):
            nome = f"{tipo}.jsonl" if len(parts) == 1 else f"{tipo}.parte-{i:04d}.jsonl"
            data = "".join(p).encode("utf-8")
            (d / nome).write_bytes(data)
            arquivos.append({"arquivo": nome, "tipo_entidade": tipo, "atomos": len(p), "bytes": len(data), "sha256": sha(data)})
    fontes = sorted({(a["fonte_nome"], a["fonte_url"] if a["fonte_url"].startswith(("https://dados", "https://download", "http://www2", "https://icdcdn", "https://medlineplus.gov/xml", "https://raw.", "https://fdc", "https://dadosabertos", "https://bvsms", MS_API)) else None, a["fonte_versao"], a["data_extracao"]) for a in atoms}, key=lambda x: (x[0], x[1] or "", x[2]))
    # para fontes com URL por entidade (MedlinePlus, CID-11), registra a URL do arquivo de origem
    fl = []
    for nome, url, versao, data in fontes:
        if url is None:
            url = next(f["url"] for f in FONTES.values() if f["nome"] == nome)
        item = {"fonte_nome": nome, "fonte_url": url, "fonte_versao": versao, "data_extracao": data}
        if item not in fl: fl.append(item)
    man = {"tema": tema, "versao_gerador": VERSAO_GERADOR, "total_atomos": len(atoms),
           "atomos_por_tipo_entidade": {k: len(v) for k, v in sorted(por_tipo.items())},
           "arquivos": arquivos, "fontes": fl, "entradas": cx.entradas, "conferencia_contagens": cx.conferencia,
           "regras": {"atom_id": "<tema>:<codigo>; codigo = chave local, com prefixo de subfonte quando o tema tem mais de uma fonte",
                      "descricao_literal": "renderização literal 'campo: valor' de todos os registros de origem da entidade (nada resumido)",
                      "sha256_atomo": "SHA-256 do JSON canônico (sort_keys, ensure_ascii=False, separators=(',',':')) do átomo sem o campo sha256",
                      "ordenacao": "um arquivo por tipo_entidade, linhas ordenadas por atom_id, partes <= 90.000.000 bytes",
                      "data_extracao": f"fixa por fonte ({DATA}), não é a data da execução"}}
    (d / "MANIFESTO.json").write_bytes((json.dumps(man, sort_keys=True, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    return man

def main():
    args = sys.argv[1:]
    base, saida = Path("/workspace/doencas"), Path("/workspace/doencas_atomizado")
    if "--entrada" in args: i = args.index("--entrada"); base = Path(args[i + 1]); del args[i:i + 2]
    if "--saida" in args: i = args.index("--saida"); saida = Path(args[i + 1]); del args[i:i + 2]
    for tema in args or list(TEMAS):
        cx = Ctx(base)
        atoms = TEMAS[tema](cx)
        man = escrever(tema, atoms, cx, saida)
        print(f"{tema}: {man['total_atomos']} átomos em {len(man['arquivos'])} arquivo(s)")

if __name__ == "__main__":
    main()
