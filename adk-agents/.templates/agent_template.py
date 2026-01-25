#!/usr/bin/env python3
"""
================================================================================
{{AGENT_NAME_UPPER}} AGENT
================================================================================

{{AGENT_DESCRIPTION}}

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
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field

# =============================================================================
# IMPORTS: GOOGLE ADK
# =============================================================================

try:
    from google.adk.agents import Agent
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types
except ImportError as e:
    print(f"[FATAL] Missing Google ADK core: {e}")
    print("Install with: pip install google-adk google-genai")
    sys.exit(1)

# =============================================================================
# IMPORTS: BUILT-IN TOOLS (uncomment as needed)
# =============================================================================

# --- Google Search (web search with grounding) ---
from google.adk.tools import google_search

# --- Code Execution (run code in sandbox) ---
# from google.adk.tools import code_execution

# --- Computer Use (UI automation - Gemini 2.0+) ---
# from google.adk.tools import computer_use

# =============================================================================
# IMPORTS: GOOGLE CLOUD TOOLS (uncomment as needed)
# =============================================================================

# --- BigQuery ---
# from google.adk.tools.bigquery import BigQueryTool
# bq_tool = BigQueryTool(project_id="your-project", dataset_id="your-dataset")

# --- Vertex AI RAG Engine ---
# from google.adk.tools.vertex_ai_rag_retrieval import VertexAiRagRetrieval
# rag_tool = VertexAiRagRetrieval(rag_corpus="projects/.../ragCorpora/...")

# --- Vertex AI Search ---
# from google.adk.tools.vertex_ai_search import VertexAiSearchTool
# search_tool = VertexAiSearchTool(data_store_id="your-data-store")

# --- Spanner ---
# from google.adk.tools.spanner import SpannerTool
# spanner_tool = SpannerTool(instance_id="...", database_id="...")

# --- GKE Code Executor (secure sandbox) ---
# from google.adk.tools.gke_code_executor import GkeCodeExecutor
# gke_executor = GkeCodeExecutor(cluster_name="...", namespace="...")

# =============================================================================
# IMPORTS: MCP TOOLS (Model Context Protocol)
# =============================================================================

# --- MCP Toolset (connect to MCP servers) ---
# from google.adk.tools.mcp_tool import MCPToolset
# mcp_tools = MCPToolset.from_server(
#     connection_params={"url": "http://localhost:3000/mcp"},
#     tools=["search", "fetch_document", "execute_query"]
# )

# --- MCP Toolbox for Databases (30+ data sources) ---
# from google.adk.tools.mcp_toolbox import MCPToolbox
# db_tools = MCPToolbox(
#     sources=["postgresql://...", "mysql://...", "mongodb://..."]
# )

# =============================================================================
# IMPORTS: OPENAPI INTEGRATION
# =============================================================================

# --- Generate tools from OpenAPI spec ---
# from google.adk.tools.openapi import OpenAPIToolset
# api_tools = OpenAPIToolset.from_spec("https://api.example.com/openapi.json")

# =============================================================================
# IMPORTS: THIRD-PARTY INTEGRATIONS
# =============================================================================

# --- GitHub ---
# from google.adk.tools.github import GitHubTool
# github_tool = GitHubTool(token=os.getenv("GITHUB_TOKEN"))

# --- Notion ---
# from google.adk.tools.notion import NotionTool
# notion_tool = NotionTool(api_key=os.getenv("NOTION_API_KEY"))

# =============================================================================
# CUSTOM FUNCTION TOOLS
# =============================================================================

def create_function_tool(func: Callable) -> Callable:
    """
    Decorator para criar function tools customizados.

    O ADK usa a docstring e type hints para gerar o schema da tool.

    Exemplo:
        @create_function_tool
        def calculate_sum(a: int, b: int) -> int:
            '''Calcula a soma de dois numeros.

            Args:
                a: Primeiro numero
                b: Segundo numero

            Returns:
                A soma de a e b
            '''
            return a + b
    """
    return func


# Exemplo de function tool customizado (descomente e adapte)
# @create_function_tool
# def search_database(query: str, limit: int = 10) -> List[Dict[str, Any]]:
#     """Busca no banco de dados local.
#
#     Args:
#         query: Termo de busca
#         limit: Numero maximo de resultados
#
#     Returns:
#         Lista de resultados encontrados
#     """
#     # Implementar logica de busca
#     return [{"id": 1, "result": "exemplo"}]


try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# ============================================================================
# SECTION 1: SYSTEM PROMPTS
# ============================================================================

SYSTEM_PROMPT = """{{SYSTEM_PROMPT}}"""

SYNTHESIS_PROMPT = """You are a research analyst. Synthesize the collected information into a structured report.

COLLECTED DATA:
{collected_data}

TOPIC: {topic}

FORMAT:
## Key Findings
- [Finding with source]

## Details
| Aspect | Information | Source |
|--------|-------------|--------|

## Limitations
- [What wasn't found]

Begin synthesis:"""


