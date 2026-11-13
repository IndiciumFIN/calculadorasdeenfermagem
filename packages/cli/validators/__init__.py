"""Validators — registry centralizado de validadores do Kernel.

Usa auto-registro via @register decorator. Cada módulo validador se registra
quando importado. O import de `packages.cli.validators` dispara todos.
"""
from packages.cli.validators.base import BaseValidator
from packages.cli.validators.registry import (
    VALIDATORS,
    get_validator,
    list_validators,
    register,
)
from packages.schemas.invariantes import AtomoBlindado

# Import tardio: os módulos registram instâncias e não reimportam este pacote.
from packages.cli.validators import (  # noqa: E402, F401
    catmat_validator,
    cid10_validator,
    cid11_validator,
    cvx_validator,
    human_review_validator,
    loinc_validator,
    mesh_validator,
    ncm_validator,
    schema_validator,
    sha256_validator,
)

__all__ = [
    "BaseValidator",
    "register",
    "get_validator",
    "list_validators",
    "VALIDATORS",
    "AtomoBlindado",
]
