import React, { useState, useRef, useEffect } from 'react';
import { AgentProfile } from '../types';
import { AVAILABLE_AGENTS } from '../constants';
import { ScaleIcon, SettingsIcon, TerminalIcon, ChevronDownIcon, GeoSpinner } from './Icons';

interface AgentSelectorProps {
  selectedAgentId: string;
  onSelectAgent: (agentId: string) => void;
}

const AgentSelector: React.FC<AgentSelectorProps> = ({ selectedAgentId, onSelectAgent }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const selectedAgent = AVAILABLE_AGENTS.find(a => a.id === selectedAgentId);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.3)]';
      case 'maintenance': return 'bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.3)]';
      case 'deprecated': return 'bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.3)]';
      default: return 'bg-stone-600';
    }
  };

  return (
    <div 
      className={`
        flex flex-col h-full bg-stone-900 border-r border-stone-800/80 transition-all duration-300 ease-in-out z-20
        ${isCollapsed ? 'w-16' : 'w-72'}
      `}
    >
      {/* Header */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-stone-800/80">
        {!isCollapsed && (
            <div className="flex items-center gap-3">
                <div className="w-8 h-8 flex items-center justify-center bg-stone-800/50 border border-stone-700/50 rounded-sm">
                    <ScaleIcon className="w-4 h-4 text-amber-600" />
                </div>
                <span className="font-bold text-[11px] text-stone-300 tracking-[0.25em] uppercase">ADK_SHELL</span>
            </div>
        )}
        <button 
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-1.5 rounded-sm hover:bg-stone-800 text-stone-600 hover:text-amber-600 transition-all mx-auto"
        >
          {isCollapsed ? (
             <GeoSpinner className="w-5 h-5" /> 
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4">
              <rect width="18" height="18" x="3" y="3" rx="1"></rect>
              <line x1="9" x2="9" y1="3" y2="21"></line>
            </svg>
          )}
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto py-8 px-5 space-y-10 custom-scrollbar">
        
        {/* Agent Selection */}
        <div className={`${isCollapsed ? 'hidden' : 'block'}`}>
            <label className="block text-[9px] font-bold text-stone-600 uppercase tracking-[0.2em] mb-4">
                Core_Agent
            </label>
            
            <div className="relative" ref={dropdownRef}>
                <button
                    onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                    className="w-full flex items-center justify-between bg-stone-800/30 border border-stone-800 hover:border-stone-700 text-stone-300 text-[11px] rounded-sm px-3 py-2 transition-all font-mono"
                >
                    <span className="truncate">{selectedAgent?.name || "INIT_NULL"}</span>
                    <ChevronDownIcon className={`w-3.5 h-3.5 text-stone-600 transition-transform duration-300 ${isDropdownOpen ? 'rotate-180' : ''}`} />
                </button>

                {isDropdownOpen && (
                    <div className="absolute z-50 w-full mt-1 bg-stone-900 border border-stone-800 rounded-sm shadow-2xl animate-in fade-in zoom-in-95 duration-200 overflow-hidden">
                        {AVAILABLE_AGENTS.map((agent) => (
                            <div 
                                key={agent.id}
                                onClick={() => {
                                    onSelectAgent(agent.id);
                                    setIsDropdownOpen(false);
                                }}
                                className={`
                                    px-3 py-2.5 text-[11px] cursor-pointer flex items-center justify-between transition-all font-mono
                                    ${selectedAgentId === agent.id ? 'bg-amber-900/10 text-amber-500' : 'text-stone-400 hover:bg-stone-800/50 hover:text-stone-200'}
                                `}
                            >
                                <span className="truncate">{agent.name}</span>
                                <div className={`w-1.5 h-1.5 rounded-full ${getStatusColor(agent.status)}`}></div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
            
            {selectedAgentId && (
                <div className="mt-4 p-3 bg-black/10 rounded-sm border border-stone-800/50 text-[10px] text-stone-500 leading-relaxed font-mono italic">
                     // {selectedAgent?.description}
                </div>
            )}
        </div>

        {/* Technical Modules */}
        <div className={`${isCollapsed ? 'hidden' : 'block'} space-y-8`}>
            <div>
                <div className="flex items-center gap-2 mb-4 text-stone-600">
                    <SettingsIcon className="w-3 h-3" />
                    <span className="text-[9px] font-bold uppercase tracking-[0.2em]">Module_Config</span>
                </div>
                <button className="w-full border border-stone-800/80 bg-stone-800/10 rounded-sm py-3 text-[10px] text-stone-600 font-mono hover:bg-stone-800/40 hover:text-stone-400 transition-all">
                     [LOAD_PARAMETERS]
                </button>
            </div>

            <div>
                <div className="flex items-center gap-2 mb-4 text-stone-600">
                    <TerminalIcon className="w-3 h-3" />
                    <span className="text-[9px] font-bold uppercase tracking-[0.2em]">Agent_Tools</span>
                </div>
                <button className="w-full border border-stone-800/80 bg-stone-800/10 rounded-sm py-3 text-[10px] text-stone-600 font-mono hover:bg-stone-800/40 hover:text-stone-400 transition-all">
                     [CONTEXT_SHELL]
                </button>
            </div>
        </div>
      </div>

      {/* Footer */}
      <div className={`p-5 border-t border-stone-800/80 ${isCollapsed ? 'flex justify-center' : ''}`}>
        <div className="flex items-center gap-3">
            <div className={`w-1.5 h-1.5 rounded-full ${selectedAgentId ? 'bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]' : 'bg-red-900'} animate-pulse`}></div>
            {!isCollapsed && (
                 <span className="text-[9px] uppercase tracking-[0.3em] text-stone-600 font-mono">STATUS_READY</span>
            )}
        </div>
      </div>
    </div>
  );
};

export default AgentSelector;