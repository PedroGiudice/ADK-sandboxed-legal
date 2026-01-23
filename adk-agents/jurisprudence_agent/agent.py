#!/usr/bin/env python3
"""
================================================================================
JURISPRUDENCE RESEARCH AGENT
================================================================================

Agente de pesquisa de jurisprudencia brasileira com loop iterativo.

Baseado no Iterative Deep Research Agent, mas com foco em:
1. Restricao de sites (whitelist de tribunais)
2. Prompts especializados para pesquisa juridica
3. Extracao de metadados juridicos (numero processo, relator, etc.)

A restricao de sites eh feita via operador site: nas queries do Google Search,
garantindo que os resultados venham apenas de portais oficiais de tribunais.

Author: Lex-Vector Team
Version: 1.0.0

Dependencies:
    pip install google-adk google-genai python-dotenv

Environment Variables Required:
    GOOGLE_API_KEY or GOOGLE_GENAI_API_KEY

================================================================================
"""

import asyncio
import json
import os
import sys
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Set
from dataclasses import dataclass, field

# Third-party imports with graceful fallback
try:
    from google.adk.agents import Agent
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.adk.tools import google_search
    from google.genai import types
except ImportError as e:
    print(f"[FATAL] Missing Google ADK dependencies: {e}")
    print("Install with: pip install google-adk google-genai")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ============================================================================
# SECTION 1: COURT DOMAIN WHITELIST
# ============================================================================

COURT_DOMAINS = {
    # Tribunais Superiores
    "stf": {"domain": "stf.jus.br", "name": "Supremo Tribunal Federal"},
    "stj": {"domain": "stj.jus.br", "name": "Superior Tribunal de Justica"},
    "tst": {"domain": "tst.jus.br", "name": "Tribunal Superior do Trabalho"},

    # Tribunais de Justica Estaduais (maiores)
    "tjsp": {"domain": "tjsp.jus.br", "name": "Tribunal de Justica de Sao Paulo"},
    "tjmg": {"domain": "tjmg.jus.br", "name": "Tribunal de Justica de Minas Gerais"},
    "tjrj": {"domain": "tjrj.jus.br", "name": "Tribunal de Justica do Rio de Janeiro"},
    "tjrs": {"domain": "tjrs.jus.br", "name": "Tribunal de Justica do Rio Grande do Sul"},
    "tjpr": {"domain": "tjpr.jus.br", "name": "Tribunal de Justica do Parana"},
    "tjdft": {"domain": "tjdft.jus.br", "name": "Tribunal de Justica do DF e Territorios"},
    "tjba": {"domain": "tjba.jus.br", "name": "Tribunal de Justica da Bahia"},
    "tjsc": {"domain": "tjsc.jus.br", "name": "Tribunal de Justica de Santa Catarina"},
    "tjpe": {"domain": "tjpe.jus.br", "name": "Tribunal de Justica de Pernambuco"},
    "tjgo": {"domain": "tjgo.jus.br", "name": "Tribunal de Justica de Goias"},

    # Tribunais Regionais Federais
    "trf1": {"domain": "trf1.jus.br", "name": "TRF da 1a Regiao"},
    "trf2": {"domain": "trf2.jus.br", "name": "TRF da 2a Regiao"},
    "trf3": {"domain": "trf3.jus.br", "name": "TRF da 3a Regiao"},
    "trf4": {"domain": "trf4.jus.br", "name": "TRF da 4a Regiao"},
    "trf5": {"domain": "trf5.jus.br", "name": "TRF da 5a Regiao"},
    "trf6": {"domain": "trf6.jus.br", "name": "TRF da 6a Regiao"},

    # Conselho da Justica Federal
    "cjf": {"domain": "cjf.jus.br", "name": "Conselho da Justica Federal"},

    # Sites juridicos de qualidade (doutrina e jurisprudencia comentada)
    "dizerodireito": {"domain": "buscadordizerodireito.com.br", "name": "Dizer o Direito"},
}

