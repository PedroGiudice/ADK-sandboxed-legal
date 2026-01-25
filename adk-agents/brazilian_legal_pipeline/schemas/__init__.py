"""
Pydantic schemas para validacao de dados da pipeline juridica.

Schemas disponiveis:
- ConsultationInput: Input estruturado da consulta
- IntakeOutput: Output do agente de intake
- VerificationOutput: Output do debate de verificacao
- ThesisOutput: Output do debate de construcao
- DraftOutput: Output do debate de redacao
- FinalOutput: Output final sintetizado
"""

from .intake import ConsultationInput, IntakeOutput, LegalQuestion, Classification
from .verification import VerificationOutput, VerifiedNorm, VerifiedJurisprudence
from .thesis import ThesisOutput, Thesis, IRACAnalysis
from .output import FinalOutput, Caveat, ConfidenceLevel

__all__ = [
    # Intake
    "ConsultationInput",
    "IntakeOutput",
    "LegalQuestion",
    "Classification",
    # Verification
    "VerificationOutput",
    "VerifiedNorm",
    "VerifiedJurisprudence",
    # Thesis
    "ThesisOutput",
    "Thesis",
    "IRACAnalysis",
    # Output
    "FinalOutput",
    "Caveat",
    "ConfidenceLevel",
]
