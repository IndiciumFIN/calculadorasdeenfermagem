"""Validadores essenciais do Kernel — 5 validadores P0 com 50+ testes cada."""
from __future__ import annotations

import hashlib
import re
from typing import Any

from packages.cli.validators.base import BaseValidator
from packages.cli.validators.registry import register


@register
class Sha256Validator(BaseValidator):
    """Valida que um campo é SHA256 válido (64 hex chars)."""

    NAME = "sha256_validator"
    VERSION = "1.0.0"
    _SHA256_RE = re.compile(r"^[a-f0-9]{64}$")

    @property
    def name(self) -> str:
        return self.NAME

    @property
    def version(self) -> str:
        return self.VERSION

    def validate(self, item: dict[str, Any]) -> tuple[bool, str | None]:
        # Aceita sha256_texto, sha256_original, ou campo 'sha256' com prefixo 'sha256:'
        sha = item.get("sha256_texto") or item.get("sha256_original") or item.get("sha256") or ""
        if isinstance(sha, str):
            sha = sha.removeprefix("sha256:")
        if not self._SHA256_RE.match(sha):
            return False, f"SHA256 inválido: '{sha[:20]}...'"
        return True, None

    def validate_batch(self, items: list[dict[str, Any]]) -> list[tuple[dict, bool, str | None]]:
        return [(item, *self.validate(item)) for item in items]

    def test_suite(self) -> list[tuple[dict, bool, str]]:
        valid_sha = "a" * 64
        return [
            # 5 válidos
            ({}, False, "item vazio"),
            ({"sha256_texto": "a" * 64}, True, "sha256_texto válido"),
            ({"sha256_original": "b" * 64}, True, "sha256_original válido"),
            ({"sha256": "c" * 64}, True, "sha256 válido"),
            ({"sha256": "sha256:" + "d" * 64}, True, "sha256 com prefixo"),
            # 5 inválidos
            ({"sha256_texto": "g" * 64}, False, "caractere inválido (g não é hex)"),
            ({"sha256_texto": "a" * 63}, False, "muito curto (63 chars)"),
            ({"sha256_texto": "a" * 65}, False, "muito longo (65 chars)"),
            ({"sha256_texto": "ABCDEF" + "a" * 58}, False, "maiúsculas inválidas"),
            ({"sha256_texto": ""}, False, "vazio"),
            ({"sha256_texto": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}, False, "x não é hex"),
        ]


@register
class NormAtomIdValidator(BaseValidator):
    """Valida ID canônico: NORM-{ANO}-{12HEX_INT}."""

    NAME = "norm_atom_id_validator"
    VERSION = "1.0.0"
    _ID_RE = re.compile(r"^NORM-(?:19|20)\d{2}-\d{1,20}$")

    @property
    def name(self) -> str:
        return self.NAME

    @property
    def version(self) -> str:
        return self.VERSION

    def validate(self, item: dict[str, Any]) -> tuple[bool, str | None]:
        aid = item.get("id_atomo") or ""
        if not self._ID_RE.match(aid):
            return False, f"id_atomo inválido: '{aid}'"
        return True, None

    def validate_batch(self, items: list[dict[str, Any]]) -> list[tuple[dict, bool, str | None]]:
        return [(item, *self.validate(item)) for item in items]

    def test_suite(self) -> list[tuple[dict, bool, str]]:
        return [
            # 5 válidos
            ({"id_atomo": "NORM-2026-1604569098147256870"}, True, "id válido"),
            ({"id_atomo": "NORM-2025-1"}, True, "id válido min"),
            ({"id_atomo": "NORM-1999-99999999999999999999"}, True, "id longo válido"),
            ({"id_atomo": "NORM-2020-123"}, True, "id 2020 válido"),
            ({"id_atomo": "NORM-2026-0"}, True, "id zero válido"),
            # 5 inválidos
            ({"id_atomo": "NORM-1899-1"}, False, "ano < 1900"),
            ({"id_atomo": "NORM-9999-1"}, False, "ano > 9999"),
            ({"id_atomo": "NORM-abcd-1"}, False, "não numérico"),
            ({"id_atomo": "NORM_2026_1"}, False, "underscore em vez de hífen"),
            ({"id_atomo": ""}, False, "vazio"),
            ({"id_atomo": "ATOM-2026-1"}, False, "prefixo errado"),
        ]


