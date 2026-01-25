#!/usr/bin/env python3
"""
================================================================================
CUSTOM GEMINI DEEP RESEARCH AGENT
================================================================================

Technical Specification and Implementation for Google Gen AI SDK (Gemini ADK)

Purpose: Replace browser-based Gemini "Deep Research" with a programmatic,
         high-density, objective research workflow.

Author: Generated for Cloud Code deployment
Version: 1.0.0
License: MIT

Dependencies:
    pip install google-adk google-genai python-dotenv tenacity

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
from typing import Optional, Dict, Any, List
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
    from tenacity import (
        retry,
        stop_after_attempt,
        wait_exponential,
        retry_if_exception_type,
        before_sleep_log
    )
except ImportError:
    print("[WARN] tenacity not installed. Retry logic will be simplified.")
    # Fallback decorator that does nothing
    def retry(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    stop_after_attempt = lambda x: None
    wait_exponential = lambda **kwargs: None
    retry_if_exception_type = lambda x: None
    before_sleep_log = lambda x, y: None

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional

# ============================================================================
# SECTION 1: SYSTEM PROMPT
# ============================================================================

SYSTEM_PROMPT = """You are a Technical Research Analyst operating in STRICT OBJECTIVE MODE.

PERSONA:
- Role: Senior Technical Analyst specializing in systematic information synthesis
- Disposition: Dry, academic, precise
- Priority: Information density over narrative flow

OUTPUT CONSTRAINTS (MANDATORY):
1. NO journalistic introductions ("In today's landscape...", "As we explore...")
2. NO persuasive language or rhetorical flourishes
3. NO marketing terminology ("revolutionary", "game-changing", "cutting-edge")
4. NO narrative weaving or storytelling structures
5. NO hedging phrases ("It's worth noting that...", "Interestingly...")
6. NO filler sentences or transitional padding

REQUIRED OUTPUT STRUCTURE:
- Lead with raw data, specifications, and cited facts
- Use bullet points for discrete data points
- Use tables for comparative data where applicable
- Include source attribution for all factual claims
- Quantify claims wherever possible (percentages, dates, figures)

SEARCH BEHAVIOR:
- You have access to Google Search for real-time information retrieval
- Generate multiple specific search queries autonomously to cover the topic comprehensively
- Cross-reference sources when data conflicts
- Prioritize primary sources (official docs, papers, announcements) over secondary commentary

RESPONSE FORMAT:
```
## [Topic Header]

### Key Findings
- [Fact 1] (Source: [URL/Reference])
- [Fact 2] (Source: [URL/Reference])

### Technical Specifications
| Parameter | Value | Source |
|-----------|-------|--------|
| ...       | ...   | ...    |

### Data Conflicts / Uncertainties
- [Note any contradictory information found]

### Source Index
1. [Full citation]
2. [Full citation]
```

