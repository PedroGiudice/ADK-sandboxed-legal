"""
Pydantic schemas para VERIFICATION phase.
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class VerifiedNorm(BaseModel):
    """Norma verificada."""
    identificador: str
    fonte: Literal["planalto.gov.br", "conhecimento_interno", "nao_encontrado"]
    confianca: Literal["alta", "media", "baixa", "nenhuma"]
    texto_extraido: str = ""
    url: Optional[str] = None
    disclaimer: Optional[str] = None


class VerifiedJurisprudence(BaseModel):
    """Jurisprudencia verificada."""
    identificador: str
    tribunal: str
    classe: Optional[str] = None
    numero: Optional[str] = None
    data: Optional[str] = None
    relator: Optional[str] = None
    status: Literal["verificado", "metadados_insuficientes", "nao_encontrado"]
    confianca: Literal["alta", "media", "baixa", "nenhuma"]
    url: Optional[str] = None


class VerificationGap(BaseModel):
    """Lacuna identificada na verificacao."""
    tipo: Literal["norma", "jurisprudencia"]
    identificador: str
    motivo: str


class VerificationStats(BaseModel):
    """Estatisticas da verificacao."""
    total_verificadas: int = 0
    fontes_oficiais: int = 0
    conhecimento_interno: int = 0
    lacunas: int = 0
    taxa_conhecimento_interno: float = 0.0


class VerificationOutput(BaseModel):
    """Output completo do debate de verificacao."""
    normas_verificadas: List[VerifiedNorm] = Field(default_factory=list)
    jurisprudencia_verificada: List[VerifiedJurisprudence] = Field(default_factory=list)
    lacunas: List[VerificationGap] = Field(default_factory=list)
    alertas: List[str] = Field(default_factory=list)
    estatisticas: VerificationStats = Field(default_factory=VerificationStats)


class SkepticQuestion(BaseModel):
    """Questionamento do agente cetico."""
    id: str
    tipo: Literal["completude", "qualidade", "jurisprudencia", "conflito"]
    severidade: Literal["bloqueante", "importante", "menor"]
    descricao: str
    acao_recomendada: str


class SkepticVerdict(BaseModel):
    """Veredicto do agente cetico."""
    aprovado: bool
    score_confiabilidade: Literal["alta", "media", "baixa"]
    requer_iteracao: bool
    questionamentos: List[SkepticQuestion] = Field(default_factory=list)
    lacunas_adicionais: List[str] = Field(default_factory=list)
    conflitos_detectados: List[str] = Field(default_factory=list)
