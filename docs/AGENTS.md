# Agentes ADK e Ferramentas LLM

Este documento descreve os agentes Python ADK e as ferramentas de desenvolvimento com LLMs (Claude/Gemini).

---

## Agentes Python ADK

### Estrutura de um Agente

```
adk-agents/
|-- brazilian_legal_pipeline/
|   |-- __init__.py
|   |-- agent.py            # Logica principal do agente
|   |-- config.py           # Configuracoes e prompts
|   |-- session_cli.py      # CLI para execucao sandboxed
|   |-- session_manager.py  # Gerenciamento de sessoes
|   |-- git_state.py        # Integracao Git para versionamento
|-- jurisprudence_agent/
|   |-- agent.py
|   |-- requirements.txt
```

### Agentes Disponiveis

| Agente | ID | Descricao |
|--------|-----|-----------|
| Pipeline Juridica | `agent-legal-pipeline` | Pipeline dialetica com verificacao, construcao e redacao |
| Jurisprudencia | `agent-jurisprudence` | Pesquisa em tribunais brasileiros (STJ, STF, TJs) |

### Como Registrar um Agente no Frontend

1. **Adicionar ao constants.ts:**

```typescript
// src/constants.ts
export const AVAILABLE_AGENTS: AgentProfile[] = [
  {
    id: 'agent-meu-agente',           // ID unico
    name: 'Nome do Agente',           // Nome para UI
    specialization: 'Especializacao', // Ex: "Pesquisa Legal"
    description: 'Descricao...',      // Descricao detalhada
    version: '1.0',
    status: 'active',                 // active | maintenance | deprecated
  },
];
```

2. **Implementar handler em App.tsx:**

```typescript
// src/App.tsx - handleSendMessage
if (activeAgent?.id === 'agent-meu-agente') {
  const result = await runPythonAgent(
    'adk-agents/meu_agente/agent.py',
    [content],
    { onProgress: (line) => console.log(line) }
  );
  // ... processar resultado
}
```

### Variaveis de Ambiente

```bash
# .env (raiz do projeto)
GEMINI_API_KEY=AIza...  # Obrigatorio para todos os agentes

# Passadas automaticamente pelo agentBridge:
MCP_SERVERS=...         # JSON array de servidores MCP
MCP_SERVER_COUNT=...    # Quantidade de servidores
FILESYSTEM_MODE=...     # whitelist | unrestricted
FILESYSTEM_FOLDERS=...  # JSON array de pastas permitidas
GOOGLE_DRIVE_TOKEN=...  # Token OAuth (se configurado)
```

### Executar Agente Manualmente

```bash
# Ativar venv do agente
cd adk-agents/brazilian_legal_pipeline
source .venv/bin/activate

# Executar
python -m brazilian_legal_pipeline.session_cli start-and-run \
  --case-path /caminho/caso \
  --case-id "case-123" \
  --consultation '{"consulta": {"texto": "..."}}'
```

---

## Sistema de Sandboxing Logico

O Legal Workbench implementa isolamento logico por caso atraves de tres componentes principais.

### Componentes Python

#### 1. GitStateBackend (`git_state.py`)

Versionamento Git invisivel para cada caso:

```python
from brazilian_legal_pipeline.git_state import GitStateBackend

# Inicializar para um caso
git = GitStateBackend(Path("/workspace/cliente/caso"))

# Criar checkpoint apos fase
commit_hash = git.create_checkpoint(
    phase="verificacao",
    message="Fase de verificacao concluida"
)

# Ver historico
commits = git.get_history(limit=10)
for c in commits:
    print(f"{c.short_hash}: {c.message}")

# Rollback se necessario
git.rollback_to("abc1234")
```

**O que e versionado:**
- Documentos em `docs/`
- Rascunhos em `drafts/`
- Estado em `.adk_state/`

**O que NAO e versionado (.gitignore):**
- `.context/` (contexto RAG, pode ser grande)
- Logs e arquivos temporarios

