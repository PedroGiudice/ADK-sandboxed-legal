# API de Servicos

Documentacao dos 6 servicos do frontend React.

---

## adkService.ts

**Caminho:** `src/services/adkService.ts`
**Linhas:** ~60
**Responsabilidade:** Cliente direto para Gemini SDK

### Funcoes

#### `sendPromptToAgent(prompt, agent, config)`

Envia prompt para Gemini via SDK direto.

```typescript
const response = await sendPromptToAgent(
  "Analise este contrato",
  activeAgent,
  runtimeConfig
);
```

**Parametros:**
- `prompt: string` - Texto do usuario
- `agent: AgentProfile` - Perfil do agente (name, specialization)
- `config: RuntimeConfig` - Configuracoes (temperature, topK, etc.)

**Retorno:** `Promise<string>` - Resposta do modelo

**Configuracao Interna:**
- Modelo: `gemini-3-pro-preview`
- Thinking Budget: 32768
- Grounding: Opcional via Google Search

---

## agentBridge.ts

**Caminho:** `src/services/agentBridge.ts`
**Linhas:** ~550
**Responsabilidade:** Bridge Tauri-Python para execucao de agentes

### Tipos

```typescript
interface AgentResult {
  success: boolean;
  output?: string;
  error?: string;
  outputPath?: string;
}

interface PipelineProgress {
  state: string;
  currentPhase: string;
  progressPercent: number;
  lastCheckpoint?: string;
}

interface SessionResult {
  success: boolean;
  sessionId?: string;
  data?: Record<string, unknown>;
  error?: string;
}
```

### Funcoes Principais

#### `runJurisprudenceAgent(topic, onProgress?)`

Executa agente de jurisprudencia.

```typescript
const result = await runJurisprudenceAgent(
  "Responsabilidade civil",
  (line) => console.log(line)
);
```

#### `startAndRunCaseSession(casePath, caseId, consultation, options?)`

Inicia sessao e executa pipeline em um comando.

```typescript
const result = await startAndRunCaseSession(
  "/workspace/cliente/caso",
  "case-123",
  {
    consulta: { texto: "Analise...", tipo_solicitado: "parecer" }
  },
  {
    onProgress: (progress) => setPipelineProgress(progress),
    onOutput: (line) => console.log('[PIPELINE]:', line)
  }
);
```

#### `parseADKEvent(line)`

Parseia eventos ADK de linha stdout.

```typescript
const event = parseADKEvent("__ADK_EVENT__{...}__ADK_EVENT__");
// { type: "loop_status", data: {...}, timestamp: "..." }
```

#### `stripADKEvents(output)`

Remove eventos ADK de string para texto limpo.

---

## caseRegistryService.ts

**Caminho:** `src/services/caseRegistryService.ts`
**Linhas:** ~385
**Responsabilidade:** Gerenciamento de casos juridicos

### Tipos

```typescript
interface CaseRegistryEntry {
  id: string;
  name: string;
  number?: string;
  client?: string;
  description?: string;
  status: 'active' | 'pending' | 'archived';
  createdAt: string;
  updatedAt: string;
  contextPath: string;  // Caminho absoluto do diretorio
  tags?: string[];
}

interface CaseRegistry {
  version: number;
  workspaceRoot: string;
  cases: CaseRegistryEntry[];
  createdAt: string;
  updatedAt: string;
}
```

### Funcoes de Workspace

#### `getWorkspaceRoot()` / `setWorkspaceRoot(path)`

Gerencia caminho do workspace via localStorage.

#### `selectWorkspaceRoot()`

Abre dialogo nativo para selecionar pasta.

```typescript
const path = await selectWorkspaceRoot();
// Retorna null se usuario cancelar
```

#### `isWorkspaceConfigured()`

Verifica se workspace existe e tem `.registry.json`.

### Funcoes de Caso

#### `createCase(name, options?)`

Cria novo caso com estrutura de diretorios.

```typescript
const caso = await createCase("Processo Trabalhista", {
  number: "0001234-56.2026.5.01.0001",
  client: "Empresa XYZ",
  description: "Reclamacao trabalhista...",
  tags: ["trabalhista", "rescisao"]
});
```

**Estrutura Criada:**
```
caso/
|-- .adk_state/    # Estado do agente
|-- .context/      # Contexto do caso
|-- docs/          # Documentos
|-- drafts/        # Rascunhos
```

