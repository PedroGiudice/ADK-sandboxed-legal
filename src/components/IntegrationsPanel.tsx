import React, { useState, useEffect } from 'react';
import {
  MCPServer,
  LocalFolder,
  FilesystemConfig,
  GoogleDriveAuth,
  DriveFile,
} from '../types';
import {
  loadIntegrationsConfig,
  saveIntegrationsConfig,
  generateId,
} from '../constants';
import { selectFolder, createLocalFolder, validateFolders } from '../services/filesystemService';
import {
  createMCPServer,
  validateMCPUrl,
  checkAllMCPHealth,
} from '../services/mcpService';
import {
  loadGoogleDriveAuth,
  initiateGoogleDriveAuth,
  completeGoogleDriveAuth,
  listDriveFiles,
  disconnectGoogleDrive,
  formatFileSize,
  getFileIcon,
} from '../services/googleDriveService';

type TabType = 'mcp' | 'filesystem' | 'googledrive';

interface IntegrationsPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

const IntegrationsPanel: React.FC<IntegrationsPanelProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<TabType>('filesystem');

  // MCP State
  const [mcpServers, setMcpServers] = useState<MCPServer[]>([]);
  const [newMcpName, setNewMcpName] = useState('');
  const [newMcpUrl, setNewMcpUrl] = useState('');
  const [mcpError, setMcpError] = useState('');

  // Filesystem State
  const [filesystemConfig, setFilesystemConfig] = useState<FilesystemConfig>({
    mode: 'whitelist',
    whitelistedFolders: [],
  });

  // Google Drive State
  const [driveAuth, setDriveAuth] = useState<GoogleDriveAuth | null>(null);
  const [driveFiles, setDriveFiles] = useState<DriveFile[]>([]);
  const [driveLoading, setDriveLoading] = useState(false);
  const [driveError, setDriveError] = useState('');
  const [showAuthDialog, setShowAuthDialog] = useState(false);
  const [authCode, setAuthCode] = useState('');
  const [clientId, setClientId] = useState('');
  const [clientSecret, setClientSecret] = useState('');

  // Load saved config on mount
  useEffect(() => {
    const config = loadIntegrationsConfig();
    setMcpServers(config.mcpServers || []);
    setFilesystemConfig(config.filesystem);

    // Load Google Drive auth from secure store
    loadGoogleDriveAuth().then(auth => {
      if (auth) {
        setDriveAuth(auth);
        setClientId(auth.clientId);
        setClientSecret(auth.clientSecret);
      }
    });
  }, []);

  // Save config whenever it changes
  const saveConfig = () => {
    saveIntegrationsConfig({
      mcpServers,
      filesystem: filesystemConfig,
      googleDrive: driveAuth || undefined,
    });
  };

  // === MCP Handlers ===

  const handleAddMcpServer = () => {
    if (!newMcpName.trim()) {
      setMcpError('Nome e obrigatorio');
      return;
    }
    if (!validateMCPUrl(newMcpUrl)) {
      setMcpError('URL invalida (use http://, https://, ws:// ou wss://)');
      return;
    }

    const server = createMCPServer(newMcpName.trim(), newMcpUrl.trim());
    const updated = [...mcpServers, server];
    setMcpServers(updated);
    setNewMcpName('');
    setNewMcpUrl('');
    setMcpError('');

    saveIntegrationsConfig({
      mcpServers: updated,
      filesystem: filesystemConfig,
      googleDrive: driveAuth || undefined,
    });
  };

  const handleRemoveMcpServer = (id: string) => {
    const updated = mcpServers.filter(s => s.id !== id);
    setMcpServers(updated);
    saveIntegrationsConfig({
      mcpServers: updated,
      filesystem: filesystemConfig,
      googleDrive: driveAuth || undefined,
    });
  };

  const handleToggleMcpServer = (id: string) => {
    const updated = mcpServers.map(s =>
      s.id === id ? { ...s, enabled: !s.enabled } : s
    );
    setMcpServers(updated);
    saveIntegrationsConfig({
      mcpServers: updated,
      filesystem: filesystemConfig,
      googleDrive: driveAuth || undefined,
    });
  };

  const handleCheckMcpHealth = async () => {
    const updated = await checkAllMCPHealth(mcpServers);
    setMcpServers(updated);
  };

  // === Filesystem Handlers ===

  const handleAddFolder = async () => {
    const path = await selectFolder();
    if (path) {
      const folder = createLocalFolder(path);
      const updated = {
        ...filesystemConfig,
        whitelistedFolders: [...filesystemConfig.whitelistedFolders, folder],
      };
      setFilesystemConfig(updated);
      saveIntegrationsConfig({
        mcpServers,
        filesystem: updated,
        googleDrive: driveAuth || undefined,
      });
    }
  };

  const handleRemoveFolder = (id: string) => {
    const updated = {
      ...filesystemConfig,
      whitelistedFolders: filesystemConfig.whitelistedFolders.filter(f => f.id !== id),
    };
    setFilesystemConfig(updated);
    saveIntegrationsConfig({
      mcpServers,
      filesystem: updated,
      googleDrive: driveAuth || undefined,
    });
  };

  const handleToggleFolder = (id: string) => {
    const updated = {
      ...filesystemConfig,
      whitelistedFolders: filesystemConfig.whitelistedFolders.map(f =>
        f.id === id ? { ...f, enabled: !f.enabled } : f
      ),
    };
    setFilesystemConfig(updated);
    saveIntegrationsConfig({
      mcpServers,
      filesystem: updated,
      googleDrive: driveAuth || undefined,
    });
  };

  const handleToggleReadOnly = (id: string) => {
    const updated = {
      ...filesystemConfig,
      whitelistedFolders: filesystemConfig.whitelistedFolders.map(f =>
        f.id === id ? { ...f, readOnly: !f.readOnly } : f
      ),
    };
    setFilesystemConfig(updated);
    saveIntegrationsConfig({
      mcpServers,
      filesystem: updated,
      googleDrive: driveAuth || undefined,
    });
  };

  const handleToggleFilesystemMode = () => {
    const updated = {
      ...filesystemConfig,
      mode: filesystemConfig.mode === 'whitelist' ? 'unrestricted' as const : 'whitelist' as const,
    };
    setFilesystemConfig(updated);
    saveIntegrationsConfig({
      mcpServers,
      filesystem: updated,
      googleDrive: driveAuth || undefined,
    });
  };

  const handleUpdateFolderAlias = (id: string, alias: string) => {
    const updated = {
      ...filesystemConfig,
      whitelistedFolders: filesystemConfig.whitelistedFolders.map(f =>
        f.id === id ? { ...f, alias } : f
      ),
    };
    setFilesystemConfig(updated);
    saveIntegrationsConfig({
      mcpServers,
      filesystem: updated,
      googleDrive: driveAuth || undefined,
    });
  };

  // === Google Drive Handlers ===

  const handleConnectDrive = async () => {
    if (!clientId.trim()) {
      setDriveError('Client ID e obrigatorio');
      return;
    }

    try {
      setDriveLoading(true);
      setDriveError('');
      await initiateGoogleDriveAuth(clientId.trim());
      setShowAuthDialog(true);
    } catch (error) {
      setDriveError(`Erro ao iniciar autenticacao: ${error}`);
    } finally {
      setDriveLoading(false);
    }
  };

  const handleCompleteAuth = async () => {
    if (!authCode.trim() || !clientId.trim() || !clientSecret.trim()) {
      setDriveError('Preencha todos os campos');
      return;
    }

    try {
      setDriveLoading(true);
      setDriveError('');
      const auth = await completeGoogleDriveAuth(
        authCode.trim(),
        clientId.trim(),
        clientSecret.trim()
      );
      setDriveAuth(auth);
      setShowAuthDialog(false);
      setAuthCode('');

      // Load files after auth
      if (auth.accessToken) {
        const result = await listDriveFiles(auth.accessToken);
        setDriveFiles(result.files);
      }
    } catch (error) {
      setDriveError(`Erro na autenticacao: ${error}`);
    } finally {
      setDriveLoading(false);
    }
  };

  const handleDisconnectDrive = async () => {
    await disconnectGoogleDrive();
    setDriveAuth(null);
    setDriveFiles([]);
    setClientSecret('');
  };

  const handleRefreshDriveFiles = async () => {
    if (!driveAuth?.accessToken) return;

    try {
      setDriveLoading(true);
      const result = await listDriveFiles(driveAuth.accessToken);
      setDriveFiles(result.files);
    } catch (error) {
      setDriveError(`Erro ao listar arquivos: ${error}`);
    } finally {
      setDriveLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="absolute inset-0 z-50 flex justify-end bg-black/40 backdrop-blur-sm">
      <div className="w-[500px] bg-surface h-full shadow-2xl border-l border-border flex flex-col animate-in slide-in-from-right duration-300">
        {/* Header */}
        <div className="p-5 border-b border-border flex justify-between items-center bg-surface">
          <div>
            <h3 className="font-bold text-foreground serif-font">Integracoes</h3>
            <p className="text-xs text-foreground-subtle">Configure MCP, Pastas e Google Drive</p>
          </div>
          <button
            onClick={onClose}
            className="text-foreground-subtle hover:text-foreground transition-colors text-2xl leading-none"
          >
            &times;
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-border bg-surface-elevated">
          {[
            { id: 'filesystem' as TabType, label: 'Pastas Locais', icon: 'M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z' },
            { id: 'mcp' as TabType, label: 'MCP Servers', icon: 'M8 4H6a2 2 0 00-2 2v12a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-2m-4-1v8m0 0l3-3m-3 3L9 8m-5 5h2.586a1 1 0 01.707.293l2.414 2.414a1 1 0 00.707.293h3.172a1 1 0 00.707-.293l2.414-2.414a1 1 0 01.707-.293H19' },
            { id: 'googledrive' as TabType, label: 'Google Drive', icon: 'M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12' },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 py-3 px-4 text-xs font-medium transition-colors flex items-center justify-center gap-2
                ${activeTab === tab.id
                  ? 'text-accent border-b-2 border-accent bg-surface'
                  : 'text-foreground-muted hover:text-foreground'
                }`}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={tab.icon} />
              </svg>
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-5">
          {/* Filesystem Tab */}
          {activeTab === 'filesystem' && (
            <div className="space-y-4">
              {/* Mode Toggle */}
              <div className="flex items-center justify-between p-3 bg-surface-elevated rounded-lg border border-border">
                <div>
                  <span className="text-sm text-foreground font-medium">Modo de Acesso</span>
                  <p className="text-xs text-foreground-subtle">
                    {filesystemConfig.mode === 'whitelist'
                      ? 'Apenas pastas autorizadas'
                      : 'Acesso livre ao sistema'}
                  </p>
                </div>
                <button
                  onClick={handleToggleFilesystemMode}
                  className={`px-3 py-1 text-xs font-medium rounded transition-colors
                    ${filesystemConfig.mode === 'whitelist'
                      ? 'bg-accent text-surface'
                      : 'bg-warning text-surface'
                    }`}
                >
                  {filesystemConfig.mode === 'whitelist' ? 'Whitelist' : 'Livre'}
                </button>
              </div>

              {filesystemConfig.mode === 'unrestricted' && (
                <div className="p-3 bg-warning/10 border border-warning/30 rounded-lg">
                  <p className="text-xs text-warning">
                    Atencao: Modo livre permite acesso a qualquer pasta do sistema. Use com cuidado.
                  </p>
                </div>
              )}

              {/* Add Folder Button */}
              <button
                onClick={handleAddFolder}
                className="w-full py-2 px-4 bg-accent hover:bg-accent-hover text-surface rounded font-medium text-sm transition-colors flex items-center justify-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Adicionar Pasta
              </button>

              {/* Folders List */}
              <div className="space-y-2">
                {filesystemConfig.whitelistedFolders.length === 0 ? (
                  <p className="text-sm text-foreground-subtle text-center py-4">
                    Nenhuma pasta configurada
                  </p>
                ) : (
                  filesystemConfig.whitelistedFolders.map(folder => (
                    <div
                      key={folder.id}
                      className={`p-3 rounded-lg border transition-colors ${
                        folder.enabled
                          ? 'bg-surface-elevated border-border'
                          : 'bg-surface border-border-subtle opacity-60'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <input
                            type="text"
                            value={folder.alias}
                            onChange={e => handleUpdateFolderAlias(folder.id, e.target.value)}
                            className="text-sm font-medium text-foreground bg-transparent border-none focus:outline-none w-full"
                          />
                          <p className="text-xs text-foreground-subtle truncate" title={folder.path}>
                            {folder.path}
                          </p>
                        </div>
                        <div className="flex items-center gap-2 ml-2">
                          <button
                            onClick={() => handleToggleReadOnly(folder.id)}
                            className={`text-xs px-2 py-1 rounded transition-colors ${
                              folder.readOnly
                                ? 'bg-warning/20 text-warning'
                                : 'bg-accent/20 text-accent'
                            }`}
                            title={folder.readOnly ? 'Somente leitura' : 'Leitura e escrita'}
                          >
                            {folder.readOnly ? 'RO' : 'RW'}
                          </button>
                          <button
                            onClick={() => handleToggleFolder(folder.id)}
                            className={`w-8 h-4 rounded-full relative transition-colors ${
                              folder.enabled ? 'bg-accent' : 'bg-surface-elevated'
                            }`}
                          >
                            <span
                              className={`absolute top-0.5 left-0.5 w-3 h-3 bg-foreground rounded-full transition-transform ${
                                folder.enabled ? 'translate-x-4' : 'translate-x-0'
                              }`}
                            />
                          </button>
                          <button
                            onClick={() => handleRemoveFolder(folder.id)}
                            className="text-error hover:text-error/80 transition-colors"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          </button>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {/* MCP Tab */}
          {activeTab === 'mcp' && (
            <div className="space-y-4">
              {/* Add Server Form */}
              <div className="space-y-2">
                <input
                  type="text"
                  value={newMcpName}
                  onChange={e => setNewMcpName(e.target.value)}
                  placeholder="Nome do servidor"
                  className="w-full p-2 text-sm bg-surface-elevated border border-border rounded text-foreground focus:ring-1 focus:ring-accent/50 focus:border-accent/50 outline-none"
                />
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={newMcpUrl}
                    onChange={e => setNewMcpUrl(e.target.value)}
                    placeholder="http://localhost:3000"
                    className="flex-1 p-2 text-sm bg-surface-elevated border border-border rounded text-foreground font-mono focus:ring-1 focus:ring-accent/50 focus:border-accent/50 outline-none"
                  />
                  <button
                    onClick={handleAddMcpServer}
                    className="px-4 py-2 bg-accent hover:bg-accent-hover text-surface rounded font-medium text-sm transition-colors"
                  >
                    Adicionar
                  </button>
                </div>
                {mcpError && (
                  <p className="text-xs text-error">{mcpError}</p>
                )}
              </div>

              {/* Health Check Button */}
              {mcpServers.length > 0 && (
                <button
                  onClick={handleCheckMcpHealth}
                  className="w-full py-2 px-4 bg-surface-elevated hover:bg-border text-foreground-muted rounded text-sm transition-colors flex items-center justify-center gap-2"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Verificar Conexoes
                </button>
              )}

              {/* Servers List */}
              <div className="space-y-2">
                {mcpServers.length === 0 ? (
                  <p className="text-sm text-foreground-subtle text-center py-4">
                    Nenhum servidor MCP configurado
                  </p>
                ) : (
                  mcpServers.map(server => (
                    <div
                      key={server.id}
                      className={`p-3 rounded-lg border transition-colors ${
                        server.enabled
                          ? 'bg-surface-elevated border-border'
                          : 'bg-surface border-border-subtle opacity-60'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-medium text-foreground">{server.name}</span>
                            {server.status && (
                              <span
                                className={`w-2 h-2 rounded-full ${
                                  server.status === 'online'
                                    ? 'bg-success'
                                    : server.status === 'offline'
                                    ? 'bg-error'
                                    : 'bg-foreground-subtle'
                                }`}
                                title={server.status}
                              />
                            )}
                          </div>
                          <p className="text-xs text-foreground-subtle font-mono truncate" title={server.url}>
                            {server.url}
                          </p>
                          {server.tools && server.tools.length > 0 && (
                            <p className="text-xs text-accent mt-1">
                              {server.tools.length} ferramenta(s)
                            </p>
                          )}
                        </div>
                        <div className="flex items-center gap-2 ml-2">
                          <button
                            onClick={() => handleToggleMcpServer(server.id)}
                            className={`w-8 h-4 rounded-full relative transition-colors ${
                              server.enabled ? 'bg-accent' : 'bg-surface-elevated'
                            }`}
                          >
                            <span
                              className={`absolute top-0.5 left-0.5 w-3 h-3 bg-foreground rounded-full transition-transform ${
                                server.enabled ? 'translate-x-4' : 'translate-x-0'
                              }`}
                            />
                          </button>
                          <button
                            onClick={() => handleRemoveMcpServer(server.id)}
                            className="text-error hover:text-error/80 transition-colors"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          </button>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {/* Google Drive Tab */}
          {activeTab === 'googledrive' && (
            <div className="space-y-4">
              {!driveAuth?.accessToken ? (
                <>
                  {/* Credentials Form */}
                  <div className="space-y-3">
                    <div>
                      <label className="text-xs font-semibold text-foreground-subtle uppercase tracking-wide block mb-1">
                        Client ID
                      </label>
                      <input
                        type="text"
                        value={clientId}
                        onChange={e => setClientId(e.target.value)}
                        placeholder="xxxxxxxx.apps.googleusercontent.com"
                        className="w-full p-2 text-sm bg-surface-elevated border border-border rounded text-foreground font-mono focus:ring-1 focus:ring-accent/50 focus:border-accent/50 outline-none"
                      />
                    </div>
                    <div>
                      <label className="text-xs font-semibold text-foreground-subtle uppercase tracking-wide block mb-1">
                        Client Secret
                      </label>
                      <input
                        type="password"
                        value={clientSecret}
                        onChange={e => setClientSecret(e.target.value)}
                        placeholder="GOCSPX-..."
                        className="w-full p-2 text-sm bg-surface-elevated border border-border rounded text-foreground font-mono focus:ring-1 focus:ring-accent/50 focus:border-accent/50 outline-none"
                      />
                    </div>
                    <p className="text-xs text-foreground-subtle">
                      Obtenha as credenciais em{' '}
                      <a
                        href="#"
                        onClick={e => {
                          e.preventDefault();
                          // Would open external link
                        }}
                        className="text-accent hover:underline"
                      >
                        console.cloud.google.com
                      </a>
                    </p>
                  </div>

                  {driveError && (
                    <p className="text-xs text-error p-2 bg-error/10 rounded">{driveError}</p>
                  )}

                  {/* Auth Dialog */}
                  {showAuthDialog ? (
                    <div className="p-4 bg-surface-elevated rounded-lg border border-border space-y-3">
                      <p className="text-sm text-foreground">
                        Uma janela foi aberta no navegador. Copie o codigo de autorizacao:
                      </p>
                      <input
                        type="text"
                        value={authCode}
                        onChange={e => setAuthCode(e.target.value)}
                        placeholder="Cole o codigo aqui"
                        className="w-full p-2 text-sm bg-surface border border-border rounded text-foreground font-mono focus:ring-1 focus:ring-accent/50 focus:border-accent/50 outline-none"
                      />
                      <div className="flex gap-2">
                        <button
                          onClick={() => {
                            setShowAuthDialog(false);
                            setAuthCode('');
                          }}
                          className="flex-1 py-2 px-4 bg-surface-elevated hover:bg-border text-foreground-muted rounded text-sm transition-colors"
                        >
                          Cancelar
                        </button>
                        <button
                          onClick={handleCompleteAuth}
                          disabled={driveLoading}
                          className="flex-1 py-2 px-4 bg-accent hover:bg-accent-hover text-surface rounded font-medium text-sm transition-colors disabled:opacity-50"
                        >
                          {driveLoading ? 'Conectando...' : 'Conectar'}
                        </button>
                      </div>
                    </div>
                  ) : (
                    <button
                      onClick={handleConnectDrive}
                      disabled={driveLoading || !clientId.trim()}
                      className="w-full py-3 px-4 bg-accent hover:bg-accent-hover text-surface rounded font-medium text-sm transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                    >
                      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12.01 1.485c-2.082 0-3.754.02-3.743.047.01.027 1.06 1.936 2.334 4.242l2.313 4.194h10.089l-4.13-7.32c-.282-.5-1.238-.827-2.103-.957-.903-.136-2.651-.205-4.76-.206zm-8.74 5.72c-1.03 1.825-1.878 3.34-1.884 3.366-.012.042 1.003 1.82 2.274 3.975l2.33 3.94 5.063-.007c2.784-.004 5.063-.037 5.063-.074 0-.036-.918-1.62-2.04-3.52l-2.041-3.454-5.12-8.476-.03-.05-3.615 4.3zm-2.41 8.89l5.117 8.576 5.024.013c2.763.008 5.024-.013 5.024-.046 0-.034-.916-1.594-2.035-3.467l-2.036-3.405-8.066.001-3.028 5.328zm11.695.697l-3.42 6.014c-.106.187.262.35.635.281.22-.042.625-.195.93-.352l.502-.26 3.025-5.333-1.672 2.65z" />
                      </svg>
                      Conectar Google Drive
                    </button>
                  )}
                </>
              ) : (
                <>
                  {/* Connected State */}
                  <div className="flex items-center justify-between p-3 bg-success/10 border border-success/30 rounded-lg">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-success rounded-full" />
                      <span className="text-sm text-success font-medium">Conectado</span>
                    </div>
                    <button
                      onClick={handleDisconnectDrive}
                      className="text-xs text-error hover:underline"
                    >
                      Desconectar
                    </button>
                  </div>

                  {/* Refresh Button */}
                  <button
                    onClick={handleRefreshDriveFiles}
                    disabled={driveLoading}
                    className="w-full py-2 px-4 bg-surface-elevated hover:bg-border text-foreground-muted rounded text-sm transition-colors flex items-center justify-center gap-2"
                  >
                    <svg className={`w-4 h-4 ${driveLoading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    {driveLoading ? 'Carregando...' : 'Atualizar Arquivos'}
                  </button>

                  {driveError && (
                    <p className="text-xs text-error p-2 bg-error/10 rounded">{driveError}</p>
                  )}

                  {/* Files List */}
                  <div className="space-y-1 max-h-[300px] overflow-y-auto">
                    {driveFiles.length === 0 ? (
                      <p className="text-sm text-foreground-subtle text-center py-4">
                        {driveLoading ? 'Carregando arquivos...' : 'Nenhum arquivo encontrado'}
                      </p>
                    ) : (
                      driveFiles.map(file => (
                        <div
                          key={file.id}
                          className="flex items-center gap-2 p-2 hover:bg-surface-elevated rounded transition-colors cursor-pointer"
                        >
                          <svg className="w-4 h-4 text-foreground-muted flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            {file.mimeType === 'application/vnd.google-apps.folder' ? (
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                            ) : (
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                            )}
                          </svg>
                          <span className="text-sm text-foreground truncate flex-1">{file.name}</span>
                          <span className="text-xs text-foreground-subtle">{formatFileSize(file.size)}</span>
                        </div>
                      ))
                    )}
                  </div>
                </>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-5 border-t border-border bg-surface">
          <button
            onClick={onClose}
            className="w-full py-2 bg-accent hover:bg-accent-hover text-surface rounded font-medium text-sm transition-colors"
          >
            Fechar
          </button>
        </div>
      </div>
    </div>
  );
};

export default IntegrationsPanel;
