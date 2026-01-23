# Deep Research Agent - Session Prompt

Copie e cole este prompt para iniciar uma nova sessao dedicada ao agente.

---

## PROMPT DE SESSAO

```
CONTEXTO DO PROJETO: Agente ADK Deep Research

Estou desenvolvendo um agente autonomo de pesquisa profunda usando o Google Agent Development Kit (ADK). O objetivo e criar uma alternativa programatica ao "Deep Research" do Gemini Web UI, com controle total sobre o output e eliminacao de "fluff" jornalistico.

LOCALIZACAO DOS ARQUIVOS:
- Implementacao: adk-agents/deep_research_sandbox/deep_research_agent.py
- README: adk-agents/deep_research_sandbox/README.md
- Dependencies: adk-agents/deep_research_sandbox/requirements.txt
- Venv: adk-agents/deep_research_sandbox/.venv/
- Plano arquitetural: docs/research-pesquisas/Gemini_ADK_Deep_Research_Agent.md

STACK TECNICA:
- Python 3.12+
- google-adk>=0.3.0 (Agent Development Kit)
- google-genai>=1.0.0 (GenAI SDK)
- tenacity (retry logic)
- Model: gemini-2.5-flash

ARQUITETURA IMPLEMENTADA:
1. DeepResearchAgent class com:
   - Lazy initialization do agent ADK
   - google_search tool para grounding
   - InMemorySessionService para sessoes
   - Runner para orquestracao
   - Error handling com retry exponencial

2. System Prompt "Technical Auditor":
   - Negative constraints (NO fluff, NO marketing, NO hedging)
   - Structured output format (tables, bullets, citations)
   - Autonomous query generation
   - Source attribution obrigatoria

3. Zero-Fail Architecture:
   - Nunca crashar o processo principal
   - Retry com exponential backoff
   - Graceful degradation (resultados parciais > nada)

STATUS ATUAL:
- [x] Implementacao base completa
- [x] README documentado
- [x] Dependencies instaladas no venv
- [ ] API key configurada (.env)
- [ ] Teste de execucao
- [ ] Integracao com Interactions API (opcional)

PROXIMOS PASSOS SUGERIDOS:
1. Configurar GOOGLE_API_KEY no .env
2. Executar teste: python deep_research_agent.py "test topic"
3. Avaliar output e ajustar System Prompt se necessario
4. Considerar integracao com Interactions API para Deep Research nativo

DECISAO ARQUITETURAL PENDENTE:
A implementacao atual usa google_search (grounding basico). Existe a opcao de usar a Interactions API com o agente deep-research-pro-preview-12-2025 para Deep Research nativo do Google. Trade-offs:

| Aspecto | google_search (atual) | Interactions API |
|---------|----------------------|------------------|
| Controle | Total (custom prompt) | Limitado |
| Output | Customizavel | Pre-definido Google |
| Tempo max | Ilimitado | 60 min |
| Complexidade | Maior | Menor |

INSTRUCAO:
Foco exclusivo no agente ADK Deep Research. Nao desviar para outros temas do repositorio. Objetivo: garantir que o agente funcione corretamente e produza outputs de alta densidade informacional.
```

---

## COMO USAR

1. Inicie uma nova sessao do Claude Code
2. Navegue ate o diretorio: `cd adk-agents/deep_research_sandbox`
3. Cole o prompt acima
4. Claude tera todo o contexto necessario para continuar o desenvolvimento

## COMANDOS UTEIS

```bash
# Ativar venv
source .venv/bin/activate

# Configurar API key
cp .env.example .env
# Edite .env com sua GOOGLE_API_KEY

# Testar agente
python deep_research_agent.py "Comparison of vector databases: Pinecone vs Weaviate vs Milvus"

# Ver logs
cat research_output/*.log
```
