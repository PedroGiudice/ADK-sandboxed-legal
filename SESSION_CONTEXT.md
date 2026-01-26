# Contexto de Sessao: ADK-SANDBOXED-LEGAL

## Resumo Executivo

Aplicativo Tauri para automacao juridica com agentes ADK (Google Gemini). Pipeline dialetico com 8 agentes especializados para producao de pareceres juridicos.

## Estado Atual

| Componente | Status |
|------------|--------|
| App Tauri | Beta funcional (v0.1.2) |
| Agentes ADK | 8 agentes implementados |
| Google Drive | Integrado |
| MCP | Estrutura pronta |
| RAG/Knowledge Base | NAO IMPLEMENTADO (gap critico) |

## Estrutura do Projeto

```
ADK-sandboxed-legal/
├── src/                    # Frontend React 19
│   ├── App.tsx            # Shell principal
│   ├── components/        # UI components
│   └── services/          # 6 servicos TypeScript
├── src-tauri/             # Backend Rust/Tauri 2.x
│   ├── src/lib.rs         # Commands Tauri
│   └── google_drive.rs    # OAuth Google Drive
├── adk-agents/            # Agentes Python ADK
│   ├── brazilian_legal_pipeline/  # Pipeline principal
│   │   ├── agent.py       # Loop principal (~650 linhas)
│   │   ├── prompts/       # 8 agentes especializados
│   │   ├── tools/         # 5 tools ADK
│   │   └── schemas/       # Pydantic schemas
│   ├── jurisprudence_agent/  # Pesquisa iterativa
│   └── deep_research_sandbox/
└── docs/                  # Documentacao
```

## Pipeline Juridico (Brazilian Legal Pipeline)

### Fluxo de Agentes
```
INTAKE → VERIFICADOR vs CETICO → CONSTRUTOR vs DESTRUIDOR → REDATOR vs CRITICO → SINTETIZADOR
```

### Agentes Especializados

| Agente | Funcao | Tools |
|--------|--------|-------|
| INTAKE | Analisa consulta, extrai elementos | - |
| VERIFICADOR | Valida fontes legais | search_planalto, search_jurisprudence |
| CETICO | Debate adversarial | - |
| CONSTRUTOR | Constroi argumentacao IRAC+ | - |
| DESTRUIDOR | Contra-argumenta | - |
| REDATOR | Produz texto final | read_file, write_file |
| CRITICO | Revisa texto | - |
| SINTETIZADOR | Consolida output final | - |

### Tools Disponiveis

| Tool | Modulo | Funcao |
|------|--------|--------|
| `search_planalto` | legal_search.py | Busca legislacao |
| `search_jurisprudence` | legal_search.py | Busca jurisprudencia |
| `validate_citation` | citation_validator.py | Valida citacoes |
| `read_file` | filesystem.py | Le arquivo do caso |
| `write_file` | filesystem.py | Escreve em drafts/ |

## GAPS CRITICOS

### 1. RAG/Vector Store (Prioridade Maxima)
- Agentes NAO acessam conhecimento extraido
- Sem embeddings de leis brasileiras
- Sem retrieval semantico

### 2. Leis em BD Local
- Busca via HTTP no Planalto (lento, falha)
- Sem cache, sem versionamento
- Leis faltando: CF, CC, CPC, CLT, LGPD, etc

### 3. Integracao com Extrator
- Texto extraido NAO alimenta agentes
- Desconexao entre lex-vector e ADK

## Servicos Frontend

| Servico | Arquivo | Funcao |
|---------|---------|--------|
| adkService | adkService.ts | Cliente Gemini SDK |
| agentBridge | agentBridge.ts | Bridge Tauri-Python |
| caseRegistry | caseRegistryService.ts | Gerenciamento de casos |
| filesystem | filesystemService.ts | FS via Tauri |
| googleDrive | googleDriveService.ts | OAuth + Google Drive |
| mcp | mcpService.ts | Config MCP |

## Estrutura de Caso

```
<workspace>/
└── <cliente>/
    └── <caso>/
        ├── .adk_state/     # Checkpoints
        ├── .context/       # RAG (futuro, vazio)
        ├── docs/           # Documentos do caso
        └── drafts/         # Outputs do agente
```

## Como Rodar

```bash
cd ~/ADK-sandboxed-legal

# Desenvolvimento
bun run tauri dev

# Build
bun run tauri build

# Testar agentes diretamente
cd adk-agents
source .venv/bin/activate  # criar se necessario
python -m brazilian_legal_pipeline.session_cli --help
```

## Documentacao

- `README.md` - Overview
- `CLAUDE.md` - Instrucoes Claude Code
- `docs/ARCHITECTURE.md` - 4 camadas
- `docs/AGENTS.md` - Agentes e tools
- `docs/SERVICES_API.md` - API de servicos

## Proximos Passos

1. **Implementar RAG** - Knowledge base com embeddings
2. **Baixar leis brasileiras** - CF, CC, CPC, CLT em DuckDB
3. **Integrar extrator** - Pipeline: PDF → texto → RAG → agentes
4. **Context Store** - Preencher `.context/` automaticamente
