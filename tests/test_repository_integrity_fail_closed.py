"""Regression tests for canonical integrity gate; no database or external services."""
import importlib.util
import json
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "scripts" / "verify_repository_integrity.py"
spec = importlib.util.spec_from_file_location("ce_integrity", MODULE)
integrity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(integrity)


def seed(root):
    sources = root / "contracts" / "fontes"
    policies = root / "contracts" / "policies"
    sources.mkdir(parents=True)
    policies.mkdir(parents=True)
    (sources / "example.json").write_text(json.dumps({
        "fonte_slug": "example",
        "source_contract": "contracts/fontes/example.json",
        "kernel_policy_id": "KERNEL-POLICY-001",
        "parser": "packages/cli/parsers/example.py",
    }), encoding="utf-8")
    (policies / "KERNEL-POLICY-001.json").write_text(json.dumps({
        "id": "KERNEL-POLICY-001",
        "source_contract": "contracts/fontes/example.json",
        "validators": ["required"],
    }), encoding="utf-8")
    return sources


def test_missing_parser_remains_hold(tmp_path):
    seed(tmp_path)
    result = integrity.inspect(tmp_path)
    assert result["structural_pass"] is True
    assert result["strict_pass"] is False
    assert any(f["code"] == "MISSING_PARSER" for f in result["findings"])


def test_legacy_source_directory_fails_closed(tmp_path):
    seed(tmp_path)
    (tmp_path / "contracts" / "fonts").mkdir()
    result = integrity.inspect(tmp_path)
    assert result["structural_pass"] is False
    assert any(f["code"] == "LEGACY_SOURCE_DIR" and f["severity"] == "error" for f in result["findings"])


def test_resolved_parser_does_not_bypass_namespace_hold(tmp_path):
    seed(tmp_path)
    parser = tmp_path / "packages" / "cli" / "parsers" / "example.py"
    parser.parent.mkdir(parents=True)
    parser.write_text("def parse(x): return x\n", encoding="utf-8")
    main = tmp_path / "packages" / "cli" / "main.py"
    main.write_text("from kernel.core import run\n", encoding="utf-8")
    result = integrity.inspect(tmp_path)
    assert result["structural_pass"] is True
    assert result["strict_pass"] is False
    assert not any(f["code"] == "MISSING_PARSER" for f in result["findings"])
    assert any(f["code"] == "PACKAGE_IMPORT_NAMESPACE" for f in result["findings"])