# ============================================================================
# SECTION 2: CONFIGURATION
# ============================================================================

@dataclass
class {{AGENT_CLASS}}Config:
    """Configuration for {{AGENT_NAME}}.

    Tool Configuration:
        tools_enabled: List of tool names to enable. Options:
            - "google_search": Web search with grounding
            - "code_execution": Execute code in sandbox
            - "computer_use": UI automation (Gemini 2.0+)
            - "mcp": Model Context Protocol tools
            - "custom": Custom function tools
    """

    # Iteration controls
    max_iterations: int = 5
    min_sources: int = 15

    # Model configuration
    model_name: str = "gemini-2.5-flash"

    # Tool configuration
    tools_enabled: List[str] = field(default_factory=lambda: ["google_search"])

    # Session identifiers
    app_name: str = "{{AGENT_ID}}"
    user_id: str = "researcher"
    session_id: str = field(default_factory=lambda: f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

    # Output settings
    output_dir: Path = field(default_factory=lambda: Path("./research_output"))

    # MCP configuration (if using MCP tools)
    mcp_server_url: Optional[str] = None
    mcp_tools: Optional[List[str]] = None

    # Logging
    log_level: str = "INFO"

    def __post_init__(self):
        self.output_dir = Path(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)


# ============================================================================
# SECTION 3: LOGGING
# ============================================================================

def setup_logging(config: {{AGENT_CLASS}}Config) -> logging.Logger:
    """Configure structured logging."""
    logger = logging.getLogger("{{AGENT_CLASS}}")
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

    def __hash__(self):
        return hash(self.url)

    def __eq__(self, other):
        return isinstance(other, Source) and self.url == other.url


@dataclass
class ResearchResult:
    """Final research result."""
    topic: str
    content: str
    sources: List[Source]
    metadata: Dict[str, Any]
    errors: List[str]


# ============================================================================
# SECTION 5: TOOL BUILDER
# ============================================================================

def build_tools(config: {{AGENT_CLASS}}Config) -> List:
    """
    Build tool list based on configuration.

    IMPORTANTE: No ADK, cada root agent suporta apenas UM built-in tool.
    Para multiplos tools, use sub-agents ou function tools customizados.
    """
    tools = []

    for tool_name in config.tools_enabled:
        if tool_name == "google_search":
            tools.append(google_search)

        # Descomente conforme necessario:
        # elif tool_name == "code_execution":
        #     from google.adk.tools import code_execution
        #     tools.append(code_execution)
        #
        # elif tool_name == "computer_use":
        #     from google.adk.tools import computer_use
        #     tools.append(computer_use)
        #
        # elif tool_name == "mcp" and config.mcp_server_url:
        #     from google.adk.tools.mcp_tool import MCPToolset
        #     mcp = MCPToolset.from_server(
        #         connection_params={"url": config.mcp_server_url},
        #         tools=config.mcp_tools or []
        #     )
        #     tools.append(mcp)

    return tools


# ============================================================================
# SECTION 6: AGENT IMPLEMENTATION
# ============================================================================

class {{AGENT_CLASS}}:
    """
    {{AGENT_DESCRIPTION}}

    Tools disponiveis (configure em config.tools_enabled):
        - google_search: Busca web com grounding
        - code_execution: Executa codigo em sandbox
        - computer_use: Automacao de UI
        - mcp: Tools via Model Context Protocol
        - custom: Function tools customizados
    """

    def __init__(self, config: Optional[{{AGENT_CLASS}}Config] = None):
        self.config = config or {{AGENT_CLASS}}Config()
        self.logger = setup_logging(self.config)

        # State
        self._agent: Optional[Agent] = None
        self._session_service: Optional[InMemorySessionService] = None
        self._runner: Optional[Runner] = None

        # Research state
        self._collected_sources: set = set()
        self._collected_info: List[str] = []

        self.logger.info(f"{{AGENT_CLASS}} initialized | Model: {self.config.model_name}")
        self.logger.info(f"Tools enabled: {self.config.tools_enabled}")

    async def _initialize_agent(self) -> None:
        """Lazy initialization of the ADK agent."""
        if self._agent is not None:
            return

        self.logger.info("Initializing Google ADK agent...")

        # Build tools based on config
        tools = build_tools(self.config)

        self._agent = Agent(
            name="{{AGENT_ID}}",
            model=self.config.model_name,
            description="{{AGENT_DESCRIPTION}}",
            instruction=SYSTEM_PROMPT,
            tools=tools,
        )

        self._session_service = InMemorySessionService()
        await self._session_service.create_session(
            app_name=self.config.app_name,
            user_id=self.config.user_id,
            session_id=self.config.session_id
        )

        self._runner = Runner(
            agent=self._agent,
            app_name=self.config.app_name,
            session_service=self._session_service
        )

        self.logger.info(f"Agent initialization complete | Tools: {len(tools)}")

    async def research(self, topic: str) -> ResearchResult:
        """
        Execute research on a topic.

        Args:
            topic: The research topic

        Returns:
            ResearchResult with collected information
        """
        self._collected_sources = set()
        self._collected_info = []

        result = ResearchResult(
            topic=topic,
            content="",
            sources=[],
            metadata={
                "start_time": datetime.now().isoformat(),
                "model": self.config.model_name,
                "session_id": self.config.session_id,
                "tools_used": self.config.tools_enabled,
            },
            errors=[]
        )

        self.logger.info(f"Starting research | Topic: {topic[:100]}...")

        try:
            await self._initialize_agent()

            # Execute main research logic
            response = await self._execute_search(topic)
            result.content = response
            result.sources = list(self._collected_sources)
            result.metadata["end_time"] = datetime.now().isoformat()
            result.metadata["total_sources"] = len(self._collected_sources)

            self.logger.info(f"Research complete | Sources: {len(self._collected_sources)}")

        except Exception as e:
            error_msg = f"{type(e).__name__}: {e}"
            result.errors.append(error_msg)
            self.logger.error(f"Research failed: {error_msg}", exc_info=True)

        return result

    async def _execute_search(self, query: str) -> str:
        """Execute a search and return response."""
        content = types.Content(
            role="user",
            parts=[types.Part(text=query)]
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

            # Extract grounding metadata (from google_search)
            if hasattr(event, 'grounding_metadata') and event.grounding_metadata:
                gm = event.grounding_metadata
                if hasattr(gm, 'grounding_chunks'):
                    for chunk in gm.grounding_chunks:
                        if hasattr(chunk, 'web') and chunk.web:
                            self._collected_sources.add(Source(
                                url=chunk.web.uri,
                                title=getattr(chunk.web, 'title', 'Unknown'),
                                snippet=getattr(chunk.web, 'snippet', '')
                            ))

            # Extract tool call results (for custom tools)
            if hasattr(event, 'tool_calls') and event.tool_calls:
                for tool_call in event.tool_calls:
                    self.logger.debug(f"Tool call: {tool_call.name}")

        return final_response

    async def save_results(self, result: ResearchResult, filename: Optional[str] = None) -> Path:
        """Save research results to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_topic = "".join(c for c in result.topic[:30] if c.isalnum() or c in " -_")
            filename = f"{{AGENT_ID}}_{safe_topic}_{timestamp}"

        output_path = self.config.output_dir / f"{filename}.md"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# {{AGENT_NAME}}: {result.topic}\n\n")
            f.write(f"**Generated:** {result.metadata['start_time']}\n")
            f.write(f"**Model:** {result.metadata['model']}\n")
            f.write(f"**Tools:** {', '.join(result.metadata.get('tools_used', []))}\n")
            f.write(f"**Sources:** {result.metadata.get('total_sources', 0)}\n\n")
            f.write("---\n\n")
            f.write(result.content)
            f.write("\n\n---\n\n## Sources\n\n")
            for i, s in enumerate(result.sources, 1):
                f.write(f"{i}. [{s.title}]({s.url})\n")

        self.logger.info(f"Results saved to: {output_path}")
        return output_path


# ============================================================================
# SECTION 7: MAIN EXECUTION
# ============================================================================

async def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python agent.py \"Your research topic\"")
        print("")
        print("Options (set via environment):")
        print("  AGENT_MODEL=gemini-2.5-flash")
        print("  AGENT_TOOLS=google_search,code_execution")
        print("  MCP_SERVER_URL=http://localhost:3000/mcp")
        sys.exit(1)

    topic = " ".join(sys.argv[1:])

    # Verify API key
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_GENAI_API_KEY")
    if not api_key:
        print("[ERROR] No API key found. Set GOOGLE_API_KEY environment variable.")
        sys.exit(1)

    # Parse tools from environment
    tools_str = os.getenv("AGENT_TOOLS", "google_search")
    tools_enabled = [t.strip() for t in tools_str.split(",")]

    config = {{AGENT_CLASS}}Config(
        model_name=os.getenv("AGENT_MODEL", "gemini-2.5-flash"),
        tools_enabled=tools_enabled,
        mcp_server_url=os.getenv("MCP_SERVER_URL"),
    )
    agent = {{AGENT_CLASS}}(config)

    print(f"\n{'='*60}")
    print("{{AGENT_NAME_UPPER}} AGENT")
    print(f"{'='*60}")
    print(f"Topic: {topic}")
    print(f"Model: {config.model_name}")
    print(f"Tools: {', '.join(config.tools_enabled)}")
    print(f"{'='*60}\n")

    result = await agent.research(topic)
    output_path = await agent.save_results(result)

    print(f"\n{'='*60}")
    print("RESEARCH COMPLETE")
    print(f"{'='*60}")
    print(f"Output: {output_path}")
    print(f"Sources: {len(result.sources)}")
    print(f"{'='*60}\n")

    if result.content:
        print(result.content[:500])
        if len(result.content) > 500:
            print(f"\n... [{len(result.content) - 500} more chars]")


if __name__ == "__main__":
    asyncio.run(main())
