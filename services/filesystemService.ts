import { open } from '@tauri-apps/plugin-dialog';
import { readTextFile, writeTextFile, exists, mkdir, readDir } from '@tauri-apps/plugin-fs';
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
