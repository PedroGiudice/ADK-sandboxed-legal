# Arquitetura do Legal Workbench

Este documento descreve a arquitetura de 4 camadas do Legal Workbench e o fluxo de dados entre componentes.

---

## Diagrama de Camadas

```
+------------------------------------------------------------------+
|                        CAMADA 1: FRONTEND                        |
|                         React 19 + Vite 6                        |
|------------------------------------------------------------------|
|  src/                                                            |
|  |-- App.tsx              # Shell principal (state management)   |
|  |-- components/          # UI React                             |
|  |   |-- Sidebar.tsx      # Navegacao Caso -> Agente             |
|  |   |-- ChatWorkspace.tsx # Interface de mensagens              |
|  |   |-- ConfigPanel.tsx  # Configuracoes runtime                |
|  |   |-- editor/          # Editor Slate.js                      |
|  |-- services/            # Camada de servicos                   |
|  |   |-- adkService.ts    # Cliente Gemini SDK                   |
|  |   |-- agentBridge.ts   # Bridge Tauri-Python                  |
|  |   |-- caseRegistryService.ts # Gerenciamento de casos         |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|                       CAMADA 2: TAURI                            |
|                      Rust + Plugins                              |
|------------------------------------------------------------------|
|  src-tauri/                                                      |
|  |-- capabilities/        # Permissoes de plugins                |
|  |   |-- default.json     # Shell scope, fs, dialog              |
|  |-- src/                                                        |
|  |   |-- lib.rs           # Commands Tauri                       |
|  |   |-- google_drive.rs  # OAuth + API Google Drive             |
|  |-- tauri.conf.json      # Configuracao principal               |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|                      CAMADA 3: AGENTES                           |
|                    Python ADK + Gemini                           |
|------------------------------------------------------------------|
|  adk-agents/                                                     |
|  |-- brazilian_legal_pipeline/                                   |
|  |   |-- agent.py         # Pipeline juridica dialetica          |
|  |   |-- session_cli.py   # CLI para execucao sandboxed          |
|  |   |-- session_manager.py # Gerenciamento de sessoes           |
|  |-- jurisprudence_agent/ # Pesquisa de jurisprudencia           |
|  |-- deep_research_sandbox/ # Deep research iterativo            |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|                        CAMADA 4: MCP                             |
|                   Model Context Protocol                         |
|------------------------------------------------------------------|
|  Servidores MCP Externos:                                        |
|  |-- context7              # Documentacao de bibliotecas         |
|  |-- greptile              # Code review                         |
|  |-- filesystem            # Acesso a arquivos                   |
|  |-- google-drive          # Integracao Google Drive             |
+------------------------------------------------------------------+
```

---

## Fluxo de Dados

### Fluxo Principal: Envio de Mensagem

```
1. Usuario digita no ChatWorkspace (SlateEditor)
       |
       v
2. App.tsx handleSendMessage()
       |
       +---> Pipeline Juridica (agent-legal-pipeline)
       |         |
       |         v
       |     agentBridge.startAndRunCaseSession()
       |         |
       |         v
       |     Tauri Shell -> Python session_cli.py
       |         |
       |         v
       |     brazilian_legal_pipeline/agent.py
       |         |
       |         v
       |     Eventos ADK (__ADK_EVENT__) -> Frontend
       |
       +---> Gemini Direto (outros agentes)
       |         |
       |         v
       |     adkService.sendPromptToAgent()
       |         |
       |         v
       |     @google/genai SDK -> Gemini API
       |
       v
3. Resposta parseada em Message com parts
       |
       v
4. ChatWorkspace renderiza (Modo Dev/Cliente)
```

### Fluxo de Caso (Sandboxing)

```
1. Usuario cria Caso (NewCaseModal)
       |
       v
2. caseRegistryService.createCase()
       |
       +---> Cria estrutura:
       |     caso/
       |     |-- .adk_state/   # Estado do agente
       |     |-- .context/     # Contexto do caso
       |     |-- docs/         # Documentos do caso
       |     |-- drafts/       # Rascunhos
       |
       v
3. Registry atualizado (.registry.json)
       |
       v
4. Caso disponivel para selecao no Sidebar
```

---

## Tabela de Servicos

| Servico | Arquivo | Linhas | Responsabilidade |
|---------|---------|--------|------------------|
| ADK Service | `src/services/adkService.ts` | ~60 | Cliente Gemini SDK direto |
| Agent Bridge | `src/services/agentBridge.ts` | ~550 | Execucao de agentes Python via Tauri Shell |
| Case Registry | `src/services/caseRegistryService.ts` | ~385 | Gerenciamento de casos juridicos |
| Filesystem | `src/services/filesystemService.ts` | ~150 | Operacoes de arquivo via Tauri |
| Google Drive | `src/services/googleDriveService.ts` | ~230 | OAuth e integracao Google Drive |
| MCP Service | `src/services/mcpService.ts` | ~145 | Configuracao de servidores MCP |

---

## Comunicacao entre Camadas

### Frontend <-> Tauri

```typescript
// Tauri commands via invoke
import { invoke } from '@tauri-apps/api/core';

// Exemplo: Google Drive
const auth = await invoke<GoogleDriveAuth>('google_drive_callback', { code, clientId });

// Tauri plugins
import { Command } from '@tauri-apps/plugin-shell';
const command = Command.create('python', ['script.py', args]);
```

### Frontend <-> Agentes Python

```typescript
// Via agentBridge.ts usando Tauri Shell
const result = await startAndRunCaseSession(casePath, caseId, consultation, {
  onProgress: (progress) => setPipelineProgress(progress),
  onOutput: (line) => console.log('[PIPELINE]:', line)
});

// Eventos ADK sao emitidos como:
// __ADK_EVENT__{"type":"loop_status","data":{...}}__ADK_EVENT__
```

### Agentes Python <-> MCP

```python
# Servidores MCP configurados via variaveis de ambiente
MCP_SERVERS = os.getenv('MCP_SERVERS')  # JSON array
MCP_SERVER_COUNT = os.getenv('MCP_SERVER_COUNT')
```

---

## Decisoes Arquiteturais

### Por que Tauri?

- Binario unico (~15MB vs ~150MB Electron)
- WebView nativo (sem Chromium bundled)
- Backend Rust para performance
- Plugins para funcionalidades nativas

### Por que Agentes Python Separados?

- Google ADK requer Python
- Isolamento de contexto por caso
- Facilita debugging e logs
- Permite execucao longa sem bloquear UI

### Por que MCP?

- Padrao aberto para extensibilidade
- Ferramentas externas (filesystem, search)
- Context7 para documentacao de libs
- Greptile para code review

---

## Seguranca

### Sandboxing de Casos

Cada caso opera em seu proprio diretorio:
- `.adk_state/`: Estado do agente (checkpoints, sessoes)
- `.context/`: Arquivos de contexto
- Agente so pode acessar arquivos dentro do caso

### Credenciais

- API keys em `.env` (nunca commitado)
- OAuth tokens em Tauri Store (criptografado)
- Secrets nunca passados para frontend
