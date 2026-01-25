import React, { useState } from 'react';
import { RuntimeConfig, Theme } from '../types';
import { saveSecureKey, THEME_CONFIG, AVAILABLE_THEMES, COMMON_FONTS, loadFont, saveFont } from '../constants';
import { useTheme } from '../App';

interface ConfigPanelProps {
  isOpen: boolean;
  onClose: () => void;
  config: RuntimeConfig;
  onUpdateConfig: (newConfig: RuntimeConfig) => void;
  onClearChat?: () => void;
}

const ConfigPanel: React.FC<ConfigPanelProps> = ({ isOpen, onClose, config, onUpdateConfig, onClearChat }) => {
  const [showApiKey, setShowApiKey] = useState(false);
  const [apiKeyInput, setApiKeyInput] = useState(config.geminiApiKey || '');
  const [currentFont, setCurrentFont] = useState(loadFont);
  const [customFont, setCustomFont] = useState('');
  const { theme, setTheme } = useTheme();

  const handleFontChange = (font: string) => {
    setCurrentFont(font);
    saveFont(font);
  };

  const handleCustomFont = () => {
    if (customFont.trim()) {
      handleFontChange(customFont.trim());
    }
  };

  const handleApiKeyChange = (value: string) => {
    setApiKeyInput(value);
  };

  const handleApiKeySave = () => {
    saveSecureKey(apiKeyInput);
    onUpdateConfig({ ...config, geminiApiKey: apiKeyInput });
  };

  const maskApiKey = (key: string): string => {
    if (!key || key.length < 8) return key ? '****' : '';
    return key.substring(0, 4) + '...' + key.substring(key.length - 4);
  };

  if (!isOpen) return null;

  return (
    <div className="absolute inset-0 z-50 flex justify-end bg-black/40 backdrop-blur-sm">
      <div className="w-96 bg-surface h-full shadow-2xl border-l border-border flex flex-col animate-in slide-in-from-right duration-300">

        {/* Header */}
        <div className="p-5 border-b border-border flex justify-between items-center bg-surface">
          <div>
            <h3 className="font-bold text-foreground serif-font">Configuration</h3>
            <p className="text-xs text-foreground-subtle">Agent Runtime Parameters</p>
          </div>
          <button
            onClick={onClose}
            className="text-foreground-subtle hover:text-foreground transition-colors text-2xl leading-none"
          >
            &times;
          </button>
        </div>

        {/* Form Fields */}
        <div className="flex-1 overflow-y-auto p-5 space-y-6">

            {/* Theme Selector */}
            <div className="space-y-3">
                <label className="text-xs font-semibold text-accent uppercase tracking-wide flex items-center gap-2">
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
                  </svg>
                  Theme
                </label>
                <div className={`grid gap-2 ${AVAILABLE_THEMES.length > 3 ? 'grid-cols-2' : 'grid-cols-3'}`}>
                    {AVAILABLE_THEMES.map((themeKey) => (
                        <button
                            key={themeKey}
                            onClick={() => setTheme(themeKey)}
                            className={`
                                p-3 rounded border text-xs font-medium transition-all
                                ${theme === themeKey
                                    ? 'bg-accent-muted border-accent text-accent'
                                    : 'bg-surface-elevated border-border-subtle text-foreground-muted hover:border-border hover:text-foreground'
                                }
                            `}
                        >
                            {THEME_CONFIG[themeKey].name}
                        </button>
                    ))}
                </div>
                <p className="text-[10px] text-foreground-subtle">
                    {THEME_CONFIG[theme].description}
                </p>
            </div>

            <hr className="border-border" />

            {/* Font Selector */}
            <div className="space-y-3">
                <label className="text-xs font-semibold text-accent uppercase tracking-wide flex items-center gap-2">
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 0h8v12H6V4zm2 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" clipRule="evenodd" />
                  </svg>
                  Font
                </label>
                <select
                    value={COMMON_FONTS.find(f => f.value === currentFont)?.value || ''}
                    onChange={(e) => handleFontChange(e.target.value)}
                    className="w-full p-2 text-sm bg-surface-elevated border border-border text-foreground rounded focus:ring-1 focus:ring-accent/50 focus:border-accent/50 outline-none"
                >
                    {COMMON_FONTS.map((font) => (
                        <option key={font.name} value={font.value}>{font.name}</option>
                    ))}
                </select>
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={customFont}
                        onChange={(e) => setCustomFont(e.target.value)}
                        placeholder="Custom font family..."
                        className="flex-1 p-2 text-sm bg-surface-elevated border border-border rounded text-foreground font-mono focus:ring-1 focus:ring-accent/50 focus:border-accent/50 outline-none"
                    />
                    <button
                        onClick={handleCustomFont}
                        className="px-3 py-2 bg-accent hover:bg-accent-hover text-surface rounded text-xs font-medium transition-colors"
                    >
                        Apply
                    </button>
                </div>
                <p className="text-[10px] text-foreground-subtle">
                    Current: <span className="font-mono">{currentFont.substring(0, 40)}...</span>
                </p>
            </div>

            <hr className="border-border" />

            {/* API Key - SECURE INPUT */}
            <div className="space-y-2">
                <label className="text-xs font-semibold text-accent uppercase tracking-wide flex items-center gap-2">
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
                  </svg>
                  Gemini API Key
                </label>
                <div className="relative">
                    <input
                        type={showApiKey ? "text" : "password"}
                        value={apiKeyInput}
                        onChange={(e) => handleApiKeyChange(e.target.value)}
                        placeholder="AIza..."
                        className="w-full p-2 pr-20 text-sm bg-surface-elevated border border-border rounded text-foreground font-mono focus:ring-1 focus:ring-accent/50 focus:border-accent/50 outline-none"
                    />
                    <button
                        type="button"
                        onClick={() => setShowApiKey(!showApiKey)}
                        className="absolute right-2 top-1/2 -translate-y-1/2 text-xs text-foreground-subtle hover:text-foreground px-2 py-1"
                    >
                        {showApiKey ? 'Hide' : 'Show'}
                    </button>
                </div>
                <div className="flex items-center justify-between">
                    <p className="text-[10px] text-foreground-subtle">
                        {config.geminiApiKey ? `Saved: ${maskApiKey(config.geminiApiKey)}` : 'Not configured'}
                    </p>
                    <button
                        onClick={handleApiKeySave}
                        disabled={apiKeyInput === config.geminiApiKey}
                        className="text-xs px-2 py-1 bg-accent hover:bg-accent-hover disabled:bg-surface-elevated disabled:text-foreground-subtle text-surface rounded transition-colors"
                    >
                        Save Key
                    </button>
                </div>
                <p className="text-[10px] text-warning">Key is stored locally and never sent to external servers except Google API.</p>
            </div>

            <hr className="border-border" />

            {/* API Endpoint */}
            <div className="space-y-2">
                <label className="text-xs font-semibold text-foreground-subtle uppercase tracking-wide">ADK Endpoint URL</label>
                <input
                    type="text"
                    value={config.apiUrl}
                    readOnly
                    className="w-full p-2 text-sm bg-surface-elevated border border-border rounded text-foreground-subtle font-mono cursor-not-allowed"
                />
                <p className="text-[10px] text-foreground-subtle">Endpoint is immutable in Sandbox Mode.</p>
            </div>

            <hr className="border-border" />

            {/* Inference Parameters */}
            <div className="space-y-4">
                <label className="text-xs font-semibold text-foreground-subtle uppercase tracking-wide">Inference Parameters</label>

                <div>
                    <div className="flex justify-between mb-1">
                        <span className="text-sm text-foreground">Temperature</span>
                        <span className="text-xs font-mono text-foreground-subtle">{config.temperature}</span>
                    </div>
                    <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.1"
                        value={config.temperature}
                        onChange={(e) => onUpdateConfig({...config, temperature: parseFloat(e.target.value)})}
                        className="w-full h-1 bg-surface-elevated rounded-lg appearance-none cursor-pointer accent-accent"
                    />
                </div>

                <div>
                    <div className="flex justify-between mb-1">
                        <span className="text-sm text-foreground">Top K</span>
                        <span className="text-xs font-mono text-foreground-subtle">{config.topK}</span>
                    </div>
                    <input
                        type="range"
                        min="1"
                        max="100"
                        step="1"
                        value={config.topK}
                        onChange={(e) => onUpdateConfig({...config, topK: parseInt(e.target.value)})}
                        className="w-full h-1 bg-surface-elevated rounded-lg appearance-none cursor-pointer accent-accent"
                    />
                </div>

                <div>
                    <div className="flex justify-between mb-1">
                        <span className="text-sm text-foreground">Context Window</span>
                        <span className="text-xs font-mono text-foreground-subtle">{config.contextWindow / 1000}k</span>
                    </div>
                    <select
                        value={config.contextWindow}
                        onChange={(e) => onUpdateConfig({...config, contextWindow: parseInt(e.target.value)})}
                        className="w-full p-2 text-sm bg-surface-elevated border border-border text-foreground rounded focus:ring-1 focus:ring-accent/50 focus:border-accent/50 outline-none"
                    >
                        <option value={32000}>32k Tokens</option>
                        <option value={128000}>128k Tokens</option>
                        <option value={1000000}>1M Tokens</option>
                    </select>
                </div>
            </div>

            <hr className="border-border" />

             {/* Logic Controls */}
             <div className="space-y-4">
                <label className="text-xs font-semibold text-foreground-subtle uppercase tracking-wide">Logic & Safety</label>

                <div className="flex items-center justify-between">
                    <span className="text-sm text-foreground">Enable Grounding</span>
                    <button
                        onClick={() => onUpdateConfig({...config, enableGrounding: !config.enableGrounding})}
                        className={`w-10 h-5 rounded-full relative transition-colors ${config.enableGrounding ? 'bg-accent' : 'bg-surface-elevated'}`}
                    >
                        <span className={`absolute top-0.5 left-0.5 w-4 h-4 bg-foreground rounded-full transition-transform ${config.enableGrounding ? 'translate-x-5' : 'translate-x-0'}`} />
                    </button>
                </div>

                <div>
                     <span className="text-sm text-foreground block mb-2">Safety Filter Level</span>
                     <div className="flex bg-surface-elevated p-1 rounded-lg border border-border">
                        {['low', 'medium', 'high'].map((level) => (
                            <button
                                key={level}
                                onClick={() => onUpdateConfig({...config, securityFilterLevel: level as any})}
                                className={`flex-1 py-1 text-xs font-medium rounded capitalize transition-colors ${
                                    config.securityFilterLevel === level
                                    ? 'bg-surface border border-border text-accent shadow-sm'
                                    : 'text-foreground-subtle hover:text-foreground'
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
        <div className="p-5 border-t border-border bg-surface space-y-3">
            {onClearChat && (
                <button
                    onClick={() => {
                        if (confirm('Limpar todo o historico de mensagens?')) {
                            onClearChat();
                        }
                    }}
                    className="w-full py-2 bg-error/20 hover:bg-error/30 text-error border border-error/30 rounded font-medium text-sm transition-colors"
                >
                    Limpar Historico de Chat
                </button>
            )}
            <button
                onClick={onClose}
                className="w-full py-2 bg-accent hover:bg-accent-hover text-surface rounded font-medium text-sm transition-colors shadow-lg"
            >
                Apply Configuration
            </button>
        </div>
      </div>
    </div>
  );
};

export default ConfigPanel;