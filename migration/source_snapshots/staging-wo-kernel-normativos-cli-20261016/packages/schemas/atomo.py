from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Literal
from datetime import date

class AtomoNormativo(BaseModel):
    id_atomo: str = Field(..., pattern=r"^NORM-\d{4}-\d+")
    texto_regra: str = Field(..., max_length=500)
    dispositivo_legal: str
    norma_origem: str
    link_fonte: HttpUrl
    status: Literal["Vigente", "Alterado", "Revogado", "Sob discussão"]
    data_verificacao: date
    versao_contrato: str = "1.0.0"

    class Config:
        json_schema_extra = {
            "example": {
                "id_atomo": "NORM-2026-001",
                "texto_regra": "Exemplo de regra atômica.",
                "dispositivo_legal": "Art. 1º",
                "norma_origem": "Resolução COFEN 736/2024",
                "link_fonte": "https://www.cofen.gov.br",
                "status": "Vigente",
                "data_verificacao": "2026-10-11"
            }
        }
