"""
Tool para validar formato e existencia de citacoes juridicas.
"""
import re
from typing import List

from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext


async def validate_citation(
    citation: str,
    citation_type: str,
    tool_context: ToolContext = None
) -> dict:
    """
    Valida formato e completude de uma citacao juridica.

    Args:
        citation: Texto da citacao a validar
        citation_type: Tipo (legislation | jurisprudence | sumula | doctrine)

    Returns:
        dict com resultado da validacao
    """
    errors: List[str] = []
    warnings: List[str] = []

    if citation_type == "legislation":
        # Formato esperado: Lei n X.XXX/AAAA, art. Y, P Z
        pattern = r"(Lei|Decreto|CF|CPC|CC|CLT|CDC|ECA|CTB|CTN).*?(\d+)[./](\d{4})"
        if not re.search(pattern, citation, re.IGNORECASE):
            errors.append("Formato de legislacao invalido. Esperado: 'Lei n X/AAAA'")

        # Verificar se tem artigo quando deveria
        if "art" not in citation.lower() and len(citation) > 20:
            warnings.append("Citacao de lei sem especificacao de artigo")

    elif citation_type == "jurisprudence":
        # Formato esperado: TRIBUNAL, CLASSE NUMERO, Rel. Min. NOME, j. DD/MM/AAAA

        # Verificar tribunal
        tribunals = ["STF", "STJ", "TST", "TSE", "TRF", "TRT", "TJ"]
        has_tribunal = any(t in citation.upper() for t in tribunals)
        if not has_tribunal:
            errors.append("Tribunal nao identificado na citacao")

        # Verificar classe processual
        classes = ["RE", "REsp", "RR", "AI", "HC", "MS", "ADI", "ADPF", "AgRg", "ARE", "RMS"]
        has_class = any(c in citation.upper() for c in classes)
        if not has_class:
            warnings.append("Classe processual nao identificada")

        # Verificar data
        date_pattern = r"\d{2}[./]\d{2}[./]\d{4}"
        if not re.search(date_pattern, citation):
            errors.append("Data de julgamento nao encontrada (formato: DD/MM/AAAA)")

    elif citation_type == "sumula":
        # Formato esperado: Sumula [Vinculante] N do TRIBUNAL
        pattern = r"[Ss][uU]mula\s+(Vinculante\s+)?(\d+)\s+(do|STF|STJ|TST)"
        if not re.search(pattern, citation, re.IGNORECASE):
            errors.append("Formato de sumula invalido. Esperado: 'Sumula N do TRIBUNAL'")

    elif citation_type == "doctrine":
        # Formato ABNT simplificado
        if "," not in citation:
            warnings.append("Citacao doutrinaria pode estar incompleta (falta autor?)")
        if not re.search(r"\d{4}", citation):
            warnings.append("Ano da publicacao nao encontrado")

    else:
        errors.append(f"Tipo de citacao desconhecido: {citation_type}")

    return {
        "valid": len(errors) == 0,
        "citation": citation,
        "type": citation_type,
        "errors": errors,
        "warnings": warnings,
        "recommendation": "Corrigir erros antes de usar" if errors else "Citacao valida"
    }


validate_citation_tool = FunctionTool(func=validate_citation)
