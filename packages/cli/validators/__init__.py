"""Validators - registry centralizado de validadores do Kernel."""
from validators.base import BaseValidator
from validators.registry import register, get_validator, list_validators
from packages.schemas.invariantes import AtomoBlindado

# Registra todos os validadores
from validators.sha256_validator import (
    Sha256Validator, NormAtomIdValidator, TextoLengthValidator,
    UrlValidator, AtomoSchemaValidator
)
from validators.cid10_validator import cid10_validator
from validators.cid11_validator import cid11_validator
from validators.mesh_validator import mesh_validator
from validators.cvx_validator import cvx_validator
from validators.schema_validator import schema_validator
from validators.loinc_validator import loinc_validator
from validators.ncm_validator import ncm_validator
from validators.catmat_validator import catmat_validator
from validators.human_review_validator import human_review_validator

__all__ = [
    "BaseValidator", "register", "get_validator", "list_validators",
    "AtomoBlindado",
]
