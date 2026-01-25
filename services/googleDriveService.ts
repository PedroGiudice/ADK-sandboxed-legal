import { invoke } from '@tauri-apps/api/core';
import { open as openUrl } from '@tauri-apps/plugin-shell';
import { Store } from '@tauri-apps/plugin-store';
import { GoogleDriveAuth, DriveFile } from '../types';

const STORE_KEY = 'google_drive_auth';
const REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'; // Desktop app flow

let store: Store | null = null;

/**
 * Gets or creates the secure store instance
 */
const getStore = async (): Promise<Store> => {
  if (!store) {
    store = await Store.load('integrations.json');
  }
  return store;
};

/**
 * Saves Google Drive credentials to secure store
 */
export const saveGoogleDriveAuth = async (auth: GoogleDriveAuth): Promise<void> => {
  const s = await getStore();
  await s.set(STORE_KEY, auth);
  await s.save();
};

/**
 * Loads Google Drive credentials from secure store
 */
export const loadGoogleDriveAuth = async (): Promise<GoogleDriveAuth | null> => {
  try {
    const s = await getStore();
    const auth = await s.get<GoogleDriveAuth>(STORE_KEY);
    return auth || null;
  } catch {
    return null;
  }
};

/**
 * Clears Google Drive credentials
 */
export const clearGoogleDriveAuth = async (): Promise<void> => {
  const s = await getStore();
  await s.delete(STORE_KEY);
  await s.save();
};

/**
 * Initiates OAuth flow by opening the authorization URL
 */
export const initiateGoogleDriveAuth = async (clientId: string): Promise<string> => {
  const authUrl: string = await invoke('google_drive_auth', {
    clientId,
    redirectUri: REDIRECT_URI,
  });

  // Open the URL in the system browser
  await openUrl(authUrl);

  return authUrl;
};

/**
 * Completes OAuth flow by exchanging the authorization code
 */
export const completeGoogleDriveAuth = async (
  code: string,
  clientId: string,
  clientSecret: string
): Promise<GoogleDriveAuth> => {
  const credentials = await invoke<{
    client_id: string;
    client_secret: string;
    access_token: string;
    refresh_token: string;
    expires_at: number;
  }>('google_drive_callback', {
    code,
    clientId,
    clientSecret,
    redirectUri: REDIRECT_URI,
  });

  const auth: GoogleDriveAuth = {
    clientId: credentials.client_id,
    clientSecret: credentials.client_secret,
    accessToken: credentials.access_token,
    refreshToken: credentials.refresh_token,
    expiresAt: credentials.expires_at,
  };

  await saveGoogleDriveAuth(auth);

  return auth;
};

/**
 * Lists files from Google Drive
 */
export const listDriveFiles = async (
  accessToken: string,
  folderId?: string,
  pageToken?: string
): Promise<{ files: DriveFile[]; nextPageToken?: string }> => {
  const result = await invoke<{
    files: Array<{
      id: string;
      name: string;
      mimeType: string;
      modifiedTime?: string;
      size?: string;
      parents?: string[];
    }>;
    next_page_token?: string;
  }>('google_drive_list_files', {
    accessToken,
    folderId: folderId || null,
    pageToken: pageToken || null,
  });

  return {
    files: result.files.map(f => ({
      id: f.id,
      name: f.name,
      mimeType: f.mimeType,
      modifiedTime: f.modifiedTime,
      size: f.size,
      parents: f.parents,
    })),
    nextPageToken: result.next_page_token,
  };
};

/**
 * Downloads a file from Google Drive
 */
export const downloadDriveFile = async (
  accessToken: string,
  fileId: string,
  fileName: string,
  downloadPath: string
): Promise<string> => {
  return await invoke<string>('google_drive_download', {
    accessToken,
    fileId,
    fileName,
    downloadPath,
  });
};

/**
 * Uploads a file to Google Drive
 */
export const uploadToDrive = async (
  accessToken: string,
  localPath: string,
  folderId?: string,
  fileName?: string
): Promise<DriveFile> => {
  const result = await invoke<{
    id: string;
    name: string;
    mimeType: string;
    modifiedTime?: string;
    size?: string;
    parents?: string[];
  }>('google_drive_upload', {
    accessToken,
    localPath,
    folderId: folderId || null,
    fileName: fileName || null,
  });

  return {
    id: result.id,
    name: result.name,
    mimeType: result.mimeType,
    modifiedTime: result.modifiedTime,
    size: result.size,
    parents: result.parents,
  };
};

/**
 * Disconnects Google Drive and clears stored credentials
 */
export const disconnectGoogleDrive = async (): Promise<void> => {
  await invoke('google_drive_disconnect');
  await clearGoogleDriveAuth();
};

/**
 * Checks if the access token is expired
 */
export const isTokenExpired = (auth: GoogleDriveAuth): boolean => {
  if (!auth.expiresAt) return true;
  // Add 60 second buffer
  return Date.now() / 1000 > auth.expiresAt - 60;
};

/**
 * Gets file icon based on mime type
 */
export const getFileIcon = (mimeType: string): string => {
  if (mimeType === 'application/vnd.google-apps.folder') return 'folder';
  if (mimeType.includes('document') || mimeType.includes('word')) return 'file-text';
  if (mimeType.includes('spreadsheet') || mimeType.includes('excel')) return 'table';
  if (mimeType.includes('presentation') || mimeType.includes('powerpoint')) return 'presentation';
  if (mimeType.includes('pdf')) return 'file-pdf';
  if (mimeType.includes('image')) return 'image';
  return 'file';
};

/**
 * Formats file size for display
 */
export const formatFileSize = (sizeStr?: string): string => {
  if (!sizeStr) return '--';
  const size = parseInt(sizeStr, 10);
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  if (size < 1024 * 1024 * 1024) return `${(size / (1024 * 1024)).toFixed(1)} MB`;
  return `${(size / (1024 * 1024 * 1024)).toFixed(1)} GB`;
};