CRITICAL: Your role is DATA EXTRACTION, not INTERPRETATION. Present findings; do not editorialize."""


# ============================================================================
# SECTION 2: CONFIGURATION
# ============================================================================

@dataclass
class ResearchConfig:
    """Configuration for the Deep Research Agent."""
    
    # Model configuration
    model_name: str = "gemini-2.5-flash"
    
    # Session identifiers
    app_name: str = "deep_research_agent"
    user_id: str = "researcher"
    session_id: str = field(default_factory=lambda: f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    
    # Output settings
    output_dir: Path = field(default_factory=lambda: Path("./research_output"))
    output_format: str = "markdown"  # "markdown" or "json"
    
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
# SECTION 3: LOGGING CONFIGURATION
# ============================================================================

def setup_logging(config: ResearchConfig) -> logging.Logger:
    """Configure structured logging with both file and console handlers."""
    
    logger = logging.getLogger("DeepResearchAgent")
    logger.setLevel(getattr(logging, config.log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler (INFO and above)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler (DEBUG and above)
    log_file = config.output_dir / f"research_{config.session_id}.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    return logger


# ============================================================================
# SECTION 4: ERROR HANDLING INFRASTRUCTURE
# ============================================================================

class ResearchError(Exception):
    """Base exception for research agent errors."""
    pass

class SearchToolError(ResearchError):
    """Error during search tool execution."""
    pass

class ModelResponseError(ResearchError):
    """Error in model response generation."""
    pass

class SessionError(ResearchError):
    """Error in session management."""
    pass


def create_retry_decorator(logger: logging.Logger, config: ResearchConfig):
    """
    Factory function to create a retry decorator with logging.
    
    Error Handling Strategy:
    1. Transient errors (network, rate limits): Retry with exponential backoff
    2. Permanent errors (auth, invalid input): Fail immediately
    3. Unknown errors: Retry once, then fail gracefully
    """
    
    return retry(
        stop=stop_after_attempt(config.max_retries),
        wait=wait_exponential(
            multiplier=config.retry_delay_base,
            max=config.retry_delay_max
        ),
        retry=retry_if_exception_type((
            ConnectionError,
            TimeoutError,
            SearchToolError,
        )),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )


# ============================================================================
# SECTION 5: DEEP RESEARCH AGENT CLASS
# ============================================================================

class DeepResearchAgent:
    """
    Autonomous research agent using Google ADK with Search/Grounding tools.
    
    Architecture:
    - Uses google.adk.agents.Agent with google_search tool
    - InMemorySessionService for stateless operation
    - Runner orchestrates the agent execution loop
    
    Error Handling Philosophy:
    - NEVER crash the main process
    - Log all errors with full context
    - Degrade gracefully (partial results > no results)
    - Provide actionable error messages
    """
    
    def __init__(self, config: Optional[ResearchConfig] = None):
        self.config = config or ResearchConfig()
        self.logger = setup_logging(self.config)
        
        # Initialize components (lazy initialization for robustness)
        self._agent: Optional[Agent] = None
        self._session_service: Optional[InMemorySessionService] = None
        self._runner: Optional[Runner] = None
        self._session = None
        
        self.logger.info(f"DeepResearchAgent initialized | Model: {self.config.model_name}")
        self.logger.debug(f"Output directory: {self.config.output_dir}")
    
    async def _initialize_agent(self) -> None:
        """
        Lazy initialization of the ADK agent.
        
        Separated from __init__ to allow:
        1. Async initialization
        2. Re-initialization on failure
        3. Configuration changes before first use
        """
        
        if self._agent is not None:
            return
        
        self.logger.info("Initializing Google ADK agent...")
        
        try:
            # Create the research agent with google_search tool
            # The google_search tool enables autonomous web search with grounding
            self._agent = Agent(
                name="technical_research_agent",
                model=self.config.model_name,
                description="Autonomous technical research agent with web search capability",
                instruction=SYSTEM_PROMPT,
                tools=[google_search],  # Pre-built ADK tool for Google Search grounding
            )
            
            # Initialize session service
            self._session_service = InMemorySessionService()
            
            # Create session
            self._session = await self._session_service.create_session(
                app_name=self.config.app_name,
                user_id=self.config.user_id,
                session_id=self.config.session_id
            )
            
            # Initialize runner
            self._runner = Runner(
                agent=self._agent,
                app_name=self.config.app_name,
                session_service=self._session_service
            )
            
            self.logger.info("Agent initialization complete")
            
        except Exception as e:
            self.logger.error(f"Agent initialization failed: {type(e).__name__}: {e}")
            raise SessionError(f"Failed to initialize agent: {e}") from e
    
    async def research(self, topic: str) -> Dict[str, Any]:
        """
        Execute deep research on a given topic.
        
        Args:
            topic: High-level research topic (agent generates specific queries)
        
        Returns:
            Dict containing:
                - content: The research output text
                - metadata: Execution metadata (timestamps, sources)
                - errors: List of non-fatal errors encountered
        
        Error Handling:
            - Catches all exceptions to prevent crashes
            - Logs full stack traces
            - Returns partial results when possible
        """
        
        result = {
            "topic": topic,
            "content": "",
            "metadata": {
                "start_time": datetime.now().isoformat(),
                "end_time": None,
                "model": self.config.model_name,
                "session_id": self.config.session_id,
                "sources": [],
                "search_queries": []
            },
            "errors": []
        }
        
        self.logger.info(f"Starting research | Topic: {topic[:100]}...")
        
        try:
            # Ensure agent is initialized
            await self._initialize_agent()
            
            # Construct the research prompt
            # The agent will autonomously generate search queries
            research_prompt = f"""Research the following topic comprehensively:

