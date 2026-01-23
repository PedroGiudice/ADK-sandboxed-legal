import React, { useState, useRef, useEffect } from 'react';
import { AgentProfile, Message, AgentRole, Attachment, OutputStyle, MessagePart } from '../types';
import { 
  SendIcon, PaperclipIcon, XIcon, AttachmentIcon, 
  CopyIcon, CheckIcon, TrashIcon, GeoSpinner,
  TerminalIcon, WrenchIcon, CodeIcon, BookOpenIcon, PlayIcon, ChevronDownIcon
} from './Icons';

type ViewMode = 'developer' | 'client';

/**
 * Helper to map technical artifacts to Client-facing Legal Intents.
 * This ensures "Client Mode" speaks the language of the domain, not the machine.
 */
const getClientIntent = (part: MessagePart): { icon: React.ReactNode, text: string } | null => {
  // Thoughts are internal monologue - hide in Client Mode
  if (part.type === 'thought') return null; 

  // Bash Commands -> Functional Actions
  if (part.type === 'bash') {
    if (part.content.includes('ls')) return { icon: <BookOpenIcon className="w-3 h-3"/>, text: "Indexing case file directory..." };
    if (part.content.includes('grep')) return { icon: <div className="w-3 h-3 font-serif italic font-bold">Q</div>, text: "Scanning documents for key terms..." };
    if (part.content.includes('curl') || part.content.includes('wget')) return { icon: <GeoSpinner className="w-3 h-3"/>, text: "Retrieving external regulations..." };
    return { icon: <TerminalIcon className="w-3 h-3"/>, text: "Executing internal system verification..." };
  }
  
  // File Operations -> Document Handling
  if (part.type === 'file_op') {
    const file = part.metadata?.filePath?.split('/').pop() || 'document';
    const isWrite = part.content.includes('write');
    return { 
        icon: <PaperclipIcon className="w-3 h-3"/>, 
        text: isWrite ? `Drafting legal memorandum: ${file}` : `Reviewing evidence file: ${file}` 
    };
  }
  
  // Tool Calls -> Expert Consultation
  if (part.type === 'tool_call') {
    if (part.metadata?.toolName?.includes('search') || part.metadata?.toolName?.includes('lookup')) {
        return { icon: <div className="w-3 h-3 font-serif">§</div>, text: "Cross-referencing legal precedents..." };
    }
    return { icon: <WrenchIcon className="w-3 h-3"/>, text: "Consulting specialized verification module..." };
  }
  
  return null;
};

/** 
 * AgentMessageBody Component
 * Renders based on ViewMode:
 * - Developer: Raw terminals, JSON tools, stack traces.
 * - Client: Polished "Intents" and natural language text.
 */
