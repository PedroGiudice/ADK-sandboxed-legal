# Visual Verifier - ADK Agent

Agente ADK (Gemini) para verificacao visual automatizada de aplicacoes web.

## Setup

```bash
cd adk-agents/visual_verifier

# Criar ambiente
python3 -m venv .venv

# Instalar dependencias
.venv/bin/pip install google-adk Pillow playwright

# Instalar browser do Playwright
.venv/bin/playwright install chromium

# Configurar API key (copiar do adk-agents/.env ou criar)
cp ../.env . || cp .env.example .env
```

## Uso

### Via CLI Wrapper (recomendado para Claude Code)

```bash
# Verificacao rapida (console + network)
.venv/bin/python3 verify.py quick https://localhost:3000

# Criar/atualizar baseline
.venv/bin/python3 verify.py baseline https://localhost:3000 homepage

# Verificacao completa (visual + console + network)
.venv/bin/python3 verify.py verify https://localhost:3000 homepage

# Listar baselines
.venv/bin/python3 verify.py list
```

### Via ADK Interativo

```bash
cd adk-agents && source visual_verifier/.venv/bin/activate && adk run visual_verifier
```

## Ferramentas

| Tool | Descricao | Quando usar |
|------|-----------|-------------|
| `verify_page` | Visual + console + network | Apos mudancas de UI |
| `update_baseline` | Salva screenshot de referencia | Apos aprovar mudanca visual |
| `list_baselines` | Lista referencias existentes | Ver o que esta configurado |
| `quick_check` | Apenas console + network | Verificacao rapida |

## Estrutura

```
visual_verifier/
├── agent.py          # Agente + tools (tudo em um arquivo)
├── verify.py         # CLI wrapper para uso direto
├── baselines/        # Screenshots de referencia
└── screenshots/      # Screenshots temporarios
```

## Integracao com Claude Code

```bash
# Comando direto (de qualquer lugar)
/home/cmr-auto/claude-work/repos/lex-vector/adk-agents/visual_verifier/.venv/bin/python3 \
  /home/cmr-auto/claude-work/repos/lex-vector/adk-agents/visual_verifier/verify.py \
  quick https://localhost:3000
```

## Output

```json
{
  "passed": true,
  "url": "https://example.com",
  "checks": ["CONSOLE: OK", "NETWORK: OK (1 requests)"]
}
```
