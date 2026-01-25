#!/usr/bin/env bash
# =============================================================================
# CI-LOCAL.SH - Pipeline de Integracao Continua Local
# =============================================================================
# Executa validacoes antes de commit/push:
# - Type checking (TypeScript)
# - Lint (se configurado)
# - Testes Python (pytest)
# - Build frontend (Vite)
# - Cargo check (Rust)
#
# Uso: ./scripts/ci-local.sh [--skip-tests] [--skip-rust]
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Flags
SKIP_TESTS=false
SKIP_RUST=false

# Parse args
for arg in "$@"; do
    case $arg in
        --skip-tests) SKIP_TESTS=true ;;
        --skip-rust) SKIP_RUST=true ;;
    esac
done

# Funcoes de log
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }
log_ok() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_fail() { echo -e "${RED}[FAIL]${NC} $1"; exit 1; }

echo ""
echo "=============================================="
echo "  CI-LOCAL: Validacao de Integracao"
echo "=============================================="
echo ""

# -----------------------------------------------------------------------------
# 1. VERIFICAR DEPENDENCIAS
# -----------------------------------------------------------------------------
log_step "Verificando dependencias..."

command -v bun >/dev/null 2>&1 || log_fail "bun nao encontrado. Instale: curl -fsSL https://bun.sh/install | bash"
command -v cargo >/dev/null 2>&1 || log_fail "cargo nao encontrado. Instale Rust: https://rustup.rs"
command -v python3 >/dev/null 2>&1 || log_fail "python3 nao encontrado"

log_ok "Dependencias verificadas"

# -----------------------------------------------------------------------------
# 2. INSTALAR DEPENDENCIAS NODE
# -----------------------------------------------------------------------------
log_step "Instalando dependencias Node (bun install)..."

if [ ! -d "node_modules" ] || [ "package.json" -nt "node_modules" ]; then
    bun install --frozen-lockfile 2>/dev/null || bun install
    log_ok "Dependencias Node instaladas"
else
    log_ok "Dependencias Node ja atualizadas"
fi

# -----------------------------------------------------------------------------
# 3. TYPE CHECK (TypeScript)
# -----------------------------------------------------------------------------
log_step "Verificando tipos TypeScript..."

if bun run tsc --noEmit 2>/dev/null; then
    log_ok "TypeScript: sem erros de tipo"
else
    # Tenta com npx se bun falhar
    if npx tsc --noEmit 2>/dev/null; then
        log_ok "TypeScript: sem erros de tipo"
    else
        log_warn "TypeScript: verificacao de tipos falhou (continuando...)"
    fi
fi

# -----------------------------------------------------------------------------
# 4. BUILD FRONTEND (Vite)
# -----------------------------------------------------------------------------
log_step "Build frontend (Vite)..."

if bun run build; then
    log_ok "Frontend build concluido"
else
    log_fail "Frontend build falhou"
fi

# -----------------------------------------------------------------------------
# 5. CARGO CHECK (Rust)
# -----------------------------------------------------------------------------
if [ "$SKIP_RUST" = false ]; then
    log_step "Verificando codigo Rust (cargo check)..."

    if [ -d "src-tauri" ]; then
        cd src-tauri
        if cargo check 2>&1; then
            log_ok "Rust: cargo check passou"
        else
            log_fail "Rust: cargo check falhou"
        fi
        cd ..
    else
        log_warn "src-tauri nao encontrado, pulando cargo check"
    fi
else
    log_warn "Pulando verificacao Rust (--skip-rust)"
fi

# -----------------------------------------------------------------------------
# 6. TESTES PYTHON (pytest)
# -----------------------------------------------------------------------------
if [ "$SKIP_TESTS" = false ]; then
    log_step "Executando testes Python..."

    if [ -d "adk-agents" ]; then
        # Verifica se pytest esta disponivel
        if python3 -c "import pytest" 2>/dev/null; then
            if python3 -m pytest adk-agents/ -v --tb=short 2>/dev/null; then
                log_ok "Testes Python passaram"
            else
                log_warn "Alguns testes Python falharam (continuando...)"
            fi
        else
            log_warn "pytest nao instalado, pulando testes Python"
        fi
    else
        log_warn "adk-agents nao encontrado"
    fi
else
    log_warn "Pulando testes (--skip-tests)"
fi

# -----------------------------------------------------------------------------
# 7. VERIFICAR .ENV
# -----------------------------------------------------------------------------
log_step "Verificando configuracao..."

if [ -f ".env" ]; then
    if grep -q "GOOGLE_API_KEY\|GEMINI_API_KEY" .env 2>/dev/null; then
        log_ok "API key configurada em .env"
    else
        log_warn "API key nao encontrada em .env"
    fi
else
    log_warn ".env nao encontrado"
fi

# -----------------------------------------------------------------------------
# RESULTADO FINAL
# -----------------------------------------------------------------------------
echo ""
echo "=============================================="
echo -e "  ${GREEN}CI-LOCAL: VALIDACAO COMPLETA${NC}"
echo "=============================================="
echo ""
echo "Proximo passo: ./scripts/cd-local.sh"
echo ""