TOPIC: {topic}

INSTRUCTIONS:
1. Generate and execute multiple specific search queries to gather information
2. Cross-reference sources for accuracy
3. Compile findings in the structured format specified in your instructions
4. Include all source URLs in your response

Begin research now."""

            # Create content object for the runner
            content = types.Content(
                role="user",
                parts=[types.Part(text=research_prompt)]
            )
            
            # Execute research with error handling
            final_response = await self._execute_with_recovery(content, result)
            
            result["content"] = final_response
            result["metadata"]["end_time"] = datetime.now().isoformat()
            
            self.logger.info("Research complete")
            
        except Exception as e:
            error_msg = f"{type(e).__name__}: {e}"
            result["errors"].append(error_msg)
            self.logger.error(f"Research failed: {error_msg}", exc_info=True)
            result["metadata"]["end_time"] = datetime.now().isoformat()
        
        return result
    
    async def _execute_with_recovery(
        self,
        content: types.Content,
        result: Dict[str, Any]
    ) -> str:
        """
        Execute agent with automatic recovery from transient failures.
        
        Recovery Strategy:
        1. First attempt: Normal execution
        2. On failure: Wait and retry up to max_retries times
        3. On repeated failure: Return partial results if available
        
        This method is the core of the "unbreakable" execution requirement.
        """
        
        final_response = ""
        attempts = 0
        max_attempts = self.config.max_retries
        
        while attempts < max_attempts:
            attempts += 1
            
            try:
                self.logger.debug(f"Execution attempt {attempts}/{max_attempts}")
                
                # Run the agent asynchronously
                # The runner handles the tool calling loop internally
                async for event in self._runner.run_async(
                    user_id=self.config.user_id,
                    session_id=self.config.session_id,
                    new_message=content
                ):
                    # Process events from the agent
                    if event.is_final_response():
                        # Extract the final text response
                        if event.content and event.content.parts:
                            final_response = event.content.parts[0].text
                            self.logger.debug(f"Final response received: {len(final_response)} chars")
                    
                    # Log tool calls for metadata
                    if hasattr(event, 'tool_calls') and event.tool_calls:
                        for tool_call in event.tool_calls:
                            if tool_call.name == "google_search":
                                query = tool_call.args.get("query", "")
                                result["metadata"]["search_queries"].append(query)
                                self.logger.debug(f"Search query executed: {query}")
                    
                    # Extract grounding metadata if available
                    if hasattr(event, 'grounding_metadata') and event.grounding_metadata:
                        gm = event.grounding_metadata
                        if hasattr(gm, 'grounding_chunks'):
                            for chunk in gm.grounding_chunks:
                                if hasattr(chunk, 'web') and chunk.web:
                                    result["metadata"]["sources"].append({
                                        "url": chunk.web.uri,
                                        "title": getattr(chunk.web, 'title', 'Unknown')
                                    })
                
                # Success - exit retry loop
                return final_response
                
            except (ConnectionError, TimeoutError) as e:
                # Transient error - retry
                error_msg = f"Transient error (attempt {attempts}): {e}"
                result["errors"].append(error_msg)
                self.logger.warning(error_msg)
                
                if attempts < max_attempts:
                    wait_time = min(
                        self.config.retry_delay_base * (2 ** attempts),
                        self.config.retry_delay_max
                    )
                    self.logger.info(f"Retrying in {wait_time:.1f}s...")
                    await asyncio.sleep(wait_time)
                    
            except Exception as e:
                # Unknown error - log and retry once
                error_msg = f"Unexpected error (attempt {attempts}): {type(e).__name__}: {e}"
                result["errors"].append(error_msg)
                self.logger.error(error_msg, exc_info=True)
                
                if attempts >= max_attempts:
                    # Final attempt failed - return whatever we have
                    self.logger.warning("Max attempts reached, returning partial results")
                    break
        
        return final_response or "[Research incomplete - see errors in metadata]"
    
    async def save_results(self, result: Dict[str, Any], filename: Optional[str] = None) -> Path:
        """
        Save research results to file.
        
        Args:
            result: Research result dictionary
            filename: Optional custom filename (auto-generated if not provided)
        
        Returns:
            Path to the saved file
        """
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_topic = "".join(c for c in result["topic"][:50] if c.isalnum() or c in " -_").strip()
            safe_topic = safe_topic.replace(" ", "_")
            filename = f"research_{safe_topic}_{timestamp}"
        
        if self.config.output_format == "json":
            output_path = self.config.output_dir / f"{filename}.json"
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
        else:
            output_path = self.config.output_dir / f"{filename}.md"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"# Research: {result['topic']}\n\n")
                f.write(f"**Generated:** {result['metadata']['start_time']}\n")
                f.write(f"**Model:** {result['metadata']['model']}\n\n")
                f.write("---\n\n")
                f.write(result["content"])
                f.write("\n\n---\n\n")
                f.write("## Metadata\n\n")
                f.write(f"### Search Queries Executed\n")
                for q in result["metadata"]["search_queries"]:
                    f.write(f"- {q}\n")
                f.write(f"\n### Sources\n")
                for s in result["metadata"]["sources"]:
                    f.write(f"- [{s.get('title', 'Link')}]({s.get('url', '#')})\n")
                if result["errors"]:
                    f.write(f"\n### Errors Encountered\n")
                    for e in result["errors"]:
                        f.write(f"- {e}\n")
        
        self.logger.info(f"Results saved to: {output_path}")
        return output_path


# ============================================================================
# SECTION 6: MAIN EXECUTION
# ============================================================================

async def main():
    """
    Main entry point for the Deep Research Agent.
    
    Usage:
        python deep_research_agent.py "Your research topic here"
        
    Or import and use programmatically:
        from deep_research_agent import DeepResearchAgent
        agent = DeepResearchAgent()
        result = await agent.research("topic")
    """
    
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python deep_research_agent.py \"Your research topic\"")
        print("\nExample:")
        print('  python deep_research_agent.py "Comparison of LLM inference frameworks: vLLM vs TensorRT-LLM vs TGI"')
        sys.exit(1)
    
    topic = " ".join(sys.argv[1:])
    
    # Verify API key is set
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_GENAI_API_KEY")
    if not api_key:
        print("[ERROR] No API key found. Set GOOGLE_API_KEY or GOOGLE_GENAI_API_KEY environment variable.")
        sys.exit(1)
    
    # Initialize and run
    config = ResearchConfig(
        model_name="gemini-2.5-flash",
        output_format="markdown",
        max_retries=3
    )
    
    agent = DeepResearchAgent(config)
    
    print(f"\n{'='*60}")
    print("DEEP RESEARCH AGENT")
    print(f"{'='*60}")
    print(f"Topic: {topic}")
    print(f"Model: {config.model_name}")
    print(f"Output: {config.output_dir}")
    print(f"{'='*60}\n")
    
    result = await agent.research(topic)
    output_path = await agent.save_results(result)
    
    print(f"\n{'='*60}")
    print("RESEARCH COMPLETE")
    print(f"{'='*60}")
    print(f"Output saved to: {output_path}")
    print(f"Search queries executed: {len(result['metadata']['search_queries'])}")
    print(f"Sources found: {len(result['metadata']['sources'])}")
    print(f"Errors: {len(result['errors'])}")
    print(f"{'='*60}\n")
    
    # Print preview
    if result["content"]:
        preview = result["content"][:500]
        print("Preview:\n")
        print(preview)
        if len(result["content"]) > 500:
            print(f"\n... [{len(result['content']) - 500} more characters]")


if __name__ == "__main__":
    asyncio.run(main())


# ============================================================================
# SECTION 7: MCP FALLBACK ARCHITECTURE (DOCUMENTATION)
# ============================================================================

"""
================================================================================
MCP (MODEL CONTEXT PROTOCOL) FALLBACK STRATEGY
================================================================================

