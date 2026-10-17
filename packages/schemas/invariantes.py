"""AtomoBlindado — schema Pydantic v2 para átomo canônico fail-closed.

Este é o schema AUTORIZADO para validação de átomos no Kernel.
Qualquer divergência entre este arquivo e o Kernel core.py → fail-closed.

Versão: 1.2.0 (Pydantic v2)
Contrato: CE-ATOMO-CANONICO-1.0.0
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Literal, Self

from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator


class AtomoBlindado(BaseModel):
    """Schema autoritativo para átomo canônico.

    Regras:
    - id_atomo: formato NORM-{ANO}-{INT12HEX}
    - texto_regra: 10-800 chars, sem termos opinativos
    - status Vigente exige link_fonte válido
    - sha256_texto ou sha256_original requerido para status=VIGENTE
    - Todas as transições de vigencia devem ser registradas
    """

    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True,
        "extra": "forbid",
    }

    # ── Identidade ───────────────────────────────────────────────────
    id_atomo: str = Field(
        ...,
        pattern=r"^NORM-(?:19|20)\d{2}-\d{1,20}$",
        description="ID canônico determinístico: NORM-{ANO}-{INT12HEX}",
        examples=["NORM-2026-1604569098147256870"],
    )
    versao_contrato: Literal["1.0.0", "1.1.0", "1.2.0"] = Field(
        default="1.2.0",
        description="Versão do schema CE-ATOMO-CANONICO",
    )

    # ── Fonte ────────────────────────────────────────────────────────
    fonte_slug: str | None = Field(
        default=None,
        description="Slug da fonte (ex: cofen_dou, cid10, anvisa_med)",
        examples=["cofen_dou"],
    )
    norma_origem: str | None = Field(
        default=None,
        description="Código normalizado da norma (ex: BR_FED_COFEN_RES_2026_N_00801)",
        examples=["BR_FED_COFEN_RES_2026_N_00801"],
    )
    dispositivo_legal: str | None = Field(
        default=None,
        description="Dispositivo legal (ex: Art. 5o)",
        examples=["Art. 5o"],
    )
    link_fonte: HttpUrl | None = Field(
        default=None,
        description="URL oficial da fonte",
        examples=["https://www.in.gov.br/web/dou/-/resolucao-cofen-801"],
    )

    # ── Conteúdo ──────────────────────────────────────────────────────
    texto_regra: str = Field(
        ...,
        min_length=10,
        max_length=800,
        description="Texto da regra atômica (10-800 caracteres)",
    )
    idioma: Literal["pt-BR", "en-US", "es-ES"] = Field(
        default="pt-BR",
    )

    # ── Integridade ───────────────────────────────────────────────────
    sha256_texto: str | None = Field(
        default=None,
        description="SHA256 do texto normalizado (prefixo sha256: opcional)",
        pattern=r"^(?:sha256:)?[a-f0-9]{64}$",
    )
    sha256_original: str | None = Field(
        default=None,
        description="SHA256 do texto original antes de canonicalização",
        pattern=r"^(?:sha256:)?[a-f0-9]{64}$",
    )
    hash_status: Literal["CONFERIDO", "PENDENTE", "FALHOU"] | None = Field(
        default=None,
    )

    # ── Status ────────────────────────────────────────────────────────
    vigencia: Literal[
        "NAO_VERIFICADO", "VIGENTE", "ALTERADO", "REVOGADO", "SOB_DISCUSSAO"
    ] = Field(
        default="NAO_VERIFICADO",
        description="Status de vigência do normativo",
    )
    data_verificacao: date | None = Field(
        default=None,
    )

    # ── Metadados de commit ─────────────────────────────────────────
    commit_sha: str | None = Field(
        default=None,
        description="SHA do commit Git onde este átomo foi persistido",
    )
    wo_id: str | None = Field(
        default=None,
        description="ID da WO que criou este átomo",
    )
    reviewed_by: str | None = Field(
        default=None,
        description="Username do revisor humano (para G6)",
    )

    # ── Validadores ─────────────────────────────────────────────────

    @field_validator("texto_regra")
    @classmethod
    def sem_termos_opinativos(cls, v: str) -> str:
        """Rejeita termos opinativos, não normativos."""
        proibidos = [
            "infelizmente",
            "importante destacar",
            "recomenda-se",
            "sugerimos",
            "a nosso ver",
            "consideramos que",
            "acreditamos que",
            "no nosso entendimento",
        ]
        lower = v.lower()
        for p in proibidos:
            if p in lower:
                raise ValueError(f"Termo opinativo proibido: '{p}'")
        return v

    @field_validator("sha256_texto", "sha256_original")
    @classmethod
    def normalize_sha_prefix(cls, v: str | None) -> str | None:
        """Remove prefixo 'sha256:' para consistência."""
        if v is None:
            return None
        return v.removeprefix("sha256:")

    @model_validator(mode="after")
    def validar_vigencia_e_fontes(self) -> Self:
        """Vigente exige link_fonte. SHA256 requerido para VIGENTE."""
        if self.vigencia == "VIGENTE":
            if not self.link_fonte:
                raise ValueError("INVARIANTE: vigencia=VIGENTE exige link_fonte")
            if not self.sha256_texto and not self.sha256_original:
                raise ValueError("INVARIANTE: vigencia=VIGENTE exige sha256_texto ou sha256_original")
        return self


# Alias para compatibilidade com código antigo
AtomoNormativo = AtomoBlindado
