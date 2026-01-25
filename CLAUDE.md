# CLAUDE.md

Este arquivo fornece orientacao ao Claude Code (claude.ai/code) ao trabalhar com este repositorio.

**PORTUGUES BRASILEIRO COM ACENTUACAO CORRETA.** Usar "eh" em vez de "e" e inaceitavel. Acentos sao obrigatorios: e, a, a, c, etc.

---

## Comandos Essenciais

```bash
# Desenvolvimento frontend
bun install && bun run dev

# Build frontend
bun run build

# Build Tauri (desktop Linux)
bun run tauri build

# Executar agente ADK (requer GOOGLE_API_KEY)
cd adk-agents/brazilian_legal_pipeline
source .venv/bin/activate
python -m brazilian_legal_pipeline.session_cli --help

# Executar pesquisa de jurisprudencia
cd adk-agents/jurisprudence_agent
python agent.py "Tema juridico"
```

---

## Arquitetura

```
ADK-sandboxed-legal/
|-- src/                         # Codigo React
|   |-- App.tsx                  # Shell principal (state: case, agent, messages)
|   |-- index.tsx                # Entry point
|   |-- constants.ts             # Configuracoes e agentes disponiveis
|   |-- types.ts                 # Tipos TypeScript principais
|   |-- components/              # UI React
|   |   |-- Sidebar.tsx          # Navegacao Caso -> Agente
|   |   |-- ChatWorkspace.tsx    # Interface de chat (Modo Dev/Cliente)
|   |   |-- ConfigPanel.tsx      # Configuracoes runtime
|   |   |-- NewCaseModal.tsx     # Criacao de casos
|   |   |-- editor/              # Editor Slate.js
|   |-- services/                # Camada de servicos
|   |   |-- adkService.ts        # Cliente Gemini SDK (@google/genai)
|   |   |-- agentBridge.ts       # Bridge Tauri-Python (shell)
|   |   |-- caseRegistryService.ts # Gerenciamento de casos
|   |   |-- filesystemService.ts # Operacoes de arquivo
|   |   |-- googleDriveService.ts # OAuth + API Google Drive
|   |   |-- mcpService.ts        # Configuracao MCP
|   |-- types/                   # Tipos adicionais
|       |-- slate.d.ts           # Tipos Slate.js
|-- src-tauri/                   # Backend Rust (Tauri 2.x)
|   |-- tauri.conf.json          # Config principal
|   |-- capabilities/            # Permissoes de plugins
|   |-- src/                     # Codigo Rust
|-- adk-agents/                  # Agentes Python autonomos
|   |-- brazilian_legal_pipeline/ # Pipeline juridica dialetica
|   |-- jurisprudence_agent/     # Pesquisa de jurisprudencia
|-- docs/                        # Documentacao
|   |-- ARCHITECTURE.md          # Arquitetura 4 camadas
|   |-- AGENTS.md                # Guia de agentes e ferramentas LLM
|   |-- SERVICES_API.md          # API de servicos
|   |-- images/                  # Imagens
|-- .claude/                     # Configuracao Claude Code
|   |-- agents/                  # Subagentes especializados
|   |-- commands/                # Comandos customizados
|   |-- skills/                  # Skills ativaveis
|   |-- skill-rules.json         # Triggers automaticos
|-- .gemini/                     # Configuracao Gemini CLI
|   |-- skills/                  # Skills espelhadas
|-- themes/                      # Temas TOML
|-- plugins/                     # Vite plugins
|-- scripts/                     # Scripts utilitarios
```

### Fluxo de Dados

```
Usuario (ChatWorkspace)
    |
    v
App.tsx (handleSendMessage)
    |
    +---> agent-legal-pipeline: agentBridge -> Tauri shell -> Python
    |
    +---> outros agentes: adkService -> Gemini SDK
    |
    v
Resposta (Message com parts: text, tool_call, file_op, etc.)
```

---

## Regras Criticas

### 1. Bun Obrigatorio (nunca npm/yarn/node)
```bash
bun install && bun run dev && bun run build
```

### 2. Variaveis de Ambiente
```bash
# .env
GEMINI_API_KEY=AIza...  # Obrigatorio para agentes ADK
```

