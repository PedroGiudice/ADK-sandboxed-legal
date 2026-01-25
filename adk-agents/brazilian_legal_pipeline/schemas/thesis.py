"""
Pydantic schemas para CONSTRUCTION phase (thesis building).
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class NormReference(BaseModel):
    """Referencia a norma na tese."""
    identificador: str
    dispositivo: Optional[str] = None
    texto: Optional[str] = None


class PrecedentReference(BaseModel):
    """Referencia a precedente na tese."""
    identificador: str
    tribunal: str
    tese: Optional[str] = None
    vinculante: bool = False


class ApplicationStep(BaseModel):
    """Passo de aplicacao (subsuncao)."""
    elemento_normativo: str
    fato_correspondente: str
    adequacao: Literal["presente", "ausente", "ambiguo"]
    interpretacao: str


class Counterargument(BaseModel):
    """Contraargumento antecipado."""
    argumento: str
    refutacao: str
    risco: Literal["alto", "medio", "baixo"] = "medio"


class Conclusion(BaseModel):
    """Conclusao da tese."""
    tese: str
    confianca: Literal["alta", "media", "baixa"]
    condicoes: List[str] = Field(default_factory=list)


class IRACAnalysis(BaseModel):
    """Analise IRAC+ completa."""
    issue: str = Field(..., description="Questao reformulada")
    rule: dict = Field(default_factory=dict, description="Normas e precedentes")
    application: List[ApplicationStep] = Field(default_factory=list)
    counterarguments: List[Counterargument] = Field(default_factory=list)
    conclusion: Conclusion


class Thesis(BaseModel):
    """Tese juridica construida."""
    questao_id: str
    metodo: Literal["literal", "sistematico", "teleologico", "ponderacao", "analogia"]
    irac: IRACAnalysis
    subsidiarias: List[str] = Field(default_factory=list)


class ThesisOutput(BaseModel):
    """Output completo do debate de construcao."""
    teses: List[Thesis] = Field(default_factory=list)


class DestructorAttack(BaseModel):
    """Ataque do agente destruidor."""
    tese_alvo: str
    tipo: Literal["subsuncao", "normativo", "jurisprudencial", "fatual"]
    severidade: Literal["fatal", "grave", "moderado", "leve"]
    descricao: str
    jurisprudencia_contraria: List[str] = Field(default_factory=list)
    recomendacao: Literal["reformular", "reforcar", "aceitar_risco", "abandonar"]


class DestructorVerdict(BaseModel):
    """Veredicto do agente destruidor."""
    tese_sobrevive: bool
    nivel_risco: Literal["alto", "medio", "baixo"]
    requer_reformulacao: bool
    ataques: List[DestructorAttack] = Field(default_factory=list)
    vulnerabilidades_criticas: List[str] = Field(default_factory=list)
