"""Regressões determinísticas do gate fail-closed; sem acesso ao banco ou rede."""
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from packages.cli.kernel import core


@pytest.fixture
def kernel(monkeypatch):
    monkeypatch.setattr(core, "_ensure_validators", lambda: None)
    instance = object.__new__(core.Kernel)
    return instance


@pytest.mark.parametrize("validator,expected", [
    (object(), 2),
    (SimpleNamespace(run_tests=None), 2),
    (SimpleNamespace(run_tests=lambda: False), 2),
    (SimpleNamespace(run_tests=lambda: 1), 2),
    (SimpleNamespace(run_tests=lambda: None), 2),
    (SimpleNamespace(run_tests=lambda: True), 0),
])
def test_gate_validator_contract(kernel, monkeypatch, tmp_path, validator, expected):
    policy = SimpleNamespace(validators=["dummy_validator"], atoms_output=str(tmp_path / "atoms"))
    monkeypatch.setattr(core, "get_policy", lambda _: policy)
    monkeypatch.setattr(core, "VALIDATORS", {"dummy_validator": validator})
    assert kernel.gate("TEST-POLICY") == expected
    assert (tmp_path / "atoms").exists() is (expected == 0)


def test_gate_exception_fails_closed(kernel, monkeypatch, tmp_path):
    def explode():
        raise RuntimeError("synthetic test exception")
    policy = SimpleNamespace(validators=["dummy_validator"], atoms_output=str(tmp_path / "atoms"))
    monkeypatch.setattr(core, "get_policy", lambda _: policy)
    monkeypatch.setattr(core, "VALIDATORS", {"dummy_validator": SimpleNamespace(run_tests=explode)})
    assert kernel.gate("TEST-POLICY") == 2
    assert not (tmp_path / "atoms").exists()


@pytest.mark.parametrize("validators,registered", [
    ([], {}),
    (["missing_validator"], {}),
])
def test_gate_missing_validators_fails_closed(kernel, monkeypatch, validators, registered):
    monkeypatch.setattr(core, "get_policy", lambda _: SimpleNamespace(validators=validators))
    monkeypatch.setattr(core, "VALIDATORS", registered)
    assert kernel.gate("TEST-POLICY") == 2


def test_gate_unknown_policy_fails_closed(kernel, monkeypatch):
    def missing(_):
        raise KeyError("missing")
    monkeypatch.setattr(core, "get_policy", missing)
    assert kernel.gate("MISSING") == 2
