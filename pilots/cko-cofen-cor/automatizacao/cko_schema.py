#!/usr/bin/env python3
"""cko_schema.py — Validador JSON Schema (subconjunto Draft 2020-12) sem dependencia.

Por que existe: o ambiente de execucao local nao alcanca PyPI, e o piloto precisa
validar os candidatos contra os contratos do anexo **offline**. Implementa apenas
as palavras-chave usadas pelos contratos do pacote:

  type, enum, const, required, properties, additionalProperties,
  pattern, minLength, maxLength, minimum, maximum,
  minItems, maxItems, uniqueItems, items

Fora desse subconjunto, a funcao `unsupported_keywords` lista o que seria
ignorado — o validador se declara incompleto em vez de fingir cobertura total.
"""
from __future__ import annotations

import re
from typing import Any

SUPPORTED = {
    "$schema", "$id", "title", "description", "type", "enum", "const",
    "required", "properties", "additionalProperties", "pattern", "minLength",
    "maxLength", "minimum", "maximum", "minItems", "maxItems", "uniqueItems",
    "items",
}

_TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "boolean": bool,
    "null": type(None),
}


def unsupported_keywords(schema: dict) -> list[str]:
    """Palavras-chave do schema que este validador NAO implementa.

    Percorre apenas posicoes de SCHEMA (nao de propriedade): dentro de
    `properties`, as chaves sao nomes de propriedade e nao palavras-chave.
    """
    out: list[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "properties" and isinstance(v, dict):
                    for sub in v.values():          # cada valor e um sub-schema
                        walk(sub)
                    continue
                if k in ("items", "additionalProperties") and isinstance(v, dict):
                    walk(v)
                    continue
                if k not in SUPPORTED and k not in ("$defs", "definitions"):
                    out.append(k)
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(schema)
    return sorted(set(out))


def _type_ok(value: Any, expected: str) -> bool:
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    cls = _TYPES.get(expected)
    if cls is None:
        return True
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "null":
        return value is None
    return isinstance(value, cls)


def validate(instance: Any, schema: dict, path: str = "$") -> list[str]:
    """Devolve lista de erros (vazia = conforme)."""
    errors: list[str] = []
    if not isinstance(schema, dict):
        return [f"{path}: schema nao e objeto"]

    if "type" in schema:
        expected = schema["type"]
        options = expected if isinstance(expected, list) else [expected]
        if not any(_type_ok(instance, opt) for opt in options):
            errors.append(f"{path}: tipo esperado {expected}, obtido {type(instance).__name__}")
            return errors

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: esperado const {schema['const']!r}, obtido {instance!r}")

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: valor {instance!r} fora do enum {schema['enum']}")

    if isinstance(instance, str):
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errors.append(f"{path}: '{instance}' nao casa com o padrao {schema['pattern']}")
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: comprimento {len(instance)} < minLength {schema['minLength']}")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            errors.append(f"{path}: comprimento {len(instance)} > maxLength {schema['maxLength']}")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: {instance} < minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: {instance} > maximum {schema['maximum']}")

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: {len(instance)} itens < minItems {schema['minItems']}")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"{path}: {len(instance)} itens > maxItems {schema['maxItems']}")
        if schema.get("uniqueItems"):
            seen: list[Any] = []
            for item in instance:
                if item in seen:
                    errors.append(f"{path}: itens duplicados (uniqueItems)")
                    break
                seen.append(item)
        if "items" in schema:
            for i, item in enumerate(instance):
                errors += validate(item, schema["items"], f"{path}[{i}]")

    if isinstance(instance, dict):
        for req in schema.get("required", []):
            if req not in instance:
                errors.append(f"{path}: obrigatorio ausente -> {req}")
        props = schema.get("properties", {})
        for key, sub in props.items():
            if key in instance:
                errors += validate(instance[key], sub, f"{path}.{key}")
        if schema.get("additionalProperties") is False:
            extra = sorted(set(instance) - set(props))
            for key in extra:
                errors.append(f"{path}: propriedade nao permitida -> {key}")
        elif isinstance(schema.get("additionalProperties"), dict):
            for key in sorted(set(instance) - set(props)):
                errors += validate(instance[key], schema["additionalProperties"],
                                   f"{path}.{key}")

    return errors