#### 2. SessionManager (`session_manager.py`)

Orquestra sessoes isoladas por caso:

```python
from brazilian_legal_pipeline.session_manager import SessionManager

manager = SessionManager()

# Iniciar sessao
session = manager.start_session(
    case_path=Path("/workspace/cliente/caso"),
    case_id="case-abc123"
)
print(f"Sessao: {session.session_id}")

# Executar pipeline na sessao
result = manager.run_pipeline(
    session_id=session.session_id,
    consultation={
        "consulta": {"texto": "Analise este contrato..."},
        "contexto": {"area_direito": "civil"}
    }
)

# Resumir sessao de checkpoint
session = manager.resume_session("session-xyz789")
```

**Metadados de Sessao (`.adk_state/.adk_session.json`):**
```json
{
  "session_id": "session-20260125-051234",
  "case_id": "case-abc123",
  "case_path": "/workspace/cliente/caso",
  "created_at": "2026-01-25T05:12:34Z",
  "status": "active",
  "last_checkpoint": "checkpoint-fase2",
  "git_commit": "abc1234"
}
```

#### 3. session_cli.py

CLI para invocacao via Tauri Shell:

```bash
# Comandos disponiveis
python -m brazilian_legal_pipeline.session_cli --help

# Iniciar e executar (mais comum)
python -m session_cli start-and-run \
  --case-path /workspace/caso \
  --case-id "case-123" \
  --consultation '{"consulta": {...}}'

# Apenas iniciar sessao
python -m session_cli start \
  --case-path /workspace/caso \
  --case-id "case-123"

# Executar em sessao existente
python -m session_cli run \
  --session-id "session-xyz" \
  --consultation '{"consulta": {...}}'

# Ver status Git do caso
python -m session_cli git-status \
  --case-path /workspace/caso
```

### Integracao com Frontend

O `agentBridge.ts` chama o `session_cli.py` via Tauri Shell:

```typescript
// src/services/agentBridge.ts
export const startAndRunCaseSession = async (
  casePath: string,
  caseId: string,
  consultation: Record<string, unknown>,
  options?: SessionOptions
): Promise<SessionResult> => {

  const command = Command.create('python', [
    '-m', 'brazilian_legal_pipeline.session_cli',
    'start-and-run',
    '--case-path', casePath,
    '--case-id', caseId,
    '--consultation', JSON.stringify(consultation)
  ], {
    cwd: 'adk-agents'  // Importante: executa do diretorio adk-agents
  });

  // Eventos sao parseados de stdout
  command.stdout.on('data', (line) => {
    const event = parseADKEvent(line);
    if (event?.type === 'loop_status' && options?.onProgress) {
      options.onProgress({
        state: event.data.state,
        currentPhase: event.data.current_phase,
        progressPercent: event.data.progress_percent
      });
    }
  });

  // ...
};
```

### Hierarquia Case -> Agent na UI

O frontend implementa selecao hierarquica:

1. **Sidebar.tsx**: Usuario primeiro seleciona um Caso
2. **Agentes aparecem**: So apos caso selecionado
3. **App.tsx**: Mantem `activeCaseId` e `activeAgentId` separados
4. **Envio**: Consulta inclui `contextPath` do caso

```typescript
// src/App.tsx
const handleSendMessage = async (content: string, ...) => {
  // Obter caso ativo
  const currentCase = cases.find(c => c.id === activeCaseId);

  if (activeAgent?.id === 'agent-legal-pipeline' && currentCase?.contextPath) {
    // Executa no contexto isolado do caso
    const result = await startAndRunCaseSession(
      currentCase.contextPath,  // Sandbox do caso
      currentCase.id,
      consultation,
      { onProgress: (p) => setPipelineProgress(p) }
    );
  }
};
```

---

## Ferramentas Claude Code

### Subagentes (.claude/agents/)

Agentes especializados para tarefas especificas:

