#!/usr/bin/env python3
"""
================================================================================
ITERATIVE DEEP RESEARCH AGENT
================================================================================

Agente de pesquisa com loop iterativo que simula Deep Research real.

Diferente do agente single-pass, este agente:
1. Decompoe o topico em sub-vetores
2. Executa pesquisas em multiplas iteracoes
3. Analisa lacunas apos cada rodada
4. Refina queries baseado no que falta
5. Para quando atinge criterio (min_sources, max_iterations, ou saturacao)

Author: Lex-Vector Team
Version: 1.0.0
License: MIT

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
# SECTION 1: SYSTEM PROMPTS
# ============================================================================

DECOMPOSITION_PROMPT = """You are a Research Planner. Your task is to decompose a research topic into specific sub-vectors (aspects to investigate).

RULES:
- Generate 5-15 sub-topics that together cover the main topic comprehensively
- Each sub-topic should be specific and searchable
- Focus on different angles: technical details, comparisons, use cases, limitations, history, future
- Output ONLY a JSON array of strings, no other text

EXAMPLE:
Topic: "LLM inference optimization"
Output:
["LLM inference latency benchmarks", "KV cache optimization techniques", "batching strategies for LLM serving", "quantization methods INT8 INT4", "speculative decoding implementation", "vLLM vs TensorRT-LLM comparison", "memory optimization GPU inference", "token throughput optimization"]

Now decompose this topic:
TOPIC: {topic}

Output:"""

GAP_ANALYSIS_PROMPT = """You are a Research Analyst reviewing collected information to identify gaps.

COLLECTED INFORMATION:
{collected_info}

ORIGINAL TOPIC: {topic}

TASK:
1. Analyze what has been covered
2. Identify what is MISSING or underexplored
3. Suggest specific new search queries to fill gaps

Output a JSON object with this structure:
{{
    "coverage_summary": "Brief summary of what's been covered",
    "gaps": ["gap1", "gap2", ...],
    "new_queries": ["specific query 1", "specific query 2", ...],
    "saturation_score": 0.0-1.0  // 1.0 means fully saturated, no new info possible
}}

Output ONLY the JSON, no other text."""

SYNTHESIS_PROMPT = """You are a Technical Research Analyst. Synthesize all collected research into a comprehensive report.

RESEARCH DATA:
{research_data}

ORIGINAL TOPIC: {topic}

OUTPUT REQUIREMENTS:
1. NO journalistic introductions or conclusions
2. Lead with data and facts
3. Use tables for comparative data
4. Include source citations inline
5. Note any conflicting information found

FORMAT:
## Key Findings
- [Fact with source]

## Technical Details
| Aspect | Details | Source |
|--------|---------|--------|

