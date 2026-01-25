import React, { useState } from 'react';
import { ScaleIcon } from './Icons';

interface WorkspaceSetupModalProps {
  isOpen: boolean;
  onComplete: (workspacePath: string) => void;
  onSelectFolder: () => Promise<string | null>;
}

const WorkspaceSetupModal: React.FC<WorkspaceSetupModalProps> = ({
  isOpen,
  onComplete,
  onSelectFolder
}) => {
  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const [isSelecting, setIsSelecting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSelectFolder = async () => {
    setIsSelecting(true);
    setError(null);

    try {
      const path = await onSelectFolder();
      if (path) {
        setSelectedPath(path);
      }
    } catch (e) {
      setError('Erro ao selecionar pasta. Tente novamente.');
      console.error('Folder selection error:', e);
    } finally {
      setIsSelecting(false);
    }
  };

  const handleConfirm = () => {
    if (selectedPath) {
      onComplete(selectedPath);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-surface border border-border rounded-lg shadow-2xl w-full max-w-lg mx-4 overflow-hidden">
        {/* Header */}
        <div className="bg-surface-elevated px-6 py-5 border-b border-border">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 flex items-center justify-center bg-accent/10 border border-accent/30 rounded-lg">
              <ScaleIcon className="w-6 h-6 text-accent" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-foreground">Configurar Workspace</h2>
              <p className="text-sm text-foreground-subtle">Primeira vez? Vamos configurar seu ambiente</p>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="px-6 py-6 space-y-6">
          {/* Explicacao */}
          <div className="space-y-3">
            <p className="text-sm text-foreground-muted leading-relaxed">
              O Legal ADK precisa de uma pasta raiz para armazenar seus casos juridicos.
              Cada caso tera sua propria pasta com versionamento automatico.
            </p>

            <div className="bg-surface-alt/50 rounded-md p-4 space-y-2">
              <p className="text-xs font-medium text-foreground-subtle uppercase tracking-wider">
                Estrutura criada automaticamente:
              </p>
              <pre className="text-xs text-foreground-muted font-mono leading-relaxed">
{`Pasta Selecionada/
  .registry.json       # Indice de casos
  Cliente_Silva/       # Pasta por cliente
    Caso_Divorcio/     # Cada caso isolado
      .git/            # Versionamento
      .adk_state/      # Checkpoints
      docs/            # Documentos
      drafts/          # Minutas`}
              </pre>
            </div>
          </div>

          {/* Selecao */}
          <div className="space-y-3">
            <label className="text-xs font-medium text-foreground-subtle uppercase tracking-wider">
              Pasta do Workspace
            </label>

            <div className="flex gap-3">
              <div className="flex-1 bg-surface-elevated border border-border rounded-md px-4 py-3">
                {selectedPath ? (
                  <span className="text-sm text-foreground font-mono truncate block">
                    {selectedPath}
                  </span>
                ) : (
                  <span className="text-sm text-foreground-subtle italic">
                    Nenhuma pasta selecionada
                  </span>
                )}
              </div>

              <button
                onClick={handleSelectFolder}
                disabled={isSelecting}
                className={`
                  px-4 py-2 rounded-md border transition-all flex items-center gap-2
                  ${isSelecting
                    ? 'bg-surface-elevated border-border text-foreground-subtle cursor-wait'
                    : 'bg-accent/10 border-accent/50 text-accent hover:bg-accent/20'
                  }
                `}
              >
                {isSelecting ? (
                  <>
                    <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    <span className="text-sm">Selecionando...</span>
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                    </svg>
                    <span className="text-sm font-medium">Selecionar</span>
                  </>
                )}
              </button>
            </div>

            {error && (
              <p className="text-xs text-error">{error}</p>
            )}
          </div>

          {/* Dicas */}
          <div className="bg-warning/5 border border-warning/20 rounded-md p-4">
            <div className="flex gap-3">
              <svg className="w-5 h-5 text-warning flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <div className="space-y-1">
                <p className="text-sm font-medium text-warning">Dicas importantes:</p>
                <ul className="text-xs text-foreground-subtle space-y-1">
                  <li>Escolha uma pasta dedicada (ex: Documentos/Legal_Workspace)</li>
                  <li>Evite pastas sincronizadas como OneDrive ou Dropbox</li>
                  <li>Voce pode mudar isso depois nas configuracoes</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-surface-alt/30 px-6 py-4 border-t border-border flex justify-end gap-3">
          <button
            onClick={handleConfirm}
            disabled={!selectedPath}
            className={`
              px-6 py-2.5 rounded-md font-medium text-sm transition-all
              ${selectedPath
                ? 'bg-accent text-white hover:bg-accent/90'
                : 'bg-surface-elevated text-foreground-subtle cursor-not-allowed'
              }
            `}
          >
            Confirmar e Continuar
          </button>
        </div>
      </div>
    </div>
  );
};

export default WorkspaceSetupModal;
