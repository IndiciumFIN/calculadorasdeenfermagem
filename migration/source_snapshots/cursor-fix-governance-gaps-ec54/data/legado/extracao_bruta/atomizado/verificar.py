#!/usr/bin/env python3
"""Verifica a saída do atomizar.py: chaves exatas, sha256 de cada átomo, ordenação, JSON canônico, LF,
atom_id único (no tema e global), fonte_url não vazia, sha256 dos arquivos = MANIFESTO, tamanho < 100 MB,
e a conferência de contagens com os CSVs limpos."""
import json, hashlib, sys, collections
from pathlib import Path
KEYS = {"atom_id","tema","tipo_entidade","codigo","titulo","sinonimos","descricao_literal","fonte_nome","fonte_url",
        "fonte_versao","data_extracao","referencias_cruzadas","sha256"}
REFK = {"cid10","cid11","mesh","medlineplus"}
canon = lambda o: json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",",":"))
base = Path(sys.argv[1] if len(sys.argv) > 1 else "/workspace/doencas_atomizado")
glob_ids = set(); ok_all = True
for man_p in sorted(base.glob("*/MANIFESTO.json")):
    tema = man_p.parent.name; man = json.loads(man_p.read_text(encoding="utf-8"))
    errs = collections.Counter(); n = 0; ids = set(); por_tipo = collections.Counter()
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
        if cnt != f["atomos"]: errs["contagem_arquivo"] += 1
    glob_ids |= ids
    if dict(por_tipo) != man["atomos_por_tipo_entidade"] or n != man["total_atomos"]: errs["contagem_manifesto"] += 1
    conf = man["conferencia_contagens"]
    soma = sum(c["atomos"] for c in conf)
    if soma != n: errs["soma_conferencia"] += 1
    sem_expl = [c["arquivo_entrada"] for c in conf if not c["confere"] and not c["explicacao"]]
    if sem_expl: errs["diferenca_sem_explicacao"] += 1
    csvjson = [e["arquivo"] for e in man["entradas"] if e["linhas_csv"] != e["registros_json"]]
    if csvjson: errs["csv_vs_json"] += 1
    status = "OK" if not errs else "FALHOU " + dict(errs).__repr__()
    ok_all &= not errs
    print(f"{tema}: {n} átomos, {len(man['arquivos'])} arquivos, conferências: "
          f"{sum(c['confere'] for c in conf)} iguais / {sum(not c['confere'] for c in conf)} com diferença explicada -> {status}")
print("TUDO OK" if ok_all else "HÁ FALHAS")
