from pydantic import BaseModel, Field, HttpUrl, validator
from typing import Literal, Optional
from datetime import date

class AtomoBlindado(BaseModel):
    id_atomo: str = Field(..., pattern=r"^NORM-\d{4}-\d+")
    texto_regra: str = Field(..., min_length=10, max_length=800)
    dispositivo_legal: str = Field(..., min_length=3)
    norma_origem: str
    link_fonte: HttpUrl
    status: Literal["Vigente", "Alterado", "Revogado", "Sob discussão"]
    data_verificacao: date
    versao_contrato: str = "1.1.0"

    @validator('texto_regra')
    def sem_termos_opinativos(cls, v):
        proibidos = ['infelizmente', 'importante destacar', 'recomenda-se', 'sugerimos', 'infelizmente']
        lower = v.lower()
        for p in proibidos:
            if p in lower:
                raise ValueError(f'Termo opinativo proibido: {p}')
        return v

    @validator('link_fonte')
    def fonte_obrigatoria_se_vigente(cls, v, values):
        if values.get('status') == 'Vigente' and not v:
            raise ValueError('INVARIANTE: status Vigente exige link_fonte válido')
        return v
