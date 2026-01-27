import { open } from '@tauri-apps/plugin-dialog';
import { readTextFile, writeTextFile, writeFile, exists, mkdir, readDir } from '@tauri-apps/plugin-fs';
import { join } from '@tauri-apps/api/path';
import { LocalFolder } from '../types';
import { generateId } from '../constants';

/**
 * Opens a native folder picker dialog and returns the selected path
 */
export const selectFolder = async (): Promise<string | null> => {
  try {
    const selected = await open({
      directory: true,
      multiple: false,
      title: 'Selecionar Pasta',
    });

    if (typeof selected === 'string') {
      return selected;
    }
    return null;
  } catch (error) {
    console.error('Erro ao selecionar pasta:', error);
    return null;
  }
};

/**
 * Creates a LocalFolder object from a path with a default alias
 */
export const createLocalFolder = (path: string, alias?: string): LocalFolder => {
  const folderName = path.split('/').pop() || path;
  return {
    id: generateId(),
    path,
    alias: alias || folderName,
    readOnly: false,
    enabled: true,
  };
};

/**
 * Checks if a folder path exists and is accessible
 */
export const checkFolderAccess = async (path: string): Promise<boolean> => {
  try {
    return await exists(path);
  } catch {
    return false;
  }
};

/**
 * Lists files in a folder
 */
export const listFolderContents = async (path: string): Promise<string[]> => {
  try {
    const entries = await readDir(path);
    return entries.map(entry => entry.name);
  } catch (error) {
    console.error('Erro ao listar pasta:', error);
    return [];
  }
};

/**
 * Reads a text file from an allowed folder
 */
export const readFileFromFolder = async (
  filePath: string,
  allowedFolders: LocalFolder[]
): Promise<string | null> => {
  // Check if file is in an allowed folder
  const isAllowed = allowedFolders.some(
    folder => folder.enabled && filePath.startsWith(folder.path)
  );

  if (!isAllowed) {
    console.error('Arquivo fora das pastas permitidas:', filePath);
    return null;
  }

  try {
    return await readTextFile(filePath);
  } catch (error) {
    console.error('Erro ao ler arquivo:', error);
    return null;
  }
};

/**
 * Writes a text file to an allowed folder
 */
export const writeFileToFolder = async (
  filePath: string,
  content: string,
  allowedFolders: LocalFolder[]
): Promise<boolean> => {
  // Check if file is in an allowed folder that is not read-only
  const folder = allowedFolders.find(
    f => f.enabled && !f.readOnly && filePath.startsWith(f.path)
  );

  if (!folder) {
    console.error('Arquivo fora das pastas permitidas ou pasta somente leitura:', filePath);
    return false;
  }

  try {
    await writeTextFile(filePath, content);
    return true;
  } catch (error) {
    console.error('Erro ao escrever arquivo:', error);
    return false;
  }
};

/**
 * Creates a directory if it doesn't exist
 */
export const ensureDirectory = async (path: string): Promise<boolean> => {
  try {
    const pathExists = await exists(path);
    if (!pathExists) {
      await mkdir(path, { recursive: true });
    }
    return true;
  } catch (error) {
    console.error('Erro ao criar diretorio:', error);
    return false;
  }
};

/**
 * Validates that all configured folders still exist
 */
export const validateFolders = async (folders: LocalFolder[]): Promise<LocalFolder[]> => {
  const validated: LocalFolder[] = [];

  for (const folder of folders) {
    const accessible = await checkFolderAccess(folder.path);
    validated.push({
      ...folder,
      enabled: accessible ? folder.enabled : false,
    });
  }

  return validated;
};

/**
 * Documento anexo salvo em disco
 */
export interface SavedDocument {
  nome: string;
  tipo: string;
  caminho: string; // Path relativo ao caso
  tamanho: number;
}

/**
 * Salva um arquivo binario (de base64) no diretorio docs/ do caso
 * Retorna o path relativo para passar ao agente Python
 */
export const saveAttachmentToCase = async (
  casePath: string,
  fileName: string,
  base64Data: string,
  mimeType: string
): Promise<SavedDocument | null> => {
  try {
    // Garantir que o diretorio docs existe
    const docsDir = await join(casePath, 'docs');
    await ensureDirectory(docsDir);

    // Sanitizar nome do arquivo
    const safeName = fileName.replace(/[^a-zA-Z0-9._-]/g, '_');
    const uniqueName = `${Date.now()}_${safeName}`;
    const fullPath = await join(docsDir, uniqueName);

    // Converter base64 para Uint8Array
    // Remove o prefixo data:mime;base64, se presente
    const base64Content = base64Data.includes(',')
      ? base64Data.split(',')[1]
      : base64Data;

    const binaryString = atob(base64Content);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }

    // Salvar arquivo
    await writeFile(fullPath, bytes);

    return {
      nome: fileName,
      tipo: mimeType,
      caminho: `docs/${uniqueName}`, // Path relativo ao caso
      tamanho: bytes.length
    };
  } catch (error) {
    console.error('Erro ao salvar anexo:', error);
    return null;
  }
};
