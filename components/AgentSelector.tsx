import React, { useState } from 'react';
import { AgentProfile } from '../types';
import { AVAILABLE_AGENTS } from '../constants';
import { ScaleIcon, SettingsIcon, TerminalIcon } from './Icons';

interface AgentSelectorProps {
  selectedAgentId: string;
  onSelectAgent: (agentId: string) => void;
}

const AgentSelector: React.FC<AgentSelectorProps> = ({ selectedAgentId, onSelectAgent }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <div 
      className={`
        flex flex-col h-full bg-stone-900 border-r border-stone-800 transition-all duration-300 ease-in-out
        ${isCollapsed ? 'w-16' : 'w-80'}
      `}
    >
      {/* Header / Toggle */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-stone-800">
        {!isCollapsed && (
            <div className="flex items-center gap-3 opacity-100 transition-opacity duration-300">
                <ScaleIcon className="w-5 h-5 text-amber-700" />
                <span className="font-bold text-stone-200 tracking-tight">ADK SHELL</span>
            </div>
        )}
        <button 
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-1.5 rounded hover:bg-stone-800 text-stone-500 hover:text-stone-300 transition-colors mx-auto"
        >
          {isCollapsed ? (
             <ScaleIcon className="w-5 h-5" /> 
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5">
              <rect width="18" height="18" x="3" y="3" rx="2" ry="2"></rect>
              <line x1="9" x2="9" y1="3" y2="21"></line>
            </svg>
          )}
        </button>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto py-6 px-4 space-y-8">
        
        {/* Agent Selection Section */}
        <div className={`${isCollapsed ? 'hidden' : 'block'}`}>
            <label className="block text-xs font-semibold text-stone-500 uppercase tracking-wider mb-3">
                Select Agent
            </label>
            <div className="relative">
                <select
                    value={selectedAgentId}
                    onChange={(e) => onSelectAgent(e.target.value)}
                    className="w-full bg-stone-800 border border-stone-700 text-stone-300 text-sm rounded-md p-2.5 focus:ring-1 focus:ring-amber-900/50 focus:border-amber-900/50 outline-none appearance-none hover:border-stone-600 transition-colors"
                >
                    <option value="" disabled>Choose an Agent</option>
                    {AVAILABLE_AGENTS.map((agent) => (
                        <option key={agent.id} value={agent.id}>
                            {agent.name}
                        </option>
                    ))}
                </select>
                {/* Custom chevron for dropdown */}
                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-stone-500">
                    <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/></svg>
                </div>
            </div>
            
            {/* Selected Agent Info */}
            {selectedAgentId && (
                <div className="mt-3 p-3 bg-stone-800/30 rounded border border-stone-800 text-xs text-stone-400">
                     {AVAILABLE_AGENTS.find(a => a.id === selectedAgentId)?.description}
                </div>
            )}
        </div>

        {/* Configuration Settings Placeholder */}
        <div className={`${isCollapsed ? 'hidden' : 'block'}`}>
            <div className="flex items-center gap-2 mb-3 text-stone-500">
                <SettingsIcon className="w-4 h-4" />
                <span className="text-xs font-semibold uppercase tracking-wider">Configuration Settings</span>
            </div>
            <div className="border border-dashed border-stone-800 bg-stone-800/30 rounded-md p-4 flex flex-col items-center justify-center text-center hover:bg-stone-800/50 transition-colors cursor-pointer">
                 <p className="text-xs text-stone-500">Runtime parameters</p>
            </div>
        </div>

        {/* Agent Specific Options Placeholder */}
        <div className={`${isCollapsed ? 'hidden' : 'block'}`}>
            <div className="flex items-center gap-2 mb-3 text-stone-500">
                <TerminalIcon className="w-4 h-4" />
                <span className="text-xs font-semibold uppercase tracking-wider">Agent Specific Options</span>
            </div>
            <div className="border border-dashed border-stone-800 bg-stone-800/30 rounded-md p-4 flex flex-col items-center justify-center text-center hover:bg-stone-800/50 transition-colors cursor-pointer">
                 <p className="text-xs text-stone-500">Contextual tools</p>
            </div>
        </div>
      </div>

      {/* Footer */}
      <div className={`p-4 border-t border-stone-800 ${isCollapsed ? 'items-center justify-center flex' : ''}`}>
        <div className={`w-2 h-2 rounded-full ${selectedAgentId ? 'bg-amber-600' : 'bg-red-900'}`}></div>
        {!isCollapsed && (
             <span className="ml-3 text-xs text-stone-500 font-mono">system_ready</span>
        )}
      </div>
    </div>
  );
};

export default AgentSelector;