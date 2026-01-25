# Claude Command: Deep Research

Execute the Gemini ADK Deep Research Agent for autonomous technical research with web search grounding.

## Usage

```
/deep-research "Your research topic here"
```

Or with arguments:
```
/deep-research --check   # Check dependencies only
/deep-research --help    # Show help
```

## What This Command Does

1. Validates that the Gemini ADK environment is properly configured
2. Executes the Deep Research Agent with the provided topic
3. The agent autonomously:
   - Generates multiple search queries
   - Retrieves information from the web via Google Search grounding
   - Synthesizes findings into a structured technical report
4. Saves results to `adk-agents/deep_research_sandbox/research_output/`

## Execution

When the user invokes this command, execute:

```bash
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "/home/cmr-auto/claude-work/repos/lex-vector")
cd "$REPO_ROOT/adk-agents" && ./run-research.sh "$ARGUMENTS"
```

If `$ARGUMENTS` is empty, ask the user for a research topic.

If `$ARGUMENTS` is `--check`, run:
```bash
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "/home/cmr-auto/claude-work/repos/lex-vector")
cd "$REPO_ROOT/adk-agents" && ./run-research.sh --check-deps
```

## Prerequisites

- `GOOGLE_API_KEY` environment variable (loaded from `adk-agents/.env`)
- Python virtual environment at `adk-agents/deep_research_sandbox/.venv/`
- Required packages: `google-adk`, `google-genai`, `tenacity`

## Output Format

Research results are saved as Markdown with:
- **Key Findings**: Bulleted facts with citations
- **Technical Specifications**: Data tables
- **Data Conflicts / Uncertainties**: Noted discrepancies
- **Source Index**: Full citations

## Examples

Basic research:
```
/deep-research "Compare vector databases: Pinecone vs Weaviate vs Milvus"
```

Technical analysis:
```
/deep-research "Latest developments in transformer attention mechanisms 2026"
```

Check setup:
```
/deep-research --check
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No API key found" | Check `adk-agents/.env` has `GOOGLE_API_KEY` |
| "Agent initialization failed" | Run `/deep-research --check` |
| Timeout | Simplify the research topic |
| Rate limit (429) | Wait and retry, or reduce query complexity |

## Notes

- Research typically takes 20-60 seconds depending on topic complexity
- The agent uses `gemini-2.5-flash` model by default
- Output directory: `adk-agents/deep_research_sandbox/research_output/`
- All searches use Google Search grounding for accuracy
