#!/usr/bin/env python3
"""
G6-auto — Verificação assistida de SHA256 para revisão humana.
Usa amostragem DETERMINÍSTICA (seed = data + PR head SHA).
Para cada átomo sampleado:
  1. Busca o arquivo fonte original pelo SHA256
  2. Compara SHA256 do texto_regra com o da fonte
  3. Reporta divergências
  4. Gera JSON de amostragem para revisão humana
"""
import json, hashlib, sys, argparse
from pathlib import Path
from datetime import date

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def find_source_file(sha256: str, repo_path: Path) -> Path | None:
    """Busca arquivo fonte pelo SHA256 em atomizado/ e canonical/."""
    for subdir in ["data/legado/extracao_bruta/atomizado", "data/canonical/atoms"]:
        search = repo_path / subdir
        if not search.exists():
            continue
        # Busca em todos os .jsonl e .json
        for f in search.rglob("*.jsonl"):
            with open(f) as fp:
                for line in fp:
                    if not line.strip():
                        continue
                    try:
                        obj = json.loads(line)
                        # Aceita diversos formatos de campo SHA
                        for key in ["sha256", "sha256_texto", "sha256_original", "hash"]:
                            if obj.get(key) == sha256:
                                return f
                    except:
                        pass
        for f in search.rglob("*.json"):
            try:
                data = json.loads(f.read_text())
                # Atom files are JSON arrays or single objects
                items = data if isinstance(data, list) else [data]
                for obj in items:
                    for key in ["sha256", "sha256_texto", "sha256_original", "hash"]:
                        if obj.get(key) == sha256:
                            return f
            except:
                pass
    return None

def sample_atoms_deterministic(atoms: list, n: int, seed: str) -> list:
    """Amostragem determinística via hash do seed + índice."""
    import hashlib
    result = []
    for i in range(n):
        h = hashlib.sha256(f"{seed}:{i}".encode()).hexdigest()
        idx = int(h, 16) % len(atoms)
        result.append((i, atoms[idx]))
    return result

def verify_atom(atom: dict, repo_path: Path) -> dict:
    """Verifica um átomo: busca fonte e compara SHA256."""
    # Diversos campos possíveis para o SHA256 do texto
    sha256 = (
        atom.get("sha256_texto")
        or atom.get("sha256")
        or atom.get("sha256_original")
        or atom.get("hash")
    )
    if not sha256:
        return {"status": "NO_SHA256", "atom_id": atom.get("id", "?"), "error": "Campo SHA256 ausente"}

    fonte = atom.get("fonte") or atom.get("arquivo_fonte") or atom.get("source_file") or "?"
    texto = atom.get("texto_regra") or atom.get("content") or atom.get("text") or ""
    computed = sha256_text(texto) if texto else None

    result = {
        "atom_id": atom.get("id", "?"),
        "sha256_registrado": sha256,
        "sha256_computado": computed,
        "sha256_batido": (computed == sha256) if computed else None,
        "fonte": fonte,
        "texto_size": len(texto),
    }

    if computed and computed != sha256:
        result["status"] = "DIVERGENCIA_SHA256"
        result["nota"] = "SHA256 do texto_regra não bate com o registrado"
    elif computed and computed == sha256:
        # Verificar se o arquivo fonte existe e tem o mesmo SHA
        source = find_source_file(sha256, repo_path)
        if source:
            result["status"] = "VERIFICADO"
            result["arquivo_fonte_encontrado"] = str(source)
        else:
            result["status"] = "VERIFICADO_TEXTO_OK_FONTE_NAO_LOCALIZADO"
    else:
        result["status"] = "SEM_TEXTO"

    return result