const AgentMessageBody: React.FC<{ parts?: MessagePart[], content: string, viewMode: ViewMode }> = ({ parts, content, viewMode }) => {
  if (!parts || parts.length === 0) {
    return <div className="whitespace-pre-wrap font-sans font-light text-stone-300 leading-relaxed">{content}</div>;
  }

  return (
    <div className="space-y-3 w-full">
      {parts.map((part, idx) => {
        
        // --- CLIENT MODE RENDERING ---
        if (viewMode === 'client') {
            const intent = getClientIntent(part);
            
            // If text, render normally. If mapped intent exists, render the "Status Pill".
            if (part.type === 'text') {
                return (
                    <div key={idx} className="whitespace-pre-wrap font-serif text-stone-300 leading-7 my-2 text-sm">
                        {part.content}
                    </div>
                );
            }
            
            if (intent) {
                return (
                    <div key={idx} className="flex items-center gap-3 py-2 px-3 my-1 rounded-md bg-stone-800/20 border border-stone-800/40">
                        <div className="text-amber-600/70">{intent.icon}</div>
                        <span className="text-xs font-medium text-stone-500 uppercase tracking-wide">{intent.text}</span>
                        {/* Simulation of progress/success tick */}
                        <div className="ml-auto w-1.5 h-1.5 rounded-full bg-emerald-500/50"></div>
                    </div>
                );
            }
            return null; // Hide unmatched parts (like raw thoughts) in Client Mode
        }

        // --- DEVELOPER MODE RENDERING (Existing logic) ---
        switch (part.type) {
          case 'text':
            return (
                <div key={idx} className="whitespace-pre-wrap font-sans font-light text-stone-300 leading-relaxed my-1">
                    {part.content}
                </div>
            );
          
          case 'thought':
            return (
              <details key={idx} className="group border-l-[2px] border-stone-800 pl-3 py-1 my-2 open:bg-stone-900/30 open:rounded-r-sm transition-all">
                <summary className="text-[10px] font-bold text-stone-600 uppercase tracking-widest cursor-pointer select-none group-hover:text-stone-400 flex items-center gap-2 outline-none">
                  <ChevronDownIcon className="w-3 h-3 transition-transform duration-200 group-open:rotate-180 opacity-50" />
                  <span>Reasoning_Chain</span>
                </summary>
                <div className="mt-2 text-[11px] text-stone-500 leading-relaxed font-mono italic pl-5 border-t border-stone-800/30 pt-2 opacity-80">
                  {part.content}
                </div>
              </details>
            );

          case 'bash':
            return (
              <div key={idx} className="my-3 rounded-sm overflow-hidden border border-stone-800 bg-[#0a0a0a] shadow-md group">
                <div className="flex items-center justify-between px-3 py-1.5 bg-[#141414] border-b border-stone-800">
                  <div className="flex items-center gap-2">
                      <TerminalIcon className="w-3 h-3 text-stone-500" />
                      <span className="text-[9px] font-bold text-stone-500 uppercase tracking-widest">shell_exec</span>
                  </div>
                  {part.metadata?.exitCode !== undefined && (
                     <span className={`text-[9px] font-mono px-1.5 rounded-sm ${part.metadata.exitCode === 0 ? 'text-emerald-500/80 bg-emerald-900/10' : 'text-red-500/80 bg-red-900/10'}`}>
                       code:{part.metadata.exitCode}
                     </span>
                  )}
                </div>
                <div className="p-3 font-mono text-[11px] overflow-x-auto custom-scrollbar">
                  <div className="flex gap-2">
                    <span className="text-emerald-600/80 select-none">$</span>
                    <span className="text-stone-300">{part.content}</span>
                  </div>
                </div>
              </div>
            );

          case 'tool_call':
            return (
              <div key={idx} className="my-3 rounded-sm border border-amber-900/20 bg-[#161210] overflow-hidden relative">
                  <div className="absolute top-0 left-0 w-0.5 h-full bg-amber-900/40"></div>
                  <div className="flex items-center gap-3 px-3 py-2 bg-amber-950/5 border-b border-amber-900/10">
                    <div className="p-1 rounded-sm bg-amber-900/10 border border-amber-900/20">
                         <WrenchIcon className="w-3 h-3 text-amber-600" />
                    </div>
                    <div className="flex flex-col">
                        <span className="text-[9px] font-bold text-amber-700/70 uppercase tracking-widest leading-none">Tool_Use</span>
                        <span className="text-[10px] font-mono text-amber-600/90 leading-tight mt-0.5">{part.metadata?.toolName}</span>
                    </div>
                  </div>
                  <div className="p-3">
                     <div className="text-[10px] font-mono text-amber-500/80 whitespace-pre-wrap break-all bg-black/20 p-2 rounded-sm border border-amber-900/10">
                        {part.content}
                     </div>
                  </div>
              </div>
            );

          case 'file_op':
             const isWrite = part.content.toLowerCase().includes('write');
            return (
              <div key={idx} className={`my-2 flex items-center gap-3 p-2 rounded-sm border ${
                  isWrite 
                    ? 'bg-[#101218] border-indigo-900/30' 
                    : 'bg-[#121212] border-stone-800'
              }`}>
                <div className={`p-1.5 rounded-sm border shrink-0 ${
                    isWrite 
                        ? 'bg-indigo-900/10 border-indigo-900/20' 
                        : 'bg-stone-800/30 border-stone-800'
                }`}>
                  <BookOpenIcon className={`w-3.5 h-3.5 ${isWrite ? 'text-indigo-400' : 'text-stone-500'}`} />
                </div>
                
                <div className="flex-1 min-w-0">
                   <div className="flex items-center justify-between">
                      <span className={`text-[9px] font-bold uppercase tracking-widest ${isWrite ? 'text-indigo-500/70' : 'text-stone-600'}`}>
                          {isWrite ? 'Write_Stream' : 'Read_Stream'}
                      </span>
                   </div>
                   <div className="text-[11px] font-mono text-stone-400 truncate mt-0.5" title={part.metadata?.filePath}>
                      {part.metadata?.filePath || './unknown'}
                   </div>
                </div>

                <div className={`px-2 py-1 rounded-sm text-[9px] font-bold font-mono border uppercase ${
                     isWrite 
                     ? 'bg-indigo-500/5 border-indigo-500/10 text-indigo-500' 
                     : 'bg-stone-800/30 border-stone-800 text-stone-500'
                }`}>
                    {isWrite ? 'W+' : 'R'}
                </div>
              </div>
            );

          default:
            return <div key={idx} className="my-1">{part.content}</div>;
        }
      })}
    </div>
  );
};

