import React, { useState, useCallback } from 'react';
import AgentSelector from './components/AgentSelector';
import ChatWorkspace from './components/ChatWorkspace';
import ConfigPanel from './components/ConfigPanel';
import { AVAILABLE_AGENTS, DEFAULT_CONFIG } from './constants';
import { Message, AgentRole, RuntimeConfig } from './types';
import { sendPromptToAgent } from './services/adkService';
import { SettingsIcon } from './components/Icons';

const App: React.FC = () => {
  const [activeAgentId, setActiveAgentId] = useState<string>(AVAILABLE_AGENTS[0].id);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isConfigOpen, setIsConfigOpen] = useState(false);
  const [runtimeConfig, setRuntimeConfig] = useState<RuntimeConfig>(DEFAULT_CONFIG);

  const activeAgent = AVAILABLE_AGENTS.find(a => a.id === activeAgentId) || AVAILABLE_AGENTS[0];

  const handleAgentSelect = (agentId: string) => {
    setActiveAgentId(agentId);
  };

  const handleSendMessage = useCallback(async (content: string) => {
    const newUserMessage: Message = {
      id: Date.now().toString(),
      role: AgentRole.USER,
      content,
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, newUserMessage]);
    await sendPromptToAgent(content, activeAgent, runtimeConfig);
  }, [activeAgent, runtimeConfig]);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-stone-900 text-stone-300">
      
      {/* Sidebar */}
      <AgentSelector 
        selectedAgentId={activeAgentId} 
        onSelectAgent={handleAgentSelect} 
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col relative">
        <ChatWorkspace 
          activeAgent={activeAgent}
          messages={messages}
          onSendMessage={handleSendMessage}
        />
        
        {/* Config Modal */}
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