"""
Pydantic schemas para INTAKE phase.
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class LegalQuestion(BaseModel):
    """Questao juridica identificada."""
    id: str = Field(..., description="ID da questao (QJ1, QJ2, etc.)")
    formulacao: str = Field(..., description="Formulacao tecnica da questao")
    area: str = Field(..., description="Area do direito")
    complexidade: Literal["alta", "media", "baixa"] = Field(default="media")


class Classification(BaseModel):
    """Classificacao da consulta."""
    tipo_output: Literal["peca_processual", "parecer", "consulta_rapida", "analise"]
    area_principal: str
    areas_conexas: List[str] = Field(default_factory=list)
    urgencia: Literal["alta", "media", "baixa"] = Field(default="media")
    criticidade: Literal["alta", "media", "baixa"] = Field(default="media")
    perfil_usuario: Literal["alta", "media", "baixa"] = Field(default="media")


class Fact(BaseModel):
    """Fato identificado na consulta."""
    id: str
    descricao: str
    data: Optional[str] = None


class IdentifiedNorm(BaseModel):
    """Norma identificada na consulta."""
    identificador: str
    dispositivos: List[str] = Field(default_factory=list)
    texto_fornecido: bool = False


class IdentifiedJurisprudence(BaseModel):
    """Jurisprudencia identificada na consulta."""
    identificador: str
    metadados_completos: bool = False


class Document(BaseModel):
    """Documento anexo."""
    id: str
    tipo: str
    resumo: str = ""


class Gap(BaseModel):
    """Lacuna identificada."""
    tipo: Literal["fato", "norma", "jurisprudencia", "documento"]
    descricao: str
    essencialidade: Literal["bloqueante", "importante", "menor"] = "importante"


class Inventory(BaseModel):
    """Inventario de elementos da consulta."""
    fatos: List[Fact] = Field(default_factory=list)
    normas: List[IdentifiedNorm] = Field(default_factory=list)
    jurisprudencia: List[IdentifiedJurisprudence] = Field(default_factory=list)
    documentos: List[Document] = Field(default_factory=list)


class IntakeOutput(BaseModel):
    """Output completo do INTAKE agent."""
    questoes_juridicas: List[LegalQuestion]
    classificacao: Classification
    inventario: Inventory
    gaps: List[Gap] = Field(default_factory=list)


# Input schema
class ConsultationContext(BaseModel):
    """Contexto da consulta."""
    area_direito: str = "geral"
    partes: dict = Field(default_factory=dict)


class ConsultationRequest(BaseModel):
    """Requisicao de consulta."""
    texto: str
    tipo_solicitado: Literal["peca_processual", "parecer", "consulta_rapida", "analise"] = "parecer"
    urgencia: Literal["alta", "media", "baixa"] = "media"


class ConsultationInput(BaseModel):
    """Input estruturado da consulta juridica."""
    consulta: ConsultationRequest
    contexto: ConsultationContext = Field(default_factory=ConsultationContext)
    fatos: List[dict] = Field(default_factory=list)
    normas_identificadas: List[dict] = Field(default_factory=list)
    jurisprudencia_identificada: List[dict] = Field(default_factory=list)
    documentos_anexos: List[dict] = Field(default_factory=list)
    restricoes: dict = Field(default_factory=dict)
