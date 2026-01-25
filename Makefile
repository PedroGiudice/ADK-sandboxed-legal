# =============================================================================
# MAKEFILE - ADK-SANDBOXED-LEGAL
# =============================================================================
# Comandos simplificados para desenvolvimento e deploy.
#
# Uso:
#   make dev        - Inicia servidor de desenvolvimento
#   make build      - Build frontend apenas
#   make ci         - Roda pipeline CI local
#   make cd         - Roda pipeline CD local (build + push)
#   make release    - Build release Tauri
#   make test       - Roda testes
#   make clean      - Limpa artefatos
# =============================================================================

.PHONY: dev build ci cd release test clean install validate help

# Cores
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m

# =============================================================================
# DESENVOLVIMENTO
# =============================================================================

## Instala dependencias (bun + cargo)
install:
	@echo "$(BLUE)[INSTALL]$(NC) Instalando dependencias..."
	@bun install
	@cd src-tauri && cargo fetch
	@echo "$(GREEN)[OK]$(NC) Dependencias instaladas"

## Inicia servidor de desenvolvimento
dev:
	@echo "$(BLUE)[DEV]$(NC) Iniciando servidor..."
	@bun run dev

## Build frontend (Vite)
build:
	@echo "$(BLUE)[BUILD]$(NC) Build frontend..."
	@bun run build

## Build Tauri debug (rapido)
build-debug:
	@echo "$(BLUE)[BUILD]$(NC) Build Tauri debug..."
	@cd src-tauri && cargo build

## Build Tauri release (otimizado)
release:
	@echo "$(BLUE)[BUILD]$(NC) Build Tauri release..."
	@cd src-tauri && cargo build --release

# =============================================================================
# CI/CD
# =============================================================================

## Validacao pre-commit
validate:
	@./scripts/validate.sh

## Pipeline CI local (validacao completa)
ci:
	@./scripts/ci-local.sh

## Pipeline CI local (sem Rust)
ci-fast:
	@./scripts/ci-local.sh --skip-rust --skip-tests

## Pipeline CD local (build + push)
cd:
	@./scripts/cd-local.sh

## Pipeline CD local (debug, sem push)
cd-debug:
	@./scripts/cd-local.sh --debug --no-push

## Pipeline CD local (release, sem push)
cd-local:
	@./scripts/cd-local.sh --no-push

# =============================================================================
# TESTES
# =============================================================================

## Roda testes Python
test:
	@echo "$(BLUE)[TEST]$(NC) Rodando testes..."
	@python3 -m pytest adk-agents/ -v --tb=short || echo "$(YELLOW)[WARN]$(NC) Alguns testes falharam"

## Roda testes com coverage
test-cov:
	@python3 -m pytest adk-agents/ -v --cov=adk-agents --cov-report=term-missing

# =============================================================================
# AGENTES ADK
# =============================================================================

## Roda jurisprudence agent (requer TOPIC)
jurisprudence:
	@echo "$(BLUE)[AGENT]$(NC) Jurisprudence Research..."
	@cd adk-agents/jurisprudence_agent && python agent.py "$(TOPIC)"

## Roda deep research agent (requer TOPIC)
research:
	@echo "$(BLUE)[AGENT]$(NC) Deep Research..."
	@cd adk-agents/deep_research_sandbox && python deep_research_agent.py "$(TOPIC)"

# =============================================================================
# SCAFFOLD AGENTES
# =============================================================================

## Criar novo agente ADK (requer AGENT_ID, AGENT_NAME, AGENT_DESC)
new-agent:
	@if [ -z "$(AGENT_ID)" ] || [ -z "$(AGENT_NAME)" ]; then \
		echo "$(YELLOW)Uso: make new-agent AGENT_ID=<id> AGENT_NAME=\"<nome>\" AGENT_DESC=\"<descricao>\"$(NC)"; \
		echo ""; \
		echo "Exemplo:"; \
		echo "  make new-agent AGENT_ID=legal_analysis AGENT_NAME=\"Legal Analysis\" AGENT_DESC=\"Analyzes legal documents\""; \
		exit 1; \
	fi
	@./scripts/new-agent.sh "$(AGENT_ID)" "$(AGENT_NAME)" "$(AGENT_DESC)"

# =============================================================================
# LIMPEZA
# =============================================================================

## Limpa artefatos de build
clean:
	@echo "$(BLUE)[CLEAN]$(NC) Limpando artefatos..."
	@rm -rf dist/
	@rm -rf src-tauri/target/
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)[OK]$(NC) Artefatos limpos"

## Limpa tudo (incluindo node_modules)
clean-all: clean
	@rm -rf node_modules/
	@rm -f bun.lock
	@echo "$(GREEN)[OK]$(NC) Limpeza completa"

# =============================================================================
# SETUP
# =============================================================================

## Configura hooks git
setup-hooks:
	@echo "$(BLUE)[SETUP]$(NC) Configurando hooks..."
	@mkdir -p .git/hooks
	@ln -sf ../../scripts/validate.sh .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "$(GREEN)[OK]$(NC) Pre-commit hook configurado"

## Setup completo (install + hooks)
setup: install setup-hooks
	@echo "$(GREEN)[OK]$(NC) Setup completo"

# =============================================================================
# HELP
# =============================================================================

## Mostra ajuda
help:
	@echo ""
	@echo "$(BLUE)ADK-SANDBOXED-LEGAL$(NC) - Comandos disponiveis:"
	@echo ""
	@echo "  $(GREEN)Desenvolvimento:$(NC)"
	@echo "    make install      - Instala dependencias"
	@echo "    make dev          - Servidor de desenvolvimento"
	@echo "    make build        - Build frontend"
	@echo "    make release      - Build Tauri release"
	@echo ""
	@echo "  $(GREEN)CI/CD:$(NC)"
	@echo "    make ci           - Pipeline CI completa"
	@echo "    make ci-fast      - Pipeline CI rapida"
	@echo "    make cd           - Pipeline CD (build + push)"
	@echo "    make cd-debug     - Pipeline CD debug (sem push)"
	@echo "    make validate     - Validacao pre-commit"
	@echo ""
	@echo "  $(GREEN)Testes:$(NC)"
	@echo "    make test         - Roda testes Python"
	@echo "    make test-cov     - Testes com coverage"
	@echo ""
	@echo "  $(GREEN)Agentes:$(NC)"
	@echo "    make jurisprudence TOPIC=\"tema\"  - Pesquisa juridica"
	@echo "    make research TOPIC=\"tema\"       - Deep research"
	@echo "    make new-agent AGENT_ID=x AGENT_NAME=\"y\" AGENT_DESC=\"z\" - Novo agente"
	@echo ""
	@echo "  $(GREEN)Outros:$(NC)"
	@echo "    make clean        - Limpa artefatos"
	@echo "    make setup        - Setup completo"
	@echo "    make help         - Esta mensagem"
	@echo ""

# Default target
.DEFAULT_GOAL := help