# Default domains for search (expanded for more coverage)
DEFAULT_DOMAINS = [
    # Tribunais Superiores
    "stj.jus.br", "stf.jus.br",
    # TJs Estaduais principais
    "tjsp.jus.br", "tjmg.jus.br", "tjrj.jus.br", "tjrs.jus.br", "tjpr.jus.br", "tjdft.jus.br",
    # TRFs
    "trf1.jus.br", "trf2.jus.br", "trf3.jus.br", "trf4.jus.br", "trf5.jus.br",
    # Sites juridicos
    "buscadordizerodireito.com.br",
]


# ============================================================================
# SECTION 2: PROMPTS ESPECIALIZADOS PARA JURISPRUDENCIA
# ============================================================================

DECOMPOSITION_PROMPT = """Voce eh um especialista em pesquisa juridica brasileira.
Sua tarefa eh decompor um tema juridico em sub-vetores de pesquisa VARIADOS.

REGRAS CRITICAS:
- Gere 8-15 sub-topicos que cubram o tema de forma ABRANGENTE
- OBRIGATORIO: Use SINONIMOS e VARIACOES de termos em diferentes queries
  - Ex: "revisao contratual" / "reequilibrio economico" / "reajuste" / "alteracao"
  - Ex: "locacao" / "aluguel" / "arrendamento" / "contrato de aluguel"
  - Ex: "onerosidade excessiva" / "desequilibrio contratual" / "quebra da base"
- Foque em aspectos: doutrina, jurisprudencia majoritaria, minoritaria, evolucao temporal
- Inclua termos tecnicos juridicos E termos coloquiais que advogados usam
- Varie os tribunais nas queries: STJ, STF, TJSP, TJMG, TJRJ, TRFs
- Inclua artigos de lei relevantes (ex: "art. 317 CC", "art. 478 CC")
- Output APENAS um array JSON de strings, sem outro texto

EXEMPLO DE VARIACOES OBRIGATORIAS:
Tema: "Revisao de contrato de locacao por aumento de IPTU"
Output RUIM (sem variacoes): ["revisao locacao IPTU", "aumento IPTU locacao", "IPTU contrato locacao"]
Output BOM (com variacoes):
["revisao contrato locacao aumento IPTU STJ",
"reequilibrio economico aluguel tributo municipal jurisprudencia",
"alteracao IPTU obras impacto contrato arrendamento TJSP",
"onerosidade excessiva locacao art 478 CC imposto predial",
"teoria imprevisao aluguel comercial aumento tributario TRF",
"desequilibrio contratual locador locatario IPTU STJ",
"revisional aluguel encargos fiscais TJMG TJRJ",
"clausula rebus sic stantibus locacao imposto predial doutrina"]

Agora decomponha este tema usando VARIACOES DE TERMOS:
TEMA: {topic}

Output:"""

GAP_ANALYSIS_PROMPT = """Voce eh um analista de pesquisa juridica revisando informacoes coletadas para identificar lacunas.

INFORMACOES COLETADAS:
{collected_info}

TEMA ORIGINAL: {topic}

TAREFA:
1. Analise o que ja foi coberto
2. Identifique o que esta FALTANDO ou subexplorado
3. Sugira novas queries especificas para preencher lacunas

ASPECTOS A VERIFICAR:
- Jurisprudencia de tribunais superiores (STJ, STF)
- Jurisprudencia de tribunais estaduais (TJs)
- Evolucao temporal da jurisprudencia
- Casos paradigmaticos citados
- Teses firmadas em recursos repetitivos
- Sumulas vinculantes ou persuasivas

Output um objeto JSON com esta estrutura:
{{
    "coverage_summary": "Resumo breve do que foi coberto",
    "gaps": ["lacuna1", "lacuna2", ...],
    "new_queries": ["query especifica 1", "query especifica 2", ...],
    "saturation_score": 0.0-1.0  // 1.0 significa totalmente saturado
}}

Output APENAS o JSON, sem outro texto."""

