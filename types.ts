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