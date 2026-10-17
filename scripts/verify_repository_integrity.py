#!/usr/bin/env python3
"""Verificação determinística, somente leitura, dos contratos canônicos Git.

Modos:
  structural: compatibilidade de nomes, vínculos e JSONs (gates deste PR).
  strict: acrescenta existência de parsers e resolução dos imports dos módulos
          críticos (requer saneamento antes de declarar a main homologada).
Não acessa Drive/Supabase e nunca altera arquivos.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

POLICY_NAME = re.compile(r"^KERNEL-POLICY-[0-9]{3}$")
BROKEN_IMPORT = re.compile(r"(?m)^\s*from\s+(kernel|validators)(?:\.|\s+import)")
SCAN_IMPORTS = (
    "packages/cli/main.py",
    "packages/cli/kernel/__init__.py",
    "packages/cli/kernel/cli.py",
    "packages/cli/kernel/core.py",
    "packages/cli/validators/__init__.py",
    "packages/cli/validators/registry.py",
)


def inspect(root: Path) -> dict:
    """Produz observações ordenadas sem mutar o filesystem."""
    root = Path(root)
    findings: list[dict[str, str]] = []

    def add(code: str, severity: str, path: str, detail: str) -> None:
        findings.append({"code": code, "severity": severity, "path": path, "detail": detail})

    legacy = root / "contracts/fonts"
    if legacy.exists():
        add("LEGACY_SOURCE_DIR", "error", "contracts/fonts", "Usar apenas contracts/fontes/")
    sources_dir = root / "contracts/fontes"
    policies_dir = root / "contracts/policies"
    sources: dict[str, dict] = {}
    policies: dict[str, dict] = {}

    if not sources_dir.is_dir() or not policies_dir.is_dir():
        add("MISSING_REGISTRY", "error", "contracts", "Faltam fontes ou políticas")
    else:
        source_files = sorted(sources_dir.glob("*.json"))
        policy_files = sorted(policies_dir.glob("*.json"))
        if not source_files or not policy_files:
            add("EMPTY_REGISTRY", "error", "contracts", "Registry não pode estar vazio")
        for file in source_files:
            rel = file.relative_to(root).as_posix()
            try:
                data = json.loads(file.read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                add("INVALID_SOURCE_JSON", "error", rel, type(exc).__name__)
                continue
            slug = file.stem
            if not re.fullmatch(r"[a-z0-9]+(?:_[a-z0-9]+)*", slug):
                add("INVALID_SOURCE_SLUG", "error", rel, slug)
            if not isinstance(data, dict) or data.get("fonte_slug") != slug:
                add("SOURCE_SLUG_MISMATCH", "error", rel, "fonte_slug != nome do arquivo")
                continue
            if data.get("source_contract") != rel:
                add("SOURCE_SELF_REFERENCE", "error", rel, "source_contract incorreto")
            if slug in sources:
                add("DUPLICATE_SOURCE", "error", rel, slug)
            sources[slug] = data
            parser = data.get("parser")
            if not isinstance(parser, str) or not (root / parser).is_file():
                add("MISSING_PARSER", "pending", rel, f"Parser indisponível: {parser}")
        for file in policy_files:
            rel = file.relative_to(root).as_posix()
            try:
                data = json.loads(file.read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                add("INVALID_POLICY_JSON", "error", rel, type(exc).__name__)
                continue
            if not isinstance(data, dict) or not POLICY_NAME.fullmatch(file.stem):
                add("INVALID_POLICY_NAME", "error", rel, "Esperado KERNEL-POLICY-NNN.json")
                continue
            identifier = data.get("id")
            if identifier != file.stem:
                add("POLICY_ID_MISMATCH", "error", rel, f"id = {identifier}")
            if identifier in policies:
                add("DUPLICATE_POLICY_ID", "error", rel, str(identifier))
            policies[identifier] = data
            link = data.get("source_contract")
            if not isinstance(link, str) or not link.startswith("contracts/fontes/") or not (root / link).is_file():
                add("POLICY_SOURCE_MISSING", "error", rel, f"source_contract = {link}")
                continue
            source_slug = Path(link).stem
            if sources.get(source_slug, {}).get("kernel_policy_id") != identifier:
                add("POLICY_SOURCE_LINK_MISMATCH", "error", rel, source_slug)
            if not isinstance(data.get("validators"), list) or not data["validators"]:
                add("POLICY_NO_VALIDATORS", "error", rel, "Lista de validadores ausente")
        for slug, data in sorted(sources.items()):
            if data.get("kernel_policy_id") not in policies:
                add("SOURCE_POLICY_MISSING", "error", f"contracts/fontes/{slug}.json",
                    str(data.get("kernel_policy_id")))

    for rel in SCAN_IMPORTS:
        f = root / rel
        if f.exists():
            try:
                code = f.read_text(encoding="utf-8")
            except OSError:
                add("UNREADABLE_CODE", "error", rel, "Arquivo ilegível")
                continue
            if BROKEN_IMPORT.search(code):
                add("PACKAGE_IMPORT_NAMESPACE", "pending", rel,
                    "Import top-level kernel/validators requer validação para python -m packages.cli.main")

    findings.sort(key=lambda r: (r["severity"], r["code"], r["path"]))
    counts = {severity: sum(f["severity"] == severity for f in findings)
              for severity in ("error", "pending")}
    return {
        "schema": "CE-CANONICAL-INTEGRITY-1.0.0",
        "mode": "READ_ONLY",
        "source_contract_count": len(sources),
        "kernel_policy_count": len(policies),
        "counts": counts,
        "structural_pass": counts["error"] == 0,
        "strict_pass": counts["error"] == 0 and counts["pending"] == 0,
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--output", type=Path, help="JSON local de evidências, opcional")
    args = parser.parse_args()
    result = inspect(args.root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                               encoding="utf-8")
    return 0 if (result["strict_pass"] if args.strict else result["structural_pass"]) else 2


if __name__ == "__main__":
    raise SystemExit(main())
