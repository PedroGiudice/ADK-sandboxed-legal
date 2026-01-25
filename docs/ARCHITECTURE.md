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

## Sandboxing Logico

O Legal Workbench implementa **isolamento logico por caso**, garantindo que cada caso juridico opere em seu proprio contexto sem interferencia de outros casos.

### Principios

1. **Zero Estado Compartilhado**: Casos nao compartilham memoria, arquivos ou historico
2. **Versionamento Automatico**: Cada mudanca e versionada via Git invisivel
3. **Execucao Paralela**: Multiplos casos podem executar simultaneamente
4. **Auditabilidade**: Historico completo de todas as operacoes

### Hierarquia Case -> Agent

```
Usuario seleciona Caso
        |
        v
Contexto do caso carregado (contextPath, .registry.json)
        |
        v
Usuario seleciona Agente (so apos selecionar caso)
        |
        v
Agente executa no contexto isolado do caso
```

**UX:**
- Agentes so sao visiveis apos selecionar um caso
- Trocar de agente mantem o contexto do caso
- Trocar de caso reseta o agente selecionado

### Estrutura de Diretorio por Caso

```
workspace/
|-- .registry.json          # Indice de todos os casos
|-- Cliente_A/              # Pasta do cliente (opcional)
|   |-- Processo_123/       # Diretorio do caso
|   |   |-- .adk_state/     # Estado do agente
|   |   |   |-- checkpoints/    # Checkpoints de pipeline
|   |   |   |-- sessions/       # Historico de sessoes
|   |   |   |-- .adk_session.json # Sessao ativa
|   |   |-- .context/       # Contexto RAG (ignorado pelo Git)
|   |   |-- .git/           # Repositorio Git invisivel
|   |   |-- .gitignore      # Ignora .context/, logs, etc.
|   |   |-- docs/           # Documentos do caso
|   |   |-- drafts/         # Rascunhos gerados
```

### GitStateBackend

Backend de versionamento Git invisivel para cada caso:

```python
class GitStateBackend:
    """
    Cada caso tem seu proprio repositorio Git isolado para:
    - Versionamento automatico de documentos
    - Historico auditavel de mudancas
    - Rollback de estado
    """

    def create_checkpoint(self, phase: str, message: str) -> str:
        """Cria commit automatico apos cada fase do pipeline."""

    def get_history(self, limit: int = 10) -> List[GitCommit]:
        """Retorna historico de commits do caso."""

    def rollback_to(self, commit_hash: str) -> bool:
        """Reverte caso para estado anterior."""
```

**Commits automaticos:**
- Apos cada fase da pipeline (verificacao, construcao, redacao)
- Quando documentos sao adicionados/modificados
- Antes de operacoes destrutivas

### SessionManager

Orquestra o ciclo de vida de sessoes isoladas:

```python
class SessionManager:
    """
    Responsabilidades:
    - Criar/resumir sessoes
    - Gerenciar isolamento de estado por caso
    - Orquestrar pipeline com contexto correto
    - Emitir eventos para o frontend
    """

    def start_session(case_path: Path, case_id: str) -> SessionInfo:
        """Inicia nova sessao no contexto do caso."""

    def run_pipeline(session_id: str, consultation: dict) -> PipelineResult:
        """Executa pipeline na sessao com isolamento."""

    def resume_session(session_id: str) -> SessionInfo:
        """Retoma sessao de checkpoint."""
```

**Eventos emitidos:**
- `session_created`: Nova sessao iniciada
- `loop_status`: Progresso da pipeline (fase, porcentagem)
- `checkpoint_created`: Checkpoint salvo
- `cli_result`: Resultado final

### session_cli.py

Interface CLI para execucao via Tauri Shell:

```bash
# Iniciar sessao e executar pipeline
python -m brazilian_legal_pipeline.session_cli start-and-run \
  --case-path /workspace/cliente/caso \
  --case-id "case-abc123" \
  --consultation '{"consulta": {"texto": "..."}}'

# Apenas iniciar sessao
python -m brazilian_legal_pipeline.session_cli start \
  --case-path /workspace/cliente/caso \
  --case-id "case-abc123"

# Executar em sessao existente
python -m brazilian_legal_pipeline.session_cli run \
  --session-id "session-xyz789" \
  --consultation '{"consulta": {"texto": "..."}}'

# Ver status Git do caso
python -m brazilian_legal_pipeline.session_cli git-status \
  --case-path /workspace/cliente/caso
```

### Fluxo Completo de Sandboxing

```
1. Usuario cria caso (NewCaseModal)
       |
       v
2. caseRegistryService.createCase()
   - Cria diretorio: workspace/cliente/caso/
   - Cria estrutura: .adk_state/, .context/, docs/, drafts/
   - Adiciona ao .registry.json
       |
       v
3. Usuario seleciona caso no Sidebar
   - App.tsx: setActiveCaseId(caseId)
   - Agentes tornam-se disponiveis
       |
       v
4. Usuario seleciona agente e envia consulta
       |
       v
5. App.tsx handleSendMessage()
   - Monta consulta estruturada com contexto do caso
   - Chama startAndRunCaseSession(casePath, caseId, consultation)
       |
       v
6. agentBridge.ts -> Tauri Shell
   - Executa: python -m session_cli start-and-run
   - Passa casePath e caseId isolados
       |
       v
7. SessionManager.start_session()
   - Inicializa GitStateBackend para o caso
   - Cria SessionInfo em .adk_state/.adk_session.json
   - Emite evento session_created
       |
       v
8. SessionManager.run_pipeline()
   - Pipeline executa no diretorio do caso
   - Checkpoints salvos em .adk_state/checkpoints/
   - Commits Git automaticos apos cada fase
   - Eventos loop_status emitidos para UI
       |
       v
9. Resultado salvo em caso/drafts/
   - Commit final no Git do caso
   - Evento cli_result retornado ao frontend
```

---

## Seguranca

### Isolamento de Acesso

- Cada agente so pode acessar arquivos dentro de seu caso
- Variaveis de ambiente nao vazam entre sessoes
- API keys nunca sao escritas em arquivos do caso

### Credenciais

- API keys em `.env` (nunca commitado)
- OAuth tokens em Tauri Store (criptografado)
- Secrets nunca passados para frontend

### Auditoria

- Git log completo de todas as mudancas por caso
- SessionInfo registra quem/quando/o que executou
- Checkpoints permitem rollback em caso de erro
