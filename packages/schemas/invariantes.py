from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator

from packages.cli.sources import dominio_oficial

VERSAO_CONTRATO = "1.2.0"
LIMITE_TEXTO_REGRA = 800
CONDICAO_DETERMINADA = frozenset({"Vigente", "Alterado", "Revogado"})

# Placeholders que já foram aceitos como fonte (teste T2). Proibidos.
DOMINIOS_PLACEHOLDER = {"example.com", "www.example.com", "localhost"}


class AtomoBlindado(BaseModel):
    """Contrato canônico único do átomo normativo (GOV-008).

    Invariantes principais:
    - extra='forbid': propriedades desconhecidas são rejeitadas;
    - status nasce 'Não verificado'; 'Vigente' nunca é default (GOV-004);
    - Vigente, Alterado e Revogado exigem data_verificacao e link_fonte oficial;
    - placeholders (example.com) são rejeitados como fonte.
    """

    model_config = ConfigDict(extra="forbid")

    id_atomo: str = Field(..., pattern=r"^NORM-\d{4}-\d+")
    texto_regra: str = Field(..., min_length=10, max_length=LIMITE_TEXTO_REGRA)
    dispositivo_legal: str = Field(..., min_length=3)
    norma_origem: str
    link_fonte: HttpUrl
    status: Literal["Não verificado", "Vigente", "Alterado", "Revogado", "Sob discussão"]
    data_verificacao: Optional[date] = None
    versao_contrato: str = VERSAO_CONTRATO
    fonte_tipo: Optional[str] = None

    @field_validator("texto_regra")
    @classmethod
    def sem_termos_opinativos(cls, v: str) -> str:
        proibidos = ["infelizmente", "importante destacar", "recomenda-se", "sugerimos"]
        lower = v.lower()
        for p in proibidos:
            if p in lower:
                raise ValueError(f"Termo opinativo proibido: {p}")
        return v

    @field_validator("link_fonte")
    @classmethod
    def sem_placeholder(cls, v: HttpUrl) -> HttpUrl:
        host = (v.host or "").lower()
        if host in DOMINIOS_PLACEHOLDER:
            raise ValueError(f"INVARIANTE: link_fonte placeholder proibido ({host})")
        return v

    @model_validator(mode="after")
    def vigencia_exige_evidencia(self):
        if self.status in CONDICAO_DETERMINADA:
            if self.data_verificacao is None:
                raise ValueError(
                    f"INVARIANTE: status {self.status} exige data_verificacao com evidência de verificação"
                )
            if not dominio_oficial(str(self.link_fonte)):
                raise ValueError(
                    f"INVARIANTE: status {self.status} exige link_fonte em domínio oficial da allowlist"
                )
        return self
