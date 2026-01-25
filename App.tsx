import React, { useState, useCallback, useEffect, createContext, useContext } from 'react';
import AgentSelector from './components/AgentSelector';
import ChatWorkspace from './components/ChatWorkspace';
import ConfigPanel from './components/ConfigPanel';
import { AVAILABLE_AGENTS, DEFAULT_CONFIG, loadTheme, saveTheme, loadFont, clearMessages as clearStoredMessages } from './constants';
import { Message, AgentRole, RuntimeConfig, Attachment, OutputStyle, MessagePart, Theme } from './types';
import { sendPromptToAgent } from './services/adkService';
import { runJurisprudenceAgent } from './services/agentBridge';
import { check } from '@tauri-apps/plugin-updater';
import { relaunch } from '@tauri-apps/plugin-process';

const LOCAL_STORAGE_KEY = 'adk_chat_history_v1';

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
  const [activeAgentId, setActiveAgentId] = useState<string>(AVAILABLE_AGENTS[0].id);
  const [isLoading, setIsLoading] = useState(false);
  const [theme, setThemeState] = useState<Theme>(loadTheme);
  const [updateStatus, setUpdateStatus] = useState<'idle' | 'checking' | 'available' | 'downloading' | 'ready'>('idle');
  const [updateProgress, setUpdateProgress] = useState(0);

  const [messages, setMessages] = useState<Message[]>(() => {
    try {
      const saved = localStorage.getItem(LOCAL_STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        return parsed.map((m: any) => ({
            ...m,
            timestamp: new Date(m.timestamp)
        }));
      }
    } catch (e) {
      console.error("Failed to load history", e);
    }
    return [];
  });

  const [isConfigOpen, setIsConfigOpen] = useState(false);
  const [runtimeConfig, setRuntimeConfig] = useState<RuntimeConfig>(DEFAULT_CONFIG);

  const activeAgent = AVAILABLE_AGENTS.find(a => a.id === activeAgentId) || AVAILABLE_AGENTS[0];

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
              const progress = (event.data.chunkLength / event.data.contentLength) * 100;
              setUpdateProgress(progress);
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

  // Clear chat handler
  const handleClearChat = useCallback(() => {
    setMessages([]);
    clearStoredMessages();
  }, []);

  useEffect(() => {
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(messages));
  }, [messages]);

  const handleAgentSelect = (agentId: string) => {
    setActiveAgentId(agentId);
  };

  /** Simulates a complex agent response with multiple dynamic parts */
  const handleSendMessage = useCallback(async (content: string, attachments: Attachment[], style: OutputStyle) => {
    const newUserMessage: Message = {
      id: Date.now().toString(),
      role: AgentRole.USER,
      content,
      timestamp: new Date(),
      attachments: attachments
    };
    
    setMessages(prev => [...prev, newUserMessage]);
    setIsLoading(true);
    
    const requestConfig = {
      ...runtimeConfig,
      outputStyle: style
    };

    try {
        let agentResponse: Message;

        if (activeAgent.id === 'agent-caselaw') {
            const result = await runJurisprudenceAgent(content, (data) => {
                // Optional: We could parse "thought" lines here if the python agent emitted them
            });

            if (!result.success) {
                throw new Error(result.error);
            }

            // Construct parts based on the output
            // For now, we treat the whole output as text, but in a real app we'd parse the markdown structure
            agentResponse = {
                id: (Date.now() + 1).toString(),
                role: AgentRole.ASSISTANT,
                content: result.output || "No output returned.",
                // Add a file operation part if an output path was detected
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
    }

  }, [activeAgent, runtimeConfig]);

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      <div className="flex h-screen w-screen overflow-hidden bg-surface text-foreground transition-colors duration-300">

        <AgentSelector
          selectedAgentId={activeAgentId}
          onSelectAgent={handleAgentSelect}
        />

        <div className="flex-1 flex flex-col relative">
          <ChatWorkspace
            activeAgent={activeAgent}
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
            onOpenConfig={() => setIsConfigOpen(true)}
          />

          <ConfigPanel
            isOpen={isConfigOpen}
            onClose={() => setIsConfigOpen(false)}
            config={runtimeConfig}
            onUpdateConfig={setRuntimeConfig}
            onClearChat={handleClearChat}
          />
        </div>
      </div>
    </ThemeContext.Provider>
  );
};

export default App;