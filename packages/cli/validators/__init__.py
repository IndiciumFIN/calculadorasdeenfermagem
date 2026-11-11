"""Validators - registry centralizado de validadores do Kernel.

Usa auto-registro via @register decorator. Cada módulo validador se registra
quando importado. O import de 'validators' como pacote dispara todos.
"""
import importlib

_base = importlib.import_module("validators.base")
_registry = importlib.import_module("validators.registry")
BaseValidator = _base.BaseValidator
register = _registry.register
get_validator = _registry.get_validator
list_validators = _registry.list_validators
VALIDATORS = _registry.VALIDATORS

# Dispara auto-registro sem importar packages.cli (evita ciclo).
for _module_name in (
    "sha256_validator",
    "cid10_validator",
    "cid11_validator",
    "mesh_validator",
    "cvx_validator",
    "schema_validator",
    "loinc_validator",
    "ncm_validator",
    "catmat_validator",
    "human_review_validator",
):
    importlib.import_module(f"validators.{_module_name}")

__all__ = [
    "BaseValidator",
    "register",
    "get_validator",
    "list_validators",
    "VALIDATORS",
]
