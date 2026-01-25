"""
Jurisprudence Research Agent

Agente de pesquisa iterativa de jurisprudencia brasileira com loop de
refinamento, baseado no Iterative Deep Research Agent.

Abordagem: Usa Google Search (via Google ADK) com restricao de sites (site:)
para buscar apenas em dominios de tribunais oficiais. Isso garante:
- Resultados de fontes confiaveis (whitelist)
- Funcionalidade mesmo com protecao CAPTCHA dos sites
- Extracao de metadados juridicos (processo, relator, data)

Tribunais suportados:
- STJ - Superior Tribunal de Justica
- STF - Supremo Tribunal Federal
- TJSP - Tribunal de Justica de Sao Paulo
- TJMG - Tribunal de Justica de Minas Gerais
- TJRJ - Tribunal de Justica do Rio de Janeiro
- TRF1-5 - Tribunais Regionais Federais

Usage:
    from jurisprudence_agent import JurisprudenceAgent, JurisprudenceConfig

    config = JurisprudenceConfig(
        court_domains=["stj.jus.br", "tjsp.jus.br"]
    )
    agent = JurisprudenceAgent(config)
    result = await agent.research("dano moral contratual")
"""

__version__ = "0.1.0"

from .agent import JurisprudenceAgent, JurisprudenceConfig, COURT_DOMAINS, DEFAULT_DOMAINS
from .models import SearchResult

__all__ = [
    "JurisprudenceAgent",
    "JurisprudenceConfig",
    "COURT_DOMAINS",
    "DEFAULT_DOMAINS",
    "SearchResult",
]
