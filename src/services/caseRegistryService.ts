/**
 * Servico de registro de casos juridicos.
 * Gerencia .registry.json e operacoes de caso no workspace.
 */
import { open } from '@tauri-apps/plugin-dialog';
import { exists, mkdir, readTextFile, writeTextFile, BaseDirectory } from '@tauri-apps/plugin-fs';
import { homeDir, join } from '@tauri-apps/api/path';
import { LegalCase, CaseStatus } from '../types';

// === Tipos ===

export interface CaseRegistryEntry {
  id: string;
  name: string;
  number?: string;
  client?: string;
  description?: string;
  status: CaseStatus;
  createdAt: string;
  updatedAt: string;
  contextPath: string;  // Caminho absoluto do diretorio do caso
  tags?: string[];
}

export interface CaseRegistry {
  version: number;
  workspaceRoot: string;
  cases: CaseRegistryEntry[];
  createdAt: string;
  updatedAt: string;
}

// === Constantes ===

const REGISTRY_VERSION = 1;
const REGISTRY_FILENAME = '.registry.json';
const WORKSPACE_KEY = 'legal_workspace_root';

// === Funcoes Auxiliares ===

/**
 * Gera ID unico para caso
 */
const generateCaseId = (): string => {
  return `case-${Date.now().toString(36)}-${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Sanitiza nome para uso como diretorio
 */
const sanitizeDirName = (name: string): string => {
  return name
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '') // Remove acentos
    .replace(/[^a-zA-Z0-9_\- ]/g, '') // Remove caracteres especiais
    .replace(/\s+/g, '_') // Espacos viram underscore
    .substring(0, 50); // Limita tamanho
};

// === Servico ===

/**
 * Carrega o caminho do workspace salvo no localStorage
 */
export const getWorkspaceRoot = (): string | null => {
  try {
    return localStorage.getItem(WORKSPACE_KEY);
  } catch {
    return null;
  }
};

/**
 * Salva o caminho do workspace no localStorage
 */
export const setWorkspaceRoot = (path: string): void => {
  localStorage.setItem(WORKSPACE_KEY, path);
};

/**
 * Abre dialogo para selecionar pasta do workspace
 */
export const selectWorkspaceRoot = async (): Promise<string | null> => {
  try {
    const selected = await open({
      directory: true,
      multiple: false,
      title: 'Selecione a pasta raiz do workspace juridico'
    });

    if (selected && typeof selected === 'string') {
      setWorkspaceRoot(selected);
      return selected;
    }

    return null;
  } catch (error) {
    console.error('Erro ao selecionar workspace:', error);
    return null;
  }
};

/**
 * Verifica se o workspace esta configurado e valido
 */
export const isWorkspaceConfigured = async (): Promise<boolean> => {
  const root = getWorkspaceRoot();
  if (!root) return false;

  try {
    const registryPath = await join(root, REGISTRY_FILENAME);
    return await exists(registryPath);
  } catch {
    return false;
  }
};

/**
 * Carrega o registry do workspace
 */
export const loadRegistry = async (): Promise<CaseRegistry | null> => {
  const root = getWorkspaceRoot();
  if (!root) return null;

  try {
    const registryPath = await join(root, REGISTRY_FILENAME);
    const fileExists = await exists(registryPath);

    if (!fileExists) {
      // Criar registry vazio
      const newRegistry = await initializeRegistry(root);
      return newRegistry;
    }

    const content = await readTextFile(registryPath);
    const registry = JSON.parse(content) as CaseRegistry;

    // Validar versao
    if (registry.version !== REGISTRY_VERSION) {
      console.warn(`Registry version mismatch: ${registry.version} vs ${REGISTRY_VERSION}`);
    }

    return registry;
  } catch (error) {
    console.error('Erro ao carregar registry:', error);
    return null;
  }
};

/**
 * Salva o registry no workspace
 */
export const saveRegistry = async (registry: CaseRegistry): Promise<boolean> => {
  try {
    const registryPath = await join(registry.workspaceRoot, REGISTRY_FILENAME);

    registry.updatedAt = new Date().toISOString();

    await writeTextFile(registryPath, JSON.stringify(registry, null, 2));
    return true;
  } catch (error) {
    console.error('Erro ao salvar registry:', error);
    return false;
  }
};

/**
 * Inicializa registry em um workspace
 */
export const initializeRegistry = async (workspaceRoot: string): Promise<CaseRegistry> => {
  const now = new Date().toISOString();

  const registry: CaseRegistry = {
    version: REGISTRY_VERSION,
    workspaceRoot,
    cases: [],
    createdAt: now,
    updatedAt: now
  };

  await saveRegistry(registry);
  return registry;
};

/**
 * Cria novo caso no workspace
 */
export const createCase = async (
  name: string,
  options?: {
    number?: string;
    client?: string;
    description?: string;
    tags?: string[];
  }
): Promise<CaseRegistryEntry | null> => {
  const registry = await loadRegistry();
  if (!registry) {
    console.error('Registry nao carregado');
    return null;
  }

  try {
    // Gerar ID e path
    const caseId = generateCaseId();
    const dirName = sanitizeDirName(name);

    // Se tem cliente, criar subpasta
    let contextPath: string;
    if (options?.client) {
      const clientDir = sanitizeDirName(options.client);
      const clientPath = await join(registry.workspaceRoot, clientDir);

      // Criar pasta do cliente se nao existir
      if (!(await exists(clientPath))) {
        await mkdir(clientPath, { recursive: true });
      }

      contextPath = await join(clientPath, dirName);
    } else {
      contextPath = await join(registry.workspaceRoot, dirName);
    }

    // Criar estrutura do caso
    await mkdir(contextPath, { recursive: true });
    await mkdir(await join(contextPath, '.adk_state'), { recursive: true });
    await mkdir(await join(contextPath, '.context'), { recursive: true });
    await mkdir(await join(contextPath, 'docs'), { recursive: true });
    await mkdir(await join(contextPath, 'drafts'), { recursive: true });

    const now = new Date().toISOString();

    const newCase: CaseRegistryEntry = {
      id: caseId,
      name,
      number: options?.number,
      client: options?.client,
      description: options?.description,
      status: 'active',
      createdAt: now,
      updatedAt: now,
      contextPath,
      tags: options?.tags || []
    };

    // Adicionar ao registry
    registry.cases.push(newCase);
    await saveRegistry(registry);

    return newCase;
  } catch (error) {
    console.error('Erro ao criar caso:', error);
    return null;
  }
};

/**
 * Atualiza caso existente
 */
export const updateCase = async (
  caseId: string,
  updates: Partial<Omit<CaseRegistryEntry, 'id' | 'contextPath' | 'createdAt'>>
): Promise<CaseRegistryEntry | null> => {
  const registry = await loadRegistry();
  if (!registry) return null;

  const caseIndex = registry.cases.findIndex(c => c.id === caseId);
  if (caseIndex === -1) return null;

  const updatedCase = {
    ...registry.cases[caseIndex],
    ...updates,
    updatedAt: new Date().toISOString()
  };

  registry.cases[caseIndex] = updatedCase;
  await saveRegistry(registry);

  return updatedCase;
};

/**
 * Arquiva caso (nao deleta, apenas muda status)
 */
export const archiveCase = async (caseId: string): Promise<boolean> => {
  const result = await updateCase(caseId, { status: 'archived' });
  return result !== null;
};

/**
 * Busca caso por ID
 */
export const getCaseById = async (caseId: string): Promise<CaseRegistryEntry | null> => {
  const registry = await loadRegistry();
  if (!registry) return null;

  return registry.cases.find(c => c.id === caseId) || null;
};

/**
 * Lista todos os casos (com filtros opcionais)
 */
export const listCases = async (filters?: {
  status?: CaseStatus;
  client?: string;
  tags?: string[];
}): Promise<CaseRegistryEntry[]> => {
  const registry = await loadRegistry();
  if (!registry) return [];

  let cases = registry.cases;

  if (filters?.status) {
    cases = cases.filter(c => c.status === filters.status);
  }

  if (filters?.client) {
    cases = cases.filter(c => c.client === filters.client);
  }

  if (filters?.tags && filters.tags.length > 0) {
    cases = cases.filter(c =>
      filters.tags!.some(tag => c.tags?.includes(tag))
    );
  }

  // Ordenar por data de atualizacao (mais recente primeiro)
  return cases.sort((a, b) =>
    new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
  );
};

/**
 * Converte CaseRegistryEntry para LegalCase (tipo usado pela UI)
 */
export const toUICase = (entry: CaseRegistryEntry): LegalCase => {
  return {
    id: entry.id,
    name: entry.name,
    number: entry.number,
    client: entry.client,
    description: entry.description,
    status: entry.status,
    createdAt: new Date(entry.createdAt),
    updatedAt: new Date(entry.updatedAt),
    contextPath: entry.contextPath,
    tags: entry.tags
  };
};

/**
 * Lista clientes unicos (para agrupamento)
 */
export const listClients = async (): Promise<string[]> => {
  const registry = await loadRegistry();
  if (!registry) return [];

  const clients = new Set<string>();
  for (const c of registry.cases) {
    if (c.client) {
      clients.add(c.client);
    }
  }

  return Array.from(clients).sort();
};

/**
 * Lista tags unicas (para filtros)
 */
export const listTags = async (): Promise<string[]> => {
  const registry = await loadRegistry();
  if (!registry) return [];

  const tags = new Set<string>();
  for (const c of registry.cases) {
    if (c.tags) {
      c.tags.forEach(t => tags.add(t));
    }
  }

  return Array.from(tags).sort();
};
