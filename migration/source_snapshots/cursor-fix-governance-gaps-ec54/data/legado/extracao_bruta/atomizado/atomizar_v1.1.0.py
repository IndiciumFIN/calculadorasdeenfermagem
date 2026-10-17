#!/usr/bin/env python3
"""
atomizar.py - transforma a biblioteca /workspace/doencas em "átomos" JSONL determinísticos.

Uso:  python3 atomizar.py [--entrada /workspace/doencas] [--saida /workspace/doencas_atomizado] [tema ...]
Fase 1 (temas únicos): cid10 icd11 medlineplus dispositivos medicamentos nutricao suprimentos epidemiologico
Fase 2 (temas sobrepostos, v1.1.0): sepse sinais_vitais vacinas vacinal_brasil ferimentos protocolos_enfermagem mesh
  (lê também a matriz de sobreposição: --matriz <csv>, padrão _entradas/MATRIZ_CRUZAMENTO_NORMATIVOS_DADOS_2026-10-10.csv)
A saída da fase 1 com a v1.1.0 é byte a byte idêntica à da v1.0.0 (o MANIFESTO dos temas da fase 1 continua registrando
"atomizar.py 1.0.0" em versao_gerador, que é a versão das regras daquele tema; nenhuma regra da fase 1 mudou).

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
import csv, hashlib, json, sys, collections, re, unicodedata
from pathlib import Path

VERSAO_GERADOR = "atomizar.py 1.1.0"
FASE1 = ("cid10", "icd11", "medlineplus", "dispositivos", "medicamentos", "nutricao", "suprimentos", "epidemiologico")
VERSAO_REGRAS_TEMA = {t: "atomizar.py 1.0.0" for t in FASE1}   # versão que define as regras (e a saída) de cada tema
MATRIZ = Path(__file__).resolve().parent / "_entradas" / "MATRIZ_CRUZAMENTO_NORMATIVOS_DADOS_2026-10-10.csv"
MATRIZ_DRIVE_ID = "1eJETouIY0YwoZ0qUg-ObYRmPLeKgcEy_"
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
        self.base = base; self.entradas = []; self.conferencia = []; self.extra = {}
    def load(self, rel):
        p = self.base / rel
        d = json.loads(p.read_text(encoding="utf-8"))
        c = p.with_suffix(".csv")
        with open(c, encoding="utf-8", newline="") as fh:
            ncsv = sum(1 for _ in csv.reader(fh)) - 1
        self.entradas.append({"arquivo": rel, "registros_json": len(d), "linhas_csv": ncsv,
                              "sha256_json": sha(p.read_bytes()), "sha256_csv": sha(c.read_bytes())})
        return d
    def load_json_only(self, rel, n_registros):
        """Arquivo JSON aninhado sem CSV equivalente (transcrições). n_registros = nº de registros-folha contados."""
        p = self.base / rel
        d = json.loads(p.read_text(encoding="utf-8"))
        self.entradas.append({"arquivo": rel, "registros_json": n_registros(d), "linhas_csv": None,
                              "sha256_json": sha(p.read_bytes()), "sha256_csv": None})
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

# ================================================================ FASE 2 (v1.1.0): temas sobrepostos
MARCA_TRANSCRICAO = "[TRANSCRITO MANUALMENTE]"
VERSAO_TRANSCRICAO = "transcrição manual digitada pelo Grok Bot em 2026-10-10 a partir da publicação citada (não é extração automática; conferir no documento original antes de uso clínico)"
FONTES.update({
    "mesh": dict(nome="NLM - MeSH Descriptors 2026 (desc2026.gz)",
                 url="https://nlmpubs.nlm.nih.gov/projects/mesh/MESH_FILES/xmlmesh/desc2026.gz", versao="MeSH 2026 (desc2026.gz baixado em 2026-10-10)"),
    "cvx": dict(nome="CDC - CVX (códigos de vacinas administradas, cvx.txt)",
                url="https://www2a.cdc.gov/vaccines/iis/iisstandards/downloads/cvx.txt", versao="cvx.txt baixado em 2026-10-10 (sem número de versão na fonte)"),
    "cdsi": dict(nome="CDC - CDSi Supporting Data (regras ACIP, ScheduleSupportingData.xml / AntigenSupportingData)",
                 url="https://www.cdc.gov/iis/downloads/supporting-data-4.65-508.zip", versao="CDSi Supporting Data v4.65"),
    "fhir_vitais": dict(nome="HL7 FHIR R4 - perfis de sinais vitais (StructureDefinition *.profile.json)",
                        url="https://hl7.org/fhir/R4/vitalsigns.profile.json", versao="FHIR R4 (4.0.1)"),
    "transc_sepsis3": dict(nome=f"{MARCA_TRANSCRICAO} Singer M, et al. Sepsis-3. JAMA. 2016;315(8):801-810",
                           url="https://doi.org/10.1001/jama.2016.0287", versao=VERSAO_TRANSCRICAO),
    "transc_sofa": dict(nome=f"{MARCA_TRANSCRICAO} Vincent JL, et al. The SOFA score. Intensive Care Med. 1996;22(7):707-710",
                        url="https://doi.org/10.1007/BF01709751", versao=VERSAO_TRANSCRICAO),
    "transc_news2": dict(nome=f"{MARCA_TRANSCRICAO} Royal College of Physicians. National Early Warning Score (NEWS) 2. London: RCP, 2017",
                         url="https://www.rcp.ac.uk/improving-care/resources/national-early-warning-score-news-2/", versao=VERSAO_TRANSCRICAO),
    "transc_dbha2020": dict(nome=f"{MARCA_TRANSCRICAO} Barroso WKS, et al. Diretrizes Brasileiras de Hipertensão Arterial - 2020. Arq Bras Cardiol. 2021;116(3):516-658",
                            url="https://doi.org/10.36660/abc.20201238", versao=VERSAO_TRANSCRICAO),
    "anvisa_nome_tecnico_curativo": dict(nome="Contagem derivada (fetch.py) de Anvisa - Produtos para saúde registrados: nomes técnicos de curativos",
                                         url="https://dados.anvisa.gov.br/dados/TA_PRODUTO_SAUDE_SITE.csv", versao="contagem sobre o arquivo baixado em 2026-10-10"),
    "catmat_pdm_6510": dict(nome="Contagem derivada (fetch.py) de Compras.gov.br - CATMAT: itens por PDM na classe 6510",
                            url="https://dadosabertos.compras.gov.br/modulo-material/4_consultarItemMaterial", versao="contagem sobre a consulta à API em 2026-10-10"),
})
MS_FASE2 = {  # chave-fonte: (endpoint, amostra?)
    "pni": ("vacinacao/doses-aplicadas-pni-2026", True), "esavi": ("vacinacao/esavi", True),
    "sies": ("vacinacao/sistema-de-informacao-de-insumos-estrategicos", True), "sesai": ("saude-indigena/sesai-cobertura-vacinal", False),
    "conitec_pcdt": ("ciencia-tecnologia/dgits-controle-pcdt", False), "conitec_tec": ("ciencia-tecnologia/dgits-tecnologias-diretrizes", False),
}

def slug(s):
    s = str(s).replace("<=", " le ").replace(">=", " ge ").replace("<", " lt ").replace(">", " gt ")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9.]+", "-", s).strip("-.")

def fonte_ms(chave, n):
    ep, amostra = MS_FASE2[chave]
    FONTES[chave] = dict(nome=f"Ministério da Saúde - API de Dados Abertos ({ep})", url=f"{MS_API}/{ep}",
                         versao=f"amostra: primeiros {n} registros devolvidos pela API em 2026-10-10" if amostra else "todos os registros devolvidos pela API em 2026-10-10")

def codigos_hash(rows):
    seen = collections.Counter(); out = []
    for r in rows:
        h = sha(canon(r).encode())[:16]; seen[h] += 1
        out.append(h if seen[h] == 1 else f"{h}-{seen[h]}")
    return out

def expl_hash(rows):
    dup = len(rows) - len({canon(r) for r in rows})
    return ("Sem identificador na fonte: código = 16 primeiros hex do SHA-256 do registro canônico"
            + (f"; {dup} linhas idênticas a outra receberam sufixo -2, -3... (ordem de ocorrência)" if dup else "") + ".")

def codigos_slug(valores):
    """slug do valor literal; se dois valores literais diferentes dão o mesmo slug (ex.: 'CURATIVO' e 'CURATIVO.'),
    todos os do grupo recebem o sufixo '-' + 8 primeiros hex do SHA-256 do valor literal."""
    sl = [slug(v) for v in valores]; c = collections.Counter(sl)
    return [x if c[x] == 1 else f"{x}-{sha(str(v).encode('utf-8'))[:8]}" for x, v in zip(sl, valores)]

def unico(codes, nome):
    c = collections.Counter(codes); d = [k for k, v in c.items() if v > 1]
    assert not d, f"{nome}: código não único {d[:3]}"

# ---- matriz de sobreposição (Calculadoras-de-Enfermagem etc.)
_MZ = None
def matriz():
    global _MZ
    if _MZ is None:
        b = MATRIZ.read_bytes()
        rows = list(csv.DictReader(b.decode("utf-8-sig").splitlines()))
        _MZ = (rows, sha(b))
    return _MZ

def sobreposicao(cx, tema, decisoes, mapeamentos=(), conflitos=()):
    rows, h = matriz()
    linha = [r for r in rows if r["chave"] == f"TEMA|{tema}"]
    cx.extra["sobreposicao_matriz"] = {
        "matriz_arquivo": MATRIZ.name, "matriz_drive_file_id": MATRIZ_DRIVE_ID, "matriz_sha256": h,
        "linha_do_tema_literal": linha[0] if linha else None,
        "decisoes": list(decisoes),
        "mapeamentos_itens_calculadoras_enfermagem": list(mapeamentos),
        "conflitos_ou_ambiguidades": list(conflitos),
        "regra": "Nenhum átomo foi removido por sobreposição (a matriz não manda remover átomos). Mapeamentos item a item só quando a linha da matriz cita literalmente o arquivo de origem do átomo (a_local) e, se a matriz traz prefixo de sha256, ele confere com o arquivo local; o resto fica registrado aqui no nível do tema. referencias_cruzadas mantém só as 4 chaves do spec (cid10, cid11, mesh, medlineplus)."}

# ---- recortes de vocabulários já atomizados (fase 1 / tema mesh)
_MP = None
def mp_index(base):
    global _MP
    if _MP is None:
        _MP = {}
        for lang in ("en", "es"):
            for r in json.loads((base / f"medlineplus/health_topics_{lang}.json").read_text(encoding="utf-8")):
                _MP[r["url"]] = f"medlineplus:{lang}:{r['id']}"
    return _MP

def recorte_cid10(cx, T, rel):
    d = cx.load(rel); out = []
    for r in d:
        ref = refs(cid10=cid10_norm(cx.base, r["codigo"]))
        assert ref["cid10"] == [r["codigo"]]
        out.append(atom(T, "recorte_cid10", f"cid10:{r['codigo']}", r["descricao"], [r["descricao_abrev"]], render(r), "cid10", ref=ref))
    cx.conf(rel.replace(".json", ".csv"), len(d), len(d))
    return out

def recorte_cid11(cx, T, rel):
    d = cx.load(rel); out = []
    for r in d:
        cod = r["codigo"] or f"bloco:{r['uri_linearizacao'].rsplit('/', 1)[-1]}"
        out.append(atom(T, "recorte_cid11", f"cid11:{cod}", r["titulo_pt"] or r["titulo_en"], [r["titulo_en"]], render(r), "icd11",
                        url=r["link_navegador"], ref=refs(cid11=[r["codigo"]] if r["codigo"] else [])))
    cx.conf(rel.replace(".json", ".csv"), len(d), len(d))
    return out

def recorte_mesh(cx, T, rel):
    d = cx.load(rel)
    out = [atom(T, "recorte_mesh", f"mesh:{r['ui']}", r["nome"], r["termos_entrada"], render(r), "mesh", ref=refs(mesh=[r["ui"]])) for r in d]
    cx.conf(rel.replace(".json", ".csv"), len(d), len(d))
    return out

def t_sepse(cx):
    T = "sepse"
    out = recorte_cid10(cx, T, "sepse/sepse_cid10.json") + recorte_cid11(cx, T, "sepse/sepse_cid11.json") + recorte_mesh(cx, T, "sepse/sepse_mesh.json")
    d = cx.load("sepse/sepse_medlineplus.json"); mp = mp_index(cx.base)
    for r in d:
        lang = {"English": "en", "Spanish": "es"}[r["idioma"]]
        proprio = mp[r["url"]]; assert proprio == f"medlineplus:{lang}:{r['id']}"
        cp = [mp[r["topico_outro_idioma_url"]]] if r["topico_outro_idioma_url"] in mp else []
        out.append(atom(T, "recorte_medlineplus", f"medlineplus:{lang}:{r['id']}", r["titulo"], list(r["tambem_chamado"]) + list(r["ver_tambem_termos"]),
                        render(r), "medlineplus", url=r["url"], ref=refs(mesh=[m.split(":", 1)[0] for m in r["mesh"] if m], medlineplus=[proprio] + cp)))
    cx.conf("sepse/sepse_medlineplus.csv", len(d), len(d))
    # transcrições manuais
    s3 = cx.load_json_only("sepse/criterios_sepsis3.json",
                           lambda j: len(j["definicoes"]) + 2 + len(j["qsofa"]["itens"]) + sum(len(x["pontuacao"]) for x in j["sofa"]["sistemas"]))
    aviso = "\n\n## aviso (criterios_sepsis3.json)\n" + s3["aviso"] + "\n\n## fontes (criterios_sepsis3.json)\n" + "\n".join(s3["fontes"])
    for k, v in s3["definicoes"].items():
        out.append(atom(T, "definicao_transcrita_manualmente", f"definicao:{slug(k)}", k.replace("_", " "), [],
                        render({"termo": k, "definicao": v}) + aviso, "transc_sepsis3"))
    out.append(atom(T, "escore_transcrito_manualmente", "escore:qsofa", "qSOFA (quick SOFA)", [],
                    render({"escore": "qSOFA", "descricao": s3["qsofa"]["descricao"]}) + "\n\n## itens\n" + "\n".join(render_line(i) for i in s3["qsofa"]["itens"]) + aviso, "transc_sepsis3"))
    out.append(atom(T, "escore_transcrito_manualmente", "escore:sofa", "SOFA (Sequential/Sepsis-related Organ Failure Assessment)", [],
                    render({"escore": "SOFA", "descricao": s3["sofa"]["descricao"]}) + "\n\n## sistemas\n" + "\n".join(render_line({"sistema": x["sistema"], "variavel": x["variavel"]}) for x in s3["sofa"]["sistemas"]) + aviso, "transc_sofa"))
    cx.conf("sepse/criterios_sepsis3.json", cx.entradas[-1]["registros_json"], 4,
            "JSON aninhado transcrito à mão, sem CSV equivalente. Geram átomos novos só as 2 definições (sepse, choque séptico) e as 2 descrições de escore (qSOFA, SOFA); "
            "os 33 itens de pontuação do JSON são os mesmos registros de criterios_sofa_qsofa.csv e viram átomos a partir dele (não duplicados).")
    c = cx.load("sepse/criterios_sofa_qsofa.json"); codes = []
    for r in c:
        cod = f"{slug(r['escore'])}:{slug(r['sistema'] or r['variavel'])}:{r['pontos']}"; codes.append(cod)
        out.append(atom(T, "criterio_escore_transcrito_manualmente", cod, f"{r['escore']} - {r['sistema'] or r['variavel']} - {r['pontos']} ponto(s): {r['criterio']}", [],
                        render(r) + aviso, "transc_sofa" if r["escore"] == "SOFA" else "transc_sepsis3"))
    unico(codes, "sofa"); cx.conf("sepse/criterios_sofa_qsofa.csv", len(c), len(c))
    sobreposicao(cx, T,
        ["Recortes (cid10, cid11, mesh, medlineplus) são registros idênticos aos dos temas canônicos cid10/icd11/mesh/medlineplus; mantidos como átomos do tema sepse (tipo 'recorte_*') com referencias_cruzadas apontando para o código canônico (cid10 = código; cid11 = código, vazio em blocos sem código; mesh = UI; medlineplus = atom_id do tópico no tema medlineplus + o do outro idioma).",
         "Matriz (TEMA|sepse, sobreposicao=parcial): Calculadoras-de-Enfermagem tem template 16 + corpus SRC-SEPSIS3-2016/SRC-SSC-2026/SRC-ILAS-2026; recomenda conferir a transcrição do A contra a fonte primária (Sepsis-3). Átomos transcritos mantidos, marcados como transcritos e pendentes dessa conferência humana."],
        conflitos=["A matriz recomenda tratar o corpus Sepsis-3 como canônico e 'conferir a transcrição do A'; isso é uma verificação humana pendente, não instrução de remover átomos. Nada removido."])
    cx.extra["marcacao_transcricao_manual"] = MARCA_DOC
    return out

def t_sinais_vitais(cx):
    T, out = "sinais_vitais", []
    d = cx.load("sinais_vitais/fhir_r4_sinais_vitais_codigos_loinc.json")
    for r in d:
        out.append(atom(T, "codigo_loinc_perfil_fhir", f"fhir:{r['perfil_fhir']}:{r['codigo']}", f"{r['titulo']} - LOINC {r['codigo']}", [], render(r), "fhir_vitais",
                        url=f"https://hl7.org/fhir/R4/{r['perfil_fhir']}.profile.json"))
    cx.conf("sinais_vitais/fhir_r4_sinais_vitais_codigos_loinc.csv", len(d), len(d))
    ref = cx.load_json_only("sinais_vitais/referencias_sinais_vitais_transcritas.json",
                            lambda j: sum(len(p["faixas"]) for p in j["news2"]["parametros"]) + len(j["news2"]["risco_clinico"]) + len(j["pressao_arterial_brasil_2020"]["classificacao"]))
    aviso = "\n\n## aviso (referencias_sinais_vitais_transcritas.json)\n" + ref["AVISO"]
    for r in ref["news2"]["risco_clinico"]:
        out.append(atom(T, "risco_news2_transcrito_manualmente", f"news2-risco:{slug(r['pontuacao'])}", f"NEWS2 {r['pontuacao']}: risco {r['risco']}", [],
                        render(r) + "\n\n## fonte\n" + ref["news2"]["fonte"] + aviso, "transc_news2"))
    cx.conf("sinais_vitais/referencias_sinais_vitais_transcritas.json", cx.entradas[-1]["registros_json"], len(ref["news2"]["risco_clinico"]),
            "JSON aninhado transcrito à mão, sem CSV equivalente. Só as 4 faixas de risco clínico do NEWS2 geram átomos novos; as 36 faixas de pontuação NEWS2 e as 6 classes de PA "
            "são os mesmos registros de news2_pontuacao_transcrita.csv e classificacao_pressao_arterial_dbha2020_transcrita.csv e viram átomos a partir deles (não duplicados).")
    n = cx.load("sinais_vitais/news2_pontuacao_transcrita.json"); codes = []
    for r in n:
        cod = f"news2:{slug(r['parametro'])}:{slug(r['faixa'])}"; codes.append(cod)
        out.append(atom(T, "pontuacao_news2_transcrita_manualmente", cod, f"NEWS2 - {r['parametro']} {r['faixa']}: {r['pontos']} ponto(s)", [],
                        render(r) + "\n\n## fonte\n" + ref["news2"]["fonte"] + aviso, "transc_news2"))
    unico(codes, "news2"); cx.conf("sinais_vitais/news2_pontuacao_transcrita.csv", len(n), len(n))
    p = cx.load("sinais_vitais/classificacao_pressao_arterial_dbha2020_transcrita.json"); codes = []
    for r in p:
        cod = f"pa-dbha2020:{slug(r['classificacao'])}"; codes.append(cod)
        out.append(atom(T, "classificacao_pa_dbha2020_transcrita_manualmente", cod, r["classificacao"], [], render(r) + aviso, "transc_dbha2020"))
    unico(codes, "pa"); cx.conf("sinais_vitais/classificacao_pressao_arterial_dbha2020_transcrita.csv", len(p), len(p))
    sobreposicao(cx, T,
        ["Matriz (TEMA|sinais_vitais, parcial): Calculadoras-de-Enfermagem tem o corpus SRC-RCP-NEWS2 (documento oficial RCP). Recomendação da matriz: canônico para NEWS2 = documento RCP; a tabela do A vale como derivada após conferência; LOINC e DBHA só existem no A.",
         "Átomos NEWS2 mantidos (tipo *_transcrita_manualmente), registrados aqui como 'tabela derivada pendente de conferência contra o documento RCP'. LOINC/FHIR e PA DBHA 2020 sem sobreposição.",
         "Perfis FHIR brutos (raw/*.profile.json, valueset) não são atomizados: o CSV limpo já traz os 12 códigos; o value set bruto inclui também 8478-0 (PA média), que não está no CSV limpo e por isso não vira átomo."],
        conflitos=["A matriz considera o documento RCP canônico para NEWS2; não manda remover a tabela transcrita. Nada removido; conferência humana pendente."])
    cx.extra["marcacao_transcricao_manual"] = MARCA_DOC
    return out

def t_vacinas(cx):
    T, out = "vacinas", []
    d = cx.load("vacinas/cdc_cvx_codigos_vacinas.json")
    for r in d: out.append(atom(T, "codigo_cvx", f"cvx:{r['cvx']}", r["nome_completo"] or r["descricao_curta"], [r["descricao_curta"]], render(r), "cvx"))
    cx.conf("vacinas/cdc_cvx_codigos_vacinas.csv", len(d), len(d))
    d = cx.load("vacinas/cdsi_cvx_para_antigeno.json"); codes = []
    for r in d:
        cod = f"cdsi-cvx-antigeno:{r['cvx']}:{slug(r['antigeno'])}"; codes.append(cod)
        out.append(atom(T, "associacao_cvx_antigeno_cdsi", cod, f"CVX {r['cvx']} ({r['descricao_curta']}) -> {r['antigeno']}", [], render(r), "cdsi"))
    unico(codes, "cvx-antigeno"); cx.conf("vacinas/cdsi_cvx_para_antigeno.csv", len(d), len(d))
    d = cx.load("vacinas/cdsi_esquemas_doses_acip.json"); codes = []
    for r in d:
        cod = f"cdsi-dose:{slug(r['antigeno'])}:{slug(r['serie'])}:{slug(r['dose'])}"; codes.append(cod)
        out.append(atom(T, "dose_esquema_cdsi_acip", cod, f"{r['serie']} - {r['dose']}", [], render(r), "cdsi"))
    unico(codes, "doses"); cx.conf("vacinas/cdsi_esquemas_doses_acip.csv", len(d), len(d))
    d = cx.load("vacinas/cdsi_observacoes_condicoes.json")
    for r in d: out.append(atom(T, "observacao_condicao_cdsi", f"cdsi-obs:{r['codigo']}", r["titulo"], [], render(r), "cdsi"))
    cx.conf("vacinas/cdsi_observacoes_condicoes.csv", len(d), len(d))
    sobreposicao(cx, T,
        ["Matriz (TEMA|vacinas, parcial): Calculadoras-de-Enfermagem tem EXTRAIDO_vaccine_json_schema_package_v0_3.zip e EXTRAIDO_CKO_Vacinas_Calculadoras_Propostas (conteúdo não aberto pela matriz). Recomendação: comparar o zip de schema com CVX antes de integrar; manter A como fonte bruta.",
         "Sem mapeamento item a item possível: a matriz não lista itens CVX. Todos os átomos mantidos.",
         "raw/: os dois zips CDSi (cdsi-supporting-data-4.65.zip e supporting-data-4.65-508.zip) são o mesmo download; não atomizados (os CSVs limpos derivam deles)."])
    return out

def t_vacinal_brasil(cx):
    T, out = "vacinal_brasil", []
    for arq, chave, tipo, idf, rot in (("pni_doses_aplicadas_2026_amostra", "pni", "dose_aplicada_pni", "codigo_documento", "Dose aplicada PNI 2026"),
                                       ("esavi_eventos_adversos_vacinacao_amostra", "esavi", "notificacao_esavi", "numero_notificacao", "Notificação ESAVI"),
                                       ("sies_insumos_estrategicos_amostra", "sies", "movimento_insumo_sies", None, "Movimento SIES"),
                                       ("sesai_cobertura_vacinal_indigena", "sesai", "cobertura_vacinal_polo_sesai", None, "Cobertura vacinal SESAI")):
        d = cx.load(f"vacinal_brasil/{arq}.json"); fonte_ms(chave, len(d))
        ks = [str(r[idf]) for r in d] if idf else codigos_hash(d)
        unico(ks, arq)
        for k, r in zip(ks, d):
            tit = f"{rot} - {k}"
            if chave == "sesai": tit = f"{rot} {r['ano']} - {r['uf']} - DSEI {r['dsei']} - polo {r['polo']}"
            if chave == "sies": tit = f"{rot} - {r['tx_insumo']} - {r['ano']}/{r['mes']} - {r['tx_sigla']} ({k})"
            out.append(atom(T, tipo, f"{chave}:{k}", tit, [], render(r), chave))
        expl = expl_hash(d) if not idf else ""
        if chave == "sesai":
            expl += " (Não há chave natural única: ano+uf+dsei+polo se repete em 1 caso, 2022/AM-RR/YANOMAMI/DEMINI, com valores diferentes; por isso o hash.)"
        cx.conf(f"vacinal_brasil/{arq}.csv", len(d), len(d), expl)
    sobreposicao(cx, T,
        ["Matriz (TEMA|vacinal_brasil, parcial): Calculadoras-de-Enfermagem só tem 8 calendariovacinal*.html na raiz (calendário = regra), enquanto o A tem dados de aplicação (amostras first-N). Canônica de calendário segundo a matriz: Instrução Normativa 2026 (PDF em protocolos_enfermagem, átomo protocolos_enfermagem:protocolo:instrucao-normativa-do-calendario-nacional-de-vacinacao-2026).",
         "Escopos diferentes (calendário x microdados): nenhum átomo removido, nenhum mapeamento item a item."])
    return out

def t_ferimentos(cx):
    T = "ferimentos"
    out = recorte_cid10(cx, T, "ferimentos/ferimentos_cid10.json") + recorte_cid11(cx, T, "ferimentos/ferimentos_cid11.json") + recorte_mesh(cx, T, "ferimentos/ferimentos_mesh.json")
    for arq, campo, tipo, pre, fonte in (("tipos_curativos_anvisa_nome_tecnico", "nome_tecnico_anvisa", "nome_tecnico_anvisa_curativo", "anvisa-nome-tecnico", "anvisa_nome_tecnico_curativo"),
                                         ("tipos_curativos_catmat_pdm_classe_6510", "pdm_catmat", "pdm_catmat_classe_6510", "catmat-pdm", "catmat_pdm_6510")):
        d = cx.load(f"ferimentos/{arq}.json"); codes = [f"{pre}:{c}" for c in codigos_slug([r[campo] for r in d])]; unico(codes, arq)
        for c, r in zip(codes, d): out.append(atom(T, tipo, c, r[campo], [], render(r), fonte))
        col = len(d) - len({slug(r[campo]) for r in d})
        cx.conf(f"ferimentos/{arq}.csv", len(d), len(d),
                f"Código = slug do nome literal; {col} par(es) de nomes que só diferem em pontuação (ex.: 'CURATIVO' e 'CURATIVO.') receberam sufixo com 8 hex do SHA-256 do nome literal." if col else "")
    sobreposicao(cx, T,
        ["Recortes cid10/cid11/mesh idênticos aos temas canônicos; mantidos (tipo 'recorte_*') com referencias_cruzadas para o código canônico (cid11 vazio nos 6 blocos sem código).",
         "Matriz (TEMA|ferimentos, parcial): Calculadoras-de-Enfermagem tem EXTRAIDO_Infograficos de curativos padronizados_v0_3.zip (conteúdo educativo) x classificações/códigos do A. Recomendação: complementares, manter ambos.",
         "Tipos de curativo = contagens de nome técnico (Anvisa) e PDM (CATMAT classe 6510) feitas pelo fetch.py; não é classificação clínica de coberturas."])
    return out

def t_protocolos_enfermagem(cx):
    T, out = "protocolos_enfermagem", []
    idx = cx.load("protocolos_enfermagem/indice_protocolos.json"); rows_mz, _ = matriz()
    pdfs, maps = [], []; codes = []
    for r in idx:
        cod = f"protocolo:{slug(r['titulo'])}"; codes.append(cod)
        fk = f"protocolo:{cod}"
        FONTES[fk] = dict(nome=f"{r['fonte']} - {r['titulo']}", url=r["url"],
                          versao=f"ano {r['ano']}; " + ("PDF baixado em 2026-10-10" if r["status"] == "ok" else "download falhou em 2026-10-10 (só o registro do índice)"))
        out.append(atom(T, "documento_protocolo", cod, r["titulo"], [], render(r), fk, url=r["url"]))
        if r["arquivo"]:
            b = (cx.base / "protocolos_enfermagem/raw/pdfs" / r["arquivo"]).read_bytes()
            assert len(b) == r["tamanho_bytes"]
            pdfs.append({"arquivo": r["arquivo"], "bytes": len(b), "sha256": sha(b), "atom_id": f"{T}:{cod}"})
            for m in rows_mz:
                if r["arquivo"] in m["a_local"]:
                    pref = re.search(r"sha256 ([0-9a-f]{6,})", m["a_local"])
                    maps.append({"atom_id": f"{T}:{cod}", "matriz_chave": m["chave"], "calc_enf_existe": m["calc_enf_existe"],
                                 "calc_enf_local": m["calc_enf_local"], "calc_enf_status": m["calc_enf_status"],
                                 "sobreposicao": m["sobreposicao"], "diferencas": m["diferencas"], "recomendacao": m["recomendacao"],
                                 "sha256_prefixo_matriz": pref.group(1) if pref else None,
                                 "sha256_confere": (sha(b).startswith(pref.group(1)) if pref else None)})
    unico(codes, "indice"); cx.conf("protocolos_enfermagem/indice_protocolos.csv", len(idx), len(idx),
                                    "")
    cx.extra["pdfs_locais"] = pdfs
    p = cx.load("protocolos_enfermagem/conitec_pcdt_situacao.json"); fonte_ms("conitec_pcdt", len(p))
    codes = [f"pcdt:{slug(r['descricao_do_nome'])}" for r in p]; unico(codes, "pcdt")
    for c, r in zip(codes, p): out.append(atom(T, "pcdt_conitec_situacao", c, r["descricao_do_nome"], [], render(r), "conitec_pcdt"))
    cx.conf("protocolos_enfermagem/conitec_pcdt_situacao.csv", len(p), len(p))
    t = cx.load("protocolos_enfermagem/conitec_tecnologias_diretrizes.json"); fonte_ms("conitec_tec", len(t))
    for k, r in zip(codigos_hash(t), t):
        out.append(atom(T, "tecnologia_diretriz_covid19_conitec", f"conitec-tecnologia:{k}", r["tecnologias_diretrizes_covid19"], [], render(r), "conitec_tec"))
    cx.conf("protocolos_enfermagem/conitec_tecnologias_diretrizes.csv", len(t), len(t),
            expl_hash(t) + " (O campo 'quantidade' não é identificador: vale '-' em 2 linhas.)")
    sobreposicao(cx, T,
        ["Matriz (TEMA|protocolos_enfermagem, parcial): Cofen 736 duplica a fonte que está em Calculadoras-de-Enfermagem (pasta V2); PNSP: o corpus tem a Portaria 529, o A tem os protocolos anexos (complementares); PCDT: o A tem a lista de situação, o corpus tem 1 PCDT.",
         "Mapeamento item a item determinístico: a linha RES|736|2024 cita literalmente o arquivo Resolucao_Cofen_no_736_2024_Processo_de_Enfermagem.pdf e o prefixo de sha256 3fb4e597, que confere com o PDF local (ver mapeamentos_itens_calculadoras_enfermagem).",
         "PDFs: 1 átomo por documento do índice; descricao_literal = registro literal do índice. O texto dos PDFs NÃO foi extraído (a extração depende da ferramenta/versão, não é trivialmente determinística, e alguns PDFs têm centenas de páginas); o sha256 e o tamanho de cada PDF local estão em pdfs_locais.",
         "Os 2 documentos da OMS cujo download falhou continuam como átomos (registro do índice com status 'falhou'), com fonte_url = URL oficial."],
        mapeamentos=maps,
        conflitos=["RES|736|2024 recomenda 'Nao duplicar 736' e diz que o PDF do A é redundante 'se sha = fonte oficial (confirmar)'. Interpretado como orientação de não duplicar o conteúdo normativo, não como ordem explícita de remover o átomo do índice (que só tem o registro do índice, não o texto). Átomo mantido e mapeado para a pasta canônica em Calculadoras-de-Enfermagem; a confirmação de que o sha é o da fonte oficial continua pendente."])
    return out

def t_mesh(cx):
    T, out = "mesh", []
    d = cx.load("mesh/mesh_descritores.json")
    rev = collections.defaultdict(list)
    for lang in ("en", "es"):
        for r in json.loads((cx.base / f"medlineplus/health_topics_{lang}.json").read_text(encoding="utf-8")):
            for m in r["mesh"]:
                if m: rev[m.split(":", 1)[0]].append(f"medlineplus:{lang}:{r['id']}")
    for r in d:
        out.append(atom(T, "descritor_mesh", r["ui"], r["nome"], r["termos_entrada"], render(r), "mesh", ref=refs(medlineplus=rev.get(r["ui"], []))))
    cx.conf("mesh/mesh_descritores.csv", len(d), len(d))
    c = cx.load("mesh/mesh_doencas_categoria_C.json")
    full = {r["ui"]: canon(r) for r in d}
    assert all(full.get(r["ui"]) == canon(r) for r in c)
    cx.conf("mesh/mesh_doencas_categoria_C.csv", len(c), 0,
            f"Subconjunto de mesh_descritores (os {len(c)} descritores com árvore C = doenças, registros idênticos); já estão nos átomos 'descritor_mesh' (campo categorias contém C). Não gera átomos novos para não duplicar.")
    sobreposicao(cx, T,
        ["Matriz (TEMA|mesh, parcial): Calculadoras-de-Enfermagem só cita SRC-DECS (DeCS/BIREME, sem blocos úteis). DeCS (PT) x MeSH (EN) são vocabulários relacionados, não idênticos. Recomendação: canônica A para MeSH; DeCS complementar.",
         "Sem mapeamento item a item (a matriz não lista descritores). referencias_cruzadas.medlineplus = atom_ids dos tópicos MedlinePlus que citam o descritor no próprio campo mesh (regra reversa determinística)."])
    return out

MARCA_DOC = {
    "regra": "Tabelas transcritas à mão (critérios Sepsis-3/SOFA/qSOFA, NEWS2, classificação da PA DBHA 2020) levam a marca em 4 lugares: "
             "(1) tipo_entidade termina em '_transcrito_manualmente' ou '_transcrita_manualmente'; (2) fonte_nome começa com '[TRANSCRITO MANUALMENTE]'; "
             "(3) fonte_versao diz que é transcrição manual digitada pelo Grok Bot em 2026-10-10, não extração automática; "
             "(4) descricao_literal termina com a seção '## aviso (...)' copiada literalmente do arquivo de origem.",
    "fonte_url": "DOI/URL da publicação citada no próprio arquivo transcrito (SOFA -> Vincent 1996; definições e qSOFA -> Singer 2016; NEWS2 -> RCP 2017; PA -> DBHA 2020)."}

TEMAS = {"cid10": t_cid10, "icd11": t_icd11, "medlineplus": t_medlineplus, "dispositivos": t_dispositivos,
         "medicamentos": t_medicamentos, "nutricao": t_nutricao, "suprimentos": t_suprimentos, "epidemiologico": t_epidemiologico,
         "sepse": t_sepse, "sinais_vitais": t_sinais_vitais, "vacinas": t_vacinas, "vacinal_brasil": t_vacinal_brasil,
         "ferimentos": t_ferimentos, "protocolos_enfermagem": t_protocolos_enfermagem, "mesh": t_mesh}

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
    man = {"tema": tema, "versao_gerador": VERSAO_REGRAS_TEMA.get(tema, VERSAO_GERADOR), "total_atomos": len(atoms),
           "atomos_por_tipo_entidade": {k: len(v) for k, v in sorted(por_tipo.items())},
           "arquivos": arquivos, "fontes": fl, "entradas": cx.entradas, "conferencia_contagens": cx.conferencia,
           "regras": {"atom_id": "<tema>:<codigo>; codigo = chave local, com prefixo de subfonte quando o tema tem mais de uma fonte",
                      "descricao_literal": "renderização literal 'campo: valor' de todos os registros de origem da entidade (nada resumido)",
                      "sha256_atomo": "SHA-256 do JSON canônico (sort_keys, ensure_ascii=False, separators=(',',':')) do átomo sem o campo sha256",
                      "ordenacao": "um arquivo por tipo_entidade, linhas ordenadas por atom_id, partes <= 90.000.000 bytes",
                      "data_extracao": f"fixa por fonte ({DATA}), não é a data da execução"}}
    man.update(cx.extra)   # vazio na fase 1 (saída idêntica à v1.0.0)
    (d / "MANIFESTO.json").write_bytes((json.dumps(man, sort_keys=True, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    return man

def main():
    args = sys.argv[1:]
    base, saida = Path("/workspace/doencas"), Path("/workspace/doencas_atomizado")
    if "--entrada" in args: i = args.index("--entrada"); base = Path(args[i + 1]); del args[i:i + 2]
    global MATRIZ
    if "--matriz" in args: i = args.index("--matriz"); MATRIZ = Path(args[i + 1]); del args[i:i + 2]
    if "--saida" in args: i = args.index("--saida"); saida = Path(args[i + 1]); del args[i:i + 2]
    for tema in args or list(TEMAS):
        cx = Ctx(base)
        atoms = TEMAS[tema](cx)
        man = escrever(tema, atoms, cx, saida)
        print(f"{tema}: {man['total_atomos']} átomos em {len(man['arquivos'])} arquivo(s)")

if __name__ == "__main__":
    main()