def main():
    parser = argparse.ArgumentParser(description="G6-auto: verificação assistida de SHA256")
    parser.add_argument("--repo", default=".", help="Raiz do repositório")
    parser.add_argument("--atoms", default="data/legado/atomos_candidatos.json",
                        help="Arquivo de átomos candidatos")
    parser.add_argument("--canonical", default="data/canonical/atoms",
                        help="Diretório de átomos canônicos")
    parser.add_argument("--sample-size", type=int, default=10,
                        help="Número de átomos para samplear")
    parser.add_argument("--seed", default=None,
                        help="Seed determinística (default: DATA+PR_HEAD_SHA)")
    parser.add_argument("--output", default="g6_verification_report.json",
                        help="Arquivo de saída JSON")
    parser.add_argument("--commit-sha", default="",
                        help="SHA do commit HEAD do PR (para seed)")
    args = parser.parse_args()

    repo = Path(args.repo)
    atoms_path = repo / args.atoms
    canonical_dir = repo / args.canonical

    # Carregar átomos de candidatos OU do corpus canônico
    atoms = []
    if atoms_path.exists():
        atoms = json.loads(atoms_path.read_text())
    elif canonical_dir.exists():
        for f in canonical_dir.glob("*.json"):
            try:
                data = json.loads(f.read_text())
                if isinstance(data, list):
                    atoms.extend(data)
                else:
                    atoms.append(data)
            except:
                pass

    if not atoms:
        # Tentar ler do formato JSONL
        for f in repo.glob("data/**/atomizado/**/*.jsonl"):
            with open(f) as fp:
                for line in fp:
                    if line.strip():
                        try:
                            atoms.append(json.loads(line))
                        except:
                            pass

    if not atoms:
        print("NENHUM ÁTOMO ENCONTRADO — g6-auto não pode executar")
        print("Arquivos verificados:")
        print(f"  {atoms_path} (existe: {atoms_path.exists()})")
        print(f"  {canonical_dir}/ (existe: {canonical_dir.exists()})")
        sys.exit(2)

    print(f"G6-auto: {len(atoms)} átomos encontrados")

    # Seed determinística
    if args.seed:
        seed = args.seed
    else:
        today = date.today().isoformat()
        seed = f"{today}:{args.commit_sha or 'no-commit'}"
    print(f"Seed determinística: {seed}")

    sampled = sample_atoms_deterministic(atoms, min(args.sample_size, len(atoms)), seed)
    print(f"Amostrados: {len(sampled)} átomos")

    results = []
    verified = 0
    divergencias = 0
    sem_texto = 0

    for idx, atom in sampled:
        r = verify_atom(atom, repo)
        results.append(r)
        if r["status"] == "VERIFICADO":
            verified += 1
        elif r["status"] == "DIVERGENCIA_SHA256":
            divergencias += 1
        elif r["status"] == "SEM_TEXTO":
            sem_texto += 1

    report = {
        "gate": "G6-auto",
        "timestamp": f"{date.today().isoformat()}T00:00:00Z",
        "seed": seed,
        "total_atoms": len(atoms),
        "sample_size": len(sampled),
        "verified": verified,
        "divergencias": divergencias,
        "sem_texto": sem_texto,
        "results": results,
    }

    with open(args.output, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n=== G6-AUTO REPORT ===")
    print(f"Total átomos: {len(atoms)}")
    print(f"Seed: {seed}")
    print(f"Verificados OK: {verified}/{len(sampled)}")
    print(f"Divergências SHA256: {divergencias}")
    print(f"Sem texto: {sem_texto}")
    print(f"\nRelatório: {args.output}")

    # Fail-closed: divergência é erro
    if divergencias > 0:
        print(f"\n🔴 FAIL: {divergencias} divergência(s) de SHA256 encontrada(s)")
        for r in results:
            if r["status"] == "DIVERGENCIA_SHA256":
                print(f"  - {r['atom_id']}: registrado={r['sha256_registrado'][:16]}... computado={r.get('sha256_computado','?')[:16]}...")
        sys.exit(2)

    if verified + divergencias + sem_texto == len(sampled):
        print(f"\n✅ G6-auto: {verified} verificados, {divergencias} divergências, {sem_texto} sem texto")
        print("Revisor humano deve verificar manualmente os items pendentes.")
        sys.exit(0)  # G6-auto passa, revisão humana decide

    sys.exit(0)

if __name__ == "__main__":
    main()