#### `listCases(filters?)`

Lista casos com filtros opcionais.

```typescript
const casosAtivos = await listCases({ status: 'active' });
const casosCliente = await listCases({ client: 'Empresa XYZ' });
const casosTrabalhistas = await listCases({ tags: ['trabalhista'] });
```

#### `updateCase(caseId, updates)`

Atualiza caso existente.

#### `archiveCase(caseId)`

Arquiva caso (muda status para 'archived').

#### `toUICase(entry)`

Converte `CaseRegistryEntry` para `LegalCase` (tipo UI).

---

## filesystemService.ts

**Caminho:** `src/services/filesystemService.ts`
**Linhas:** ~150
**Responsabilidade:** Operacoes de arquivo via Tauri plugins

### Funcoes

#### `selectFolder()`

Abre dialogo nativo para selecionar pasta.

```typescript
const path = await selectFolder();
```

#### `createLocalFolder(path, alias?)`

Cria objeto `LocalFolder` a partir de caminho.

#### `checkFolderAccess(path)`

Verifica se pasta existe e esta acessivel.

#### `listFolderContents(path)`

Lista arquivos em uma pasta.

#### `readFileFromFolder(filePath, allowedFolders)`

Le arquivo somente se estiver em pasta permitida.

```typescript
const content = await readFileFromFolder(
  "/workspace/caso/docs/contrato.txt",
  allowedFolders
);
```

#### `writeFileToFolder(filePath, content, allowedFolders)`

Escreve arquivo somente se pasta nao for read-only.

#### `validateFolders(folders)`

Valida que todas as pastas configuradas existem.

---

## googleDriveService.ts

**Caminho:** `src/services/googleDriveService.ts`
**Linhas:** ~230
**Responsabilidade:** OAuth e integracao Google Drive

### Autenticacao

#### `initiateGoogleDriveAuth(clientId)`

Inicia fluxo OAuth abrindo URL no navegador.

#### `completeGoogleDriveAuth(code, clientId, clientSecret)`

Completa OAuth trocando codigo por tokens.

```typescript
const auth = await completeGoogleDriveAuth(
  "4/0AXxxxxxx",   // Codigo do OAuth
  "client-id",
  "client-secret"
);
```

#### `loadGoogleDriveAuth()` / `saveGoogleDriveAuth(auth)`

Gerencia credenciais via Tauri Store (criptografado).

#### `clearGoogleDriveAuth()` / `disconnectGoogleDrive()`

Remove credenciais salvas.

#### `isTokenExpired(auth)`

Verifica se token expirou (com buffer de 60s).

### Operacoes de Arquivo

#### `listDriveFiles(accessToken, folderId?, pageToken?)`

Lista arquivos do Drive.

```typescript
const { files, nextPageToken } = await listDriveFiles(token, folderId);
```

#### `downloadDriveFile(accessToken, fileId, fileName, downloadPath)`

Baixa arquivo do Drive para sistema local.

#### `uploadToDrive(accessToken, localPath, folderId?, fileName?)`

Envia arquivo local para o Drive.

### Utilitarios

#### `getFileIcon(mimeType)`

Retorna nome do icone baseado no tipo MIME.

#### `formatFileSize(sizeStr)`

Formata tamanho para exibicao (KB, MB, GB).

---

## mcpService.ts

**Caminho:** `src/services/mcpService.ts`
**Linhas:** ~145
**Responsabilidade:** Configuracao de servidores MCP

### Funcoes

#### `createMCPServer(name, url)`

Cria novo servidor MCP.

```typescript
const server = createMCPServer("Context7", "http://localhost:3000");
```

#### `validateMCPUrl(url)`

Valida URL do servidor (http, https, ws, wss).

#### `checkMCPHealth(server)` / `checkAllMCPHealth(servers)`

Verifica status dos servidores (GET /health).

```typescript
const healthyServer = await checkMCPHealth(server);
// server.status = 'online' | 'offline'
```

#### `discoverMCPTools(server)` / `discoverAllMCPTools(servers)`

Descobre ferramentas disponiveis (GET /tools).

#### `mcpServersToEnv(servers)`

Converte configuracao para variaveis de ambiente.

```typescript
const env = mcpServersToEnv(enabledServers);
// { MCP_SERVERS: "[{...}]", MCP_SERVER_COUNT: "2" }
```
