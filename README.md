# Legal Workbench

Aplicacao desktop para assistencia juridica com IA, utilizando agentes ADK (Agent Development Kit) e Gemini.

![Status](https://img.shields.io/badge/status-beta-yellow)
![Tauri](https://img.shields.io/badge/tauri-2.x-blue)
![React](https://img.shields.io/badge/react-19.x-61dafb)

---

## Funcionalidades

- **Pipeline Juridica Dialetica**: Raciocinio juridico com debates adversariais
- **Pesquisa de Jurisprudencia**: Busca em tribunais brasileiros (STJ, STF, TJs)
- **Gerenciamento de Casos**: Workspace isolado por caso com versionamento
- **Integracoes**: Google Drive, MCP servers, sistema de arquivos local
- **Modos de Visualizacao**: Desenvolvedor (tecnico) e Cliente (simplificado)

---

## Pre-requisitos

| Ferramenta | Versao | Verificar |
|------------|--------|-----------|
| Bun | 1.3+ | `bun --version` |
| Rust | 1.77+ | `rustc --version` |
| Python | 3.10+ | `python --version` |
| Node.js | 20+ | `node --version` |

---

## Instalacao

### 1. Clonar e Instalar Dependencias

```bash
git clone https://github.com/PedroGiudice/ADK-sandboxed-legal.git
cd ADK-sandboxed-legal

# Frontend (obrigatorio usar bun)
bun install
```

### 2. Configurar Variaveis de Ambiente

```bash
cp .env.example .env

# Editar .env
GEMINI_API_KEY=AIza...  # Obrigatorio
```

### 3. Configurar Agentes Python

```bash
cd adk-agents/brazilian_legal_pipeline
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Comandos

### Desenvolvimento

```bash
# Frontend (dev server)
bun run dev

# Tauri (desktop com hot reload)
bun run tauri dev
```

### Build

```bash
# Frontend apenas
bun run build

# Desktop completo
bun run tauri build
```

### Agentes Python

```bash
# Pipeline juridica
cd adk-agents/brazilian_legal_pipeline
source .venv/bin/activate
python -m brazilian_legal_pipeline.session_cli --help

# Pesquisa de jurisprudencia
cd adk-agents/jurisprudence_agent
python agent.py "tema de pesquisa"
```

---

## Estrutura do Projeto

```
ADK-sandboxed-legal/
|-- src/                    # Frontend React
|   |-- App.tsx             # Shell principal
|   |-- components/         # Componentes UI
|   |-- services/           # Camada de servicos
|   |-- types.ts            # Tipos TypeScript
|-- src-tauri/              # Backend Rust (Tauri 2.x)
|-- adk-agents/             # Agentes Python ADK
|-- docs/                   # Documentacao
|   |-- ARCHITECTURE.md     # Arquitetura 4 camadas
|   |-- AGENTS.md           # Guia de agentes
|   |-- SERVICES_API.md     # API de servicos
|-- themes/                 # Temas TOML
|-- plugins/                # Vite plugins
```

---

## Documentacao

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Arquitetura do sistema
- [AGENTS.md](docs/AGENTS.md) - Agentes ADK e ferramentas LLM
- [SERVICES_API.md](docs/SERVICES_API.md) - API de servicos frontend
- [CLAUDE.md](CLAUDE.md) - Instrucoes para Claude Code

---

## Desenvolvimento

### Stack

| Camada | Tecnologia |
|--------|------------|
| Frontend | React 19, Vite 6, Tailwind |
| Desktop | Tauri 2.x, Rust |
| Agentes | Python, Google ADK, Gemini |
| Integracao | MCP, Google Drive |

### Regras

- **Bun obrigatorio** (nunca npm/yarn/node)
- **Zero emojis** em outputs (bug no CLI Rust)
- **Portugues brasileiro** com acentuacao correta

### Contribuindo

1. Fork o repositorio
2. Crie branch: `git checkout -b feature/minha-feature`
3. Commit: `git commit -m "feat: descricao"`
4. Push: `git push origin feature/minha-feature`
5. Abra Pull Request

---

## Licenca

Proprietario - Pedro Giudice

---

## Links

- [Tauri Documentation](https://tauri.app/v2/guide/)
- [Google ADK](https://github.com/google/adk-python)
- [Model Context Protocol](https://modelcontextprotocol.io/)
