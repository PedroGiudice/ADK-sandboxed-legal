#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# Legal ADK Sandbox - Release Script
# Builda localmente e publica no GitHub Releases para auto-update
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
TAURI_CONF="$PROJECT_DIR/src-tauri/tauri.conf.json"
BUNDLE_DIR="$PROJECT_DIR/src-tauri/target/release/bundle"
SIGNING_KEY="$HOME/.tauri/legal-adk.key"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# =============================================================================
# Funcoes
# =============================================================================

get_current_version() {
    grep '"version"' "$TAURI_CONF" | head -1 | sed 's/.*"\([0-9]*\.[0-9]*\.[0-9]*\)".*/\1/'
}

bump_version() {
    local current="$1"
    local type="${2:-patch}"

    IFS='.' read -r major minor patch <<< "$current"

    case "$type" in
        major) echo "$((major + 1)).0.0" ;;
        minor) echo "$major.$((minor + 1)).0" ;;
        patch) echo "$major.$minor.$((patch + 1))" ;;
        *) echo "$current" ;;
    esac
}

update_version_in_files() {
    local new_version="$1"

    # tauri.conf.json
    sed -i "s/\"version\": \"[0-9]*\.[0-9]*\.[0-9]*\"/\"version\": \"$new_version\"/" "$TAURI_CONF"

    # package.json
    sed -i "s/\"version\": \"[0-9]*\.[0-9]*\.[0-9]*\"/\"version\": \"$new_version\"/" "$PROJECT_DIR/package.json"

    # Cargo.toml
    sed -i "s/^version = \"[0-9]*\.[0-9]*\.[0-9]*\"/version = \"$new_version\"/" "$PROJECT_DIR/src-tauri/Cargo.toml"
}

build_app() {
    log_info "Buildando aplicacao..."
    cd "$PROJECT_DIR"

    # Build com assinatura
    if [[ -f "$SIGNING_KEY" ]]; then
        export TAURI_SIGNING_PRIVATE_KEY=$(cat "$SIGNING_KEY")
        export TAURI_SIGNING_PRIVATE_KEY_PASSWORD="${TAURI_KEY_PASSWORD:-Chicago00@}"
    fi

    bun run tauri build 2>&1 | tail -20 || true

    # Verificar se .deb foi criado
    if ! ls "$BUNDLE_DIR/deb/"*.deb 1>/dev/null 2>&1; then
        log_error "Build falhou - .deb nao encontrado"
    fi

    log_success "Build completo"
}

generate_latest_json() {
    local version="$1"
    local repo="$2"
    local output="$PROJECT_DIR/latest.json"

    # Pegar assinatura do AppImage se existir
    local linux_sig=""
    local sig_file="$BUNDLE_DIR/appimage/Legal ADK Sandbox_${version}_amd64.AppImage.sig"
    if [[ -f "$sig_file" ]]; then
        linux_sig=$(cat "$sig_file")
    fi

    cat > "$output" << EOF
{
  "version": "${version}",
  "notes": "Atualizacao automatica v${version}",
  "pub_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "platforms": {
    "linux-x86_64": {
      "signature": "${linux_sig}",
      "url": "https://github.com/${repo}/releases/download/v${version}/Legal.ADK.Sandbox_${version}_amd64.AppImage"
    }
  }
}
EOF

    log_success "latest.json gerado"
}

create_github_release() {
    local version="$1"
    local repo="$2"

    log_info "Criando release no GitHub..."

    # Coletar arquivos para upload
    local files=()

    # DEB
    for f in "$BUNDLE_DIR/deb/"*.deb; do
        [[ -f "$f" ]] && files+=("$f")
    done

    # RPM
    for f in "$BUNDLE_DIR/rpm/"*.rpm; do
        [[ -f "$f" ]] && files+=("$f")
    done

    # AppImage
    for f in "$BUNDLE_DIR/appimage/"*.AppImage; do
        [[ -f "$f" ]] && files+=("$f")
    done

    # AppImage signature
    for f in "$BUNDLE_DIR/appimage/"*.AppImage.sig; do
        [[ -f "$f" ]] && files+=("$f")
    done

    # latest.json
    files+=("$PROJECT_DIR/latest.json")

    # Deletar release existente se houver
    gh release delete "v${version}" --repo "$repo" --yes 2>/dev/null || true

    # Criar nova release
    gh release create "v${version}" \
        --repo "$repo" \
        --title "Legal ADK Sandbox v${version}" \
        --notes "Release automatico v${version}" \
        "${files[@]}"

    log_success "Release v${version} publicado!"
    echo -e "${GREEN}URL:${NC} https://github.com/${repo}/releases/tag/v${version}"
}

# =============================================================================
# Main
# =============================================================================

main() {
    cd "$PROJECT_DIR"

    echo ""
    echo "=========================================="
    echo "  Legal ADK Sandbox - Release Script"
    echo "=========================================="
    echo ""

    # Detectar repositorio
    local repo
    repo=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null) || log_error "gh CLI nao autenticado. Rode: gh auth login"
    log_info "Repositorio: $repo"

    # Versao atual
    local current_version
    current_version=$(get_current_version)
    log_info "Versao atual: $current_version"

    # Determinar nova versao
    local new_version
    if [[ $# -gt 0 ]]; then
        case "$1" in
            major|minor|patch)
                new_version=$(bump_version "$current_version" "$1")
                ;;
            *)
                new_version="$1"
                ;;
        esac
    else
        new_version=$(bump_version "$current_version" "patch")
    fi

    log_info "Nova versao: $new_version"
    echo ""

    # Confirmar
    read -p "Continuar com release v${new_version}? [Y/n] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]?$ ]]; then
        log_warn "Cancelado"
        exit 0
    fi

    # Executar pipeline
    echo ""
    log_info "Atualizando versao nos arquivos..."
    update_version_in_files "$new_version"
    log_success "Versao atualizada"

    build_app

    generate_latest_json "$new_version" "$repo"

    create_github_release "$new_version" "$repo"

    # Commit da versao
    log_info "Commitando alteracao de versao..."
    git add -A
    git commit -m "chore: bump version to ${new_version}" || true
    git push || true

    echo ""
    echo "=========================================="
    echo -e "  ${GREEN}Release v${new_version} completo!${NC}"
    echo "=========================================="
    echo ""
    echo "O app vai detectar a atualizacao em ~30 segundos"
    echo ""
}

# Rodar
main "$@"
