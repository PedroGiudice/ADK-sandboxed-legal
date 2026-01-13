import React, { useState, useRef, useEffect } from 'react';
import { AgentProfile, Message, AgentRole } from '../types';
import { SendIcon } from './Icons';

interface ChatWorkspaceProps {
  activeAgent: AgentProfile;
  messages: Message[];
  onSendMessage: (content: string) => void;
}

const ChatWorkspace: React.FC<ChatWorkspaceProps> = ({ activeAgent, messages, onSendMessage }) => {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = () => {
    if (!inputValue.trim()) return;
    onSendMessage(inputValue);
    setInputValue('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex-1 flex flex-col bg-stone-900 relative">
      
      {/* Top Bar */}
      <div className="h-16 flex items-center justify-between px-8 border-b border-stone-800 bg-stone-900/90 backdrop-blur-sm">
         <div>
            <h1 className="text-stone-200 font-medium tracking-wide">{activeAgent.name}</h1>
            <p className="text-[10px] text-stone-500 font-mono uppercase mt-0.5">Session ID: 0x82A1</p>
         </div>
      </div>

      {/* Messages Area - Minimalist Log View */}
      <div className="flex-1 overflow-y-auto p-8 space-y-8 scroll-smooth bg-stone-900">
        {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-stone-600 select-none">
                <span className="text-4xl opacity-20 mb-4 font-mono text-stone-500">://</span>
                <p className="text-sm font-mono opacity-50 text-stone-500">Awaiting input stream...</p>
            </div>
        ) : (
            messages.map((msg) => (
            <div
                key={msg.id}
                className="flex flex-col w-full max-w-4xl mx-auto"
            >
                {/* Header */}
                <div className="flex items-baseline gap-3 mb-2">
                    <span className={`text-xs font-bold uppercase tracking-wider ${
                        msg.role === AgentRole.USER ? 'text-amber-600' : 'text-stone-400'
                    }`}>
                        {msg.role === AgentRole.USER ? 'USER' : 'AGENT'}
                    </span>
                    <span className="text-[10px] text-stone-600 font-mono">
                        {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                    </span>
                </div>
                
                {/* Content - No Bubble, Raw Text */}
                <div className="pl-0 text-sm leading-7 text-stone-300 whitespace-pre-wrap font-light">
                    {msg.content}
                </div>
                
                {/* Separator */}
                <div className="w-full border-b border-stone-800/40 mt-6"></div>
            </div>
            ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area - Functional Footer */}
      <div className="bg-stone-900 p-8 border-t border-stone-800">
        <div className="max-w-4xl mx-auto">
            <div className="relative bg-stone-800 rounded-lg border border-stone-700 focus-within:border-stone-500 transition-colors shadow-sm">
                <textarea
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Type your request here..."
                    className="w-full p-4 bg-transparent text-stone-200 placeholder-stone-600 focus:outline-none resize-none min-h-[50px] max-h-[200px] text-sm font-mono leading-relaxed"
                    rows={1}
                />
                <button
                    onClick={handleSend}
                    disabled={!inputValue.trim()}
                    className="absolute right-2 bottom-2 p-2 text-stone-500 hover:text-amber-500 disabled:opacity-0 transition-all"
                >
                    <SendIcon className="w-4 h-4" />
                </button>
            </div>
        </div>
      </div>
    </div>
  );
};

export default ChatWorkspace;