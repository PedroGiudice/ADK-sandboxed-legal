import { AgentProfile, RuntimeConfig, Theme, MCPServer, LocalFolder, FilesystemConfig, IntegrationsConfig } from './types';
import themesMetadata from '../themes/themes-metadata.json';

// Theme configuration from TOML-generated JSON
export const THEME_CONFIG: Record<string, { name: string; description: string }> = themesMetadata.themes;
export const DEFAULT_THEME = themesMetadata.defaultTheme as Theme;
export const AVAILABLE_THEMES = Object.keys(THEME_CONFIG) as Theme[];

// Storage keys
const THEME_STORAGE_KEY = 'adk_theme_v1';
const FONT_STORAGE_KEY = 'adk_font_v1';
const MESSAGES_STORAGE_KEY = 'adk_chat_history_v1';
const MCP_SERVERS_STORAGE_KEY = 'adk_mcp_servers_v1';
const LOCAL_FOLDERS_STORAGE_KEY = 'adk_local_folders_v1';
const FILESYSTEM_CONFIG_STORAGE_KEY = 'adk_filesystem_config_v1';
const INTEGRATIONS_STORAGE_KEY = 'adk_integrations_v1';

// Common fonts available on most Linux systems
export const COMMON_FONTS = [
  { name: 'System Default', value: 'system-ui, -apple-system, sans-serif' },
  { name: 'Monospace', value: 'ui-monospace, "Cascadia Code", "Source Code Pro", Menlo, Consolas, monospace' },
  { name: 'JetBrains Mono', value: '"JetBrains Mono", monospace' },
  { name: 'Fira Code', value: '"Fira Code", monospace' },
  { name: 'Ubuntu Mono', value: '"Ubuntu Mono", monospace' },
  { name: 'DejaVu Sans Mono', value: '"DejaVu Sans Mono", monospace' },
  { name: 'Liberation Mono', value: '"Liberation Mono", monospace' },
  { name: 'Noto Sans', value: '"Noto Sans", sans-serif' },
  { name: 'Roboto', value: '"Roboto", sans-serif' },
  { name: 'Inter', value: '"Inter", sans-serif' },
];

export const DEFAULT_FONT = COMMON_FONTS[1].value; // Monospace as default

export const loadTheme = (): Theme => {
  if (typeof window !== 'undefined') {
    const saved = localStorage.getItem(THEME_STORAGE_KEY);
    if (saved && AVAILABLE_THEMES.includes(saved as Theme)) {
      return saved as Theme;
    }
  }
  return DEFAULT_THEME;
};

export const saveTheme = (theme: Theme): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(THEME_STORAGE_KEY, theme);
  }
};

// Font management
export const loadFont = (): string => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(FONT_STORAGE_KEY) || DEFAULT_FONT;
  }
  return DEFAULT_FONT;
};

export const saveFont = (font: string): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(FONT_STORAGE_KEY, font);
    document.documentElement.style.setProperty('--font-primary', font);
  }
};

// Messages management
export const clearMessages = (): void => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(MESSAGES_STORAGE_KEY);
  }
};

export const AVAILABLE_AGENTS: AgentProfile[] = [
  {
    id: 'agent-legal-pipeline',
    name: 'Pipeline Juridica Dialetica',
    specialization: 'Raciocinio Juridico',
    description: 'Pipeline completa com debates adversariais (verificacao, construcao, redacao).',
    version: '4.0',
    status: 'active',
  },
  {
    id: 'agent-jurisprudence',
    name: 'Pesquisa de Jurisprudencia',
    specialization: 'Pesquisa Legal',
    description: 'Busca iterativa em tribunais brasileiros (STJ, STF, TJs).',
    version: '1.0',
    status: 'active',
  },
];

// API Key is stored separately for security
const SECURE_KEY_STORAGE = 'adk_secure_key_v1';

const loadSecureKey = (): string => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(SECURE_KEY_STORAGE) || '';
  }
  return '';
};

export const saveSecureKey = (key: string): void => {
  if (typeof window !== 'undefined') {
    if (key) {
      localStorage.setItem(SECURE_KEY_STORAGE, key);
    } else {
      localStorage.removeItem(SECURE_KEY_STORAGE);
    }
  }
};

export const DEFAULT_CONFIG: RuntimeConfig = {
  apiUrl: 'https://generativelanguage.googleapis.com/v1beta',
  contextWindow: 128000,
  temperature: 0.2,
  topK: 40,
  enableGrounding: true,
  securityFilterLevel: 'high',
  outputStyle: 'normal',
  geminiApiKey: loadSecureKey(),
};

// === MCP Servers Storage ===

export const loadMCPServers = (): MCPServer[] => {
  if (typeof window !== 'undefined') {
    const saved = localStorage.getItem(MCP_SERVERS_STORAGE_KEY);
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch {
        return [];
      }
    }
  }
  return [];
};

export const saveMCPServers = (servers: MCPServer[]): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(MCP_SERVERS_STORAGE_KEY, JSON.stringify(servers));
  }
};

// === Local Folders Storage ===

export const loadLocalFolders = (): LocalFolder[] => {
  if (typeof window !== 'undefined') {
    const saved = localStorage.getItem(LOCAL_FOLDERS_STORAGE_KEY);
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch {
        return [];
      }
    }
  }
  return [];
};

export const saveLocalFolders = (folders: LocalFolder[]): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(LOCAL_FOLDERS_STORAGE_KEY, JSON.stringify(folders));
  }
};

// === Filesystem Config Storage ===

export const DEFAULT_FILESYSTEM_CONFIG: FilesystemConfig = {
  mode: 'whitelist',
  whitelistedFolders: [],
};

export const loadFilesystemConfig = (): FilesystemConfig => {
  if (typeof window !== 'undefined') {
    const saved = localStorage.getItem(FILESYSTEM_CONFIG_STORAGE_KEY);
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch {
        return DEFAULT_FILESYSTEM_CONFIG;
      }
    }
  }
  return DEFAULT_FILESYSTEM_CONFIG;
};

export const saveFilesystemConfig = (config: FilesystemConfig): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(FILESYSTEM_CONFIG_STORAGE_KEY, JSON.stringify(config));
  }
};

// === Full Integrations Config ===

export const DEFAULT_INTEGRATIONS_CONFIG: IntegrationsConfig = {
  filesystem: DEFAULT_FILESYSTEM_CONFIG,
  mcpServers: [],
};

export const loadIntegrationsConfig = (): IntegrationsConfig => {
  if (typeof window !== 'undefined') {
    const saved = localStorage.getItem(INTEGRATIONS_STORAGE_KEY);
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch {
        return DEFAULT_INTEGRATIONS_CONFIG;
      }
    }
  }
  return DEFAULT_INTEGRATIONS_CONFIG;
};

export const saveIntegrationsConfig = (config: IntegrationsConfig): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(INTEGRATIONS_STORAGE_KEY, JSON.stringify(config));
  }
};

// === UUID Generator ===

export const generateId = (): string => {
  return crypto.randomUUID ? crypto.randomUUID() :
    'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
};