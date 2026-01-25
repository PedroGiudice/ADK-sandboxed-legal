import React, { useState, useRef, useEffect } from 'react';
import { AgentProfile, LegalCase, CaseStatus } from '../types';
import { AVAILABLE_AGENTS } from '../constants';
import { ScaleIcon, ChevronDownIcon, GeoSpinner } from './Icons';

// === Mock de Casos (sera substituido por dados reais) ===
const MOCK_CASES: LegalCase[] = [
  {
    id: 'case-001',
    name: 'Silva vs. Banco Nacional',
    number: '0001234-56.2024.8.26.0100',
    client: 'Joao Silva',
    description: 'Acao de indenizacao por danos morais',
    status: 'active',
    createdAt: new Date('2024-01-15'),
    updatedAt: new Date('2024-03-10'),
    tags: ['consumidor', 'bancario'],
  },
  {
    id: 'case-002',
    name: 'Heranca Oliveira',
    number: '0005678-90.2023.8.26.0002',
    client: 'Familia Oliveira',
    description: 'Inventario e partilha de bens',
    status: 'active',
    createdAt: new Date('2023-11-20'),
    updatedAt: new Date('2024-02-28'),
    tags: ['sucessoes', 'familia'],
  },
  {
    id: 'case-003',
    name: 'Contrato TechCorp',
    client: 'TechCorp Ltda',
    description: 'Revisao contratual e compliance',
    status: 'pending',
    createdAt: new Date('2024-03-01'),
    updatedAt: new Date('2024-03-01'),
    tags: ['empresarial', 'contratos'],
  },
];

interface SidebarProps {
  selectedCaseId: string | null;
  selectedAgentId: string | null;
  onSelectCase: (caseId: string | null) => void;
  onSelectAgent: (agentId: string) => void;
  cases?: LegalCase[];
}

