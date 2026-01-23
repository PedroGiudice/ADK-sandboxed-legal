import { AgentProfile, RuntimeConfig } from './types';

export const AVAILABLE_AGENTS: AgentProfile[] = [
  {
    id: 'agent-contract',
    name: 'Contract Analysis Agent',
    specialization: 'Contract Law',
    description: 'Analyzes contractual obligations and validity.',
    version: '1.0',
    status: 'active',
  },
  {
    id: 'agent-caselaw',
    name: 'Case Law Research Agent',
    specialization: 'Legal Research',
    description: 'Retrieves and summarizes relevant case law.',
    version: '1.0',
    status: 'active',
  },
  {
    id: 'agent-statutory',
    name: 'Statutory Interpretation Agent',
    specialization: 'Statutory Law',
    description: 'Interprets legislative text and statutes.',
    version: '1.0',
    status: 'active',
  }
];

export const DEFAULT_CONFIG: RuntimeConfig = {
  apiUrl: 'https://api.google.adk.example/v1',
  contextWindow: 128000,
  temperature: 0.2,
  topK: 40,
  enableGrounding: true,
  securityFilterLevel: 'high',
  outputStyle: 'normal',
};