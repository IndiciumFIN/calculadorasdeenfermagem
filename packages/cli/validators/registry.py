"""Registry de validadores — registro centralizado."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from validators.base import BaseValidator

VALIDATORS: dict[str, BaseValidator] = {}


def register(cls: type["BaseValidator"]) -> type["BaseValidator"]:
    """Decorador: registra validador no registry global."""
    validator = cls()
    VALIDATORS[validator.name] = validator
    return cls


def get_validator(name: str) -> "BaseValidator":
    """Retorna validador por nome. Raise KeyError se não existir."""
    if name not in VALIDATORS:
        available = sorted(VALIDATORS.keys())
        raise KeyError(
            f"Validador '{name}' não registrado. "
            f"Disponíveis: {available}. "
            f"Importe o módulo do validador para registrá-lo."
        )
    return VALIDATORS[name]


def list_validators() -> list[str]:
    """Lista nomes de todos os validadores registrados."""
    return sorted(VALIDATORS.keys())
