# Custom Gemini Deep Research Agent

## Overview

A programmatic replacement for browser-based Gemini "Deep Research" that provides:

- **High information density** output (no journalistic fluff)
- **Autonomous query generation** (agent decides what to search)
- **Robust error handling** (never crashes, always recovers)
- **Structured output** with source attribution

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set API key
export GOOGLE_API_KEY="your-api-key-here"

# 3. Run research
python deep_research_agent.py "Comparison of vector databases: Pinecone vs Weaviate vs Milvus"
```

## Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    DEEP RESEARCH AGENT                         │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐ │
│  │   System     │    │   Gemini     │    │   google_search  │ │
│  │   Prompt     │───►│   Agent      │◄──►│   Tool           │ │
│  │   (Strict)   │    │              │    │   (Grounding)    │ │
│  └──────────────┘    └──────────────┘    └──────────────────┘ │
│                             │                                  │
│                             ▼                                  │
│                      ┌──────────────┐                         │
│                      │    Runner    │                         │
│                      │  (ADK Core)  │                         │
│                      └──────────────┘                         │
│                             │                                  │
│         ┌───────────────────┼───────────────────┐             │
│         ▼                   ▼                   ▼             │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐      │
│  │   Session    │   │    Error     │   │    Output    │      │
│  │   Service    │   │   Recovery   │   │    Saver     │      │
│  └──────────────┘   └──────────────┘   └──────────────┘      │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

## System Prompt

The agent uses a strict system prompt that enforces:

| Constraint | Description |
|------------|-------------|
| No journalistic intros | Eliminates "In today's landscape..." |
| No persuasive language | Pure factual reporting |
| No marketing terms | No "revolutionary", "game-changing" |
| Structured output | Bullet points, tables, citations |
| Source attribution | All claims must cite sources |

## Error Handling Strategy

The agent implements a "never crash" philosophy:

```python
# Retry hierarchy (in order of attempt)
1. Transient errors (network, rate limits) → Exponential backoff retry
2. Tool failures (search timeout) → Skip and continue with partial data
3. Model errors (context overflow) → Graceful degradation
4. Unknown errors → Log, retry once, return partial results
```

**Maximum retries:** 3 (configurable)
**Backoff:** 1s → 2s → 4s → ... → 30s max

## Output Formats

### Markdown (default)

```markdown
# Research: [Topic]

**Generated:** 2025-01-07T10:30:00
**Model:** gemini-2.5-flash

---

## Key Findings
- [Fact] (Source: [URL])

## Technical Specifications
| Parameter | Value | Source |

---

## Metadata
### Search Queries Executed
- query 1
- query 2

### Sources
- [Title](url)
```

### JSON

```json
{
  "topic": "...",
  "content": "...",
  "metadata": {
    "start_time": "2025-01-07T10:30:00",
    "end_time": "2025-01-07T10:32:00",
    "model": "gemini-2.5-flash",
    "search_queries": ["query1", "query2"],
    "sources": [{"url": "...", "title": "..."}]
  },
  "errors": []
}
```

## Configuration Options

```python
from deep_research_agent import DeepResearchAgent, ResearchConfig

config = ResearchConfig(
    model_name="gemini-2.5-flash",      # or "gemini-2.5-pro"
    output_dir="./my_research",          # Output directory
    output_format="markdown",            # "markdown" or "json"
    max_retries=3,                       # Retry attempts
    retry_delay_base=1.0,                # Base delay (seconds)
    retry_delay_max=30.0,                # Max delay (seconds)
    log_level="INFO"                     # DEBUG for verbose
)

agent = DeepResearchAgent(config)
result = await agent.research("Your topic")
```

## Programmatic Usage

```python
import asyncio
from deep_research_agent import DeepResearchAgent

async def run_research():
    agent = DeepResearchAgent()
    
    # Single topic
    result = await agent.research(
        "Technical comparison of transformer attention mechanisms: "
        "Flash Attention vs Multi-Query Attention vs Grouped-Query Attention"
    )
    
    # Save results
    output_path = await agent.save_results(result)
    print(f"Saved to: {output_path}")
    
    # Access structured data
    print(f"Queries executed: {result['metadata']['search_queries']}")
    print(f"Sources found: {len(result['metadata']['sources'])}")

asyncio.run(run_research())
```

## MCP Fallback

If Google Search is unavailable, the agent can use MCP (Model Context Protocol) servers as an alternative search backend. See the docstring in `deep_research_agent.py` Section 7 for:

- MCP server configuration
- Context bloat mitigation strategies
- Integration code examples

### Context Bloat Mitigation

| Strategy | Implementation |
|----------|----------------|
| Chunked retrieval | Max 5 results × 500 tokens each |
| Summary injection | Pre-summarize before context |
| Sliding window | Keep only last 3 iterations |
| Explicit budget | Warning at 50%, block at 80% |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | Yes* | Google AI Studio API key |
| `GOOGLE_GENAI_API_KEY` | Yes* | Alternative key name |

*One of these is required.

## Troubleshooting

### "No API key found"

```bash
export GOOGLE_API_KEY="AIza..."
```

### "Agent initialization failed"

Check that `google-adk` is installed correctly:

```bash
pip install --upgrade google-adk google-genai
```

### "Search tool failed"

The google_search tool requires a valid API key with Gemini API access enabled. Verify at https://aistudio.google.com/

### Rate limiting

Increase retry delays:

```python
config = ResearchConfig(
    retry_delay_base=2.0,
    retry_delay_max=60.0
)
```

## License

MIT
