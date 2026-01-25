"""
Pydantic schemas para output final.
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class ConfidenceLevel(BaseModel):
    """Nivel de confianca do output."""
    geral: Literal["alta", "media", "baixa"]
    verificacoes_recomendadas: List[str] = Field(default_factory=list)
    pontos_atencao: List[str] = Field(default_factory=list)


class Caveat(BaseModel):
    """Ressalva do output."""
    tipo: Literal["fonte_parcial", "jurisprudencia_desatualizada", "tese_risco", "lacuna_aceita"]
    descricao: str
    severidade: Literal["alta", "media", "baixa"] = "media"


class DebateSummary(BaseModel):
    """Resumo de um debate."""
    fase: str
    iteracoes: int
    convergiu: bool
    motivo_saida: str


class PipelineMetadata(BaseModel):
    """Metadados do pipeline."""
    start_time: str
    end_time: Optional[str] = None
    model: str
    max_debate_iterations: int
    total_debates: int = 3
    success: bool = False


class FinalOutput(BaseModel):
    """Output final completo da pipeline."""
    texto_principal: str = Field(..., description="Texto juridico produzido")
    ressalvas: List[Caveat] = Field(default_factory=list)
    confianca: ConfidenceLevel
    debates: List[DebateSummary] = Field(default_factory=list)
    metadata: PipelineMetadata


# Draft-specific schemas
class DraftProblem(BaseModel):
    """Problema identificado no draft."""
    id: str
    tipo: Literal["citacao", "consistencia", "estrutura", "registro", "linguagem", "conformidade"]
    severidade: Literal["bloqueante", "grave", "moderado", "leve"]
    localizacao: str
    descricao: str
    correcao_sugerida: Optional[str] = None


class CriticVerdict(BaseModel):
    """Veredicto do agente critico."""
    aprovado: bool
    score_qualidade: Literal["excelente", "bom", "adequado", "insuficiente"]
    requer_revisao: bool
    problemas: List[DraftProblem] = Field(default_factory=list)
    citacoes_problematicas: List[str] = Field(default_factory=list)
    sugestoes_melhoria: List[str] = Field(default_factory=list)
