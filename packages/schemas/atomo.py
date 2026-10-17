"""
Contrato de átomo normativo.

Este módulo existia com um contrato divergente do de invariantes.py
(max_length, versão e validações diferentes — achado GOV-008). Agora há um
único contrato canônico: AtomoBlindado. O nome AtomoNormativo é mantido
apenas como alias de compatibilidade e não deve ser usado em código novo.
"""
from packages.schemas.invariantes import VERSAO_CONTRATO, AtomoBlindado

AtomoNormativo = AtomoBlindado

__all__ = ["AtomoBlindado", "AtomoNormativo", "VERSAO_CONTRATO"]