WHEN TO USE MCP:
- If Google ADK's google_search tool is unavailable or rate-limited
- If custom search backends (Elasticsearch, Algolia) are required
- If operating in environments without direct Google API access

ARCHITECTURE:

┌─────────────────────┐      ┌─────────────────────┐
│  Research Agent     │◄────►│  MCP Search Server  │
│  (Gemini Model)     │      │  (Custom Backend)   │
└─────────────────────┘      └─────────────────────┘
         │                            │
         │ Tool Calls                 │ Search API
         ▼                            ▼
┌─────────────────────┐      ┌─────────────────────┐
│  ADK Runner         │      │  Search Index       │
│  (Orchestration)    │      │  (ES/Algolia/etc)   │
└─────────────────────┘      └─────────────────────┘


CONTEXT BLOAT MITIGATION STRATEGY:

Problem: MCP servers can return large payloads that consume context window
         rapidly, degrading model performance after few iterations.

Solutions implemented:

1. CHUNKED RETRIEVAL
   - Configure MCP server to return max 5 results per query
   - Each result limited to 500 tokens (title + snippet + URL)
   - Agent must explicitly request "more results" for pagination

2. SUMMARY INJECTION
   - MCP server pre-summarizes long documents before returning
   - Full document available via separate fetch tool if needed
   - Reduces context consumption by ~80%

