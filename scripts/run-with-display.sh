#!/bin/bash
# Script para rodar Tauri app com display virtual usando Podman
# Isso permite que Claude Code capture screenshots via MCP

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CONTAINER_NAME="tauri-dev-display"

echo "=== Tauri Dev com Display Virtual ==="

# Verifica se o container ja existe
if podman ps -a --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo "Container $CONTAINER_NAME ja existe. Parando..."
    podman stop $CONTAINER_NAME 2>/dev/null || true
    podman rm $CONTAINER_NAME 2>/dev/null || true
fi

# Cria e executa container com Xvfb + VNC
echo "Iniciando container com Xvfb + noVNC..."
podman run -d \
    --name $CONTAINER_NAME \
    -p 5900:5900 \
    -p 6080:6080 \
    -p 9999:9999 \
    -v "$PROJECT_DIR:/app:z" \
    -w /app \
    -e DISPLAY=:99 \
    docker.io/consol/ubuntu-xfce-vnc:latest \
    /bin/bash -c "
        # Atualiza e instala dependencias
        apt-get update && apt-get install -y curl build-essential libwebkit2gtk-4.1-dev libgtk-3-dev libsoup-3.0-dev libjavascriptcoregtk-4.1-dev librsvg2-dev

        # Instala Rust
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
        source ~/.cargo/env

        # Instala Bun
        curl -fsSL https://bun.sh/install | bash
        export PATH=~/.bun/bin:\$PATH

        # Inicia VNC e mantem container rodando
        /dockerstartup/vnc_startup.sh --wait
    "

echo ""
echo "=== Container iniciado! ==="
echo ""
echo "Acesse via VNC: vnc://localhost:5900"
echo "Ou via noVNC (browser): http://localhost:6080"
echo ""
echo "Para executar o app Tauri dentro do container:"
echo "  podman exec -it $CONTAINER_NAME bash"
echo "  cd /app && bun run tauri dev"
echo ""
echo "O MCP server estara disponivel na porta 9999"