| Agente | Arquivo | Funcao |
|--------|---------|--------|
| tauri-frontend-dev | `tauri-frontend-dev.md` | Desenvolvimento UI React/Vite/Tailwind |
| tauri-rust-dev | `tauri-rust-dev.md` | Desenvolvimento backend Rust |
| tauri-reviewer | `tauri-reviewer.md` | Revisao de seguranca e QA |

**Uso:**
```
@tauri-frontend-dev Implemente um componente de modal
```

### Skills (.claude/skills/)

Skills ativaveis por padroes:

| Skill | Arquivo | Trigger |
|-------|---------|---------|
| Tauri Core | `tauri-core.md` | Mencao de "tauri" |
| Tauri Frontend | `tauri-frontend.md` | Arquivos .tsx/.jsx |
| Tauri Native APIs | `tauri-native-apis.md` | Plugins Tauri |

### Comandos (.claude/commands/)

Comandos customizados:

| Comando | Funcao |
|---------|--------|
| /commit | Cria commit seguindo convencoes |
| /deep-research | Pesquisa profunda sobre topico |

### skill-rules.json

Configuracao de triggers automaticos:

```json
{
  "rules": [
    {
      "name": "tauri-frontend",
      "trigger": {
        "filePatterns": ["**/*.tsx", "**/*.jsx"],
        "keywords": ["component", "react", "hook"]
      },
      "skill": "tauri-frontend"
    }
  ]
}
```

---

## Ferramentas Gemini CLI

### Skills (.gemini/skills/)

Espelhadas do Claude Code para consistencia:

```
.gemini/
|-- skills/
|   |-- skill-developer.md
|   |-- systematic-debugging.md
|   |-- tauri-core.md
|   |-- tauri-frontend.md
|   |-- tauri-reviewer.md
```

---

## Protocolo de Eventos ADK

Agentes Python emitem eventos via stdout:

```python
def emit_event(event_type: str, data: dict):
    event = {"type": event_type, "data": data, "timestamp": datetime.now().isoformat()}
    print(f"__ADK_EVENT__{json.dumps(event)}__ADK_EVENT__")
```

### Tipos de Eventos

| Tipo | Dados | Descricao |
|------|-------|-----------|
| `session_created` | `{session_id: string}` | Sessao iniciada |
| `loop_status` | `{state, current_phase, progress_percent}` | Progresso da pipeline |
| `cli_result` | `{success, data?, error?}` | Resultado final |

### Parser no Frontend

```typescript
// src/services/agentBridge.ts
export const parseADKEvent = (line: string): ADKEvent | null => {
  const eventPattern = /__ADK_EVENT__(.+?)__ADK_EVENT__/;
  const match = line.match(eventPattern);
  if (match && match[1]) {
    return JSON.parse(match[1]);
  }
  return null;
};
```

---

## Criando Novo Agente

### 1. Estrutura de Arquivos

```bash
mkdir -p adk-agents/meu_agente
cd adk-agents/meu_agente

# Criar venv
python -m venv .venv
source .venv/bin/activate
pip install google-adk google-genai python-dotenv
```

### 2. agent.py Basico

```python
import os
import sys
import json
from datetime import datetime
from google import genai

def emit_event(event_type: str, data: dict):
    event = {"type": event_type, "data": data, "timestamp": datetime.now().isoformat()}
    print(f"__ADK_EVENT__{json.dumps(event)}__ADK_EVENT__")

def main(consulta: str):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        emit_event("cli_result", {"success": False, "error": "GEMINI_API_KEY nao configurada"})
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    emit_event("session_created", {"session_id": f"session-{datetime.now().strftime('%Y%m%d%H%M%S')}"})

    # ... logica do agente ...

    emit_event("cli_result", {"success": True, "data": {"output": resultado}})

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python agent.py <consulta>")
        sys.exit(1)
    main(sys.argv[1])
```

### 3. Registrar no Frontend

Ver secao "Como Registrar um Agente no Frontend" acima.