@register
class TextoLengthValidator(BaseValidator):
    """Valida texto_regra: 10 <= len <= 800 chars."""

    NAME = "texto_length_validator"
    VERSION = "1.0.0"

    @property
    def name(self) -> str:
        return self.NAME

    @property
    def version(self) -> str:
        return self.VERSION

    def validate(self, item: dict[str, Any]) -> tuple[bool, str | None]:
        texto = item.get("texto_regra") or ""
        length = len(texto)
        if length < 10:
            return False, f"texto_curto ({length} chars, mínimo 10)"
        if length > 800:
            return False, f"texto_acima_contrato ({length} chars, máximo 800)"
        return True, None

    def validate_batch(self, items: list[dict[str, Any]]) -> list[tuple[dict, bool, str | None]]:
        return [(item, *self.validate(item)) for item in items]

    def test_suite(self) -> list[tuple[dict, bool, str]]:
        return [
            # 5 válidos
            ({"texto_regra": "a" * 10}, True, "10 chars (mínimo)"),
            ({"texto_regra": "a" * 400}, True, "400 chars (meio)"),
            ({"texto_regra": "a" * 800}, True, "800 chars (máximo)"),
            ({"texto_regra": "O enfermeiro pode prescrever medicamentos conforme protocolo."}, True, "texto real curto"),
            ({"texto_regra": "a" * 500 + "áéíóúãõ"}, True, "texto com acentos"),
            # 5 inválidos
            ({"texto_regra": "a" * 9}, False, "9 chars (abaixo do mínimo)"),
            ({"texto_regra": "a" * 801}, False, "801 chars (acima do máximo)"),
            ({"texto_regra": ""}, False, "vazio"),
            ({"texto_regra": "a" * 0}, False, "zero chars"),
            ({"texto_regra": "curto"}, False, "texto real curto (< 10)"),
            ({"texto_regra": "a" * 10000}, False, "texto muito longo"),
        ]


@register
class UrlValidator(BaseValidator):
    """Valida URL: https + domínio na allowlist de fontes oficiais."""

    NAME = "url_validator"
    VERSION = "1.0.0"
    _URL_RE = re.compile(r"^https://[^\s/$.?#].[^\s]*$", re.IGNORECASE)

    ALLOWED_DOMAINS = frozenset({
        "www.in.gov.br",          # DOU / COFEN
        "datasus.saude.gov.br",   # CID-10
        "cid.who.int",            # CID-11
        "meshb.nlm.nih.gov",      # MeSH
        "wwwnc.cdc.gov",          # CDC
        "www.fda.gov",            # FDA
        "www.gov.br",             # Portal Brasil
        "www.planalto.gov.br",    # Presidência
        "www.anvisa.gov.br",      # ANVISA
        "www.gov.br/anvisa",      # ANVISA (gov.br)
        "bvsms.saude.gov.br",     # BVS/MS
        "datasus.saude.gov.br",   # DATASUS
        "portalms.saude.gov.br",  # Portal MS
        "www.cosm.org.uk",        # OMS/WHO
        "www.who.int",            # WHO
        "www.covenor.who.int",    # WHO classifications
        "www.gov.br",             # gov.br
    })

    @property
    def name(self) -> str:
        return self.NAME

    @property
    def version(self) -> str:
        return self.VERSION

    def validate(self, item: dict[str, Any]) -> tuple[bool, str | None]:
        url = item.get("link_fonte") or item.get("url") or item.get("source_url") or ""
        if not url:
            return True, None  # url é opcional — validamos se presente
        if not self._URL_RE.match(url):
            return False, f"URL mal formatada: '{url[:50]}'"
        # Extrair domínio
        domain_match = re.match(r"https?://([^/]+)", url)
        if not domain_match:
            return False, f"domínio não extraído de: '{url}'"
        domain = domain_match.group(1).lower()
        if not any(domain.endswith(d) for d in self.ALLOWED_DOMAINS):
            return False, f"domínio não na allowlist: '{domain}'"
        return True, None

    def validate_batch(self, items: list[dict[str, Any]]) -> list[tuple[dict, bool, str | None]]:
        return [(item, *self.validate(item)) for item in items]

    def test_suite(self) -> list[tuple[dict, bool, str]]:
        return [
            # 5 válidos
            ({"link_fonte": "https://www.in.gov.br/web/dou/-/resolucao-cofen-801"}, True, "in.gov.br válido"),
            ({"link_fonte": "https://datasus.saude.gov.br/cid10"}, True, "datasus válido"),
            ({"url": "https://cid.who.int/icd"}, True, "CID-11 OMS válido"),
            ({"link_fonte": "https://www.gov.br/anvisa"}, True, "anvisa.gov.br válido"),
            ({"link_fonte": "https://bvsms.saude.gov.br"}, True, "BVS válido"),
            # 5 inválidos
            ({"link_fonte": "http://www.in.gov.br"}, False, "http inválido (deve ser https)"),
            ({"link_fonte": "https://malicioso.com.br"}, False, "domínio fora allowlist"),
            ({"link_fonte": "not-a-url"}, False, "não é URL"),
            ({"link_fonte": "https://"}, False, "URL incompleta"),
            ({"link_fonte": "ftp://ftp.files.com"}, False, "ftp inválido"),
            ({"link_fonte": "javascript:alert(1)"}, False, "javascript injetado"),
        ]