SYNTHESIS_PROMPT = """Voce eh um pesquisador juridico especialista. Sintetize toda a pesquisa coletada em um relatorio tecnico.

DADOS DA PESQUISA:
{research_data}

TEMA ORIGINAL: {topic}

REQUISITOS DO OUTPUT:
1. SEM introducoes ou conclusoes jornalisticas
2. Lidere com dados e fatos juridicos
3. Use tabelas para dados comparativos
4. Inclua citacoes de fontes inline
5. Note informacoes conflitantes encontradas

FORMATO:
## Principais Entendimentos

### Posicao Majoritaria
- [Entendimento com citacao]

### Posicao Minoritaria (se houver)
- [Entendimento divergente]

## Casos Paradigmaticos
| Processo | Tribunal | Tese | Data |
|----------|----------|------|------|

## Sumulas e Teses Vinculantes
- [Sumula/tese com numero]

## Lacunas e Limitacoes
- [O que nao foi encontrado]

## Indice de Fontes
1. [URL] - [Tribunal] - [Breve descricao]

Inicie a sintese:"""


# ============================================================================
# SECTION 3: CONFIGURATION
# ============================================================================

@dataclass
class JurisprudenceConfig:
    """Configuration for the Jurisprudence Research Agent."""

    # Iteration controls
    max_iterations: int = 5
    min_sources: int = 15
    saturation_threshold: float = 0.8

    # Depth controls
    queries_per_subtopic: int = 3
    max_subtopics: int = 12

    # Domain filtering
    court_domains: List[str] = field(default_factory=lambda: DEFAULT_DOMAINS)

    # Model configuration
    model_name: str = "gemini-2.5-flash"

    # Session identifiers
    app_name: str = "jurisprudence_agent"
    user_id: str = "researcher"
    session_id: str = field(default_factory=lambda: f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

    # Output settings
    output_dir: Path = field(default_factory=lambda: Path("./research_output"))
    output_format: str = "markdown"

    # Logging
    log_level: str = "INFO"

    def __post_init__(self):
        self.output_dir = Path(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)


# ============================================================================
# SECTION 4: LOGGING
# ============================================================================

def setup_logging(config: JurisprudenceConfig) -> logging.Logger:
    """Configure structured logging."""
    logger = logging.getLogger("JurisprudenceAgent")
    logger.setLevel(getattr(logging, config.log_level.upper()))
    logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    log_file = config.output_dir / f"jurisprudence_{config.session_id}.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s | %(funcName)s:%(lineno)d | %(message)s"
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    return logger


# ============================================================================
# SECTION 5: DATA STRUCTURES
# ============================================================================

@dataclass
class JurisprudenceSource:
    """Represents a jurisprudence source."""
    url: str
    title: str
    snippet: str = ""
    query: str = ""
    iteration: int = 0
    tribunal: str = ""
    numero_processo: Optional[str] = None
    data_julgamento: Optional[str] = None
    relator: Optional[str] = None

    def __hash__(self):
        return hash(self.url)

    def __eq__(self, other):
        return isinstance(other, JurisprudenceSource) and self.url == other.url


@dataclass
class IterationResult:
    """Result of a single research iteration."""
    iteration: int
    queries_executed: List[str]
    sources_found: List[JurisprudenceSource]
    gaps_identified: List[str]
    saturation_score: float
    raw_response: str = ""


@dataclass
class ResearchResult:
    """Final research result."""
    topic: str
    content: str
    iterations: List[IterationResult]
    all_sources: List[JurisprudenceSource]
    metadata: Dict[str, Any]
    errors: List[str]


# ============================================================================
# SECTION 6: JURISPRUDENCE RESEARCH AGENT
# ============================================================================

class JurisprudenceAgent:
    """
    Agente de pesquisa de jurisprudencia brasileira com loop iterativo.

    Executa multiplas rodadas de pesquisa em sites de tribunais:
    1. Decompoe tema em sub-vetores juridicos
    2. Adiciona restricao de sites (whitelist) nas queries
    3. Acumula fontes e informacoes
    4. Analisa lacunas e refina queries
    5. Sintetiza relatorio final
    """

    def __init__(self, config: Optional[JurisprudenceConfig] = None):
        self.config = config or JurisprudenceConfig()
        self.logger = setup_logging(self.config)

        # State
        self._agent: Optional[Agent] = None
        self._session_service: Optional[InMemorySessionService] = None
        self._runner: Optional[Runner] = None
        self._session = None

        # Research state (reset per research call)
        self._collected_sources: Set[JurisprudenceSource] = set()
        self._collected_info: List[str] = []
        self._executed_queries: Set[str] = set()

        self.logger.info(f"JurisprudenceAgent initialized | Model: {self.config.model_name}")
        self.logger.info(f"Target domains: {', '.join(self.config.court_domains)}")

    def _build_site_restriction(self) -> str:
        """Build site: restriction clause for Google queries."""
        if not self.config.court_domains:
            return ""

        site_clauses = [f"site:{domain}" for domain in self.config.court_domains]
        return f"({' OR '.join(site_clauses)})"

    def _add_site_restriction(self, query: str) -> str:
        """Add site restriction to a query."""
        restriction = self._build_site_restriction()
        if restriction:
            return f"{query} {restriction}"
        return query

    async def _initialize_agent(self) -> None:
        """Lazy initialization of the ADK agent."""
        if self._agent is not None:
            return

        self.logger.info("Initializing Google ADK agent...")

        self._agent = Agent(
            name="jurisprudence_research_agent",
            model=self.config.model_name,
            description="Jurisprudence research agent for Brazilian courts",
            instruction=(
                "Voce eh um assistente de pesquisa juridica. "
                "Execute queries de busca e retorne os achados principais. "
                "Foque em jurisprudencia, sumulas e teses de tribunais brasileiros."
            ),
            tools=[google_search],
        )

        self._session_service = InMemorySessionService()
        self._session = await self._session_service.create_session(
            app_name=self.config.app_name,
            user_id=self.config.user_id,
            session_id=self.config.session_id
        )

        self._runner = Runner(
            agent=self._agent,
            app_name=self.config.app_name,
            session_service=self._session_service
        )

        self.logger.info("Agent initialization complete")

    async def research(self, topic: str) -> ResearchResult:
        """
        Execute iterative jurisprudence research on a topic.

        Args:
            topic: The legal research topic

        Returns:
            ResearchResult with all collected jurisprudence
        """
        # Reset state
        self._collected_sources = set()
        self._collected_info = []
        self._executed_queries = set()

        result = ResearchResult(
            topic=topic,
            content="",
            iterations=[],
            all_sources=[],
            metadata={
                "start_time": datetime.now().isoformat(),
                "end_time": None,
                "model": self.config.model_name,
                "session_id": self.config.session_id,
                "court_domains": self.config.court_domains,
                "total_iterations": 0,
                "total_queries": 0,
                "total_sources": 0,
                "stopped_by": None
            },
            errors=[]
        )

        self.logger.info(f"Starting jurisprudence research | Topic: {topic[:100]}...")

        try:
            await self._initialize_agent()

            # Phase 1: Decompose topic
            self.logger.info("Phase 1: Decompondo tema em sub-vetores juridicos...")
            subtopics = await self._decompose_topic(topic)
            self.logger.info(f"Generated {len(subtopics)} sub-topics")

            # Initial queries from subtopics
            current_queries = subtopics[:self.config.max_subtopics]

            # Iteration loop
            for iteration in range(1, self.config.max_iterations + 1):
                self.logger.info(f"=== Iteracao {iteration}/{self.config.max_iterations} ===")

                # Phase 2: Execute searches with site restrictions
                iter_result = await self._search_iteration(
                    queries=current_queries,
                    iteration=iteration,
                    topic=topic
                )
                result.iterations.append(iter_result)

                # Check stopping criteria
                stop_reason = self._check_stopping_criteria(iter_result)
                if stop_reason:
                    self.logger.info(f"Stopping: {stop_reason}")
                    result.metadata["stopped_by"] = stop_reason
                    break

                # Phase 3 & 4: Gap analysis and query refinement
                self.logger.info("Analisando lacunas e refinando queries...")
                gap_result = await self._analyze_gaps(topic)

                if gap_result["saturation_score"] >= self.config.saturation_threshold:
                    self.logger.info(f"Saturacao atingida: {gap_result['saturation_score']:.2f}")
                    result.metadata["stopped_by"] = "saturation"
                    break

                # Get new queries from gap analysis
                current_queries = [
                    q for q in gap_result.get("new_queries", [])
                    if q not in self._executed_queries
                ][:10]

                if not current_queries:
                    self.logger.info("Sem novas queries para executar")
                    result.metadata["stopped_by"] = "no_new_queries"
                    break

            # Phase 5: Final synthesis
            self.logger.info("Phase 5: Sintetizando relatorio final...")
            result.content = await self._synthesize_final(topic)

            # Compile results
            result.all_sources = list(self._collected_sources)
            result.metadata["end_time"] = datetime.now().isoformat()
            result.metadata["total_iterations"] = len(result.iterations)
            result.metadata["total_queries"] = len(self._executed_queries)
            result.metadata["total_sources"] = len(self._collected_sources)

            self.logger.info(
                f"Pesquisa completa | Iteracoes: {len(result.iterations)} | "
                f"Fontes: {len(self._collected_sources)} | "
                f"Queries: {len(self._executed_queries)}"
            )

        except Exception as e:
            error_msg = f"{type(e).__name__}: {e}"
            result.errors.append(error_msg)
            self.logger.error(f"Research failed: {error_msg}", exc_info=True)
            result.metadata["end_time"] = datetime.now().isoformat()
            result.metadata["stopped_by"] = "error"

        return result

    async def _decompose_topic(self, topic: str) -> List[str]:
        """Decompose topic into searchable sub-vectors."""
        prompt = DECOMPOSITION_PROMPT.format(topic=topic)

        try:
            response = await self._execute_prompt(prompt)
            # Parse JSON response
            subtopics = json.loads(response.strip())
            if isinstance(subtopics, list):
                return subtopics
        except (json.JSONDecodeError, Exception) as e:
            self.logger.warning(f"Failed to parse decomposition: {e}")

        # Fallback: generate basic queries
        return [
            f"{topic} jurisprudencia STJ",
            f"{topic} jurisprudencia tribunal de justica",
            f"{topic} sumula",
            f"{topic} acordao",
            f"{topic} tese firmada"
        ]

    async def _search_iteration(
        self,
        queries: List[str],
        iteration: int,
        topic: str
    ) -> IterationResult:
        """Execute a single search iteration with site restrictions."""
        iter_result = IterationResult(
            iteration=iteration,
            queries_executed=[],
            sources_found=[],
            gaps_identified=[],
            saturation_score=0.0
        )

        for query in queries:
            if query in self._executed_queries:
                continue

            # Add site restriction to query
            restricted_query = self._add_site_restriction(query)
            self.logger.debug(f"Executing: {restricted_query[:80]}...")

            try:
                # Execute search via agent
                search_prompt = (
                    f"Pesquise: {restricted_query}\n\n"
                    "Retorne os principais achados com URLs das fontes. "
                    "Foque em acordaos, sumulas e teses de tribunais."
                )
                response, sources = await self._execute_search(search_prompt)

                self._executed_queries.add(query)
                iter_result.queries_executed.append(query)

                # Collect sources with metadata extraction
                for source in sources:
                    self._enrich_source(source, query, iteration)
                    if source not in self._collected_sources:
                        self._collected_sources.add(source)
                        iter_result.sources_found.append(source)

                # Collect information
                if response:
                    self._collected_info.append(f"Query: {query}\n{response}")

            except Exception as e:
                self.logger.warning(f"Query failed: {query[:50]} - {e}")

        self.logger.info(
            f"Iteracao {iteration}: {len(iter_result.queries_executed)} queries, "
            f"{len(iter_result.sources_found)} novas fontes"
        )

        return iter_result

    def _enrich_source(self, source: JurisprudenceSource, query: str, iteration: int) -> None:
        """Extract jurisprudence metadata from source."""
        source.query = query
        source.iteration = iteration

        # Determine tribunal from URL
        for key, info in COURT_DOMAINS.items():
            if info["domain"] in source.url:
                source.tribunal = key.upper()
                break

        # Extract process number from title/snippet
        text = f"{source.title} {source.snippet}"

        # CNJ format: 1234567-89.2020.8.26.0100
        cnj_match = re.search(r"(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})", text)
        if cnj_match:
            source.numero_processo = cnj_match.group(1)
        else:
            # STJ format: REsp 1234567/SP
            stj_match = re.search(
                r"(REsp|AgInt|AgRg|HC|RHC|MS|RMS|EREsp)\s*[\d\./-]+(/[A-Z]{2})?",
                text
            )
            if stj_match:
                source.numero_processo = stj_match.group()

        # Extract date
        date_match = re.search(r"(\d{2}/\d{2}/\d{4})", text)
        if date_match:
            source.data_julgamento = date_match.group(1)

        # Extract relator
        relator_match = re.search(
            r"(?:Relator|Min\.|Ministro|Des\.)[:\s]+([A-Z][a-zA-Z\s]+?)(?:\s*[-,;]|$)",
            text
        )
        if relator_match:
            source.relator = relator_match.group(1).strip()

    async def _analyze_gaps(self, topic: str) -> Dict[str, Any]:
        """Analyze collected information and identify gaps."""
        collected_summary = "\n\n---\n\n".join(self._collected_info[-20:])

        prompt = GAP_ANALYSIS_PROMPT.format(
            collected_info=collected_summary,
            topic=topic
        )

        try:
            response = await self._execute_prompt(prompt)
            result = json.loads(response.strip())
            return result
        except (json.JSONDecodeError, Exception) as e:
            self.logger.warning(f"Failed to parse gap analysis: {e}")
            return {
                "coverage_summary": "",
                "gaps": [],
                "new_queries": [],
                "saturation_score": 0.5
            }

    async def _synthesize_final(self, topic: str) -> str:
        """Synthesize all collected information into final report."""
        research_data = {
            "sources": [
                {
                    "url": s.url,
                    "title": s.title,
                    "tribunal": s.tribunal,
                    "processo": s.numero_processo,
                    "snippet": s.snippet
                }
                for s in list(self._collected_sources)[:50]
            ],
            "collected_info": self._collected_info[:30]
        }

        prompt = SYNTHESIS_PROMPT.format(
            research_data=json.dumps(research_data, indent=2, ensure_ascii=False),
            topic=topic
        )

        try:
            response = await self._execute_prompt(prompt)
            return response
        except Exception as e:
            self.logger.error(f"Synthesis failed: {e}")
            return "\n\n".join(self._collected_info)

    async def _execute_prompt(self, prompt: str) -> str:
        """Execute a prompt and return the text response."""
        content = types.Content(
            role="user",
            parts=[types.Part(text=prompt)]
        )

        final_response = ""

        async for event in self._runner.run_async(
            user_id=self.config.user_id,
            session_id=self.config.session_id,
            new_message=content
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response = event.content.parts[0].text

        return final_response

    async def _execute_search(self, prompt: str) -> tuple[str, List[JurisprudenceSource]]:
        """Execute a search prompt and return response + sources."""
        content = types.Content(
            role="user",
            parts=[types.Part(text=prompt)]
        )

        final_response = ""
        sources = []

        async for event in self._runner.run_async(
            user_id=self.config.user_id,
            session_id=self.config.session_id,
            new_message=content
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response = event.content.parts[0].text

            # Extract grounding metadata
            if hasattr(event, 'grounding_metadata') and event.grounding_metadata:
                gm = event.grounding_metadata
                if hasattr(gm, 'grounding_chunks'):
                    for chunk in gm.grounding_chunks:
                        if hasattr(chunk, 'web') and chunk.web:
                            sources.append(JurisprudenceSource(
                                url=chunk.web.uri,
                                title=getattr(chunk.web, 'title', 'Unknown'),
                                snippet=getattr(chunk.web, 'snippet', '')
                            ))

        return final_response, sources

    def _check_stopping_criteria(self, iter_result: IterationResult) -> Optional[str]:
        """Check if research should stop."""
        if len(self._collected_sources) >= self.config.min_sources:
            return f"min_sources_reached ({len(self._collected_sources)} >= {self.config.min_sources})"

        if len(iter_result.sources_found) == 0 and iter_result.iteration > 1:
            return "no_new_sources"

        return None

    async def save_results(self, result: ResearchResult, filename: Optional[str] = None) -> Path:
        """Save research results to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_topic = "".join(c for c in result.topic[:50] if c.isalnum() or c in " -_").strip()
            safe_topic = safe_topic.replace(" ", "_")
            filename = f"jurisprudence_{safe_topic}_{timestamp}"

        output_path = self.config.output_dir / f"{filename}.md"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# Pesquisa de Jurisprudencia: {result.topic}\n\n")
            f.write(f"**Gerado em:** {result.metadata['start_time']}\n")
            f.write(f"**Modelo:** {result.metadata['model']}\n")
            f.write(f"**Iteracoes:** {result.metadata['total_iterations']}\n")
            f.write(f"**Total de Fontes:** {result.metadata['total_sources']}\n")
            f.write(f"**Total de Queries:** {result.metadata['total_queries']}\n")
            f.write(f"**Dominios:** {', '.join(result.metadata['court_domains'])}\n")
            f.write(f"**Parou por:** {result.metadata.get('stopped_by', 'completo')}\n\n")
            f.write("---\n\n")
            f.write(result.content)
            f.write("\n\n---\n\n")
            f.write("## Resumo das Iteracoes\n\n")
            for ir in result.iterations:
                f.write(f"### Iteracao {ir.iteration}\n")
                f.write(f"- Queries executadas: {len(ir.queries_executed)}\n")
                f.write(f"- Novas fontes: {len(ir.sources_found)}\n\n")
            f.write("## Todas as Fontes\n\n")
            f.write("| # | Tribunal | Processo | Titulo | URL |\n")
            f.write("|---|----------|----------|--------|-----|\n")
            for i, s in enumerate(result.all_sources, 1):
                title_short = s.title[:50] + "..." if len(s.title) > 50 else s.title
                f.write(
                    f"| {i} | {s.tribunal or 'N/A'} | {s.numero_processo or 'N/A'} | "
                    f"{title_short} | [link]({s.url}) |\n"
                )
            if result.errors:
                f.write("\n## Erros\n\n")
                for e in result.errors:
                    f.write(f"- {e}\n")

        self.logger.info(f"Resultados salvos em: {output_path}")
        return output_path


# ============================================================================
# SECTION 7: MAIN EXECUTION
# ============================================================================

async def main():
    """Main entry point for the Jurisprudence Research Agent."""
    if len(sys.argv) < 2:
        print("Uso: python agent.py \"Seu tema de pesquisa juridica\"")
        print("\nExemplo:")
        print('  python agent.py "Responsabilidade civil por dano moral em relacoes de consumo"')
        print("\nDominios disponiveis:")
        for key, info in COURT_DOMAINS.items():
            print(f"  {key}: {info['name']} ({info['domain']})")
        sys.exit(1)

    topic = " ".join(sys.argv[1:])

    # Verify API key
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_GENAI_API_KEY")
    if not api_key:
        print("[ERRO] Chave API nao encontrada. Configure GOOGLE_API_KEY.")
        sys.exit(1)

    # Initialize and run
    config = JurisprudenceConfig(
        model_name="gemini-2.5-flash",
        output_format="markdown",
        max_iterations=5,
        min_sources=15,
        saturation_threshold=0.8,
        court_domains=DEFAULT_DOMAINS
    )

    agent = JurisprudenceAgent(config)

    print(f"\n{'='*60}")
    print("JURISPRUDENCE RESEARCH AGENT")
    print(f"{'='*60}")
    print(f"Tema: {topic}")
    print(f"Modelo: {config.model_name}")
    print(f"Max Iteracoes: {config.max_iterations}")
    print(f"Min Fontes: {config.min_sources}")
    print(f"Dominios: {', '.join(config.court_domains)}")
    print(f"Output: {config.output_dir}")
    print(f"{'='*60}\n")

    result = await agent.research(topic)
    output_path = await agent.save_results(result)

    print(f"\n{'='*60}")
    print("PESQUISA COMPLETA")
    print(f"{'='*60}")
    print(f"Output salvo em: {output_path}")
    print(f"Iteracoes: {result.metadata['total_iterations']}")
    print(f"Total queries: {result.metadata['total_queries']}")
    print(f"Total fontes: {result.metadata['total_sources']}")
    print(f"Parou por: {result.metadata.get('stopped_by', 'completo')}")
    print(f"Erros: {len(result.errors)}")
    print(f"{'='*60}\n")

    if result.content:
        preview = result.content[:500]
        print("Preview:\n")
        print(preview)
        if len(result.content) > 500:
            print(f"\n... [{len(result.content) - 500} mais caracteres]")


if __name__ == "__main__":
    asyncio.run(main())