### 3. Agentes Python Requerem venv
```bash
cd adk-agents/brazilian_legal_pipeline
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Nunca Commitar
- `.venv/`, `__pycache__/`, `node_modules/`, `dist/`, `target/`
- `.env` (contem API keys)

### 5. ZERO Emojis
Proibido usar emojis em qualquer output. Bug no CLI Rust causa crash em char boundaries.

### 6. Shell Plugin Tauri 2.x
O `agentBridge.ts` usa `@tauri-apps/plugin-shell` para executar agentes Python.

**IMPORTANTE:** No Tauri 2.x, o scope vai em `capabilities/default.json`, NAO em `tauri.conf.json`:
```json
// src-tauri/capabilities/default.json
{
  "permissions": [
    "shell:default",
    {
      "identifier": "shell:allow-execute",
      "allow": [
        { "name": "python", "cmd": "python", "args": true }
      ]
    }
  ]
}
```

Em `tauri.conf.json`, apenas:
```json
"plugins": { "shell": { "open": true } }
```

---

## Stack

| Tecnologia | Versao | Uso |
|------------|--------|-----|
| React | 19.x | Frontend UI |
| Vite | 6.x | Build tool |
| Tauri | 2.x | Desktop wrapper |
| TypeScript | 5.8 | Tipagem |
| @google/genai | 1.38+ | Gemini SDK |
| google-adk | - | Agentes Python |
| Bun | 1.3+ | Runtime/package manager |
| Rust | 1.77+ | Backend Tauri |

---

## Documentacao Adicional

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Arquitetura 4 camadas
- [docs/AGENTS.md](docs/AGENTS.md) - Agentes e ferramentas LLM
- [docs/SERVICES_API.md](docs/SERVICES_API.md) - API de servicos

---

## Erros Aprendidos

**INSTRUCAO PARA CLAUDE:** Adicione uma entrada aqui quando:
- O usuario corrigir um erro seu
- Voce cometer erro grosseiro
- Um erro acontecer mais de uma vez

| Data | Erro | Regra |
|------|------|-------|
| 2026-01-24 | IP interno da VM (10.0.0.13) em vez de IP publico (129.148.53.187) | Sempre usar `curl ifconfig.me` para IP publico |
| 2026-01-24 | `plugins.shell.scope` no tauri.conf.json (Tauri 1.x syntax) | Tauri 2.x usa `capabilities/default.json` para scope |
| 2026-01-24 | `cargo build --release` nao embute assets do frontend | Usar `bun run tauri build` para bundle completo |
| 2026-01-24 | `dpkg -L arquivo.deb` em vez de `dpkg -L nome-pacote` | dpkg -L recebe nome do pacote, nao arquivo |
| 2026-01-24 | Nao verificou onde binario foi instalado antes de instruir usuario | Sempre verificar paths de instalacao antes de passar comandos |

---

## Conversao React -> Tauri

Ver `docs/TAURI_CONVERSION_PLAYBOOK.md` para guia completo. Pontos-chave:
- Frontend React permanece 100% identico
- WebView moderno suporta todas APIs web (localStorage, IndexedDB, etc.)
- Plugins Tauri para funcionalidades nativas (fs, dialog, notification)
- Android: remover `enableEdgeToEdge()` do MainActivity.kt

---

## Debugging

Tecnica dos 5 Porques para bugs nao-triviais:
1. Sintoma -> 2. Por que? -> 3. Por que? -> 4. Por que? -> 5. **CAUSA RAIZ**

```bash
# Logs de hooks
tail -50 ~/.vibe-log/hooks.log

# Logs Tauri
RUST_LOG=debug cargo tauri dev

# TypeScript check
bunx tsc --noEmit
```

---

## Subagentes e Skills Claude Code

### Subagentes (.claude/agents/)
- **tauri-frontend-dev**: Especialista UI React/Vite/Tailwind
- **tauri-rust-dev**: Especialista backend Rust
- **tauri-reviewer**: Seguranca e QA

### Skills (.claude/skills/)
- tauri-core.md
- tauri-frontend.md
- tauri-native-apis.md
- skill-developer.md
- systematic-debugging.md

### Comandos (.claude/commands/)
- /commit - Cria commit seguindo convencoes
- /deep-research - Pesquisa profunda

---

## Ferramentas Gemini CLI

Skills espelhadas em `.gemini/skills/`:
- skill-developer.md
- systematic-debugging.md
- tauri-core.md
- tauri-frontend.md
- tauri-reviewer.md
