"""
Configuracoes da pipeline juridica brasileira.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


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

    # === Sandboxing: Paths por caso ===
    workspace_path: Optional[Path] = None
    case_id: Optional[str] = None

    def get_checkpoint_dir(self) -> Path:
        """Retorna diretorio de checkpoints (isolado por caso se workspace_path definido)."""
        if self.workspace_path:
            return self.workspace_path / ".adk_state"
        return Path("./checkpoints")

    def get_output_dir(self) -> Path:
        """Retorna diretorio de output (isolado por caso se workspace_path definido)."""
        if self.workspace_path:
            return self.workspace_path / "drafts"
        return Path("./output")

    def get_docs_dir(self) -> Path:
        """Retorna diretorio de documentos do caso."""
        if self.workspace_path:
            return self.workspace_path / "docs"
        return Path("./docs")

    def ensure_directories(self) -> None:
        """Cria todos os diretorios necessarios para o caso."""
        self.get_checkpoint_dir().mkdir(parents=True, exist_ok=True)
        self.get_output_dir().mkdir(parents=True, exist_ok=True)
        self.get_docs_dir().mkdir(parents=True, exist_ok=True)


# Instancia global
config = PipelineConfig()
