"""Validators - registry centralizado de validadores do Kernel.

Usa auto-registro via @register decorator. Cada módulo validador se registra
quando importado. O import de 'validators' como pacote dispara todos.
"""
from packages.cli.validators.base import BaseValidator
from packages.cli.validators.registry import register, get_validator, list_validators, VALIDATORS
from packages.schemas.invariantes import AtomoBlindado

# Dispara auto-registro de TODOS os validadores (um por módulo)
from packages.cli import validators as _validator_pkg  # noqa: F401

__all__ = [
    "BaseValidator",
    "register",
    "get_validator",
    "list_validators",
    "VALIDATORS",
    "AtomoBlindado",
]