const Sidebar: React.FC<SidebarProps> = ({
  selectedCaseId,
  selectedAgentId,
  onSelectCase,
  onSelectAgent,
  cases = MOCK_CASES,
}) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isCaseDropdownOpen, setIsCaseDropdownOpen] = useState(false);
  const [isAgentDropdownOpen, setIsAgentDropdownOpen] = useState(false);
  const caseDropdownRef = useRef<HTMLDivElement>(null);
  const agentDropdownRef = useRef<HTMLDivElement>(null);

  const selectedCase = cases.find(c => c.id === selectedCaseId);
  const selectedAgent = AVAILABLE_AGENTS.find(a => a.id === selectedAgentId);

  // Fecha dropdowns ao clicar fora
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (caseDropdownRef.current && !caseDropdownRef.current.contains(event.target as Node)) {
        setIsCaseDropdownOpen(false);
      }
      if (agentDropdownRef.current && !agentDropdownRef.current.contains(event.target as Node)) {
        setIsAgentDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const getCaseStatusColor = (status: CaseStatus) => {
    switch (status) {
      case 'active': return 'bg-accent';
      case 'pending': return 'bg-warning';
      case 'archived': return 'bg-foreground-subtle';
      default: return 'bg-foreground-subtle';
    }
  };

  const getAgentStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-success';
      case 'maintenance': return 'bg-warning';
      case 'deprecated': return 'bg-error';
      default: return 'bg-foreground-subtle';
    }
  };

  return (
    <div
      className={`
        flex flex-col h-full w-full bg-surface border-r border-border transition-all duration-300 ease-in-out z-20
        ${isCollapsed ? '!w-16' : ''}
      `}
    >
      {/* === HEADER === */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-border">
        {!isCollapsed && (
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 flex items-center justify-center bg-surface-elevated border border-border rounded-sm">
              <ScaleIcon className="w-4 h-4 text-accent" />
            </div>
            <span className="font-bold text-[11px] text-foreground tracking-[0.25em] uppercase">LEGAL_ADK</span>
          </div>
        )}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-1.5 rounded-sm hover:bg-surface-elevated text-foreground-subtle hover:text-accent transition-all mx-auto"
          title={isCollapsed ? 'Expandir' : 'Recolher'}
        >
          {isCollapsed ? (
            <GeoSpinner className="w-5 h-5" />
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4">
              <rect width="18" height="18" x="3" y="3" rx="1" />
              <line x1="9" x2="9" y1="3" y2="21" />
            </svg>
          )}
        </button>
      </div>

      {/* === CONTENT === */}
      <div className="flex-1 overflow-y-auto py-6 px-4 space-y-6 custom-scrollbar">

        {/* NIVEL 1: SELECAO DE CASO */}
        <div className={`${isCollapsed ? 'hidden' : 'block'}`}>
          <label className="flex items-center gap-2 text-[9px] font-bold text-foreground-subtle uppercase tracking-[0.2em] mb-3">
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
            </svg>
            Caso Ativo
          </label>

          <div className="relative" ref={caseDropdownRef}>
            <button
              onClick={() => setIsCaseDropdownOpen(!isCaseDropdownOpen)}
              className={`
                w-full flex items-center justify-between border rounded-sm px-3 py-2.5 transition-all
                ${selectedCase
                  ? 'bg-accent/10 border-accent/50 text-foreground'
                  : 'bg-surface-elevated/50 border-border hover:border-accent/30 text-foreground-muted'
                }
              `}
            >
              <div className="flex items-center gap-2 min-w-0">
                {selectedCase && (
                  <div className={`w-2 h-2 rounded-full flex-shrink-0 ${getCaseStatusColor(selectedCase.status)}`} />
                )}
                <span className="text-[11px] font-medium truncate">
                  {selectedCase?.name || 'Selecione um caso...'}
                </span>
              </div>
              <ChevronDownIcon className={`w-3.5 h-3.5 text-foreground-subtle transition-transform duration-200 flex-shrink-0 ${isCaseDropdownOpen ? 'rotate-180' : ''}`} />
            </button>

            {isCaseDropdownOpen && (
              <div className="absolute z-50 w-full mt-1 bg-surface border border-border rounded-sm shadow-2xl overflow-hidden">
                {/* Opcao para limpar selecao */}
                {selectedCase && (
                  <div
                    onClick={() => {
                      onSelectCase(null);
                      setIsCaseDropdownOpen(false);
                    }}
                    className="px-3 py-2 text-[10px] text-foreground-subtle hover:bg-surface-elevated cursor-pointer border-b border-border flex items-center gap-2"
                  >
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                    Limpar selecao
                  </div>
                )}

                {/* Lista de casos */}
                {cases.map((legalCase) => (
                  <div
                    key={legalCase.id}
                    onClick={() => {
                      onSelectCase(legalCase.id);
                      setIsCaseDropdownOpen(false);
                    }}
                    className={`
                      px-3 py-2.5 cursor-pointer transition-all
                      ${selectedCaseId === legalCase.id
                        ? 'bg-accent/15 text-accent'
                        : 'text-foreground-muted hover:bg-surface-elevated hover:text-foreground'
                      }
                    `}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] font-medium truncate">{legalCase.name}</span>
                      <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${getCaseStatusColor(legalCase.status)}`} />
                    </div>
                    {legalCase.number && (
                      <p className="text-[9px] text-foreground-subtle mt-0.5 font-mono">{legalCase.number}</p>
                    )}
                  </div>
                ))}

                {/* Adicionar novo caso */}
                <div className="border-t border-border px-3 py-2 hover:bg-surface-elevated cursor-pointer flex items-center gap-2 text-accent">
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  <span className="text-[10px] font-medium">Novo Caso</span>
                </div>
              </div>
            )}
          </div>

          {/* Info do caso selecionado */}
          {selectedCase && (
            <div className="mt-3 p-3 bg-surface-alt/50 rounded-sm border border-border-subtle">
              {selectedCase.client && (
                <p className="text-[10px] text-foreground-muted">
                  <span className="text-foreground-subtle">Cliente:</span> {selectedCase.client}
                </p>
              )}
              {selectedCase.tags && selectedCase.tags.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {selectedCase.tags.map(tag => (
                    <span key={tag} className="px-1.5 py-0.5 bg-surface-elevated text-[8px] text-foreground-subtle rounded uppercase">
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* NIVEL 2: SELECAO DE AGENTE (so visivel apos selecionar caso) */}
        <div className={`${isCollapsed || !selectedCase ? 'hidden' : 'block'} transition-all duration-300`}>
          <label className="flex items-center gap-2 text-[9px] font-bold text-foreground-subtle uppercase tracking-[0.2em] mb-3">
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            Agente
          </label>

          <div className="relative" ref={agentDropdownRef}>
            <button
              onClick={() => setIsAgentDropdownOpen(!isAgentDropdownOpen)}
              className={`
                w-full flex items-center justify-between border rounded-sm px-3 py-2.5 transition-all
                ${selectedAgent
                  ? 'bg-success/10 border-success/50 text-foreground'
                  : 'bg-surface-elevated/50 border-border hover:border-success/30 text-foreground-muted'
                }
              `}
            >
              <div className="flex items-center gap-2 min-w-0">
                {selectedAgent && (
                  <div className={`w-2 h-2 rounded-full flex-shrink-0 ${getAgentStatusColor(selectedAgent.status)}`} />
                )}
                <span className="text-[11px] font-medium truncate">
                  {selectedAgent?.name || 'Selecione um agente...'}
                </span>
              </div>
              <ChevronDownIcon className={`w-3.5 h-3.5 text-foreground-subtle transition-transform duration-200 flex-shrink-0 ${isAgentDropdownOpen ? 'rotate-180' : ''}`} />
            </button>

            {isAgentDropdownOpen && (
              <div className="absolute z-50 w-full mt-1 bg-surface border border-border rounded-sm shadow-2xl overflow-hidden max-h-64 overflow-y-auto">
                {AVAILABLE_AGENTS.map((agent) => (
                  <div
                    key={agent.id}
                    onClick={() => {
                      onSelectAgent(agent.id);
                      setIsAgentDropdownOpen(false);
                    }}
                    className={`
                      px-3 py-2.5 cursor-pointer transition-all
                      ${selectedAgentId === agent.id
                        ? 'bg-success/15 text-success'
                        : 'text-foreground-muted hover:bg-surface-elevated hover:text-foreground'
                      }
                    `}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] font-medium">{agent.name}</span>
                      <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${getAgentStatusColor(agent.status)}`} />
                    </div>
                    <p className="text-[9px] text-foreground-subtle mt-0.5">{agent.specialization}</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Descricao do agente */}
          {selectedAgent && (
            <div className="mt-3 p-3 bg-surface-alt/50 rounded-sm border border-border-subtle">
              <p className="text-[10px] text-foreground-subtle leading-relaxed">
                {selectedAgent.description}
              </p>
            </div>
          )}
        </div>

        {/* Mensagem quando nenhum caso selecionado */}
        {!isCollapsed && !selectedCase && (
          <div className="py-8 text-center">
            <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-surface-elevated flex items-center justify-center">
              <svg className="w-6 h-6 text-foreground-subtle" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
              </svg>
            </div>
            <p className="text-[11px] text-foreground-subtle">
              Selecione um caso para<br />habilitar os agentes
            </p>
          </div>
        )}
      </div>

      {/* === FOOTER: STATUS === */}
      <div className={`p-4 border-t border-border ${isCollapsed ? 'flex justify-center' : ''}`}>
        {!isCollapsed ? (
          <div className="space-y-2">
            {/* Status do Caso */}
            <div className="flex items-center gap-2">
              <div className={`w-1.5 h-1.5 rounded-full ${selectedCase ? 'bg-accent' : 'bg-foreground-subtle'}`} />
              <span className="text-[9px] text-foreground-subtle font-mono truncate">
                {selectedCase ? selectedCase.name : 'SEM_CASO'}
              </span>
            </div>
            {/* Status do Agente */}
            <div className="flex items-center gap-2">
              <div className={`w-1.5 h-1.5 rounded-full ${selectedAgent ? 'bg-success animate-pulse' : 'bg-foreground-subtle'}`} />
              <span className="text-[9px] text-foreground-subtle font-mono truncate">
                {selectedAgent ? selectedAgent.name : 'SEM_AGENTE'}
              </span>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-1">
            <div className={`w-2 h-2 rounded-full ${selectedCase ? 'bg-accent' : 'bg-foreground-subtle'}`} />
            <div className={`w-2 h-2 rounded-full ${selectedAgent ? 'bg-success animate-pulse' : 'bg-foreground-subtle'}`} />
          </div>
        )}
      </div>
    </div>
  );
};

export default Sidebar;
