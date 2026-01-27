import React, { useState, useCallback, useEffect, createContext, useContext } from 'react';
import Sidebar from './components/Sidebar';
import ChatWorkspace from './components/ChatWorkspace';
import ConfigPanel from './components/ConfigPanel';
import IntegrationsPanel from './components/IntegrationsPanel';
import WorkspaceSetupModal from './components/WorkspaceSetupModal';
import NewCaseModal, { NewCaseData } from './components/NewCaseModal';
import ResizeHandle, { useResizable } from './components/ResizeHandle';
import { AVAILABLE_AGENTS, DEFAULT_CONFIG, loadTheme, saveTheme, loadFont, loadIntegrationsConfig, loadMessagesForContext, saveMessagesForContext, clearMessagesForContext } from './constants';
import { Message, AgentRole, RuntimeConfig, Attachment, OutputStyle, Theme, IntegrationsConfig, LegalCase } from './types';
import { sendPromptToAgent } from './services/adkService';
import { runJurisprudenceAgent, startAndRunCaseSession, PipelineProgress } from './services/agentBridge';
import {
  getWorkspaceRoot,
  isWorkspaceConfigured,
  selectWorkspaceRoot,
  loadRegistry,
  createCase,
  listCases,
  listClients,
  toUICase,
  CaseRegistryEntry
} from './services/caseRegistryService';
import { saveAttachmentToCase, SavedDocument } from './services/filesystemService';
import { check } from '@tauri-apps/plugin-updater';
import { relaunch } from '@tauri-apps/plugin-process';

// Removido: const LOCAL_STORAGE_KEY = 'adk_chat_history_v1';
// Agora usamos loadMessagesForContext/saveMessagesForContext por caso+agente

// Theme Context
interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

export const ThemeContext = createContext<ThemeContextType>({
  theme: 'dark',
  setTheme: () => {},
});

export const useTheme = () => useContext(ThemeContext);

