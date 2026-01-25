export enum AgentRole {
  SYSTEM = 'SYSTEM',
  USER = 'USER',
  ASSISTANT = 'ASSISTANT'
}

export type Theme = 'dark' | 'light' | 'high-contrast' | 'ocean';

export type OutputStyle = 'concise' | 'normal' | 'verbose';

export type MessagePartType = 'text' | 'thought' | 'tool_call' | 'tool_result' | 'bash' | 'file_op';

export interface MessagePart {
  type: MessagePartType;
  content: string;
  metadata?: {
    toolName?: string;
    filePath?: string;
    exitCode?: number;
    language?: string;
    isCollapsed?: boolean;
  };
}

export interface Attachment {
  id: string;
  name: string;
  type: string;
  size: number;
  data: string; // Base64 string
}

export interface AgentProfile {
  id: string;
  name: string;
  specialization: string;
  description: string;
  version: string;
  status: 'active' | 'maintenance' | 'deprecated';
  mcpServers?: MCPServer[]; // MCPs especificos deste agente
}

export interface Message {
  id: string;
  role: AgentRole;
  content: string; // Fallback text
  parts?: MessagePart[]; // Structured dynamic content
  timestamp: Date;
  metadata?: Record<string, unknown>;
  attachments?: Attachment[];
}

export interface RuntimeConfig {
  apiUrl: string;
  contextWindow: number;
  temperature: number;
  topK: number;
  enableGrounding: boolean;
  securityFilterLevel: 'low' | 'medium' | 'high';
  outputStyle: OutputStyle;
  geminiApiKey: string; // Stored securely, never logged
}

// === MCP (Model Context Protocol) ===

export interface MCPServer {
  id: string;
  name: string;
  url: string;
  tools?: string[];
  enabled: boolean;
  lastHealthCheck?: Date;
  status?: 'online' | 'offline' | 'unknown';
}

// === Filesystem ===

export interface LocalFolder {
  id: string;
  path: string;
  alias: string; // Nome amigavel
  readOnly: boolean;
  enabled: boolean;
}

export interface FilesystemConfig {
  mode: 'whitelist' | 'unrestricted';
  whitelistedFolders: LocalFolder[];
}

// === Google Drive ===

export interface GoogleDriveAuth {
  clientId: string;
  clientSecret: string;
  accessToken?: string;
  refreshToken?: string;
  expiresAt?: number;
  userEmail?: string;
}

export interface DriveFile {
  id: string;
  name: string;
  mimeType: string;
  modifiedTime?: string;
  size?: string;
  parents?: string[];
}

// === Integrations Config (combines all) ===

export interface IntegrationsConfig {
  filesystem: FilesystemConfig;
  googleDrive?: GoogleDriveAuth;
  mcpServers: MCPServer[];
}

// === Legal Case (Entidade Juridica / Projeto) ===

export type CaseStatus = 'active' | 'archived' | 'pending';

export interface LegalCase {
  id: string;
  name: string;
  number?: string; // Numero do processo (opcional)
  client?: string;
  description?: string;
  status: CaseStatus;
  createdAt: Date;
  updatedAt: Date;
  // Contexto isolado
  contextPath?: string; // Caminho do diretorio/branch
  tags?: string[];
}

// === Agent Instance (Instancia Efemera Vinculada) ===

export interface AgentInstance {
  agentId: string;
  caseId: string;
  sessionId: string;
  createdAt: Date;
  // Historico da sessao (hot-swapping preserva isso)
  messageHistory?: Message[];
}

// === Workspace Context (Estado Global da UI) ===

export interface WorkspaceContext {
  activeCase: LegalCase | null;
  activeAgent: AgentProfile | null;
  agentInstance: AgentInstance | null;
}