## Limitations & Gaps
- [What wasn't found]

## Source Index
1. [URL] - [Brief description]

Begin synthesis:"""


# ============================================================================
# SECTION 2: CONFIGURATION
# ============================================================================

@dataclass
class IterativeResearchConfig:
    """Configuration for the Iterative Deep Research Agent."""

    # Iteration controls
    max_iterations: int = 5
    min_sources: int = 20
    saturation_threshold: float = 0.8

    # Depth controls
    queries_per_subtopic: int = 3
    max_subtopics: int = 15

    # Model configuration
    model_name: str = "gemini-2.5-flash"

    # Session identifiers
    app_name: str = "iterative_research_agent"
    user_id: str = "researcher"
    session_id: str = field(default_factory=lambda: f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

    # Output settings
    output_dir: Path = field(default_factory=lambda: Path("./research_output"))
    output_format: str = "markdown"

    # Retry configuration
    max_retries: int = 3
    retry_delay_base: float = 1.0
    retry_delay_max: float = 30.0

    # Logging
    log_level: str = "INFO"

    def __post_init__(self):
        self.output_dir = Path(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)


# ============================================================================
# SECTION 3: LOGGING
# ============================================================================

def setup_logging(config: IterativeResearchConfig) -> logging.Logger:
    """Configure structured logging."""
    logger = logging.getLogger("IterativeResearchAgent")
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

    log_file = config.output_dir / f"iterative_research_{config.session_id}.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s | %(funcName)s:%(lineno)d | %(message)s"
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    return logger


# ============================================================================
# SECTION 4: DATA STRUCTURES
# ============================================================================

@dataclass
class Source:
    """Represents a research source."""
    url: str
    title: str
    snippet: str = ""
    query: str = ""
    iteration: int = 0

    def __hash__(self):
        return hash(self.url)

    def __eq__(self, other):
        return isinstance(other, Source) and self.url == other.url


@dataclass
class IterationResult:
    """Result of a single research iteration."""
    iteration: int
    queries_executed: List[str]
    sources_found: List[Source]
    gaps_identified: List[str]
    saturation_score: float
    raw_response: str = ""


@dataclass
class ResearchResult:
    """Final research result."""
    topic: str
    content: str
    iterations: List[IterationResult]
    all_sources: List[Source]
    metadata: Dict[str, Any]
    errors: List[str]


# ============================================================================
# SECTION 5: ITERATIVE RESEARCH AGENT
# ============================================================================

class IterativeResearchAgent:
    """
    Agente de pesquisa iterativo com loop de refinamento.

    Executa multiplas rodadas de pesquisa, cada uma:
    1. Identifica lacunas no conhecimento coletado
    2. Gera novas queries para preencher lacunas
    3. Acumula fontes e informacoes
    4. Para quando atinge criterio de parada
    """

    def __init__(self, config: Optional[IterativeResearchConfig] = None):
        self.config = config or IterativeResearchConfig()
        self.logger = setup_logging(self.config)

        # State
        self._agent: Optional[Agent] = None
        self._session_service: Optional[InMemorySessionService] = None
        self._runner: Optional[Runner] = None
        self._session = None

        # Research state (reset per research call)
        self._collected_sources: Set[Source] = set()
        self._collected_info: List[str] = []
        self._executed_queries: Set[str] = set()

        self.logger.info(f"IterativeResearchAgent initialized | Model: {self.config.model_name}")

    async def _initialize_agent(self) -> None:
        """Lazy initialization of the ADK agent."""
        if self._agent is not None:
            return

        self.logger.info("Initializing Google ADK agent...")

        self._agent = Agent(
            name="iterative_research_agent",
            model=self.config.model_name,
            description="Iterative research agent with loop refinement",
            instruction="You are a research assistant. Execute search queries and report findings.",
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
        Execute iterative deep research on a topic.

        Args:
            topic: The research topic

        Returns:
            ResearchResult with all collected information
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
                "total_iterations": 0,
                "total_queries": 0,
                "total_sources": 0,
                "stopped_by": None
            },
            errors=[]
        )

        self.logger.info(f"Starting iterative research | Topic: {topic[:100]}...")

        try:
            await self._initialize_agent()

            # Phase 1: Decompose topic
            self.logger.info("Phase 1: Decomposing topic into sub-vectors...")
            subtopics = await self._decompose_topic(topic)
            self.logger.info(f"Generated {len(subtopics)} sub-topics")

            # Initial queries from subtopics
            current_queries = subtopics[:self.config.max_subtopics]

            # Iteration loop
            for iteration in range(1, self.config.max_iterations + 1):
                self.logger.info(f"=== Iteration {iteration}/{self.config.max_iterations} ===")

                # Phase 2: Execute searches
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
                self.logger.info("Analyzing gaps and refining queries...")
                gap_result = await self._analyze_gaps(topic)

                if gap_result["saturation_score"] >= self.config.saturation_threshold:
                    self.logger.info(f"Saturation reached: {gap_result['saturation_score']:.2f}")
                    result.metadata["stopped_by"] = "saturation"
                    break

                # Get new queries from gap analysis
                current_queries = [
                    q for q in gap_result.get("new_queries", [])
                    if q not in self._executed_queries
                ][:10]

                if not current_queries:
                    self.logger.info("No new queries to execute")
                    result.metadata["stopped_by"] = "no_new_queries"
                    break

            # Phase 5: Final synthesis
            self.logger.info("Phase 5: Synthesizing final report...")
            result.content = await self._synthesize_final(topic)

            # Compile results
            result.all_sources = list(self._collected_sources)
            result.metadata["end_time"] = datetime.now().isoformat()
            result.metadata["total_iterations"] = len(result.iterations)
            result.metadata["total_queries"] = len(self._executed_queries)
            result.metadata["total_sources"] = len(self._collected_sources)

            self.logger.info(
                f"Research complete | Iterations: {len(result.iterations)} | "
                f"Sources: {len(self._collected_sources)} | "
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
            f"{topic} overview",
            f"{topic} technical details",
            f"{topic} comparison",
            f"{topic} use cases",
            f"{topic} limitations"
        ]

    async def _search_iteration(
        self,
        queries: List[str],
        iteration: int,
        topic: str
    ) -> IterationResult:
        """Execute a single search iteration."""
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

            self.logger.debug(f"Executing query: {query}")

            try:
                # Execute search via agent
                search_prompt = f"Search for: {query}\n\nReturn the key findings with source URLs."
                response, sources = await self._execute_search(search_prompt)

                self._executed_queries.add(query)
                iter_result.queries_executed.append(query)

                # Collect sources
                for source in sources:
                    source.query = query
                    source.iteration = iteration
                    if source not in self._collected_sources:
                        self._collected_sources.add(source)
                        iter_result.sources_found.append(source)

                # Collect information
                if response:
                    self._collected_info.append(f"Query: {query}\n{response}")

            except Exception as e:
                self.logger.warning(f"Query failed: {query} - {e}")

        self.logger.info(
            f"Iteration {iteration}: {len(iter_result.queries_executed)} queries, "
            f"{len(iter_result.sources_found)} new sources"
        )

        return iter_result

    async def _analyze_gaps(self, topic: str) -> Dict[str, Any]:
        """Analyze collected information and identify gaps."""
        collected_summary = "\n\n---\n\n".join(self._collected_info[-20:])  # Last 20 items

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
        # Prepare research data
        research_data = {
            "sources": [
                {"url": s.url, "title": s.title, "snippet": s.snippet}
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
            # Fallback: return raw collected info
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

    async def _execute_search(self, prompt: str) -> tuple[str, List[Source]]:
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
                            sources.append(Source(
                                url=chunk.web.uri,
                                title=getattr(chunk.web, 'title', 'Unknown'),
                                snippet=getattr(chunk.web, 'snippet', '')
                            ))

        return final_response, sources

    def _check_stopping_criteria(self, iter_result: IterationResult) -> Optional[str]:
        """Check if research should stop."""
        # Check min_sources
        if len(self._collected_sources) >= self.config.min_sources:
            return f"min_sources_reached ({len(self._collected_sources)} >= {self.config.min_sources})"

        # Check if iteration found no new sources (potential saturation)
        if len(iter_result.sources_found) == 0 and iter_result.iteration > 1:
            return "no_new_sources"

        return None

    async def save_results(self, result: ResearchResult, filename: Optional[str] = None) -> Path:
        """Save research results to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_topic = "".join(c for c in result.topic[:50] if c.isalnum() or c in " -_").strip()
            safe_topic = safe_topic.replace(" ", "_")
            filename = f"iterative_research_{safe_topic}_{timestamp}"

        if self.config.output_format == "json":
            output_path = self.config.output_dir / f"{filename}.json"
            with open(output_path, "w", encoding="utf-8") as f:
                data = {
                    "topic": result.topic,
                    "content": result.content,
                    "metadata": result.metadata,
                    "sources": [
                        {"url": s.url, "title": s.title, "snippet": s.snippet}
                        for s in result.all_sources
                    ],
                    "iterations": [
                        {
                            "iteration": ir.iteration,
                            "queries": ir.queries_executed,
                            "sources_count": len(ir.sources_found)
                        }
                        for ir in result.iterations
                    ],
                    "errors": result.errors
                }
                json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            output_path = self.config.output_dir / f"{filename}.md"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"# Iterative Research: {result.topic}\n\n")
                f.write(f"**Generated:** {result.metadata['start_time']}\n")
                f.write(f"**Model:** {result.metadata['model']}\n")
                f.write(f"**Iterations:** {result.metadata['total_iterations']}\n")
                f.write(f"**Total Sources:** {result.metadata['total_sources']}\n")
                f.write(f"**Total Queries:** {result.metadata['total_queries']}\n")
                f.write(f"**Stopped By:** {result.metadata.get('stopped_by', 'completed')}\n\n")
                f.write("---\n\n")
                f.write(result.content)
                f.write("\n\n---\n\n")
                f.write("## Iteration Summary\n\n")
                for ir in result.iterations:
                    f.write(f"### Iteration {ir.iteration}\n")
                    f.write(f"- Queries: {len(ir.queries_executed)}\n")
                    f.write(f"- New Sources: {len(ir.sources_found)}\n\n")
                f.write("## All Sources\n\n")
                for i, s in enumerate(result.all_sources, 1):
                    f.write(f"{i}. [{s.title}]({s.url})\n")
                if result.errors:
                    f.write("\n## Errors\n\n")
                    for e in result.errors:
                        f.write(f"- {e}\n")

        self.logger.info(f"Results saved to: {output_path}")
        return output_path