const App: React.FC = () => {
  // Hierarquia de contexto: Caso -> Agente
  const [activeCaseId, setActiveCaseId] = useState<string | null>(null);
  const [activeAgentId, setActiveAgentId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [theme, setThemeState] = useState<Theme>(loadTheme);
  const [updateStatus, setUpdateStatus] = useState<'idle' | 'checking' | 'available' | 'downloading' | 'ready'>('idle');
  const [updateProgress, setUpdateProgress] = useState(0);

  // Workspace e Casos
  const [workspaceRoot, setWorkspaceRoot] = useState<string | null>(getWorkspaceRoot());
  const [cases, setCases] = useState<LegalCase[]>([]);
  const [clients, setClients] = useState<string[]>([]);
  const [showWorkspaceSetup, setShowWorkspaceSetup] = useState(false);
  const [showNewCaseModal, setShowNewCaseModal] = useState(false);

  // Progresso do pipeline
  const [pipelineProgress, setPipelineProgress] = useState<PipelineProgress | null>(null);

  // Mensagens agora sao gerenciadas por contexto (caso + agente)
  const [messages, setMessages] = useState<Message[]>([]);

  const [isConfigOpen, setIsConfigOpen] = useState(false);
  const [isIntegrationsOpen, setIsIntegrationsOpen] = useState(false);
  const [runtimeConfig, setRuntimeConfig] = useState<RuntimeConfig>(DEFAULT_CONFIG);
  const [integrationsConfig, setIntegrationsConfig] = useState<IntegrationsConfig>(loadIntegrationsConfig);

  const activeAgent = activeAgentId
    ? AVAILABLE_AGENTS.find(a => a.id === activeAgentId) || null
    : null;

  // Handler para selecao de caso (reseta agente ao trocar de caso)
  const handleCaseSelect = useCallback((caseId: string | null) => {
    setActiveCaseId(caseId);
    // Opcional: resetar agente ao trocar de caso
    // setActiveAgentId(null);
  }, []);

  // Resizable sidebar
  const { size: sidebarWidth, handleResize: handleSidebarResize } = useResizable(
    280, // initial
    200, // min
    500, // max
    'adk_sidebar_width'
  );

  // Theme handler
  const setTheme = useCallback((newTheme: Theme) => {
    setThemeState(newTheme);
    saveTheme(newTheme);
  }, []);

  // Apply theme class to document root
  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove('theme-dark', 'theme-light', 'theme-high-contrast', 'theme-ocean');
    root.classList.add(`theme-${theme}`);
  }, [theme]);

  // Apply font on initial load
  useEffect(() => {
    const savedFont = loadFont();
    document.documentElement.style.setProperty('--font-primary', savedFont);
  }, []);

  // Check for updates on startup
  useEffect(() => {
    const checkForUpdates = async () => {
      try {
        setUpdateStatus('checking');
        const update = await check();
        if (update) {
          setUpdateStatus('available');
          console.log(`Update available: ${update.version}`);

          // Auto-download
          setUpdateStatus('downloading');
          await update.downloadAndInstall((event) => {
            if (event.event === 'Progress') {
              const data = event.data as { chunkLength: number; contentLength?: number };
              if (data.contentLength && data.contentLength > 0) {
                const progress = (data.chunkLength / data.contentLength) * 100;
                setUpdateProgress(progress);
              }
            }
          });
          setUpdateStatus('ready');

          // Prompt user to restart
          if (confirm(`Nova versao ${update.version} instalada! Reiniciar agora?`)) {
            await relaunch();
          }
        } else {
          setUpdateStatus('idle');
        }
      } catch (e) {
        console.log('Update check failed (normal in dev):', e);
        setUpdateStatus('idle');
      }
    };

    // Check after 3 seconds to not block startup
    const timer = setTimeout(checkForUpdates, 3000);
    return () => clearTimeout(timer);
  }, []);

  // Verificar workspace na inicializacao
  useEffect(() => {
    const checkWorkspace = async () => {
      const configured = await isWorkspaceConfigured();
      if (!configured && !workspaceRoot) {
        setShowWorkspaceSetup(true);
      } else if (workspaceRoot) {
        // Carregar casos
        await refreshCases();
      }
    };
    checkWorkspace();
  }, [workspaceRoot]);

  // Carregar casos do registry
  const refreshCases = useCallback(async () => {
    try {
      const caseEntries = await listCases();
      setCases(caseEntries.map(toUICase));

      const clientList = await listClients();
      setClients(clientList);
    } catch (e) {
      console.error('Erro ao carregar casos:', e);
    }
  }, []);

  // Handler para configurar workspace
  const handleWorkspaceComplete = useCallback(async (path: string) => {
    setWorkspaceRoot(path);
    setShowWorkspaceSetup(false);
    await refreshCases();
  }, [refreshCases]);

  // Handler para criar novo caso
  const handleCreateCase = useCallback(async (data: NewCaseData): Promise<boolean> => {
    try {
      const newCase = await createCase(data.name, {
        number: data.number,
        client: data.client,
        description: data.description,
        tags: data.tags
      });

      if (newCase) {
        await refreshCases();
        setActiveCaseId(newCase.id);
        return true;
      }
      return false;
    } catch (e) {
      console.error('Erro ao criar caso:', e);
      return false;
    }
  }, [refreshCases]);

  // Carregar mensagens ao trocar de caso ou agente
  useEffect(() => {
    const loaded = loadMessagesForContext(activeCaseId, activeAgentId);
    setMessages(loaded);
  }, [activeCaseId, activeAgentId]);

  // Salvar mensagens quando mudam (com debounce implicito pelo estado)
  useEffect(() => {
    // So salvar se houver caso e agente selecionados e mensagens para salvar
    if (activeCaseId && activeAgentId && messages.length > 0) {
      saveMessagesForContext(activeCaseId, activeAgentId, messages);
    }
  }, [messages, activeCaseId, activeAgentId]);

  // Clear chat handler
  const handleClearChat = useCallback(() => {
    setMessages([]);
    clearMessagesForContext(activeCaseId, activeAgentId);
  }, [activeCaseId, activeAgentId]);

  const handleAgentSelect = useCallback((agentId: string) => {
    setActiveAgentId(agentId);
  }, []);

  // Encontrar caso ativo
  const activeCase = cases.find(c => c.id === activeCaseId);

  /** Envia mensagem para o agente, usando sandboxing quando aplicavel */
  const handleSendMessage = useCallback(async (content: string, attachments: Attachment[], style: OutputStyle) => {
    // Verificar se ha caso e agente selecionados
    if (!activeCaseId || !activeAgent) {
      const errorMsg: Message = {
        id: Date.now().toString(),
        role: AgentRole.ASSISTANT,
        content: 'Selecione um Caso e um Agente antes de enviar mensagens.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMsg]);
      return;
    }

    // Obter caso ativo para contexto
    const currentCase = cases.find(c => c.id === activeCaseId);

    const newUserMessage: Message = {
      id: Date.now().toString(),
      role: AgentRole.USER,
      content,
      timestamp: new Date(),
      attachments: attachments
    };

    setMessages(prev => [...prev, newUserMessage]);
    setIsLoading(true);
    setPipelineProgress(null);

    const requestConfig = {
      ...runtimeConfig,
      outputStyle: style
    };

    try {
        let agentResponse: Message;

        // Usar pipeline sandboxed para agente legal-pipeline
        if (activeAgent?.id === 'agent-legal-pipeline' && currentCase?.contextPath) {
            // Salvar arquivos anexos no diretorio do caso
            const savedDocs: SavedDocument[] = [];
            for (const att of attachments) {
              const saved = await saveAttachmentToCase(
                currentCase.contextPath,
                att.name,
                att.data,
                att.type
              );
              if (saved) {
                savedDocs.push(saved);
              } else {
                console.warn(`Falha ao salvar anexo: ${att.name}`);
              }
            }

            // Construir consulta estruturada
            const consultation = {
              consulta: {
                texto: content,
                tipo_solicitado: 'parecer',
                urgencia: 'media'
              },
              contexto: {
                area_direito: currentCase.tags?.[0] || 'geral',
                caso_id: currentCase.id,
                caso_nome: currentCase.name
              },
              fatos: [],
              normas_identificadas: [],
              jurisprudencia_identificada: [],
              documentos_anexos: savedDocs, // Agora passa path em vez de base64
              restricoes: {}
            };

            const result = await startAndRunCaseSession(
              currentCase.contextPath,
              currentCase.id,
              consultation,
              {
                onProgress: (progress) => {
                  setPipelineProgress(progress);
                },
                onOutput: (line) => {
                  console.log('[PIPELINE]:', line);
                }
              }
            );

            if (!result.success) {
              throw new Error(result.error);
            }

            const pipelineResult = result.data?.pipeline_result as Record<string, unknown> | undefined;

            agentResponse = {
              id: (Date.now() + 1).toString(),
              role: AgentRole.ASSISTANT,
              content: pipelineResult?.output_path
                ? `Pipeline concluido! Resultado salvo em: ${pipelineResult.output_path}`
                : 'Pipeline concluido com sucesso.',
              parts: [
                { type: 'text', content: `Fases completadas: ${(pipelineResult?.phases_completed as string[] || []).join(', ')}` }
              ],
              timestamp: new Date()
            };

        } else if (activeAgent?.id === 'agent-caselaw') {
            const result = await runJurisprudenceAgent(content, (data) => {
                // Optional: We could parse "thought" lines here if the python agent emitted them
            });

            if (!result.success) {
                throw new Error(result.error);
            }

            agentResponse = {
                id: (Date.now() + 1).toString(),
                role: AgentRole.ASSISTANT,
                content: result.output || "No output returned.",
                parts: result.outputPath ? [
                    { type: 'text', content: result.output || "" },
                    { type: 'file_op', content: `read ${result.outputPath}`, metadata: { filePath: result.outputPath } }
                ] : undefined,
                timestamp: new Date()
            };

        } else {
            const responseText = await sendPromptToAgent(content, activeAgent, requestConfig);
            agentResponse = {
                id: (Date.now() + 1).toString(),
                role: AgentRole.ASSISTANT,
                content: responseText,
                timestamp: new Date()
            };
        }

        setMessages(prev => [...prev, agentResponse]);

    } catch (error) {
        console.error("Agent Execution Failed", error);
        const errorMsg: Message = {
            id: (Date.now() + 1).toString(),
            role: AgentRole.ASSISTANT,
            content: `CRITICAL_SESSION_ERROR: ${String(error)}`,
            timestamp: new Date()
        };
        setMessages(prev => [...prev, errorMsg]);
    } finally {
        setIsLoading(false);
        setPipelineProgress(null);
    }

  }, [activeAgent, activeCaseId, cases, runtimeConfig]);

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      <div className="flex h-screen w-screen overflow-hidden bg-surface text-foreground transition-colors duration-300">

        {/* Resizable Sidebar */}
        <div style={{ width: sidebarWidth }} className="flex-shrink-0">
          <Sidebar
            selectedCaseId={activeCaseId}
            selectedAgentId={activeAgentId}
            onSelectCase={handleCaseSelect}
            onSelectAgent={handleAgentSelect}
            cases={cases}
            onNewCase={() => setShowNewCaseModal(true)}
            pipelineProgress={pipelineProgress}
          />
        </div>

        {/* Sidebar Resize Handle */}
        <ResizeHandle
          direction="horizontal"
          onResize={handleSidebarResize}
          className="z-10"
        />

        <div className="flex-1 flex flex-col relative min-w-0">
          <ChatWorkspace
            activeAgent={activeAgent}
            activeCaseId={activeCaseId}
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
            onOpenConfig={() => setIsConfigOpen(true)}
            onOpenIntegrations={() => setIsIntegrationsOpen(true)}
          />

          <ConfigPanel
            isOpen={isConfigOpen}
            onClose={() => setIsConfigOpen(false)}
            config={runtimeConfig}
            onUpdateConfig={setRuntimeConfig}
            onClearChat={handleClearChat}
          />

          <IntegrationsPanel
            isOpen={isIntegrationsOpen}
            onClose={() => setIsIntegrationsOpen(false)}
          />
        </div>

        {/* Modals */}
        <WorkspaceSetupModal
          isOpen={showWorkspaceSetup}
          onComplete={handleWorkspaceComplete}
          onSelectFolder={selectWorkspaceRoot}
        />

        <NewCaseModal
          isOpen={showNewCaseModal}
          onClose={() => setShowNewCaseModal(false)}
          onCreate={handleCreateCase}
          existingClients={clients}
        />
      </div>
    </ThemeContext.Provider>
  );
};

export default App;