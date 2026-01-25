"""
Data models for the Jurisprudence Research Agent.

Dataclasses representing search results, decisions, and research outputs.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any


@dataclass
class SearchResult:
    """
    Represents a single search result from a tribunal.

    Attributes:
        url: Direct URL to the decision
        title: Title or ementa of the decision
        snippet: Short excerpt or summary
        tribunal: Tribunal identifier (STJ, TJSP, etc)
        numero_processo: Case number (optional)
        data_julgamento: Judgment date (optional)
        relator: Reporting judge (optional)
        classe: Process class (REsp, AgInt, etc)
        raw_html: Raw HTML for debugging (optional)
    """
    url: str
    title: str
    snippet: str
    tribunal: str
    numero_processo: Optional[str] = None
    data_julgamento: Optional[str] = None
    relator: Optional[str] = None
    classe: Optional[str] = None
    raw_html: Optional[str] = None

    def __hash__(self):
        return hash(self.url)

    def __eq__(self, other):
        if not isinstance(other, SearchResult):
            return False
        return self.url == other.url


@dataclass
class Decision:
    """
    Represents a full court decision with all available metadata.

    Attributes:
        numero_processo: Case number
        tribunal: Tribunal identifier
        relator: Reporting judge
        orgao_julgador: Judging body (Turma, Secao, etc)
        data_julgamento: Judgment date
        data_publicacao: Publication date
        ementa: Decision summary
        inteiro_teor: Full text (optional)
        acordao: Final ruling text
        votos: Individual votes (if available)
        url_fonte: Source URL
    """
    numero_processo: str
    tribunal: str
    relator: str
    orgao_julgador: str
    data_julgamento: str
    data_publicacao: str
    ementa: str
    inteiro_teor: Optional[str] = None
    acordao: Optional[str] = None
    votos: Optional[list[dict]] = None
    url_fonte: Optional[str] = None


@dataclass
class IterationResult:
    """
    Result of a single research iteration.

    Attributes:
        iteration: Iteration number (1-based)
        queries_executed: List of queries executed
        sources_found: List of SearchResults found
        gaps_identified: Gaps identified by LLM
        saturation_score: How saturated the search is (0.0-1.0)
        raw_response: Raw LLM response for debugging
    """
    iteration: int
    queries_executed: list[str]
    sources_found: list[SearchResult]
    gaps_identified: list[str] = field(default_factory=list)
    saturation_score: float = 0.0
    raw_response: str = ""


@dataclass
class ResearchResult:
    """
    Final result of a research session.

    Attributes:
        topic: Original research topic
        content: Synthesized content (markdown)
        iterations: List of iteration results
        all_sources: Deduplicated list of all sources
        metadata: Research metadata (timing, model, etc)
        errors: Any errors encountered
    """
    topic: str
    content: str
    iterations: list[IterationResult]
    all_sources: list[SearchResult]
    metadata: dict[str, Any]
    errors: list[str]

    def to_markdown(self) -> str:
        """Generate markdown report."""
        lines = [
            f"# Pesquisa: {self.topic}",
            "",
            f"**Gerado:** {self.metadata.get('end_time', 'N/A')}",
            f"**Iteracoes:** {len(self.iterations)}",
            f"**Fontes:** {len(self.all_sources)}",
            f"**Parada:** {self.metadata.get('stopped_by', 'N/A')}",
            "",
            "---",
            "",
            self.content,
            "",
            "---",
            "",
            "## Fontes",
            "",
        ]

        for i, source in enumerate(self.all_sources, 1):
            lines.append(f"{i}. [{source.title}]({source.url}) - {source.tribunal}")

        if self.errors:
            lines.extend([
                "",
                "## Erros",
                "",
            ])
            for error in self.errors:
                lines.append(f"- {error}")

        return "\n".join(lines)
