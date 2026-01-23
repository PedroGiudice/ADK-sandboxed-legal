import React, { useState, useCallback, useEffect } from 'react';
import AgentSelector from './components/AgentSelector';
import ChatWorkspace from './components/ChatWorkspace';
import ConfigPanel from './components/ConfigPanel';
import { AVAILABLE_AGENTS, DEFAULT_CONFIG } from './constants';
import { Message, AgentRole, RuntimeConfig, Attachment, OutputStyle, MessagePart } from './types';
import { sendPromptToAgent } from './services/adkService';

const LOCAL_STORAGE_KEY = 'adk_chat_history_v1';

const App: React.FC = () => {
  const [activeAgentId, setActiveAgentId] = useState<string>(AVAILABLE_AGENTS[0].id);
  const [isLoading, setIsLoading] = useState(false);
  
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
        // Here we'd call the real service. For demonstration of the dynamic UI, 
        // we simulate a structured multi-part response if grounding or complex query is detected.
        
        await new Promise(resolve => setTimeout(resolve, 2000));

        const agentParts: MessagePart[] = [
          { type: 'thought', content: 'The user is requesting a legal interpretation involving specific case files. I need to index the local repository and check the validity of the contract hash.' },
          { type: 'bash', content: 'ls -R ./case_files | grep "contract_v2"', metadata: { exitCode: 0 } },
          { type: 'file_op', content: 'read', metadata: { filePath: './case_files/contract_v2_signed.pdf' } },
          { type: 'tool_call', content: '{"action": "lookup_precedent", "case_id": "STJ-2024-X"}', metadata: { toolName: 'mcp-legal-search' } },
          { type: 'text', content: `ANALYSIS_COMPLETE:\nBased on my findings in the case files and the precedent lookup, the clause 4.2 of the analyzed document remains enforceable under current statutory interpretation. See detailed breakdown above for the technical verification steps taken.` }
        ];

        const agentResponse: Message = {
            id: (Date.now() + 1).toString(),
            role: AgentRole.ASSISTANT,
            content: "Execution summary complete.",
            parts: agentParts,
            timestamp: new Date()
        };
        setMessages(prev => [...prev, agentResponse]);

    } catch (error) {
        console.error("Agent Execution Failed", error);
        const errorMsg: Message = {
            id: (Date.now() + 1).toString(),
            role: AgentRole.ASSISTANT,
            content: "CRITICAL_SESSION_ERROR: Model communication failed. Please check runtime parameters.",
            timestamp: new Date()
        };
        setMessages(prev => [...prev, errorMsg]);
    } finally {
        setIsLoading(false);
    }

  }, [activeAgent, runtimeConfig]);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-stone-900 text-stone-300">
      
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
        />
        
        <ConfigPanel 
          isOpen={isConfigOpen}
          onClose={() => setIsConfigOpen(false)}
          config={runtimeConfig}
          onUpdateConfig={setRuntimeConfig}
        />
      </div>
    </div>
  );
};

export default App;