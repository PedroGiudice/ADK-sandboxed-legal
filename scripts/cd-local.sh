#!/usr/bin/env bash
# =============================================================================
# CD-LOCAL.SH - Pipeline de Deploy Continuo Local
# =============================================================================
# Executa build completo e push para repositorio:
# - Roda CI primeiro (validacao)
# - Build Tauri release (Linux)
# - Commit automatico (se houver mudancas)
# - Push para remote
#
# Uso: ./scripts/cd-local.sh [--no-push] [--debug] [--skip-ci]
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Flags
NO_PUSH=false
DEBUG_BUILD=false
SKIP_CI=false
COMMIT_MSG=""

# Parse args
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-push) NO_PUSH=true; shift ;;
        --debug) DEBUG_BUILD=true; shift ;;
        --skip-ci) SKIP_CI=true; shift ;;
        -m|--message) COMMIT_MSG="$2"; shift 2 ;;
        *) shift ;;
    esac
done

# Funcoes
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }
log_ok() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_fail() { echo -e "${RED}[FAIL]${NC} $1"; exit 1; }
log_info() { echo -e "${CYAN}[INFO]${NC} $1"; }

echo ""
echo "=============================================="
echo "  CD-LOCAL: Pipeline de Deploy"
echo "=============================================="
echo ""

# Captura tempo inicio
START_TIME=$(date +%s)

# -----------------------------------------------------------------------------
# 1. RODAR CI PRIMEIRO
# -----------------------------------------------------------------------------
if [ "$SKIP_CI" = false ]; then
    log_step "Executando CI-LOCAL primeiro..."

    if "$SCRIPT_DIR/ci-local.sh" --skip-rust; then
        log_ok "CI passou"
    else
        log_fail "CI falhou - corrija os erros antes de fazer deploy"
    fi
else
    log_warn "Pulando CI (--skip-ci)"
fi

# -----------------------------------------------------------------------------
# 2. BUILD TAURI
# -----------------------------------------------------------------------------
log_step "Build Tauri..."

cd src-tauri

if [ "$DEBUG_BUILD" = true ]; then
    log_info "Modo debug (mais rapido)"
    if cargo build 2>&1; then
        log_ok "Tauri build (debug) concluido"
        BUILD_PATH="target/debug"
    else
        log_fail "Tauri build falhou"
    fi
else
    log_info "Modo release (otimizado)"
    if cargo build --release 2>&1; then
        log_ok "Tauri build (release) concluido"
        BUILD_PATH="target/release"
    else
        log_fail "Tauri build falhou"
    fi
fi

cd ..

# Mostrar artefatos
if [ -d "src-tauri/$BUILD_PATH" ]; then
    log_info "Artefatos em: src-tauri/$BUILD_PATH"
    ls -lh "src-tauri/$BUILD_PATH"/*.AppImage 2>/dev/null || true
    ls -lh "src-tauri/$BUILD_PATH"/*.deb 2>/dev/null || true
fi

# -----------------------------------------------------------------------------
# 3. GIT STATUS E COMMIT
# -----------------------------------------------------------------------------
log_step "Verificando mudancas Git..."

# Adicionar arquivos importantes (excluindo build artifacts)
git add -A
git add --force .env.example 2>/dev/null || true

# Verificar se ha mudancas
if git diff --cached --quiet; then
    log_info "Sem mudancas para commit"
else
    # Gerar mensagem de commit se nao fornecida
    if [ -z "$COMMIT_MSG" ]; then
        CHANGED_FILES=$(git diff --cached --name-only | head -5 | tr '\n' ', ' | sed 's/,$//')
        COMMIT_MSG="chore: update $CHANGED_FILES"
    fi

    log_step "Criando commit..."
    git commit -m "$COMMIT_MSG

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"

    log_ok "Commit criado: $COMMIT_MSG"
fi

# -----------------------------------------------------------------------------
# 4. PUSH PARA REMOTE
# -----------------------------------------------------------------------------
if [ "$NO_PUSH" = false ]; then
    log_step "Push para remote..."

    CURRENT_BRANCH=$(git branch --show-current)

    if git push -u origin "$CURRENT_BRANCH" 2>&1; then
        log_ok "Push concluido para branch: $CURRENT_BRANCH"
    else
        log_warn "Push falhou - verifique autenticacao Git"
    fi
else
    log_warn "Pulando push (--no-push)"
fi

# -----------------------------------------------------------------------------
# RESULTADO FINAL
# -----------------------------------------------------------------------------
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo "=============================================="
echo -e "  ${GREEN}CD-LOCAL: DEPLOY COMPLETO${NC}"
echo "=============================================="
echo ""
echo "Duracao: ${DURATION}s"
echo "Branch: $(git branch --show-current)"
echo "Commit: $(git rev-parse --short HEAD)"
echo ""

if [ "$DEBUG_BUILD" = false ]; then
    echo "Artefatos de release:"
    ls -lh src-tauri/target/release/*.AppImage 2>/dev/null || echo "  (nenhum .AppImage encontrado)"
    ls -lh src-tauri/target/release/*.deb 2>/dev/null || echo "  (nenhum .deb encontrado)"
fi

echo ""
