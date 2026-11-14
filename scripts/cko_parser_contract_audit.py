"""Static-only contract audit for CKO source parsers (no code execution).

This supplement is NOT an ingestion test, a license review or a clinical gate.
For source-specific candidate modules under packages/cli/parsers, check:
- source path, pinned contract identity and parser version
- a real parse entrypoint with explicit provenance arguments
- presence of explicit ParseHold rejection and publication HOLD literals
Missing parser modules remain pending; other adapter families stay unassessed.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Any

CANDIDATE_PREFIX = "packages/cli/parsers/"


def _declared_string(tree: ast.Module, field: str):
    for stmt in tree.body:
        if isinstance(stmt, (ast.Assign, ast.AnnAssign)):
            targets = stmt.targets if isinstance(stmt, ast.Assign) else [stmt.target]
            if any(isinstance(t, ast.Name) and t.id == field for t in targets):
                val = stmt.value
                return val.value if isinstance(val, ast.Constant) and isinstance(val.value, str) else None
    return None


def _raise_hold(node: ast.AST) -> bool:
    for child in ast.walk(node):
        if isinstance(child, ast.Raise) and isinstance(child.exc, ast.Call):
            if isinstance(child.exc.func, ast.Name) and child.exc.func.id == "ParseHold":
                return True
    return False


def _has_false_publication(node: ast.AST) -> bool:
    for item in ast.walk(node):
        if not isinstance(item, ast.Dict):
            continue
        for key, val in zip(item.keys, item.values):
            if (isinstance(key, ast.Constant) and key.value in ("publication_allowed", "release_allowed")
                    and isinstance(val, ast.Constant) and val.value is False):
                return True
    return False


def inspect(root: Path) -> dict[str, Any]:
    root = Path(root)
    problems: list[dict[str, str]] = []
    checked = []
    missing = []
    legacy = []
    contracts = sorted((root / "contracts/fontes").glob("*.json"))
    for contract_file in contracts:
        rel = contract_file.relative_to(root).as_posix()
        try:
            doc = json.loads(contract_file.read_text(encoding="utf-8"))
            path = doc.get("parser")
        except (OSError, ValueError):
            problems.append({"contract": rel, "code": "INVALID_CONTRACT"})
            continue
        if not isinstance(path, str) or ".." in Path(path).parts or not path.startswith("packages/cli/"):
            problems.append({"contract": rel, "code": "UNSAFE_PARSER_PATH"})
            continue
        module = root / path
        if not module.is_file():
            missing.append(rel)
            continue
        if not path.startswith(CANDIDATE_PREFIX):
            legacy.append(rel)
            continue
        try:
            tree = ast.parse(module.read_text(encoding="utf-8"), filename=path)
        except (SyntaxError, UnicodeError, OSError):
            problems.append({"contract": rel, "code": "INVALID_PARSER_AST"})
            continue
        required = {
            "SOURCE_CONTRACT": rel,
            "PARSER_API_VERSION": doc.get("parser_version"),
        }
        for field, value in required.items():
            if _declared_string(tree, field) != value:
                problems.append({"contract": rel, "code": f"MISMATCH_{field}"})
        entrypoints = [x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == "parse"]
        if len(entrypoints) != 1:
            problems.append({"contract": rel, "code": "MISSING_PARSE_ENTRYPOINT"})
            continue
        fn = entrypoints[0]
        args = {a.arg for a in fn.args.posonlyargs + fn.args.args + fn.args.kwonlyargs}
        if not {"raw", "source_id", "document_id"} <= args:
            problems.append({"contract": rel, "code": "MISSING_PROVENANCE_PARAMETERS"})
        if not any(isinstance(x, ast.ClassDef) and x.name == "ParseHold" for x in tree.body):
            problems.append({"contract": rel, "code": "MISSING_PARSE_HOLD_CLASS"})
        # Raise may live in a helper; accept at module level, but never as
        # sufficient proof of runtime behavior. Actual adversarial tests apply.
        if not _raise_hold(tree):
            problems.append({"contract": rel, "code": "NO_EXPLICIT_REJECTION"})
        if not _has_false_publication(tree):
            problems.append({"contract": rel, "code": "NO_STATIC_RELEASE_HOLD"})
        checked.append(rel)
    result = {
        "schema": "CE-CKO-PARSER-CONTRACT-AST-1.0.0",
        "mode": "READ_ONLY_STATIC_ONLY",
        "contracts": len(contracts),
        "candidate_parsers_checked": sorted(checked),
        "legacy_adapters_unassessed": sorted(legacy),
        "missing_parsers": sorted(missing),
        "problems": sorted(problems, key=lambda x: (x["contract"], x["code"])),
        "static_pass": not problems,
        "clinical_approval": False,
        "publication_allowed": False,
    }
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--output", type=Path)
    ap.add_argument("--fail-on-missing", action="store_true")
    args = ap.parse_args()
    report = inspect(args.root)
    blob = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(blob)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(blob, encoding="utf-8")
    return 0 if report["static_pass"] and (
        not args.fail_on_missing or not report["missing_parsers"]
    ) else 2


if __name__ == "__main__":
    raise SystemExit(main())
