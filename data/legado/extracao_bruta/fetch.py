#!/usr/bin/env python3
"""Baixa e converte a biblioteca de saúde (doenças, CID-11, dispositivos, vacinas, nutrição, sepse, medicamentos, MeSH).

Uso:  python3 fetch.py                 -> atualiza tudo
      python3 fetch.py cid10 icd11      -> só os tópicos escolhidos
Tópicos: cid10 medlineplus icd11 dispositivos vacinas nutricao medicamentos mesh sepse
Requer só a biblioteca padrão do Python 3.8+. Saída: <topico>/raw (originais) + <topico>/*.json e *.csv (UTF-8)
"""
import csv, io, json, re, sys, html, urllib.request, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = Path(__file__).resolve().parent
RAW = BASE / "raw"
UA = {"User-Agent": "Mozilla/5.0 (doencas-fetch)"}

CID10_URLS = [
    "http://www2.datasus.gov.br/cid10/V2008/downloads/CID10CSV.zip",          # oficial (pode bloquear IPs fora do Brasil)
    "https://web.archive.org/web/2024id_/http://www2.datasus.gov.br/cid10/V2008/downloads/CID10CSV.zip",  # cópia arquivada idêntica
]
MPLUS_INDEX = "https://medlineplus.gov/xml.html"


