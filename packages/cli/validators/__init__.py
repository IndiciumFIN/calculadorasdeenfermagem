"""Validators — registry centralizado. Importar o pacote registra os validadores."""
from __future__ import annotations

from packages.cli.validators.base import BaseValidator
from packages.cli.validators.registry import (
    VALIDATORS,
    get_validator,
    list_validators,
    register,
)
from packages.schemas.invariantes import AtomoBlindado

from . import catmat_validator as _catmat_validator
from . import cid10_validator as _cid10_validator
from . import cid11_validator as _cid11_validator
from . import cvx_validator as _cvx_validator
from . import human_review_validator as _human_review_validator
from . import loinc_validator as _loinc_validator
from . import mesh_validator as _mesh_validator
from . import ncm_validator as _ncm_validator
from . import schema_validator as _schema_validator
from . import sha256_validator as _sha256_validator

__all__ = [
    "AtomoBlindado",
    "BaseValidator",
    "VALIDATORS",
    "get_validator",
    "list_validators",
    "register",
]
