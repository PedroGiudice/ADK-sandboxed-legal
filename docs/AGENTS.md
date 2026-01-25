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