def get(url, timeout=90):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def write_out(folder, name, rows, fields):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{name}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    with open(folder / f"{name}.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: ("; ".join(v) if isinstance(v, list) else v) for k, v in r.items()})
    print(f"  {folder.name}/{name}: {len(rows)} registros")


# ---------------- CID-10 (DATASUS, português) ----------------
def fetch_cid10():
    RAW.mkdir(exist_ok=True)
    zpath = RAW / "CID10CSV.zip"
    data = None
    for u in CID10_URLS:
        try:
            data = get(u)
            zipfile.ZipFile(io.BytesIO(data))  # valida
            print(f"CID-10 baixado de {u}")
            break
        except Exception as e:
            print(f"  falhou {u}: {e}")
            data = None
    if data:
        zpath.write_bytes(data)
    elif not zpath.exists():
        sys.exit("Não foi possível baixar o CID-10.")
    z = zipfile.ZipFile(zpath)
    z.extractall(RAW / "cid10")
    out = BASE / "cid10"

    def read(fn):
        txt = z.read(fn).decode("latin-1")
        rows = list(csv.DictReader(io.StringIO(txt), delimiter=";"))
        clean = []
        for r in rows:
            r = {k.strip(): (v or "").strip() for k, v in r.items() if k and k.strip()}
            clean.append(r)
        return clean

    def fmt(code):  # A000 -> A00.0
        return code if len(code) <= 3 else code[:3] + "." + code[3:]

    caps = read("CID-10-CAPITULOS.CSV")
    grupos = read("CID-10-GRUPOS.CSV")
    cats = read("CID-10-CATEGORIAS.CSV")
    subs = read("CID-10-SUBCATEGORIAS.CSV")

    def capitulo_de(cat):
        for c in caps:
            if c["CATINIC"] <= cat <= c["CATFIM"]:
                return c
        return None

    def grupo_de(cat):
        for g in grupos:
            if g["CATINIC"] <= cat <= g["CATFIM"]:
                return g
        return None

    cat_nome = {c["CAT"]: c["DESCRICAO"] for c in cats}

    capitulos = [{"numero": int(c["NUMCAP"]), "cat_inicio": c["CATINIC"], "cat_fim": c["CATFIM"],
                  "descricao": c["DESCRICAO"], "descricao_abrev": c["DESCRABREV"]} for c in caps]
    write_out(out, "capitulos", capitulos, list(capitulos[0]))

    gr = [{"cat_inicio": g["CATINIC"], "cat_fim": g["CATFIM"], "descricao": g["DESCRICAO"],
           "descricao_abrev": g["DESCRABREV"]} for g in grupos]
    write_out(out, "grupos", gr, list(gr[0]))

    categorias = []
    for c in cats:
        cap, g = capitulo_de(c["CAT"]), grupo_de(c["CAT"])
        categorias.append({"codigo": c["CAT"], "descricao": c["DESCRICAO"], "descricao_abrev": c["DESCRABREV"],
                           "classif": c["CLASSIF"], "refer": c["REFER"], "excluidos": c["EXCLUIDOS"],
                           "capitulo": int(cap["NUMCAP"]) if cap else None,
                           "grupo": g["DESCRICAO"] if g else ""})
    write_out(out, "categorias", categorias, list(categorias[0]))

    subcats = []
    for s in subs:
        code = s["SUBCAT"]
        cat = code[:3]
        cap, g = capitulo_de(cat), grupo_de(cat)
        subcats.append({"codigo": fmt(code), "codigo_sem_ponto": code, "descricao": s["DESCRICAO"],
                        "descricao_abrev": s["DESCRABREV"], "categoria": cat, "categoria_descricao": cat_nome.get(cat, ""),
                        "classif": s["CLASSIF"], "restr_sexo": s["RESTRSEXO"], "causa_obito": s["CAUSAOBITO"],
                        "refer": s["REFER"], "excluidos": s["EXCLUIDOS"],
                        "capitulo": int(cap["NUMCAP"]) if cap else None,
                        "capitulo_descricao": cap["DESCRICAO"] if cap else "",
                        "grupo": g["DESCRICAO"] if g else ""})
    write_out(out, "subcategorias", subcats, list(subcats[0]))

    for fn, name in [("CID-O-CATEGORIAS.CSV", "cid_o_categorias"), ("CID-O-GRUPOS.CSV", "cid_o_grupos")]:
        rows = [{k.lower(): v for k, v in r.items()} for r in read(fn)]
        write_out(out, name, rows, list(rows[0]))


# ---------------- MedlinePlus Health Topics (NLM/NIH) ----------------
def strip_html(s):
    s = re.sub(r"<(br|/p|/li)[^>]*>", "\n", s or "")
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    return re.sub(r"\n\s*\n+", "\n", s).strip()


def fetch_medlineplus():
    RAW.mkdir(exist_ok=True)
    idx = get(MPLUS_INDEX).decode("utf-8", "replace")
    urls = sorted(set(re.findall(r"https://medlineplus\.gov/xml/mplus_topics_\d{4}-\d{2}-\d{2}\.xml", idx)))
    if not urls:
        sys.exit("Não achei o XML do MedlinePlus em " + MPLUS_INDEX)
    url = urls[-1]
    fname = url.rsplit("/", 1)[1]
    for old in RAW.glob("mplus_topics_*.xml"):
        if old.name != fname:
            old.unlink()
    path = RAW / fname
    if not path.exists():
        path.write_bytes(get(url, timeout=300))
    print(f"MedlinePlus: {url}")
    root = ET.parse(path).getroot()
    rows = []
    for t in root.findall("health-topic"):
        rows.append({
            "id": t.get("id"), "idioma": t.get("language"), "titulo": t.get("title"), "url": t.get("url"),
            "data_criacao": t.get("date-created"), "meta_descricao": t.get("meta-desc"),
            "tambem_chamado": [e.text for e in t.findall("also-called")],
            "ver_tambem_termos": [e.text for e in t.findall("see-reference")],
            "grupos": [e.text for e in t.findall("group")],
            "mesh": [f'{d.get("id")}:{d.text}' for d in t.findall("mesh-heading/descriptor")],
            "topicos_relacionados": [e.text for e in t.findall("related-topic")],
            "topico_outro_idioma": (t.find("language-mapped-topic").text if t.find("language-mapped-topic") is not None else ""),
            "topico_outro_idioma_url": (t.find("language-mapped-topic").get("url") if t.find("language-mapped-topic") is not None else ""),
            "instituto_primario": (t.find("primary-institute").text if t.find("primary-institute") is not None else ""),
            "resumo_texto": strip_html(t.findtext("full-summary")),
            "resumo_html": t.findtext("full-summary") or "",
        })
    fields = list(rows[0])
    out = BASE / "medlineplus"
    write_out(out, "health_topics_todos", rows, fields)
    for lang, name in [("English", "health_topics_en"), ("Spanish", "health_topics_es")]:
        write_out(out, name, [r for r in rows if r["idioma"] == lang], fields)



# =====================================================================
# Utilidades extras
# =====================================================================
import gzip, json as _json

def download(url, dest, timeout=900):
    dest = Path(dest); dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r, open(str(dest) + ".part", "wb") as f:
        while True:
            b = r.read(1 << 20)
            if not b: break
            f.write(b)
    Path(str(dest) + ".part").replace(dest)
    print(f"  baixado {url}")
    return dest


def read_csv_text(txt, delimiter=";"):
    rows = []
    for r in csv.DictReader(io.StringIO(txt), delimiter=delimiter):
        rows.append({(k or "").strip().lower(): (v or "").strip() for k, v in r.items() if k and k.strip()})
    return rows


def openfda_json(zpath):
    z = zipfile.ZipFile(zpath)
    return _json.loads(z.read(z.namelist()[0]))["results"]


def j(v):  # lista -> texto
    return "; ".join(str(x) for x in v) if isinstance(v, list) else ("" if v is None else v)


# =====================================================================
# CID-11 (OMS) - tabela simples MMS, em português (inclui título em inglês)
# =====================================================================
ICD11_RELEASE = "2026-01"

def fetch_icd11():
    d = BASE / "icd11"; raw = d / "raw"
    url = f"https://icdcdn.who.int/static/releasefiles/{ICD11_RELEASE}/SimpleTabulation-ICD-11-MMS-pt.zip"
    zp = download(url, raw / f"SimpleTabulation-ICD-11-MMS-pt.zip")
    z = zipfile.ZipFile(zp)
    name = [n for n in z.namelist() if n.endswith(".txt") and "Simple" in n][0]
    txt = z.read(name).decode("utf-8-sig")
    rdr = csv.reader(io.StringIO(txt), delimiter="\t")
    header = next(rdr)
    rows = []
    for r in rdr:
        if not r: continue
        r = dict(zip(header, r))
        clean = lambda s: (s or "").strip().strip('"').lstrip("- ").strip()
        depth_title = (r.get("Title") or "").strip('"')
        rows.append({
            "codigo": r.get("Code", ""), "bloco_id": r.get("BlockId", ""),
            "titulo_pt": clean(r.get("Title")), "titulo_en": clean(r.get("TitleEN")),
            "nivel": len(re.match(r"^(- )*", depth_title).group(0)) // 2,
            "tipo": r.get("ClassKind", ""), "profundidade_no_tipo": r.get("DepthInKind", ""),
            "residual": r.get("IsResidual", "") == "True", "folha": r.get("isLeaf", "") == "True",
            "capitulo": r.get("ChapterNo", ""), "tabulacao_primaria": r.get("Primary tabulation", ""),
            "agrupamentos": [r.get(f"Grouping{i}", "") for i in range(1, 6) if r.get(f"Grouping{i}")],
            "nota_codificacao": r.get("CodingNote", ""),
            "uri_foundation": r.get("Foundation URI", ""), "uri_linearizacao": r.get("Linearization URI", ""),
            "uri_pai": r.get("Parent", ""),
            "link_navegador": "https://icd.who.int/browse/latestrelease/mms/pt#" + r.get("Foundation URI", "").rsplit("/", 1)[-1],
        })
    fields = list(rows[0])
    write_out(d, "cid11_mms_completa", rows, fields)
    write_out(d, "cid11_mms_categorias_com_codigo", [r for r in rows if r["codigo"]], fields)


# =====================================================================
# Dispositivos médicos: FDA (classificação) + Anvisa (produtos para saúde)
# =====================================================================
def fetch_dispositivos():
    d = BASE / "dispositivos"; raw = d / "raw"
    zp = download("https://download.open.fda.gov/device/classification/device-classification-0001-of-0001.json.zip",
                  raw / "device-classification.json.zip")
    rows = []
    for r in openfda_json(zp):
        rows.append({k: j(r.get(k)) for k in ["product_code", "device_name", "device_class", "medical_specialty",
                     "medical_specialty_description", "review_panel", "regulation_number", "definition",
                     "submission_type_id", "implant_flag", "life_sustain_support_flag", "gmp_exempt_flag",
                     "third_party_flag", "unclassified_reason", "summary_malfunction_reporting"]})
    write_out(d, "fda_classificacao_dispositivos", rows, list(rows[0]))

    p = download("https://dados.anvisa.gov.br/dados/TA_PRODUTO_SAUDE_SITE.csv", raw / "TA_PRODUTO_SAUDE_SITE.csv")
    rows = read_csv_text(p.read_bytes().decode("latin-1"))
    write_out(d, "anvisa_produtos_saude_registrados", rows, list(rows[0]))


# =====================================================================
# Vacinas: CDC CVX + CDC CDSi (regras ACIP)
# =====================================================================
CDSI_URL = "https://www.cdc.gov/iis/downloads/supporting-data-4.65-508.zip"
def fetch_vacinas():
    d = BASE / "vacinas"; raw = d / "raw"
    p = download("https://www2a.cdc.gov/vaccines/iis/iisstandards/downloads/cvx.txt", raw / "cvx.txt")
    rows = []
    for line in p.read_bytes().decode("utf-8-sig", "replace").splitlines():
        f = [x.strip() for x in line.split("|")]
        if len(f) < 7: continue
        rows.append({"cvx": f[0], "descricao_curta": f[1], "nome_completo": f[2], "notas": f[3],
                     "status": f[4], "nao_vacina": f[5] == "True", "ultima_atualizacao": f[6]})
    write_out(d, "cdc_cvx_codigos_vacinas", rows, list(rows[0]))

    zp = download(CDSI_URL, raw / Path(CDSI_URL).name)
    z = zipfile.ZipFile(zp)
    T = lambda e, p: (e.findtext(p) or "").strip()
    sched = [n for n in z.namelist() if n.endswith("ScheduleSupportingData.xml")][0]
    root = ET.fromstring(z.read(sched))
    cvxmap = []
    for m in root.iter("cvxMap"):
        for a in m.findall("association"):
            cvxmap.append({"cvx": T(m, "cvx"), "descricao_curta": T(m, "shortDescription"), "antigeno": T(a, "antigen"),
                           "idade_inicio": T(a, "associationBeginAge"), "idade_fim": T(a, "associationEndAge")})
    write_out(d, "cdsi_cvx_para_antigeno", cvxmap, list(cvxmap[0]))
    obs = [{"codigo": T(o, "observationCode"), "titulo": T(o, "observationTitle"), "grupo": T(o, "group"),
            "texto_indicacao": T(o, "indicationText"), "texto_contraindicacao": T(o, "contraindicationText"),
            "texto_esclarecimento": T(o, "clarifyingText")} for o in root.iter("observation")]
    write_out(d, "cdsi_observacoes_condicoes", obs, list(obs[0]))
    doses = []
    for n in sorted(z.namelist()):
        if "/XML/AntigenSupportingData-" not in n or not n.endswith(".xml"): continue
        ar = ET.fromstring(z.read(n))
        antigeno = re.sub(r"^.*AntigenSupportingData-\s*|-508\.xml$", "", n)
        for s in ar.findall("series"):
            for sd in s.findall("seriesDose"):
                iv = sd.find("interval")
                doses.append({
                    "antigeno": antigeno, "serie": T(s, "seriesName"), "tipo_serie": T(s, "seriesType"),
                    "doenca_alvo": T(s, "targetDisease"), "grupo_vacinal": T(s, "vaccineGroup"),
                    "serie_padrao": T(s, "selectSeries/defaultSeries"), "sexo_exigido": T(s, "requiredGender"),
                    "indicacoes": [f'{T(i, "observationCode/code")}:{T(i, "observationCode/text")}' for i in s.findall("indication") if T(i, "observationCode/code")],
                    "dose": T(sd, "doseNumber"),
                    "idade_minima_absoluta": T(sd, "age/absMinAge"), "idade_minima": T(sd, "age/minAge"),
                    "idade_recomendada_inicio": T(sd, "age/earliestRecAge"), "idade_recomendada_limite": T(sd, "age/latestRecAge"),
                    "idade_maxima": T(sd, "age/maxAge"),
                    "intervalo_minimo": T(iv, "minInt") if iv is not None else "",
                    "intervalo_recomendado": T(iv, "earliestRecInt") if iv is not None else "",
                    "vacinas_preferenciais": sorted({T(v, "vaccineType") + " (CVX " + T(v, "cvx") + ")" for v in sd.findall("preferableVaccine")}),
                    "dose_recorrente": T(sd, "recurringDose"),
                })
    write_out(d, "cdsi_esquemas_doses_acip", doses, list(doses[0]))

    # Coberturas vacinais da OMS (GHO/WUENIC) foram retiradas a pedido do usuário.


# =====================================================================
# Nutrição: TACO (Brasil) + USDA FoodData Central (SR Legacy e Foundation)
# =====================================================================
TACO_BASE = "https://raw.githubusercontent.com/brolesi/taco/main/data/processed/"
FDC = {"sr_legacy": "https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_sr_legacy_food_csv_2018-04.zip",
       "foundation": "https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_foundation_food_csv_2026-04-30.zip"}

def fetch_nutricao():
    d = BASE / "nutricao"; raw = d / "raw"
    for f in ["taco/taco_composicao", "taco/taco_acidos_graxos", "taco/taco_aminoacidos", "pof/pof_medidas_caseiras"]:
        p = download(TACO_BASE + f + ".csv", raw / (f.split("/")[1] + ".csv"))
        rows = read_csv_text(p.read_text(encoding="utf-8"), delimiter=",")
        write_out(d, f.split("/")[1], rows, list(rows[0]))

    for nome, url in FDC.items():
        zp = download(url, raw / Path(url).name)
        z = zipfile.ZipFile(zp)
        rd = lambda fn: read_csv_text(z.read([n for n in z.namelist() if n.endswith("/" + fn)][0]).decode("utf-8-sig"), ",")
        cats = {c["id"]: c["description"] for c in rd("food_category.csv")}
        nutr = {n["id"]: n for n in rd("nutrient.csv")}
        keep = {r["fdc_id"] for r in rd("foundation_food.csv")} if nome == "foundation" else None
        foods = {}
        for f in rd("food.csv"):
            if keep is not None and f["fdc_id"] not in keep: continue
            foods[f["fdc_id"]] = {"fdc_id": f["fdc_id"], "descricao": f["description"], "tipo_dado": f["data_type"],
                                  "categoria": cats.get(f.get("food_category_id", ""), f.get("food_category_id", "")),
                                  "data_publicacao": f.get("publication_date", "")}
        long = []
        for fn in rd("food_nutrient.csv"):
            if fn["fdc_id"] not in foods or not fn.get("amount"): continue
            n = nutr.get(fn["nutrient_id"], {})
            long.append({"fdc_id": fn["fdc_id"], "nutriente_id": fn["nutrient_id"], "nutriente": n.get("name", ""),
                         "unidade": n.get("unit_name", ""), "quantidade_por_100g": float(fn["amount"])})
        write_out(d, f"usda_{nome}_alimentos", list(foods.values()), ["fdc_id", "descricao", "tipo_dado", "categoria", "data_publicacao"])
        write_out(d, f"usda_{nome}_nutrientes", long, ["fdc_id", "nutriente_id", "nutriente", "unidade", "quantidade_por_100g"])


# =====================================================================
# Medicamentos: Anvisa (registrados) + openFDA (NDC e desabastecimento)
# =====================================================================
def fetch_medicamentos():
    d = BASE / "medicamentos"; raw = d / "raw"
    p = download("https://dados.anvisa.gov.br/dados/DADOS_ABERTOS_MEDICAMENTOS.csv", raw / "DADOS_ABERTOS_MEDICAMENTOS.csv")
    rows = read_csv_text(p.read_bytes().decode("latin-1"))
    write_out(d, "anvisa_medicamentos_registrados", rows, list(rows[0]))

    zp = download("https://download.open.fda.gov/drug/ndc/drug-ndc-0001-of-0001.json.zip", raw / "drug-ndc.json.zip")
    rows = []
    for r in openfda_json(zp):
        o = r.get("openfda", {})
        rows.append({"product_ndc": r.get("product_ndc"), "generic_name": r.get("generic_name"), "brand_name": r.get("brand_name"),
                     "labeler_name": r.get("labeler_name"), "product_type": r.get("product_type"), "dosage_form": r.get("dosage_form"),
                     "route": j(r.get("route")),
                     "active_ingredients": j([f'{a.get("name")} {a.get("strength", "")}'.strip() for a in r.get("active_ingredients", [])]),
                     "pharm_class": j(r.get("pharm_class")), "marketing_category": r.get("marketing_category"),
                     "application_number": r.get("application_number"), "dea_schedule": r.get("dea_schedule"),
                     "marketing_start_date": r.get("marketing_start_date"), "listing_expiration_date": r.get("listing_expiration_date"),
                     "rxcui": j(o.get("rxcui")), "unii": j(o.get("unii")), "num_embalagens": len(r.get("packaging", []))})
    write_out(d, "fda_ndc_produtos", rows, list(rows[0]))

    zp = download("https://download.open.fda.gov/drug/shortages/drug-shortages-0001-of-0001.json.zip", raw / "drug-shortages.json.zip")
    rows = [{"generic_name": r.get("generic_name"), "presentation": r.get("presentation"), "dosage_form": r.get("dosage_form"),
             "status": r.get("status"), "availability": r.get("availability"), "therapeutic_category": j(r.get("therapeutic_category")),
             "company_name": r.get("company_name"), "package_ndc": r.get("package_ndc"), "shortage_reason": r.get("shortage_reason"),
             "related_info": r.get("related_info"), "initial_posting_date": r.get("initial_posting_date"),
             "update_date": r.get("update_date"), "update_type": r.get("update_type")} for r in openfda_json(zp)]
    write_out(d, "fda_desabastecimento", rows, list(rows[0]))


# =====================================================================
# MeSH (NLM) - descritores
# =====================================================================
MESH_YEAR = 2026

def fetch_mesh():
    d = BASE / "mesh"; raw = d / "raw"
    gz = download(f"https://nlmpubs.nlm.nih.gov/projects/mesh/MESH_FILES/xmlmesh/desc{MESH_YEAR}.gz", raw / f"desc{MESH_YEAR}.gz")
    rows = []
    with gzip.open(gz) as f:
        for ev, e in ET.iterparse(f):
            if e.tag != "DescriptorRecord": continue
            terms, notes = [], ""
            for c in e.iter("Concept"):
                if c.get("PreferredConceptYN") == "Y":
                    notes = (c.findtext("ScopeNote") or "").strip()
                terms += [t.findtext("String") for t in c.iter("Term")]
            nome = e.findtext("DescriptorName/String")
            trees = [t.text for t in e.findall("TreeNumberList/TreeNumber")]
            rows.append({"ui": e.findtext("DescriptorUI"), "nome": nome, "arvores": trees,
                         "categorias": sorted({t[0] for t in trees}), "nota_escopo": notes,
                         "termos_entrada": [t for t in dict.fromkeys(terms) if t != nome],
                         "data_introducao": "-".join(filter(None, [e.findtext("DateIntroduced/Year"), e.findtext("DateIntroduced/Month"), e.findtext("DateIntroduced/Day")])),
                         "ultima_atualizacao": "-".join(filter(None, [e.findtext("LastUpdated/Year"), e.findtext("LastUpdated/Month"), e.findtext("LastUpdated/Day")]))})
            e.clear()
    fields = list(rows[0])
    write_out(d, "mesh_descritores", rows, fields)
    write_out(d, "mesh_doencas_categoria_C", [r for r in rows if "C" in r["categorias"]], fields)


# =====================================================================
# Sepse: recorte de CID-10, CID-11, MedlinePlus e MeSH + critérios Sepsis-3
# (rode depois dos outros tópicos; usa os arquivos já gerados)
# =====================================================================
SEPSE_RE = re.compile(r"seps|sépt|septic|septicemi|bacteri?emi|meningococcemi|choque s|toxic shock", re.I)
# exclui assepsia/antissépticos/organismos com "septica" no nome
SEPSE_EXCL = re.compile(r"assep|asep|asép|antis+[eé]p|gallisepticum|clostridium septicum|anti-s[eé]p|antisep|bronchiseptica|meningoseptica|septisol|isopropyl|water pollution", re.I)
sep_ok = lambda t: bool(SEPSE_RE.search(t)) and not SEPSE_EXCL.search(t)

def fetch_sepse():
    d = BASE / "sepse"
    load = lambda p: _json.loads((BASE / p).read_text(encoding="utf-8")) if (BASE / p).exists() else []
    sub = load("cid10/subcategorias.json")
    c10 = [r for r in sub if sep_ok(r["descricao"]) or r["categoria"] in ("A40", "A41", "P36", "O85", "R65")]
    write_out(d, "sepse_cid10", c10, list(sub[0]) if sub else ["codigo"])
    c11all = load("icd11/cid11_mms_completa.json")
    c11 = [r for r in c11all if sep_ok(r["titulo_en"] + " " + r["titulo_pt"])]
    write_out(d, "sepse_cid11", c11, list(c11all[0]) if c11all else ["codigo"])
    mp = load("medlineplus/health_topics_todos.json")
    mps = [r for r in mp if sep_ok(r["titulo"] + " " + " ".join(r["tambem_chamado"]) + " " + " ".join(r["ver_tambem_termos"])) or re.search(r"sepsis", r["titulo"], re.I)]
    write_out(d, "sepse_medlineplus", mps, list(mp[0]) if mp else ["id"])
    ms = load("mesh/mesh_descritores.json")
    mss = [r for r in ms if sep_ok(r["nome"])]
    write_out(d, "sepse_mesh", mss, list(ms[0]) if ms else ["ui"])
    # Critérios Sepsis-3 (qSOFA e SOFA): copiados de criterios_sepsis3.json, mantido à mão (ver README)
    crit = BASE / "sepse" / "criterios_sepsis3.json"
    if crit.exists():
        c = _json.loads(crit.read_text(encoding="utf-8"))
        rows = [{"escore": "SOFA", "sistema": s["sistema"], "variavel": s["variavel"], "pontos": p["pontos"], "criterio": p["criterio"]}
                for s in c["sofa"]["sistemas"] for p in s["pontuacao"]]
        rows += [{"escore": "qSOFA", "sistema": "", "variavel": q["variavel"], "pontos": 1, "criterio": q["criterio"]} for q in c["qsofa"]["itens"]]
        write_out(d, "criterios_sofa_qsofa", rows, ["escore", "sistema", "variavel", "pontos", "criterio"])



# =====================================================================
# Rodada 3: medicamentos (CMED), vacinal Brasil, epidemiológico, suprimentos,
# ferimentos, protocolos, sinais vitais
# =====================================================================
MS_API = "https://apidadosabertos.saude.gov.br"
CATMAT_API = "https://dadosabertos.compras.gov.br/modulo-material"

def ms_api(path, max_records=1000, page=1000, extra=""):
    """Baixa registros da API de Dados Abertos do Ministério da Saúde (DEMAS), paginando até max_records."""
    out, off = [], 0
    while len(out) < max_records:
        url = f"{MS_API}/{path}?limit={page}&offset={off}{extra}"
        d = _json.loads(get(url, timeout=180))
        key = [k for k in d if isinstance(d[k], list)][0]
        rows = d[key]
        out += rows
        if len(rows) < page: break
        off += page
    return out[:max_records]


def flat_rows(rows):
    fields = []
    for r in rows:
        for k in r:
            if k not in fields: fields.append(k)
    return [{k: r.get(k) for k in fields} for r in rows], fields


def save_api(d, name, rows):
    (d / "raw").mkdir(parents=True, exist_ok=True)
    (d / "raw" / f"{name}.json").write_text(_json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    rows, fields = flat_rows(rows)
    if rows: write_out(d, name, rows, fields)
    else: print(f"  {name}: 0 registros")


def fetch_medicamentos_cmed():
    d = BASE / "medicamentos"; raw = d / "raw"
    p = download("https://dados.anvisa.gov.br/dados/TA_PRECO_MEDICAMENTO.csv", raw / "TA_PRECO_MEDICAMENTO.csv")
    txt = p.read_bytes().decode("utf-8-sig", "replace")
    rows = read_csv_text(txt)
    write_out(d, "anvisa_cmed_precos_medicamentos", rows, list(rows[0]))


def fetch_vacinal_brasil():
    d = BASE / "vacinal_brasil"
    # Microdados de doses aplicadas são enormes (centenas de milhões de linhas/ano): só AMOSTRA.
    save_api(d, "pni_doses_aplicadas_2026_amostra", ms_api("vacinacao/doses-aplicadas-pni-2026", 5000))
    save_api(d, "esavi_eventos_adversos_vacinacao_amostra", ms_api("vacinacao/esavi", 5000))
    save_api(d, "sies_insumos_estrategicos_amostra", ms_api("vacinacao/sistema-de-informacao-de-insumos-estrategicos", 5000))
    save_api(d, "sesai_cobertura_vacinal_indigena", ms_api("saude-indigena/sesai-cobertura-vacinal", 20000))


def fetch_notificacao_compulsoria():
    """Extrai a tabela do Anexo I da Portaria GM/MS 11.211/2026 (lista nacional de notificação compulsória)."""
    d = BASE / "epidemiologico"; raw = d / "raw"
    url = "https://bvsms.saude.gov.br/bvs/saudelegis/gm/2026/prt11211_14_05_2026.html"
    p = download(url, raw / "portaria_gm_ms_11211_2026.html")
    b = p.read_bytes()
    try: h = b.decode("utf-8")
    except UnicodeDecodeError: h = b.decode("latin-1")
    from html.parser import HTMLParser
    class TP(HTMLParser):
        def __init__(s): super().__init__(); s.tables=[]; s.cell=None; s.row=None
        def handle_starttag(s, t, a):
            if t == "table": s.tables.append([])
            elif t == "tr" and s.tables: s.row = []
            elif t in ("td", "th") and s.row is not None: s.cell = []
        def handle_endtag(s, t):
            if t in ("td", "th") and s.cell is not None and s.row is not None:
                s.row.append(re.sub(r"\s+", " ", "".join(s.cell)).strip()); s.cell = None
            elif t == "tr" and s.row is not None and s.tables:
                s.tables[-1].append(s.row); s.row = None
        def handle_data(s, x):
            if s.cell is not None: s.cell.append(x)
    tp = TP(); tp.feed(h)
    tab = max(tp.tables, key=len)
    rows, num = [], ""
    for r in tab:
        if len(r) < 2 or not any(r): continue
        if r[0].isdigit(): num = r[0]
        elif r[0] and not r[0].isdigit() and len(r) >= 5 and r[1] == "": pass
        txt = r[1] if r[0].isdigit() or r[0] == "" else r[0]
        flags = r[2:6] if r[0].isdigit() or r[0] == "" else r[1:5]
        if not txt or txt.upper().startswith("DOENÇA OU AGRAVO") or txt in ("MS", "SES", "SMS", "Nº", "&nbsp;"): continue
        flags += [""] * (4 - len(flags))
        rows.append({"numero": num, "doenca_ou_agravo": txt, "imediata_ms": flags[0].upper() == "X",
                     "imediata_ses": flags[1].upper() == "X", "imediata_sms": flags[2].upper() == "X",
                     "semanal": flags[3].upper() == "X", "fonte": "Portaria GM/MS nº 11.211/2026, Anexo I", "url": url})
    write_out(d, "lista_notificacao_compulsoria_2026", rows, list(rows[0]))


GHO_BRASIL = ["WHOSIS_000001", "WHOSIS_000015", "MDG_0000000001", "MDG_0000000007", "MDG_0000000026",
              "NCDMORT3070", "MDG_0000000020", "NCD_BMI_30A", "SA_0000001688"]

def fetch_epidemiologico():
    d = BASE / "epidemiologico"; raw = d / "raw"
    try: fetch_notificacao_compulsoria()
    except Exception as e: print("  ERRO notificação compulsória:", e)
    save_api(d, "sinan_dengue_2026_amostra", ms_api("arboviroses/dengue", 5000, extra="&nu_ano=2026"))
    save_api(d, "sinan_chikungunya_2026_amostra", ms_api("arboviroses/chikungunya", 3000, extra="&nu_ano=2026"))
    save_api(d, "sinan_zika_2026_amostra", ms_api("arboviroses/zikavirus", 3000, extra="&nu_ano=2026"))
    save_api(d, "sim_mortalidade_amostra", ms_api("vigilancia-e-meio-ambiente/sistema-de-informacao-sobre-mortalidade", 5000))
    # SINASC: em 10/10/2026 o endpoint da API retornava lista vazia ({"sinasc": []}); não salvo.
    save_api(d, "srag_2019_2026_amostra", ms_api("vigilancia-e-meio-ambiente/srag-2019-2026", 5000))
    save_api(d, "mpox_amostra", ms_api("vigilancia-e-meio-ambiente/mpox", 5000))
    for nome, path in (("febre_amarela_epizootias", "arboviroses/febre-amarela-epzootias"),
                       ("febre_amarela_humanos_primatas", "arboviroses/febre-amarela-humanos-primatas-nao-humanos")):
        try: save_api(d, nome, ms_api(path, 20000))
        except Exception as e: print(f"  ERRO {nome}: {e}")
    # OMS GHO, indicadores não vacinais, só Brasil
    names = {}
    try:
        names = {x["IndicatorCode"]: x["IndicatorName"] for x in _json.loads(get("https://ghoapi.azureedge.net/api/Indicator", 180))["value"]}
    except Exception as e: print("  GHO Indicator falhou:", e)
    rows = []
    for c in GHO_BRASIL:
        try:
            data = get(f"https://ghoapi.azureedge.net/api/{c}?$filter=SpatialDim%20eq%20%27BRA%27", 180)
        except Exception as e:
            print(f"  pulando GHO {c}: {e}"); continue
        (raw / "gho").mkdir(parents=True, exist_ok=True); (raw / "gho" / f"{c}_BRA.json").write_bytes(data)
        for v in _json.loads(data)["value"]:
            rows.append({"indicador": c, "indicador_nome": names.get(c, ""), "ano": v.get("TimeDim"), "sexo": v.get("Dim1"),
                         "valor": v.get("NumericValue"), "valor_texto": v.get("Value"), "limite_inferior": v.get("Low"), "limite_superior": v.get("High")})
    if rows: write_out(d, "oms_gho_indicadores_brasil", rows, list(rows[0]))


SUPRIMENTO_RE = re.compile(r"seringa|agulha|luva|curativ|gaze|atadura|bandag|esparadrapo|fita adesiva|compressa|cateter intravenoso|scalp|lanceta|dressing|syringe|needle|glove|bandage|gauze", re.I)

def fetch_suprimentos():
    d = BASE / "suprimentos"; raw = d / "raw"
    def cat(classe):
        out, pg = [], 1
        while True:
            r = _json.loads(get(f"{CATMAT_API}/4_consultarItemMaterial?pagina={pg}&tamanhoPagina=500&codigoClasse={classe}", 180))
            out += r["resultado"]
            if r.get("paginasRestantes", 0) <= 0: break
            pg += 1
        return out
    allitems = []
    for c in (6510, 6515, 6530, 6532):
        items = cat(c); print(f"  CATMAT classe {c}: {len(items)} itens"); allitems += items
    (raw).mkdir(parents=True, exist_ok=True)
    (raw / "catmat_classes_6510_6515_6530_6532.json").write_text(_json.dumps(allitems, ensure_ascii=False), encoding="utf-8")
    rows, fields = flat_rows(allitems)
    write_out(d, "catmat_itens_classes_6510_6515_6530_6532", rows, fields)
    filt = [r for r in rows if SUPRIMENTO_RE.search((r.get("descricaoItem") or "") + " " + (r.get("nomePdm") or ""))]
    write_out(d, "catmat_seringas_agulhas_luvas_curativos", filt, fields)
    an = load_json_local("dispositivos/anvisa_produtos_saude_registrados.json")
    fa = [r for r in an if SUPRIMENTO_RE.search(r["nome_tecnico"] + " " + r["nome_comercial"])]
    write_out(d, "anvisa_registros_seringas_agulhas_luvas_curativos", fa, list(an[0]))
    fd = load_json_local("dispositivos/fda_classificacao_dispositivos.json")
    ff = [r for r in fd if SUPRIMENTO_RE.search(r["device_name"])]
    write_out(d, "fda_classificacao_seringas_agulhas_luvas_curativos", ff, list(fd[0]))


def load_json_local(p):
    f = BASE / p
    return _json.loads(f.read_text(encoding="utf-8")) if f.exists() else []


FERIDA_PT = re.compile(r"ferimento|ferida|úlcera|ulcera|queimadura|corrosão|lacera|escoria|abrasão|mordedura|deiscência|gangrena|necrose|esmagamento|amputação traumática|lesão por pressão|decúbito", re.I)
FERIDA_EN = re.compile(r"wound|ulcer|burn|laceration|abrasion|bite|dehiscence|gangrene|necrosis|crush|traumatic amputation|pressure injur|decubitus", re.I)

def fetch_ferimentos():
    d = BASE / "ferimentos"
    sub = load_json_local("cid10/subcategorias.json")
    c10 = [r for r in sub if FERIDA_PT.search(r["descricao"])]
    write_out(d, "ferimentos_cid10", c10, list(sub[0]))
    c11 = [r for r in load_json_local("icd11/cid11_mms_completa.json") if r["capitulo"] != "X" and FERIDA_EN.search(r["titulo_en"])]
    write_out(d, "ferimentos_cid11", c11, list(c11[0]))
    ms = load_json_local("mesh/mesh_descritores.json")
    msf = [r for r in ms if any(t.startswith("C26") for t in r["arvores"]) or re.search(r"ulcer|wound|bandage|dressing|burn", r["nome"], re.I)]
    write_out(d, "ferimentos_mesh", msf, list(ms[0]))
    an = load_json_local("dispositivos/anvisa_produtos_saude_registrados.json")
    from collections import Counter
    cnt = Counter(r["nome_tecnico"] for r in an if re.search(r"curativ|cobertura", r["nome_tecnico"], re.I))
    rows = [{"nome_tecnico_anvisa": k, "registros": v} for k, v in cnt.most_common()]
    write_out(d, "tipos_curativos_anvisa_nome_tecnico", rows, ["nome_tecnico_anvisa", "registros"])
    cm = load_json_local("suprimentos/catmat_itens_classes_6510_6515_6530_6532.json")
    cnt2 = Counter(r.get("nomePdm") for r in cm if r.get("codigoClasse") == 6510)
    rows = [{"pdm_catmat": k, "itens": v} for k, v in cnt2.most_common()]
    if rows: write_out(d, "tipos_curativos_catmat_pdm_classe_6510", rows, ["pdm_catmat", "itens"])


PROTOCOLOS = [
    ("Manual de Normas e Procedimentos para Vacinação (2ª ed. rev.)", "Ministério da Saúde", "2024", "vacinação",
     "https://www.gov.br/saude/pt-br/centrais-de-conteudo/publicacoes/guias-e-manuais/2024/manual-de-normas-e-procedimentos-para-vacinacao.pdf"),
    ("Instrução Normativa do Calendário Nacional de Vacinação 2026", "Ministério da Saúde", "2026", "vacinação",
     "https://www.gov.br/saude/pt-br/vacinacao/publicacoes/instrucao-normativa-que-instrui-o-calendario-nacional-de-vacinacao-2026.pdf"),
    ("Protocolo para Cirurgia Segura (PNSP)", "MS/Anvisa/Fiocruz", "2013", "segurança do paciente",
     "https://bibliotecadigital.anvisa.gov.br/jspui/bitstream/anvisa/1771/1/MS_ANVISA_FIOCRUZ_Protocolo%20para%20cirurgia%20segura_09.07.2013.pdf"),
    ("Protocolo para a Prática de Higiene das Mãos em Serviços de Saúde (PNSP)", "MS/Anvisa/Fiocruz", "2013", "segurança do paciente",
     "https://bibliotecadigital.anvisa.gov.br/jspui/bitstream/anvisa/1772/1/MS_ANVISA_FIOCRUZ_Protocolo%20para%20a%20pr%c3%a1tica%20de%20higiene%20das%20m%c3%a3os%20em%20servi%c3%a7os%20de%20sa%c3%bade_09.07.2013.pdf"),
    ("Protocolo de Identificação do Paciente (PNSP)", "MS/Anvisa/Fiocruz", "2013", "segurança do paciente",
     "https://bibliotecadigital.anvisa.gov.br/jspui/bitstream/anvisa/1778/1/MS_ANVISA_FIOCRUZ_Protocolo%20de%20identifica%c3%a7%c3%a3o%20do%20paciente_2013.pdf"),
    ("Portaria GM-MS 2.095/2013 com anexos: Protocolo de Prevencao de Ulcera por Pressao e Protocolo para Cirurgia Segura", "Ministério da Saúde (cópia SESA-PR)", "2013", "segurança do paciente",
     "https://www.saude.pr.gov.br/sites/default/arquivos_restritos/files/documento/2020-05/portaria_2095_2013.pdf"),
    ("Resolução Cofen nº 736/2024 - Processo de Enfermagem", "Cofen", "2024", "processo de enfermagem",
     "https://www.cofen.gov.br/wp-content/uploads/2024/01/Resolucao-736-2024.pdf"),
    ("Protocolos da Atenção Básica: Saúde das Mulheres", "Ministério da Saúde", "2016", "atenção básica",
     "https://bvsms.saude.gov.br/bvs/publicacoes/protocolos_atencao_basica_saude_mulheres.pdf"),
    ("Guidelines for the Prevention of Intravascular Catheter-Related Infections", "CDC/HICPAC", "2011", "controle de infecção",
     "https://www.cdc.gov/infection-control/media/pdfs/guideline-bsi-h.pdf"),
    ("Guideline for Isolation Precautions", "CDC/HICPAC", "2007", "controle de infecção",
     "https://www.cdc.gov/infection-control/media/pdfs/guideline-isolation-h.pdf"),
    ("WHO Guidelines on Hand Hygiene in Health Care", "OMS", "2009", "controle de infecção",
     "https://iris.who.int/bitstream/handle/10665/44102/9789241597906_eng.pdf"),
    ("WHO Surgical Safety Checklist", "OMS", "2009", "segurança do paciente",
     "https://iris.who.int/bitstream/handle/10665/44186/9789241598590_eng_Checklist.pdf"),
]

def fetch_protocolos():
    d = BASE / "protocolos_enfermagem"; pdfdir = d / "raw" / "pdfs"; pdfdir.mkdir(parents=True, exist_ok=True)
    idx = []
    for titulo, fonte, ano, tema, url in PROTOCOLOS:
        import unicodedata
        asc = unicodedata.normalize("NFKD", titulo).encode("ascii", "ignore").decode()
        fn = re.sub(r"[^A-Za-z0-9]+", "_", asc)[:80].strip("_") + ".pdf"
        st, size = "ok", 0
        try:
            b = get(url, timeout=300)
            if not b.startswith(b"%PDF"): raise ValueError("resposta não é PDF")
            (pdfdir / fn).write_bytes(b); size = len(b)
        except Exception as e:
            st = f"falhou: {e}"; fn = ""
        print(f"  {st[:40]} {titulo[:60]}")
        idx.append({"titulo": titulo, "fonte": fonte, "ano": ano, "tema": tema, "url": url, "arquivo": fn, "tamanho_bytes": size, "status": st})
    write_out(d, "indice_protocolos", idx, list(idx[0]))
    save_api(d, "conitec_pcdt_situacao", ms_api("ciencia-tecnologia/dgits-controle-pcdt", 5000))
    save_api(d, "conitec_tecnologias_diretrizes", ms_api("ciencia-tecnologia/dgits-tecnologias-diretrizes", 5000))


FHIR_VITAIS = ["vitalsigns", "vitalspanel", "resprate", "heartrate", "oxygensat", "bodytemp", "bodyheight",
               "headcircum", "bodyweight", "bmi", "bp"]

def fetch_sinais_vitais():
    d = BASE / "sinais_vitais"; raw = d / "raw"
    rows = []
    for n in FHIR_VITAIS:
        p = download(f"https://hl7.org/fhir/R4/{n}.profile.json", raw / f"{n}.profile.json")
        sd = _json.loads(p.read_text(encoding="utf-8"))
        els = sd.get("snapshot", {}).get("element", [])
        units = [e["fixedCode"] for e in els if e.get("fixedCode") and e["id"].endswith("valueQuantity.code")]
        for e in els:
            if e.get("fixedCode") and e["id"].endswith(".code") and ".coding:" in e["id"] and "category" not in e["id"]:
                sysid = e["id"][:-5] + ".system"
                sysv = next((x.get("fixedUri", "") for x in els if x["id"] == sysid), "")
                rows.append({"perfil_fhir": n, "titulo": sd.get("title") or sd.get("name"), "elemento": e["id"],
                             "sistema": sysv, "codigo": e["fixedCode"], "unidades_ucum_perfil": ", ".join(dict.fromkeys(units)),
                             "descricao": (sd.get("description") or "")[:300], "url_perfil": sd.get("url")})
    write_out(d, "fhir_r4_sinais_vitais_codigos_loinc", rows, list(rows[0]))
    crit = d / "referencias_sinais_vitais_transcritas.json"
    if crit.exists():
        c = _json.loads(crit.read_text(encoding="utf-8"))
        r1 = [{"escore": "NEWS2", "parametro": p["parametro"], "faixa": f["faixa"], "pontos": f["pontos"]}
              for p in c["news2"]["parametros"] for f in p["faixas"]]
        write_out(d, "news2_pontuacao_transcrita", r1, ["escore", "parametro", "faixa", "pontos"])
        r2 = [dict(x, fonte=c["pressao_arterial_brasil_2020"]["fonte"]) for x in c["pressao_arterial_brasil_2020"]["classificacao"]]
        write_out(d, "classificacao_pressao_arterial_dbha2020_transcrita", r2, list(r2[0]))

TOPICOS = {"cid10": fetch_cid10, "medlineplus": fetch_medlineplus, "icd11": fetch_icd11,
           "dispositivos": fetch_dispositivos, "vacinas": fetch_vacinas, "nutricao": fetch_nutricao,
           "medicamentos": fetch_medicamentos, "mesh": fetch_mesh, "sepse": fetch_sepse,
           "medicamentos_cmed": fetch_medicamentos_cmed, "vacinal_brasil": fetch_vacinal_brasil,
           "epidemiologico": fetch_epidemiologico, "suprimentos": fetch_suprimentos, "ferimentos": fetch_ferimentos,
           "protocolos": fetch_protocolos, "sinais_vitais": fetch_sinais_vitais}

if __name__ == "__main__":
    escolhidos = sys.argv[1:] or list(TOPICOS)
    for t in escolhidos:
        print(f"== {t}")
        try:
            TOPICOS[t]()
        except Exception as e:
            print(f"  ERRO em {t}: {e}")
    print("OK")
