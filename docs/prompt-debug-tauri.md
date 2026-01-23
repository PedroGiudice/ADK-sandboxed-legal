# HotCocoa - Debug Sistematico do Tauri

## Contexto
App Tauri (Couple's Memory Deck) com frontend React/TypeScript.
- Browser: FUNCIONA perfeitamente
- Tauri executavel: TRAVA em "standby" (nao renderiza UI corretamente)
- Tailwind: Migrado de CDN para local (ja feito)
- Backend Modal: OK (0 containers = nao e problema de backend)
- Branch: `feat/next-iteration` (CONTINUAR NESTA BRANCH)

## Objetivo
Identificar e corrigir por que o app funciona no browser mas trava no Tauri.

## Instrucoes

### 1. USAR SKILL /systematic-debugging
Invocar IMEDIATAMENTE:
```
/systematic-debugging
```
Seguir o fluxo da skill rigorosamente.

### 2. Hipoteses a Testar (em ordem)
1. **JS Error silencioso** - Verificar console do Tauri WebView
2. **CSS nao carregando** - Verificar se index.css esta no bundle
3. **Estado React travado** - Verificar se App monta e transiciona estados
4. **Recurso bloqueado** - CSP ainda bloqueando algo?
5. **Race condition** - Algo inicializa antes de estar pronto?

### 3. Comandos de Diagnostico
```bash
# Verificar build inclui CSS
ls -la dist/assets/

# Rodar Tauri em modo dev com logs
cargo tauri dev 2>&1 | tee tauri-debug.log

# Verificar CSP atual
grep -A5 '"csp"' src-tauri/tauri.conf.json
```

### 4. Limite de Tentativas
- **MAX 3 tentativas** por hipotese
- Se hipotese falhar 3x, documentar e passar para proxima
- Se TODAS hipoteses falharem: **PARAR e propor migracao para Electron**

### 5. Criterio de Sucesso
- App Tauri abre e mostra tela de upload (PhotoUploader)
- Usuario consegue interagir (upload, navegacao)
- Layout identico ao browser

### 6. Se Precisar Migrar para Electron
Nao e derrota. Plano B pronto:
1. Remover `src-tauri/`
2. Criar `electron/main.js`
3. Ajustar `package.json`
4. Build e testar

## Resultado Esperado
Ao final da sessao:
- App Tauri funcionando OU
- Decisao documentada de migrar para Electron com plano de execucao

## Regras
- ZERO "debug ate a morte" - ser sistematico
- Commitar apos cada fix que funcionar
- Documentar cada tentativa (funcionou/falhou/por que)
- Perguntar ao usuario antes de decisoes grandes
- Usar `/systematic-debugging` skill obrigatoriamente
