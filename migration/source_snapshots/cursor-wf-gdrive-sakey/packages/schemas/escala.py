from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class ParametroEscala(BaseModel):
    nome: str
    tipo: str  # number, select, boolean
    opcoes: Optional[List[str]] = None
    peso: Optional[float] = None

class EscalaClinica(BaseModel):
    id_escala: str = Field(..., pattern=r"^ESC-\d{4}-\d+")
    nome: str
    descricao: str
    fonte_normativa: Optional[str] = None
    parametros: List[ParametroEscala]
    formula: Optional[str] = None
    versao_contrato: str = "1.0.0"
