"""Fail-closed technical admission for NCOS/CKO; never authorizes clinical release.

The legacy repository checker only verifies that referenced parser paths exist.
This gate layers contract AST validation, active negative-validator self-tests,
policy registry checks, and unconditional-true validator detection on top.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Any

from scripts.verify_repository_integrity import inspect as inspect_repository
from scripts.cko_parser_contract_audit import inspect as inspect_parser_contracts


def is_unconditional_true_validator(path: Path) -> bool:
    """Detect the specific unsafe stub: validate() returns (True, None)."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, UnicodeError, OSError):
        return True
    for klass in (n for n in tree.body if isinstance(n, ast.ClassDef)):
        for fn in (n for n in klass.body if isinstance(n, ast.FunctionDef) and n.name == "validate"):
            executable = [s for s in fn.body if not isinstance(s, ast.Expr)
                          or not isinstance(s.value, ast.Constant)]
            if len(executable) == 1 and isinstance(executable[0], ast.Return):
                val = executable[0].value
                if isinstance(val, ast.Tuple) and len(val.elts) == 2:
                    first, second = val.elts
                    if (isinstance(first, ast.Constant) and first.value is True
                            and isinstance(second, ast.Constant) and second.value is None):
                        return True
    return False


def evaluate(*, repository: dict[str, Any], parser_ast: dict[str, Any],
             validator_holds: dict[str, str], missing_policy_validators: list[str],
             unconditional_true: list[str]) -> dict[str, Any]:
    """Decision logic is pure and testable with negative fixtures."""
    findings = []
    if not repository.get("strict_pass"):
        findings.append({"code": "REPOSITORY_STRICT_INCOMPLETE",
                         "count": repository.get("counts", {}).get("pending", -1)})
    if not parser_ast.get("static_pass"):
        findings.append({"code": "PARSER_CONTRACT_AST_INVALID",
                         "count": len(parser_ast.get("problems", []))})
    if parser_ast.get("missing_parsers"):
        findings.append({"code": "SOURCE_PARSERS_MISSING",
                         "count": len(parser_ast["missing_parsers"])})
    for name in sorted(set(unconditional_true)):
        findings.append({"code": "UNCONDITIONAL_VALIDATOR_APPROVAL", "path": name})
    for name, reason in sorted(validator_holds.items()):
        findings.append({"code": "VALIDATOR_HOLD", "name": name, "reason": reason})
    for name in sorted(set(missing_policy_validators)):
        findings.append({"code": "UNIMPLEMENTED_POLICY_VALIDATOR", "name": name})
    return {
        "schema": "CE-CKO-TECHNICAL-ADMISSION-1.0.0",
        "mode": "READ_ONLY",
        "repository_structural_pass": bool(repository.get("structural_pass")),
        "repository_strict_pass": bool(repository.get("strict_pass")),
        "source_contract_ast_pass": bool(parser_ast.get("static_pass")),
        "missing_parsers": len(parser_ast.get("missing_parsers", [])),
        "validator_holds": len(validator_holds),
        "unimplemented_policy_validators": len(set(missing_policy_validators)),
        "unconditional_true_validators": len(set(unconditional_true)),
        "findings": findings,
        "technical_admission_pass": len(findings) == 0,
        "clinical_release_allowed": False,
        "editorial_publication_allowed": False,
    }


def inspect(root: Path) -> dict[str, Any]:
    """Read-only snapshot, invoking self-tests on repository-owned validators."""
    root = Path(root)
    repo = inspect_repository(root)
    parser_ast = inspect_parser_contracts(root)
    unconditional_true = []
    validator_dir = root / "packages/cli/validators"
    for path in sorted(validator_dir.glob("*_validator.py")):
        if is_unconditional_true_validator(path):
            unconditional_true.append(path.relative_to(root).as_posix())

    # Self-tests are not proof of clinical validity, but failed tests forbid
    # technical admission. Import only repository-owned Kernel modules.
    from packages.cli.kernel import core
    core._ensure_validators()
    holds = dict(core.VALIDATOR_HOLDS)
    active = set(core.VALIDATORS)

    missing = []
    for file in sorted((root / "contracts/policies").glob("KERNEL-POLICY-*.json")):
        try:
            p = json.loads(file.read_text(encoding="utf-8"))
            for name in p.get("validators", []):
                if not isinstance(name, str) or name not in active:
                    missing.append(str(name))
        except (OSError, ValueError, TypeError):
            missing.append(f"invalid-policy:{file.name}")

    result = evaluate(repository=repo, parser_ast=parser_ast,
                      validator_holds=holds, missing_policy_validators=missing,
                      unconditional_true=unconditional_true)
    result["repository_findings"] = repo.get("findings", [])
    result["parser_ast_problems"] = parser_ast.get("problems", [])
    result["active_validators"] = sorted(active)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = inspect(args.root)
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(output)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    return 0 if report["technical_admission_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
