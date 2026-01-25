"""
Configuracoes da pipeline juridica brasileira.
"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class PipelineConfig:
    """Configuracoes globais da pipeline."""

    # Modelo a usar (Gemini)
    model: str = "gemini-2.5-flash"
    model_advanced: str = "gemini-2.5-pro"  # Para tarefas complexas

    # Limites de iteracao dos debates
    max_debate_iterations: int = 3

    # Timeout em segundos
    tool_timeout: int = 30

    # Base de conhecimento
    knowledge_cutoff: str = "2025-01"

    # URLs de fontes oficiais
    planalto_base: str = "https://www.planalto.gov.br"
    stf_base: str = "https://portal.stf.jus.br"
    stj_base: str = "https://www.stj.jus.br"
    tst_base: str = "https://www.tst.jus.br"

    # Dominios de tribunais para busca
    court_domains: List[str] = field(default_factory=lambda: [
        "stf.jus.br",
        "stj.jus.br",
        "tst.jus.br",
        "tse.jus.br",
        "tjsp.jus.br",
        "tjrj.jus.br",
        "tjmg.jus.br",
        "planalto.gov.br",
    ])


# Instancia global
config = PipelineConfig()
