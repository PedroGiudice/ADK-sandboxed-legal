"""
Tools para busca em fontes juridicas oficiais.
"""
import re
from typing import Optional

import httpx
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext


async def search_planalto(
    norm_type: str,
    number: str,
    year: str,
    article: Optional[str] = None,
    tool_context: ToolContext = None
) -> dict:
    """
    Busca legislacao no portal Planalto.gov.br.

    Args:
        norm_type: Tipo da norma (lei, lei_complementar, decreto, constituicao)
        number: Numero da norma
        year: Ano da norma
        article: Artigo especifico a extrair (opcional)

    Returns:
        dict com status, texto e metadados da norma
    """
    # Construir URL baseada no tipo
    base = "https://www.planalto.gov.br/ccivil_03"

    url_map = {
        "constituicao": f"{base}/constituicao/constituicao.htm",
        "lei_complementar": f"{base}/leis/lcp/Lcp{number}.htm",
        "lei": f"{base}/leis/L{number}.htm",
        "decreto": f"{base}/decreto/D{number}.htm",
        "decreto_lei": f"{base}/decreto-lei/Del{number}.htm",
    }

    # Leis pos-2000 tem estrutura diferente
    if norm_type == "lei" and int(year) >= 2000:
        period_start = (int(year) // 4) * 4 + 1
        period_end = period_start + 3
        period = f"{period_start}-{period_end}"
        url = f"{base}/_ato{period}/{year}/lei/L{number}.htm"
    else:
        url = url_map.get(norm_type, f"{base}/leis/L{number}.htm")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)

            if response.status_code == 200:
                text = response.text

                # Extrair artigo especifico se solicitado
                extracted = text
                if article:
                    # Logica de extracao de artigo
                    pattern = rf"Art\.\s*{article}[^0-9][\s\S]*?(?=Art\.\s*\d|$)"
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        extracted = match.group(0)

                return {
                    "status": "found",
                    "source": "planalto.gov.br",
                    "url": url,
                    "text": extracted[:5000],  # Limitar tamanho
                    "full_identifier": f"{norm_type.replace('_', ' ').title()} {number}/{year}",
                    "confidence": "high"
                }
            else:
                return {
                    "status": "not_found",
                    "source": "planalto.gov.br",
                    "url": url,
                    "error": f"HTTP {response.status_code}",
                    "confidence": "none"
                }

    except Exception as e:
        return {
            "status": "error",
            "source": "planalto.gov.br",
            "error": str(e),
            "confidence": "none"
        }


async def search_jurisprudence(
    tribunal: str,
    case_class: str,
    number: str,
    tool_context: ToolContext = None
) -> dict:
    """
    Busca jurisprudencia em portais de tribunais.

    Args:
        tribunal: Sigla do tribunal (STF, STJ, TST, etc.)
        case_class: Classe processual (RE, REsp, RR, etc.)
        number: Numero do processo

    Returns:
        dict com status e dados do precedente
    """
    # Mapeamento de URLs por tribunal
    tribunal_urls = {
        "STF": "https://portal.stf.jus.br/jurisprudencia/",
        "STJ": "https://scon.stj.jus.br/SCON/",
        "TST": "https://jurisprudencia.tst.jus.br/",
        "TSE": "https://jurisprudencia.tse.jus.br/",
    }

    base_url = tribunal_urls.get(tribunal.upper())
    if not base_url:
        return {
            "status": "unsupported_tribunal",
            "tribunal": tribunal,
            "error": f"Tribunal {tribunal} nao suportado para busca automatica",
            "supported": list(tribunal_urls.keys())
        }

    # Busca simplificada (producao usaria APIs especificas de cada tribunal)
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Cada tribunal tem API diferente - isso e ilustrativo
            search_url = f"{base_url}?classe={case_class}&numero={number}"
            response = await client.get(search_url)

            if response.status_code == 200:
                return {
                    "status": "found",
                    "tribunal": tribunal,
                    "case_class": case_class,
                    "number": number,
                    "source": base_url,
                    "confidence": "medium",  # Requer validacao manual
                    "note": "Dados requerem confirmacao no portal oficial"
                }
            else:
                return {
                    "status": "not_found",
                    "tribunal": tribunal,
                    "case_class": case_class,
                    "number": number,
                    "error": f"HTTP {response.status_code}"
                }

    except Exception as e:
        return {
            "status": "error",
            "tribunal": tribunal,
            "error": str(e)
        }


# Registrar como FunctionTools
search_planalto_tool = FunctionTool(func=search_planalto)
search_jurisprudence_tool = FunctionTool(func=search_jurisprudence)
