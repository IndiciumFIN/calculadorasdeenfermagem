#!/usr/bin/env python3
"""verificar.py 1.1.0 - verifica a saída do atomizar.py: chaves exatas, sha256 de cada átomo, ordenação, JSON canônico, LF,
atom_id único (no tema e global), fonte_url não vazia, sha256 dos arquivos = MANIFESTO, tamanho < 100 MB,
conferência de contagens com os CSVs limpos (arquivos JSON sem CSV: linhas_csv = null, diferença tem de estar explicada).
Novidades 1.1.0: (a) marca de transcrição manual coerente (fonte_nome com '[TRANSCRITO MANUALMENTE]' <=> tipo_entidade
'*_manualmente' <=> fonte_versao com 'transcrição manual' <=> descricao_literal com '## aviso'); (b) toda referência cruzada
aponta para átomo existente (cid10 -> cid10:<código>, cid11 -> icd11:<código>, mesh -> mesh:<UI>, medlineplus -> atom_id),
verificado só para os vocabulários presentes na pasta."""
import json, hashlib, sys, collections
from pathlib import Path
KEYS = {"atom_id","tema","tipo_entidade","codigo","titulo","sinonimos","descricao_literal","fonte_nome","fonte_url",
        "fonte_versao","data_extracao","referencias_cruzadas","sha256"}
REFK = {"cid10","cid11","mesh","medlineplus"}
MARCA = "[TRANSCRITO MANUALMENTE]"
canon = lambda o: json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",",":"))
base = Path(sys.argv[1] if len(sys.argv) > 1 else "/workspace/doencas_atomizado")
glob_ids = set(); ok_all = True; refs_por_tema = {}
for man_p in sorted(base.glob("*/MANIFESTO.json")):
    tema = man_p.parent.name; man = json.loads(man_p.read_text(encoding="utf-8"))
    errs = collections.Counter(); n = 0; ids = set(); por_tipo = collections.Counter(); refs = []; ntransc = 0
    for f in man["arquivos"]:
        p = man_p.parent / f["arquivo"]; data = p.read_bytes()
        if hashlib.sha256(data).hexdigest() != f["sha256"]: errs["sha256_arquivo"] += 1
        if len(data) >= 100_000_000: errs["arquivo>=100MB"] += 1
        if b"\r" in data: errs["CR"] += 1
        prev = None; cnt = 0
        for line in data.decode("utf-8").split("\n")[:-1]:
            a = json.loads(line); cnt += 1; n += 1
            if canon(a) != line: errs["nao_canonico"] += 1
            if set(a) != KEYS: errs["chaves"] += 1
            if set(a["referencias_cruzadas"]) != REFK: errs["refs_chaves"] += 1
            if not isinstance(a["sinonimos"], list): errs["sinonimos"] += 1
            s = a.pop("sha256")
            if hashlib.sha256(canon(a).encode()).hexdigest() != s: errs["sha256_atomo"] += 1
            if a["atom_id"] != f"{a['tema']}:{a['codigo']}" or a["tema"] != tema: errs["atom_id_formato"] += 1
            if a["tipo_entidade"] != f["tipo_entidade"]: errs["tipo_arquivo"] += 1
            if not a["fonte_url"]: errs["fonte_url_vazia"] += 1
            if not a["data_extracao"]: errs["data_vazia"] += 1
            if prev is not None and a["atom_id"] <= prev: errs["ordenacao"] += 1
            prev = a["atom_id"]
            if a["atom_id"] in ids: errs["atom_id_dup"] += 1
            ids.add(a["atom_id"]); por_tipo[a["tipo_entidade"]] += 1
            if a["atom_id"] in glob_ids: errs["atom_id_dup_global"] += 1
            marcas = (a["fonte_nome"].startswith(MARCA), a["tipo_entidade"].endswith("_manualmente"),
                      "transcrição manual" in a["fonte_versao"], "\n## aviso" in a["descricao_literal"])
            if any(marcas) and not all(marcas): errs["marca_transcricao_incoerente"] += 1
            ntransc += all(marcas)
            for k, vs in a["referencias_cruzadas"].items():
                for v in vs: refs.append((a["atom_id"], k, v))
        if cnt != f["atomos"]: errs["contagem_arquivo"] += 1
    glob_ids |= ids; refs_por_tema[tema] = refs
    if dict(por_tipo) != man["atomos_por_tipo_entidade"] or n != man["total_atomos"]: errs["contagem_manifesto"] += 1
    conf = man["conferencia_contagens"]
    if sum(c["atomos"] for c in conf) != n: errs["soma_conferencia"] += 1
    if [c for c in conf if not c["confere"] and not c["explicacao"]]: errs["diferenca_sem_explicacao"] += 1
    if [e for e in man["entradas"] if e["linhas_csv"] is not None and e["linhas_csv"] != e["registros_json"]]: errs["csv_vs_json"] += 1
    status = "OK" if not errs else "FALHOU " + dict(errs).__repr__()
    ok_all &= not errs
    print(f"{tema}: {n} átomos, {len(man['arquivos'])} arquivos, conferências: "
          f"{sum(c['confere'] for c in conf)} iguais / {sum(not c['confere'] for c in conf)} com diferença explicada, "
          f"transcritos manualmente: {ntransc} -> {status}")
# referências cruzadas -> átomo existente
alvo = {"cid10": lambda v: f"cid10:{v}", "cid11": lambda v: f"icd11:{v}", "mesh": lambda v: f"mesh:{v}", "medlineplus": lambda v: v}
pasta = {"cid10": "cid10", "cid11": "icd11", "mesh": "mesh", "medlineplus": "medlineplus"}
temas = set(refs_por_tema)
for tema, refs in sorted(refs_por_tema.items()):
    ruins = [(i, k, v) for i, k, v in refs if pasta[k] in temas and alvo[k](v) not in glob_ids]
    nchk = sum(1 for _, k, _ in refs if pasta[k] in temas)
    if ruins: ok_all = False
    if refs: print(f"  refs {tema}: {nchk} referências conferidas contra átomos existentes, {len(ruins)} quebradas {ruins[:3] if ruins else ''}")
print("TUDO OK" if ok_all else "HÁ FALHAS")
