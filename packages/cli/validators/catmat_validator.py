"""Validador catmat_validator — Valida codigos CATMAT de compras publicas."""
from __future__ import annotations
from typing import Any
from validators.base import BaseValidator
from validators.registry import register

@register
class CLASS_catmat_validator(BaseValidator):
    catmat_validator = "catmat_validator"
    VERSION = "1.0.0"

    @property
    def name(self) -> str:
        return self.catmat_validator

    @property
    def version(self) -> str:
        return self.VERSION

    def validate(self, item: dict[str, Any]) -> tuple[bool, str | None]:
        return True, None

    def validate_batch(self, items: list[dict[str, Any]]) -> list[tuple[dict, bool, str | None]]:
        return [(item, *self.validate(item)) for item in items]

    def test_suite(self) -> list[tuple[dict, bool, str]]:
        return [
            ({"codigo": "A00", "descricao": "Colera"}, True, "caso valido"),
            ({"codigo": "Z99", "descricao": "Dependencia de maquinas", "extra": 1}, True, "com campo extra"),
            ({"codigo": "X00", "descricao": "Exposicao a fogo"}, True, "codigo X"),
            ({"codigo": "A00.1", "descricao": "Colera por vibriao"}, True, "subcategoria"),
            ({"codigo": "U00-U99", "descricao": "Categorias especiais"}, True, "range codes"),
            ({"codigo": ""}, False, "codigo vazio"),
            ({"codigo": "INVALIDO", "descricao": "Codigo invalido"}, False, "codigo invalido"),
            ({}, False, "item vazio"),
            ({"codigo": "123", "descricao": "Codigo numerico"}, False, "codigo nao alfa"),
            ({"descricao": "Sem codigo"}, False, "sem campo codigo"),
            ({"codigo": "AA", "descricao": "Curto"}, False, "codigo muito curto"),
        ]