interface ChatWorkspaceProps {
  activeAgent: AgentProfile;
  messages: Message[];
  onSendMessage: (content: string, attachments: Attachment[], style: OutputStyle) => void;
  isLoading?: boolean;
}

const ChatWorkspace: React.FC<ChatWorkspaceProps> = ({ activeAgent, messages, onSendMessage, isLoading = false }) => {
  const [viewMode, setViewMode] = useState<ViewMode>('developer');
  
  const [inputValue, setInputValue] = useState('');
  const [outputStyle, setOutputStyle] = useState<OutputStyle>('normal');
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, isUploading, viewMode]);

  const handleSend = () => {
    if ((!inputValue.trim() && attachments.length === 0) || isLoading || isUploading) return;
    onSendMessage(inputValue, attachments, outputStyle);
    setInputValue('');
    setAttachments([]);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setIsUploading(true);
      setUploadProgress(10);
      
      const newAttachments: Attachment[] = [];
      const files = Array.from(e.target.files) as File[];
      
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        setUploadProgress(Math.floor((i / files.length) * 100) || 20);
        
        const base64 = await new Promise<string>((resolve) => {
          const reader = new FileReader();
          reader.onloadend = () => resolve(reader.result as string);
          reader.readAsDataURL(file);
        });

        newAttachments.push({
          id: Date.now().toString() + i,
          name: file.name,
          type: file.type,
          size: file.size,
          data: base64
        });
      }
      
      setUploadProgress(100);
      setTimeout(() => {
        setAttachments(prev => [...prev, ...newAttachments]);
        if (fileInputRef.current) fileInputRef.current.value = '';
        setIsUploading(false);
        setUploadProgress(0);
      }, 300);
    }
  };

  const removeAttachment = (id: string) => {
    setAttachments(prev => prev.filter(a => a.id !== id));
  };

  const removeAllAttachments = () => {
    setAttachments([]);
  };

  const handleCopy = async (content: string, id: string) => {
    await navigator.clipboard.writeText(content);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="flex-1 flex flex-col bg-stone-900 relative">
      
      {/* Top Bar with Mode Toggle */}
      <div className="h-16 flex items-center justify-between px-8 border-b border-stone-800 bg-stone-900/95 backdrop-blur-sm z-10">
         <div className="flex flex-col">
            <h1 className="text-stone-200 font-medium tracking-wide text-sm flex items-center gap-2">
                {activeAgent.name}
            </h1>
            <div className="flex items-center gap-2 mt-0.5">
                <span className={`w-1 h-1 rounded-full ${isLoading ? 'bg-amber-500 animate-pulse' : 'bg-emerald-500'}`}></span>
                <p className="text-[9px] text-stone-600 font-mono uppercase tracking-tighter">Session ID: 0x82A1</p>
            </div>
         </div>

         {/* Center: Mode Toggle */}
         <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 flex items-center bg-stone-950/50 p-1 rounded-full border border-stone-800">
             <button
                onClick={() => setViewMode('developer')}
                className={`px-3 py-1 text-[9px] uppercase font-bold tracking-wider rounded-full transition-all ${
                    viewMode === 'developer' 
                    ? 'bg-stone-800 text-stone-200 shadow-sm' 
                    : 'text-stone-600 hover:text-stone-400'
                }`}
             >
                Dev_Mode
             </button>
             <button
                onClick={() => setViewMode('client')}
                className={`px-3 py-1 text-[9px] uppercase font-bold tracking-wider rounded-full transition-all ${
                    viewMode === 'client' 
                    ? 'bg-amber-900/20 text-amber-500 shadow-sm' 
                    : 'text-stone-600 hover:text-stone-400'
                }`}
             >
                Client_View
             </button>
         </div>

         <div className="flex items-center gap-4">
            <GeoSpinner className="w-5 h-5" />
            {isLoading && (
                <div className="flex items-center gap-2 text-amber-600/80 animate-pulse">
                    <span className="text-[10px] font-mono tracking-widest">THINKING_STREAM</span>
                </div>
            )}
         </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-8 space-y-8 scroll-smooth bg-stone-900 custom-scrollbar">
        {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-stone-600 select-none">
                {isLoading ? (
                    <GeoSpinner className="w-10 h-10 mb-4" />
                ) : (
                    <div className="flex flex-col items-center gap-2 opacity-20">
                        <span className="text-4xl font-mono text-stone-500">://</span>
                        <p className="text-[10px] font-mono tracking-[0.2em] text-stone-500 uppercase">System_Standby</p>
                    </div>
                )}
            </div>
        ) : (
            messages.map((msg) => {
              const isUser = msg.role === AgentRole.USER;
              return (
                <div
                    key={msg.id}
                    className={`flex flex-col w-full max-w-5xl mx-auto group ${isUser ? 'items-end' : 'items-start'}`}
                >
                    <div className={`relative max-w-[85%] ${isUser ? 'pl-16' : 'pr-16'}`}>
                        
                        {/* Header Label */}
                        <div className={`flex items-center gap-2 mb-2 ${isUser ? 'justify-end' : 'justify-start'}`}>
                            <span className={`text-[9px] font-bold uppercase tracking-[0.15em] ${
                                isUser ? 'text-amber-700/80' : 'text-stone-600'
                            }`}>
                                {isUser ? 'CLIENT_INPUT' : (viewMode === 'client' ? 'LEGAL_COUNSEL' : 'ADK_OUTPUT')}
                            </span>
                            <span className="text-[9px] text-stone-700 font-mono">
                                {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                            </span>
                        </div>

                        {/* Content Bubble */}
                        <div className={`
                            relative p-5 text-[13px] leading-relaxed transition-all duration-300
                            ${isUser 
                                ? 'bg-[#1e1c1b] border border-stone-800/60 rounded-sm text-stone-300' 
                                : 'bg-[#181d24] border border-blue-900/10 rounded-sm text-stone-300'
                            }
                        `}>
                            {isUser ? (
                              <div className="whitespace-pre-wrap font-serif text-stone-300">{msg.content}</div>
                            ) : (
                              <AgentMessageBody parts={msg.parts} content={msg.content} viewMode={viewMode} />
                            )}

                            {/* Attachments within message */}
                            {msg.attachments && msg.attachments.length > 0 && (
                                <div className="mt-4 pt-3 border-t border-stone-800/40 flex flex-wrap gap-2">
                                    {msg.attachments.map(att => (
                                    <div key={att.id} className="flex items-center gap-2 p-1.5 bg-black/20 border border-stone-800/30 rounded-sm text-[10px] text-stone-500 font-mono">
                                        <AttachmentIcon className="w-2.5 h-2.5" />
                                        <span className="max-w-[120px] truncate">{att.name}</span>
                                    </div>
                                    ))}
                                </div>
                            )}

                            {/* Hover Actions (Copy) */}
                            <button 
                                onClick={() => handleCopy(msg.content, msg.id)}
                                className={`
                                    absolute top-2 right-2 p-1 rounded-sm opacity-0 group-hover:opacity-100 transition-all
                                    text-stone-600 hover:text-amber-500 hover:bg-stone-800/80
                                `}
                                title="Copy Content"
                            >
                                {copiedId === msg.id ? <CheckIcon className="w-3 h-3" /> : <CopyIcon className="w-3 h-3" />}
                            </button>
                        </div>
                    </div>
                </div>
            )})
        )}
        
        {/* Thinking Indicator */}
        {isLoading && (
             <div className="flex flex-col w-full max-w-5xl mx-auto items-start animate-in fade-in slide-in-from-bottom-2 duration-500">
                 <div className="pr-16">
                     <div className="flex items-center gap-2 mb-2">
                         <span className="text-[9px] font-bold uppercase tracking-[0.2em] text-amber-600/50">PROCESSING</span>
                     </div>
                     <div className="bg-[#181d24] border border-blue-900/10 rounded-sm p-4 w-12 flex items-center justify-center">
                         <GeoSpinner className="w-4 h-4" />
                     </div>
                 </div>
             </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-stone-900 p-6 border-t border-stone-800/60">
        <div className="max-w-4xl mx-auto space-y-4">
            
            {/* Attachment Bar */}
            {(attachments.length > 0 || isUploading) && (
              <div className="flex flex-col gap-2 p-3 bg-stone-950/20 border border-stone-800/60 rounded-sm animate-in slide-in-from-bottom-1">
                <div className="flex items-center justify-between">
                    <span className="text-[9px] uppercase font-bold text-stone-600 tracking-wider">Payload Cache</span>
                    {attachments.length > 0 && (
                        <button 
                            onClick={removeAllAttachments}
                            className="text-[9px] uppercase font-bold text-red-900 hover:text-red-500 flex items-center gap-1 transition-colors"
                        >
                            <TrashIcon className="w-2.5 h-2.5" />
                            Purge_All
                        </button>
                    )}
                </div>
                
                <div className="flex flex-wrap gap-2">
                    {attachments.map(att => (
                        <div key={att.id} className="flex items-center gap-2 px-2 py-1 bg-stone-800 border border-stone-700/40 rounded-sm text-[10px] text-stone-400 group">
                            <span className="max-w-[150px] truncate font-mono">{att.name}</span>
                            <button onClick={() => removeAttachment(att.id)} className="text-stone-600 hover:text-red-600 transition-colors">
                                <XIcon className="w-2.5 h-2.5" />
                            </button>
                        </div>
                    ))}
                    {isUploading && (
                        <div className="flex flex-col w-full gap-1.5 mt-1">
                            <div className="flex justify-between text-[9px] font-mono text-amber-700">
                                <span>UPLOADING_CONTEXT</span>
                                <span>{uploadProgress}%</span>
                            </div>
                            <div className="w-full h-0.5 bg-stone-800 rounded-full overflow-hidden">
                                <div 
                                    className="h-full bg-amber-600 transition-all duration-300" 
                                    style={{ width: `${uploadProgress}%` }}
                                />
                            </div>
                        </div>
                    )}
                </div>
              </div>
            )}

            {/* Input Component */}
            <div className={`
                relative bg-stone-800/20 border transition-all duration-300 rounded-sm
                ${isLoading ? 'border-stone-800/20' : 'border-stone-800/80 focus-within:border-stone-600 focus-within:bg-stone-800/30'}
            `}>
                <textarea
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={handleKeyDown}
                    disabled={isLoading}
                    placeholder={isLoading ? "System is analyzing..." : "Enter legal inquiry..."}
                    className="w-full p-4 bg-transparent text-stone-300 placeholder-stone-700 focus:outline-none resize-none min-h-[50px] max-h-[180px] text-[13px] font-mono leading-relaxed disabled:cursor-not-allowed"
                    rows={1}
                />
                <div className="absolute right-2 bottom-2">
                    <button
                        onClick={handleSend}
                        disabled={(!inputValue.trim() && attachments.length === 0) || isLoading}
                        className={`
                            p-2 rounded-sm transition-all duration-200
                            ${(!inputValue.trim() && attachments.length === 0) || isLoading 
                                ? 'text-stone-800' 
                                : 'text-stone-900 bg-amber-600 hover:bg-amber-500'}
                        `}
                    >
                        <SendIcon className="w-3.5 h-3.5" />
                    </button>
                </div>
            </div>

            {/* Toolbar */}
            <div className="flex flex-wrap items-center justify-between gap-4 pt-1">
              
              <div className="flex items-center gap-2">
                <input type="file" ref={fileInputRef} className="hidden" onChange={handleFileSelect} multiple disabled={isLoading} />
                <button 
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isLoading}
                  className="flex items-center gap-2 px-2.5 py-1 text-[10px] uppercase font-bold tracking-widest text-stone-500 hover:text-stone-300 bg-transparent border border-stone-800 hover:border-stone-700 rounded-sm transition-all disabled:opacity-20"
                >
                  <PaperclipIcon className="w-3 h-3" />
                  <span>Attach_Context</span>
                </button>
              </div>

              {/* Style Selection */}
              <div className="flex items-center bg-black/20 rounded-sm border border-stone-800 p-0.5">
                 {(['concise', 'normal', 'verbose'] as OutputStyle[]).map((style) => (
                    <button
                      key={style}
                      onClick={() => setOutputStyle(style)}
                      disabled={isLoading}
                      className={`
                        px-3 py-1 text-[9px] uppercase font-bold tracking-[0.2em] rounded-sm transition-all
                        ${outputStyle === style 
                          ? 'bg-stone-800 text-amber-500 border border-stone-700/50' 
                          : 'text-stone-600 hover:text-stone-400'
                        }
                      `}
                    >
                      {style}
                    </button>
                 ))}
              </div>

            </div>
        </div>
      </div>
    </div>
  );
};

export default ChatWorkspace;