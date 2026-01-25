# {{AGENT_NAME}}

{{AGENT_DESCRIPTION}}

## Quick Start

```bash
# Install dependencies
pip install google-adk google-genai python-dotenv

# Set API key
export GOOGLE_API_KEY="your-api-key"

# Run agent
python agent.py "Your research topic"
```

## Configuration

Edit `config.py` to customize:
- `max_iterations`: Maximum research iterations
- `min_sources`: Minimum sources to collect
- `model_name`: Gemini model to use

## Output

Results are saved to `./research_output/` as Markdown files.

## Architecture

```
{{AGENT_ID}}/
├── agent.py      # Main agent implementation
├── config.py     # Configuration
├── __init__.py   # Package exports
└── README.md     # This file
```

## Usage in Code

```python
from {{AGENT_ID}}.agent import {{AGENT_CLASS}}, {{AGENT_CLASS}}Config

config = {{AGENT_CLASS}}Config(max_iterations=3)
agent = {{AGENT_CLASS}}(config)

result = await agent.research("Your topic")
print(result.content)
```
