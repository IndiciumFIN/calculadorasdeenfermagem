"""Validators - registry centralizado de validadores do Kernel."""
from packages.cli.validators.base import BaseValidator
from packages.cli.validators.registry import register, get_validator, list_validators
from packages.schemas.invariantes import AtomoBlindado

# Registra todos os validadores
from packages.cli.validators.sha256_validator import (
    Sha256Validator, NormAtomIdValidator, TextoLengthValidator,
    UrlValidator, AtomoSchemaValidator
)
from packages.cli.validators.cid10_validator import cid10_validator
from packages.cli.validators.cid11_validator import cid11_validator
from packages.cli.validators.mesh_validator import mesh_validator
from packages.cli.validators.cvx_validator import cvx_validator
from packages.cli.validators.schema_validator import schema_validator
from packages.cli.validators.loinc_validator import loinc_validator
from packages.cli.validators.ncm_validator import ncm_validator
from packages.cli.validators.catmat_validator import catmat_validator
from packages.cli.validators.human_review_validator import human_review_validator

__all__ = [
    "BaseValidator", "register", "get_validator", "list_validators",
    "AtomoBlindado",
]