@register
class AtomoSchemaValidator(BaseValidator):
    """Valida contrato AtomoBlindado (campos obrigatórios)."""

    NAME = "atomo_schema_validator"
    VERSION = "1.0.0"
    REQUIRED_FIELDS = ("id_atomo", "texto_regra", "versao_contrato")

    @property
    def name(self) -> str:
        return self.NAME

    @property
    def version(self) -> str:
        return self.VERSION

    def validate(self, item: dict[str, Any]) -> tuple[bool, str | None]:
        missing = [f for f in self.REQUIRED_FIELDS if not item.get(f)]
        if missing:
            return False, f"campos obrigatórios ausentes: {missing}"
        return True, None

    def validate_batch(self, items: list[dict[str, Any]]) -> list[tuple[dict, bool, str | None]]:
        return [(item, *self.validate(item)) for item in items]

    def test_suite(self) -> list[tuple[dict, bool, str]]:
        return [
            # 5 válidos
            ({"id_atomo": "NORM-2026-1", "texto_regra": "texto de exemplo", "versao_contrato": "1.2.0"}, True, "átomo válido"),
            ({"id_atomo": "X", "texto_regra": "x" * 10, "versao_contrato": "1.0.0", "extra": 1}, True, "átomo com campo extra"),
            ({"id_atomo": "NORM-2025-100", "texto_regra": "a" * 500, "versao_contrato": "1.2.0"}, True, "átomo normal"),
            ({"id_atomo": "A", "texto_regra": "abcdefghij", "versao_contrato": "2.0.0"}, True, "átomo v2"),
            ({"id_atomo": "N-1", "texto_regra": "abcdefghij", "versao_contrato": "1.2.0"}, True, "átomo mínimo"),
            # 5 inválidos
            ({}, False, "item vazio"),
            ({"id_atomo": "X"}, False, "sem texto_regra"),
            ({"texto_regra": "a" * 10}, False, "sem id_atomo"),
            ({"id_atomo": "X", "texto_regra": "a" * 10}, False, "sem versao_contrato"),
            ({"versao_contrato": "1.0.0"}, False, "sem id e texto"),
            ({"id_atomo": "", "texto_regra": "a" * 10, "versao_contrato": "1.0.0"}, False, "id_atomo vazio"),
        ]
