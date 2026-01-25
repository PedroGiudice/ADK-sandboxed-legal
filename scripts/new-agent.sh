#!/usr/bin/env bash
# =============================================================================
# NEW-AGENT.SH - Scaffold para novo agente ADK
# =============================================================================
# Cria estrutura de diretorio e arquivos para novo agente ADK.
#
# Uso: ./scripts/new-agent.sh <agent-id> "<Agent Name>" "<Description>"
#
# Exemplo:
#   ./scripts/new-agent.sh legal_analysis "Legal Analysis" "Agent for analyzing legal documents"
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEMPLATES_DIR="$PROJECT_ROOT/adk-agents/.templates"
AGENTS_DIR="$PROJECT_ROOT/adk-agents"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }
log_ok() { echo -e "${GREEN}[OK]${NC} $1"; }
log_fail() { echo -e "${RED}[FAIL]${NC} $1"; exit 1; }

# =============================================================================
# VALIDACAO DE ARGUMENTOS
# =============================================================================

if [ $# -lt 3 ]; then
    echo "Uso: $0 <agent-id> \"<Agent Name>\" \"<Description>\""
    echo ""
    echo "Exemplo:"
    echo "  $0 legal_analysis \"Legal Analysis\" \"Agent for analyzing legal documents\""
    echo ""
    echo "Parametros:"
    echo "  agent-id    : Identificador do agente (snake_case, ex: legal_analysis)"
    echo "  Agent Name  : Nome do agente (ex: Legal Analysis Agent)"
    echo "  Description : Descricao do agente"
    exit 1
fi

AGENT_ID="$1"
AGENT_NAME="$2"
AGENT_DESCRIPTION="$3"

# Derivar outros nomes
AGENT_NAME_UPPER=$(echo "$AGENT_NAME" | tr '[:lower:]' '[:upper:]')
AGENT_CLASS=$(echo "$AGENT_ID" | sed -r 's/(^|_)([a-z])/\U\2/g')  # snake_case -> PascalCase
AGENT_DIR="$AGENTS_DIR/${AGENT_ID}_agent"

# Prompt padrao
SYSTEM_PROMPT="You are a research assistant specializing in $AGENT_NAME. Execute searches and report findings with source citations."

# =============================================================================
# VERIFICACOES
# =============================================================================

log_step "Verificando pre-requisitos..."

if [ -d "$AGENT_DIR" ]; then
    log_fail "Diretorio ja existe: $AGENT_DIR"
fi

if [ ! -f "$TEMPLATES_DIR/agent_template.py" ]; then
    log_fail "Template nao encontrado: $TEMPLATES_DIR/agent_template.py"
fi

log_ok "Pre-requisitos OK"

# =============================================================================
# CRIAR ESTRUTURA
# =============================================================================

log_step "Criando estrutura do agente..."

mkdir -p "$AGENT_DIR"
mkdir -p "$AGENT_DIR/research_output"

log_ok "Diretorio criado: $AGENT_DIR"

# =============================================================================
# GERAR ARQUIVOS A PARTIR DOS TEMPLATES
# =============================================================================

log_step "Gerando arquivos..."

# agent.py
sed -e "s/{{AGENT_ID}}/$AGENT_ID/g" \
    -e "s/{{AGENT_NAME}}/$AGENT_NAME/g" \
    -e "s/{{AGENT_NAME_UPPER}}/$AGENT_NAME_UPPER/g" \
    -e "s/{{AGENT_CLASS}}/$AGENT_CLASS/g" \
    -e "s/{{AGENT_DESCRIPTION}}/$AGENT_DESCRIPTION/g" \
    -e "s/{{SYSTEM_PROMPT}}/$SYSTEM_PROMPT/g" \
    "$TEMPLATES_DIR/agent_template.py" > "$AGENT_DIR/agent.py"

log_ok "agent.py criado"

# README.md
sed -e "s/{{AGENT_ID}}/$AGENT_ID/g" \
    -e "s/{{AGENT_NAME}}/$AGENT_NAME/g" \
    -e "s/{{AGENT_CLASS}}/$AGENT_CLASS/g" \
    -e "s/{{AGENT_DESCRIPTION}}/$AGENT_DESCRIPTION/g" \
    "$TEMPLATES_DIR/README_template.md" > "$AGENT_DIR/README.md"

log_ok "README.md criado"

# __init__.py
cat > "$AGENT_DIR/__init__.py" << EOF
"""
$AGENT_NAME

$AGENT_DESCRIPTION
"""

from .agent import ${AGENT_CLASS}, ${AGENT_CLASS}Config

__all__ = ["${AGENT_CLASS}", "${AGENT_CLASS}Config"]
EOF

log_ok "__init__.py criado"

# config.py (opcional, para configuracoes extras)
cat > "$AGENT_DIR/config.py" << EOF
"""
Configuration for $AGENT_NAME.
"""

# Default settings
DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_MAX_ITERATIONS = 5
DEFAULT_MIN_SOURCES = 15

# Add custom configuration here
EOF

log_ok "config.py criado"

# =============================================================================
# TORNAR EXECUTAVEL
# =============================================================================

chmod +x "$AGENT_DIR/agent.py"

# =============================================================================
# RESULTADO
# =============================================================================

echo ""
echo "=============================================="
echo -e "${GREEN}AGENTE CRIADO COM SUCESSO${NC}"
echo "=============================================="
echo ""
echo "Diretorio: $AGENT_DIR"
echo ""
echo "Arquivos:"
echo "  - agent.py      # Implementacao principal"
echo "  - config.py     # Configuracoes"
echo "  - __init__.py   # Package exports"
echo "  - README.md     # Documentacao"
echo ""
echo "Proximo passo:"
echo "  cd $AGENT_DIR"
echo "  python agent.py \"Seu topico de pesquisa\""
echo ""
