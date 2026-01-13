import React from 'react';
import { RuntimeConfig } from '../types';

interface ConfigPanelProps {
  isOpen: boolean;
  onClose: () => void;
  config: RuntimeConfig;
  onUpdateConfig: (newConfig: RuntimeConfig) => void;
}

const ConfigPanel: React.FC<ConfigPanelProps> = ({ isOpen, onClose, config, onUpdateConfig }) => {
  if (!isOpen) return null;

  return (
    <div className="absolute inset-0 z-50 flex justify-end bg-black/40 backdrop-blur-sm">
      <div className="w-96 bg-stone-900 h-full shadow-2xl border-l border-stone-800 flex flex-col animate-in slide-in-from-right duration-300">
        
        {/* Header */}
        <div className="p-5 border-b border-stone-800 flex justify-between items-center bg-stone-900">
          <div>
            <h3 className="font-bold text-stone-200 serif-font">Configuration</h3>
            <p className="text-xs text-stone-500">Agent Runtime Parameters</p>
          </div>
          <button 
            onClick={onClose}
            className="text-stone-500 hover:text-stone-200 transition-colors text-2xl leading-none"
          >
            &times;
          </button>
        </div>

        {/* Form Fields */}
        <div className="flex-1 overflow-y-auto p-5 space-y-6">
            
            {/* API Endpoint */}
            <div className="space-y-2">
                <label className="text-xs font-semibold text-stone-500 uppercase tracking-wide">ADK Endpoint URL</label>
                <input 
                    type="text" 
                    value={config.apiUrl}
                    readOnly
                    className="w-full p-2 text-sm bg-stone-800 border border-stone-700 rounded text-stone-500 font-mono cursor-not-allowed"
                />
                <p className="text-[10px] text-stone-600">Endpoint is immutable in Sandbox Mode.</p>
            </div>

            <hr className="border-stone-800" />

            {/* Inference Parameters */}
            <div className="space-y-4">
                <label className="text-xs font-semibold text-stone-500 uppercase tracking-wide">Inference Parameters</label>
                
                <div>
                    <div className="flex justify-between mb-1">
                        <span className="text-sm text-stone-300">Temperature</span>
                        <span className="text-xs font-mono text-stone-500">{config.temperature}</span>
                    </div>
                    <input 
                        type="range" 
                        min="0" 
                        max="1" 
                        step="0.1"
                        value={config.temperature}
                        onChange={(e) => onUpdateConfig({...config, temperature: parseFloat(e.target.value)})}
                        className="w-full h-1 bg-stone-800 rounded-lg appearance-none cursor-pointer accent-amber-600"
                    />
                </div>

                <div>
                    <div className="flex justify-between mb-1">
                        <span className="text-sm text-stone-300">Top K</span>
                        <span className="text-xs font-mono text-stone-500">{config.topK}</span>
                    </div>
                    <input 
                        type="range" 
                        min="1" 
                        max="100" 
                        step="1"
                        value={config.topK}
                        onChange={(e) => onUpdateConfig({...config, topK: parseInt(e.target.value)})}
                        className="w-full h-1 bg-stone-800 rounded-lg appearance-none cursor-pointer accent-amber-600"
                    />
                </div>

                <div>
                    <div className="flex justify-between mb-1">
                        <span className="text-sm text-stone-300">Context Window</span>
                        <span className="text-xs font-mono text-stone-500">{config.contextWindow / 1000}k</span>
                    </div>
                    <select 
                        value={config.contextWindow}
                        onChange={(e) => onUpdateConfig({...config, contextWindow: parseInt(e.target.value)})}
                        className="w-full p-2 text-sm bg-stone-800 border border-stone-700 text-stone-200 rounded focus:ring-1 focus:ring-amber-900/50 focus:border-amber-900/50 outline-none"
                    >
                        <option value={32000}>32k Tokens</option>
                        <option value={128000}>128k Tokens</option>
                        <option value={1000000}>1M Tokens</option>
                    </select>
                </div>
            </div>

            <hr className="border-stone-800" />

             {/* Logic Controls */}
             <div className="space-y-4">
                <label className="text-xs font-semibold text-stone-500 uppercase tracking-wide">Logic & Safety</label>
                
                <div className="flex items-center justify-between">
                    <span className="text-sm text-stone-300">Enable Grounding</span>
                    <button 
                        onClick={() => onUpdateConfig({...config, enableGrounding: !config.enableGrounding})}
                        className={`w-10 h-5 rounded-full relative transition-colors ${config.enableGrounding ? 'bg-amber-700' : 'bg-stone-700'}`}
                    >
                        <span className={`absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full transition-transform ${config.enableGrounding ? 'translate-x-5' : 'translate-x-0'}`} />
                    </button>
                </div>

                <div>
                     <span className="text-sm text-stone-300 block mb-2">Safety Filter Level</span>
                     <div className="flex bg-stone-800 p-1 rounded-lg border border-stone-700">
                        {['low', 'medium', 'high'].map((level) => (
                            <button
                                key={level}
                                onClick={() => onUpdateConfig({...config, securityFilterLevel: level as any})}
                                className={`flex-1 py-1 text-xs font-medium rounded capitalize transition-colors ${
                                    config.securityFilterLevel === level 
                                    ? 'bg-stone-700 text-amber-500 shadow-sm' 
                                    : 'text-stone-500 hover:text-stone-300'
                                }`}
                            >
                                {level}
                            </button>
                        ))}
                     </div>
                </div>
            </div>

        </div>

        {/* Footer actions */}
        <div className="p-5 border-t border-stone-800 bg-stone-900">
            <button 
                onClick={onClose}
                className="w-full py-2 bg-amber-800 hover:bg-amber-700 text-white rounded font-medium text-sm transition-colors shadow-lg shadow-amber-900/20"
            >
                Apply Configuration
            </button>
        </div>
      </div>
    </div>
  );
};

export default ConfigPanel;