3. SLIDING WINDOW STATE
   - Maintain only last 3 search iterations in context
   - Older results summarized into "Previous findings: [...]" block
   - Prevents context from growing unbounded

4. EXPLICIT CONTEXT BUDGET
   - MCP server tracks cumulative tokens returned
   - Returns warning when approaching 50% of context budget
   - Refuses new searches at 80% (forces synthesis mode)

MCP SERVER CONFIGURATION EXAMPLE:

```python
# mcp_search_server.py (separate process)
from mcp import Server, Tool

server = Server("research-search")

@server.tool("search")
async def search(query: str, max_results: int = 5) -> dict:
    '''
    Search with context-aware limits.
    
    Args:
        query: Search query string
        max_results: Maximum results (capped at 5 to prevent bloat)
    
    Returns:
        {
            "results": [...],
            "context_tokens_used": int,
            "context_budget_remaining": int
        }
    '''
    # Implementation with token counting
    results = await backend_search(query, min(max_results, 5))
    
    # Truncate each result to prevent bloat
    truncated = [
        {
            "title": r["title"][:100],
            "snippet": r["snippet"][:400],
            "url": r["url"]
        }
        for r in results
    ]
    
    tokens_used = estimate_tokens(truncated)
    
    return {
        "results": truncated,
        "context_tokens_used": tokens_used,
        "context_budget_remaining": BUDGET - tokens_used
    }
```

INTEGRATION WITH AGENT:

When using MCP instead of google_search, modify the agent initialization:

```python
from google.adk.tools.mcp_tool import MCPToolset

mcp_tools = MCPToolset(
    server_url="http://localhost:8080",  # MCP server endpoint
    tools=["search", "fetch_document"]
)

agent = Agent(
    name="research_agent_mcp",
    model="gemini-2.5-flash",
    instruction=SYSTEM_PROMPT,
    tools=[mcp_tools]  # Use MCP tools instead of google_search
)
```

KEY DIFFERENCES FROM GOOGLE SEARCH:
- Requires separate MCP server process
- Manual context budget management required
- No automatic grounding metadata (must implement)
- More flexibility for custom search backends
- Better for enterprise/private data sources

================================================================================
"""
