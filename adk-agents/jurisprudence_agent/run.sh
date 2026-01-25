#!/bin/bash
# =============================================================================
# Jurisprudence Research Agent - Runner Script
# =============================================================================
#
# Usage:
#   ./run.sh "Seu tema de pesquisa juridica"
#
# Example:
#   ./run.sh "Responsabilidade civil por dano moral em relacoes de consumo"
#
# Environment:
#   Requires GOOGLE_API_KEY or GOOGLE_GENAI_API_KEY
#
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate virtual environment if it exists
if [ -d "$SCRIPT_DIR/.venv" ]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
elif [ -d "$SCRIPT_DIR/../.venv" ]; then
    source "$SCRIPT_DIR/../.venv/bin/activate"
fi

# Check for API key
if [ -z "$GOOGLE_API_KEY" ] && [ -z "$GOOGLE_GENAI_API_KEY" ]; then
    echo "ERRO: Chave API nao encontrada."
    echo "Configure: export GOOGLE_API_KEY='sua-chave'"
    exit 1
fi

# Run the agent
cd "$SCRIPT_DIR"
python agent.py "$@"
