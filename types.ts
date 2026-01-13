export enum AgentRole {
  SYSTEM = 'SYSTEM',
  USER = 'USER',
  ASSISTANT = 'ASSISTANT'
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
  content: string;
  timestamp: Date;
  metadata?: Record<string, unknown>;
}

export interface RuntimeConfig {
  apiUrl: string;
  contextWindow: number;
  temperature: number;
  topK: number;
  enableGrounding: boolean;
  securityFilterLevel: 'low' | 'medium' | 'high';
}