# ============================================================================
# SECTION 6: MAIN EXECUTION
# ============================================================================

async def main():
    """Main entry point for the Iterative Deep Research Agent."""
    if len(sys.argv) < 2:
        print("Usage: python iterative_research_agent.py \"Your research topic\"")
        print("\nExample:")
        print('  python iterative_research_agent.py "Comparison of LLM inference frameworks"')
        sys.exit(1)

    topic = " ".join(sys.argv[1:])

    # Verify API key
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_GENAI_API_KEY")
    if not api_key:
        print("[ERROR] No API key found. Set GOOGLE_API_KEY environment variable.")
        sys.exit(1)

    # Initialize and run
    config = IterativeResearchConfig(
        model_name="gemini-2.5-flash",
        output_format="markdown",
        max_iterations=5,
        min_sources=20,
        saturation_threshold=0.8
    )

    agent = IterativeResearchAgent(config)

    print(f"\n{'='*60}")
    print("ITERATIVE DEEP RESEARCH AGENT")
    print(f"{'='*60}")
    print(f"Topic: {topic}")
    print(f"Model: {config.model_name}")
    print(f"Max Iterations: {config.max_iterations}")
    print(f"Min Sources: {config.min_sources}")
    print(f"Output: {config.output_dir}")
    print(f"{'='*60}\n")

    result = await agent.research(topic)
    output_path = await agent.save_results(result)

    print(f"\n{'='*60}")
    print("RESEARCH COMPLETE")
    print(f"{'='*60}")
    print(f"Output saved to: {output_path}")
    print(f"Iterations: {result.metadata['total_iterations']}")
    print(f"Total queries: {result.metadata['total_queries']}")
    print(f"Total sources: {result.metadata['total_sources']}")
    print(f"Stopped by: {result.metadata.get('stopped_by', 'completed')}")
    print(f"Errors: {len(result.errors)}")
    print(f"{'='*60}\n")

    if result.content:
        preview = result.content[:500]
        print("Preview:\n")
        print(preview)
        if len(result.content) > 500:
            print(f"\n... [{len(result.content) - 500} more characters]")


if __name__ == "__main__":
    asyncio.run(main())
