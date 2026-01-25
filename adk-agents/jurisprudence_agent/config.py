"""
Configuration for the Jurisprudence Research Agent.

Whitelist of tribunal sites, search parameters, and agent settings.
"""

from pathlib import Path
from typing import Final

# =============================================================================
# PATHS
# =============================================================================

BASE_DIR: Final[Path] = Path(__file__).parent
OUTPUT_DIR: Final[Path] = BASE_DIR / "research_output"
OUTPUT_DIR.mkdir(exist_ok=True)


# =============================================================================
# WHITELIST DE TRIBUNAIS
# =============================================================================

WHITELIST_SITES: dict = {
    # MVP - Prioridade Alta
    "stj": {
        "name": "Superior Tribunal de Justica",
        "short_name": "STJ",
        "base_url": "https://scon.stj.jus.br",
        "search_url": "https://scon.stj.jus.br/SCON/pesquisar.jsp",
        "enabled": True,
        "priority": 1,
        "specialization": ["civil", "criminal", "federal", "consumidor"],
        "notes": "API de dados abertos tambem disponivel",
    },
    "tjsp": {
        "name": "Tribunal de Justica de Sao Paulo",
        "short_name": "TJSP",
        "base_url": "https://esaj.tjsp.jus.br",
        "search_url": "https://esaj.tjsp.jus.br/cjsg/consultaCompleta.do",
        "enabled": True,
        "priority": 2,
        "specialization": ["civil", "criminal", "fazenda"],
        "notes": "Maior volume de decisoes estaduais",
    },
    "tjmg": {
        "name": "Tribunal de Justica de Minas Gerais",
        "short_name": "TJMG",
        "base_url": "https://www.tjmg.jus.br",
        "search_url": "https://www5.tjmg.jus.br/jurisprudencia/pesquisaPalavrasEspelhoAcordao.do",
        "enabled": True,
        "priority": 3,
        "specialization": ["civil", "criminal", "fazenda"],
        "notes": "Sistema proprio de busca",
    },
    "tjrj": {
        "name": "Tribunal de Justica do Rio de Janeiro",
        "short_name": "TJRJ",
        "base_url": "https://www3.tjrj.jus.br",
        "search_url": "https://www3.tjrj.jus.br/ejuris/ConsultarJurisprudencia.aspx",
        "enabled": True,
        "priority": 4,
        "specialization": ["civil", "criminal", "fazenda"],
        "notes": "Operadores booleanos suportados",
    },

    # Expansao Futura - Tribunais Superiores
    "stf": {
        "name": "Supremo Tribunal Federal",
        "short_name": "STF",
        "base_url": "https://portal.stf.jus.br",
        "search_url": "https://jurisprudencia.stf.jus.br/pages/search",
        "enabled": False,  # Fase 4
        "priority": 10,
        "specialization": ["constitucional"],
        "notes": "Repercussao geral, sumulas vinculantes",
    },
    "tst": {
        "name": "Tribunal Superior do Trabalho",
        "short_name": "TST",
        "base_url": "https://jurisprudencia.tst.jus.br",
        "search_url": "https://jurisprudencia.tst.jus.br/",
        "enabled": False,  # Fase 4
        "priority": 11,
        "specialization": ["trabalhista"],
        "notes": "Sumulas e OJs",
    },

    # Expansao Futura - TRFs
    "trf1": {
        "name": "Tribunal Regional Federal 1a Regiao",
        "short_name": "TRF1",
        "base_url": "https://jurisprudencia.trf1.jus.br",
        "search_url": "https://jurisprudencia.trf1.jus.br/busca/",
        "enabled": False,  # Fase 4
        "priority": 20,
        "specialization": ["federal", "previdenciario"],
        "notes": "AC, AM, AP, BA, DF, GO, MA, MT, PA, PI, RO, RR, TO",
    },
    "trf2": {
        "name": "Tribunal Regional Federal 2a Regiao",
        "short_name": "TRF2",
        "base_url": "https://www.trf2.jus.br",
        "search_url": "https://www.trf2.jus.br/jurisprudencia/",
        "enabled": False,
        "priority": 21,
        "specialization": ["federal", "previdenciario"],
        "notes": "RJ, ES",
    },
    "trf3": {
        "name": "Tribunal Regional Federal 3a Regiao",
        "short_name": "TRF3",
        "base_url": "https://www.trf3.jus.br",
        "search_url": "https://web.trf3.jus.br/base-textual",
        "enabled": False,
        "priority": 22,
        "specialization": ["federal", "previdenciario"],
        "notes": "SP, MS",
    },
    "trf4": {
        "name": "Tribunal Regional Federal 4a Regiao",
        "short_name": "TRF4",
        "base_url": "https://www.trf4.jus.br",
        "search_url": "https://jurisprudencia.trf4.jus.br/pesquisa/",
        "enabled": False,
        "priority": 23,
        "specialization": ["federal", "previdenciario"],
        "notes": "RS, SC, PR",
    },

    # Agregadores
    "cjf": {
        "name": "Conselho da Justica Federal",
        "short_name": "CJF",
        "base_url": "https://www.cjf.jus.br",
        "search_url": "https://www.cjf.jus.br/jurisprudencia/",
        "enabled": False,
        "priority": 30,
        "specialization": ["federal", "tnu"],
        "notes": "Jurisprudencia unificada da JF",
    },
}


# =============================================================================
# PARAMETROS DO AGENTE
# =============================================================================

# Criterios de parada (otimizado para mais resultados)
MAX_ITERATIONS: Final[int] = 7  # Mais iteracoes para mais cobertura
MIN_SOURCES: Final[int] = 50  # Mais fontes para compensar snippets curtos
SATURATION_THRESHOLD: Final[float] = 0.85  # Saturacao mais alta

# Limites de busca (aumentados para mais dados)
MAX_RESULTS_PER_TRIBUNAL: Final[int] = 15  # Mais resultados por tribunal
MAX_QUERIES_PER_ITERATION: Final[int] = 15  # Mais queries por iteracao
MAX_SUBTOPICS: Final[int] = 15  # Mais sub-topicos na decomposicao

# Rate limiting
DEFAULT_DELAY_SECONDS: Final[float] = 1.0
MAX_CONCURRENT_SCRAPERS: Final[int] = 3


# =============================================================================
# LLM CONFIG (Gemini)
# =============================================================================

LLM_MODEL: Final[str] = "gemini-2.5-flash"


# =============================================================================
# HELPERS
# =============================================================================

def get_enabled_sites() -> dict:
    """Return only enabled tribunal sites."""
    return {
        k: v for k, v in WHITELIST_SITES.items()
        if v.get("enabled", False)
    }


def get_sites_by_specialization(spec: str) -> dict:
    """Return sites that cover a specific area of law."""
    return {
        k: v for k, v in WHITELIST_SITES.items()
        if v.get("enabled", False) and spec in v.get("specialization", [])
    }
