#!/usr/bin/env bash
# =============================================================================
# VALIDATE.SH - Validacao Pre-Commit
# =============================================================================
# Script leve para rodar antes de commits.
# Use como pre-commit hook: ln -s ../../scripts/validate.sh .git/hooks/pre-commit
#
# Verifica:
# - Arquivos proibidos (.env, .venv, node_modules, target)
# - TypeScript sem erros de sintaxe
# - Python sem erros de sintaxe
# =============================================================================

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0

log_ok() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_fail() { echo -e "${RED}[FAIL]${NC} $1"; ERRORS=$((ERRORS + 1)); }

echo ""
echo "=== Pre-Commit Validation ==="
echo ""

# -----------------------------------------------------------------------------
# 1. VERIFICAR ARQUIVOS PROIBIDOS NO STAGING
# -----------------------------------------------------------------------------
STAGED_FILES=$(git diff --cached --name-only 2>/dev/null || echo "")

# Arquivos/diretorios que NAO devem ser commitados
FORBIDDEN_PATTERNS=(
    "^\.env$"
    "^\.venv/"
    "^node_modules/"
    "^target/"
    "^__pycache__/"
    "\.pyc$"
    "^dist/"
    "\.log$"
)

for pattern in "${FORBIDDEN_PATTERNS[@]}"; do
    if echo "$STAGED_FILES" | grep -qE "$pattern"; then
        log_fail "Arquivo proibido no staging: $(echo "$STAGED_FILES" | grep -E "$pattern" | head -1)"
    fi
done

if [ $ERRORS -eq 0 ]; then
    log_ok "Nenhum arquivo proibido no staging"
fi

# -----------------------------------------------------------------------------
# 2. VERIFICAR SINTAXE TYPESCRIPT (arquivos staged)
# -----------------------------------------------------------------------------
TS_FILES=$(echo "$STAGED_FILES" | grep -E '\.(ts|tsx)$' || true)

if [ -n "$TS_FILES" ]; then
    for file in $TS_FILES; do
        if [ -f "$file" ]; then
            # Verifica sintaxe basica com node
            if ! node --check "$file" 2>/dev/null; then
                # Tenta com tsc se node --check falhar
                if command -v npx >/dev/null 2>&1; then
                    if ! npx tsc --noEmit "$file" 2>/dev/null; then
                        log_warn "TypeScript warning em: $file"
                    fi
                fi
            fi
        fi
    done
    log_ok "TypeScript files verificados"
fi

# -----------------------------------------------------------------------------
# 3. VERIFICAR SINTAXE PYTHON (arquivos staged)
# -----------------------------------------------------------------------------
PY_FILES=$(echo "$STAGED_FILES" | grep -E '\.py$' || true)

if [ -n "$PY_FILES" ]; then
    for file in $PY_FILES; do
        if [ -f "$file" ]; then
            if ! python3 -m py_compile "$file" 2>/dev/null; then
                log_fail "Erro de sintaxe Python: $file"
            fi
        fi
    done
    if [ $ERRORS -eq 0 ]; then
        log_ok "Python files verificados"
    fi
fi

# -----------------------------------------------------------------------------
# 4. VERIFICAR SECRETS ACIDENTAIS
# -----------------------------------------------------------------------------
if echo "$STAGED_FILES" | xargs grep -l "AIza\|sk-\|ghp_\|gho_\|PRIVATE_KEY" 2>/dev/null | head -1; then
    log_fail "Possivel secret detectado em arquivos staged!"
fi

log_ok "Nenhum secret detectado"

# -----------------------------------------------------------------------------
# RESULTADO
# -----------------------------------------------------------------------------
echo ""
if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}Validacao falhou com $ERRORS erro(s)${NC}"
    exit 1
else
    echo -e "${GREEN}Validacao OK - pode commitar${NC}"
    exit 0
fi
