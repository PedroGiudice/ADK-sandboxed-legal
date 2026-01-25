# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**PORTUGUES BRASILEIRO COM ACENTUACAO CORRETA.** Usar "eh" em vez de "e" e inaceitavel. Acentos sao obrigatorios: e, a, a, c, etc.

---

## Comandos Essenciais

```bash
# Desenvolvimento frontend
bun install && bun run dev

# Build frontend
bun run build

# Build Tauri (desktop Linux)
cd src-tauri && cargo build --release

# Executar agente ADK (requer GOOGLE_API_KEY)
cd adk-agents/jurisprudence_agent && python agent.py "Tema juridico"

# Executar deep research
cd adk-agents/deep_research_sandbox && python deep_research_agent.py "Topico"
```

---

## Arquitetura

```
ADK-sandboxed-legal/
├── App.tsx                  # Shell principal React (state: agent, messages, config)
├── components/              # UI React
│   ├── AgentSelector.tsx    # Selecao de agentes
│   ├── ChatWorkspace.tsx    # Interface de chat com mensagens estruturadas
│   ├── ConfigPanel.tsx      # Configuracoes runtime
│   └── Icons.tsx            # SVG icons
├── services/
│   ├── adkService.ts        # Cliente para Gemini SDK (@google/genai)
│   └── agentBridge.ts       # Bridge Tauri-Python (executa agentes via shell)
├── adk-agents/              # Agentes Python autonomos
│   ├── jurisprudence_agent/ # Pesquisa juridica com whitelist de tribunais
│   ├── deep_research_sandbox/ # Deep Research iterativo
│   ├── visual_verifier/     # Verificador de UI
│   └── iterative_research_agent.py  # Pesquisador com loop
├── src-tauri/               # Backend Rust (Tauri 2.x)
│   ├── tauri.conf.json      # Config principal (shell scope, identifier)
│   ├── capabilities/        # Permissoes de plugins
│   └── src/                 # Codigo Rust
└── .claude/                 # Claude Code config
    ├── agents/              # Subagentes especializados
    ├── skills/              # Skills Tauri
    └── skill-rules.json     # Triggers MCP
```

### Fluxo de Dados

```
Usuario (ChatWorkspace)
    |
    v
App.tsx (handleSendMessage)
    |
    +---> agent-caselaw: agentBridge.ts -> Tauri shell -> Python agent
    |
    +---> outros agentes: adkService.ts -> Gemini SDK diretamente
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
cd adk-agents/jurisprudence_agent
python -m venv .venv
source .venv/bin/activate
pip install google-adk google-genai python-dotenv
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
```

---

## Subagentes Disponiveis

Definidos em `.claude/agents/`:
- **tauri-frontend-dev**: Especialista UI React/Vite/Tailwind
- **tauri-rust-dev**: Especialista backend Rust
- **tauri-reviewer**: Seguranca e QA

Skills em `.claude/skills/`:
- tauri-core.md
- tauri-frontend.md
- tauri-native-apis.md
