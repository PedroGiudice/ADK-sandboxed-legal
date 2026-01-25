import React, { useState } from 'react';

interface NewCaseModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreate: (data: NewCaseData) => Promise<boolean>;
  existingClients?: string[];
}

export interface NewCaseData {
  name: string;
  number?: string;
  client?: string;
  description?: string;
  tags?: string[];
}

const COMMON_TAGS = [
  'trabalhista',
  'civil',
  'criminal',
  'familia',
  'consumidor',
  'bancario',
  'empresarial',
  'tributario',
  'previdenciario',
  'ambiental',
  'contratos',
  'sucessoes'
];

const NewCaseModal: React.FC<NewCaseModalProps> = ({
  isOpen,
  onClose,
  onCreate,
  existingClients = []
}) => {
  const [name, setName] = useState('');
  const [number, setNumber] = useState('');
  const [client, setClient] = useState('');
  const [description, setDescription] = useState('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!name.trim()) {
      setError('Nome do caso e obrigatorio');
      return;
    }

    setIsCreating(true);
    setError(null);

    try {
      const success = await onCreate({
        name: name.trim(),
        number: number.trim() || undefined,
        client: client.trim() || undefined,
        description: description.trim() || undefined,
        tags: selectedTags.length > 0 ? selectedTags : undefined
      });

      if (success) {
        // Reset form
        setName('');
        setNumber('');
        setClient('');
        setDescription('');
        setSelectedTags([]);
        onClose();
      } else {
        setError('Erro ao criar caso. Tente novamente.');
      }
    } catch (e) {
      setError('Erro inesperado ao criar caso.');
      console.error('Create case error:', e);
    } finally {
      setIsCreating(false);
    }
  };

  const toggleTag = (tag: string) => {
    setSelectedTags(prev =>
      prev.includes(tag)
        ? prev.filter(t => t !== tag)
        : [...prev, tag]
    );
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-surface border border-border rounded-lg shadow-2xl w-full max-w-lg mx-4 overflow-hidden">
        {/* Header */}
        <div className="bg-surface-elevated px-6 py-4 border-b border-border flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 flex items-center justify-center bg-accent/10 border border-accent/30 rounded-lg">
              <svg className="w-5 h-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            </div>
            <h2 className="text-lg font-semibold text-foreground">Novo Caso</h2>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-md hover:bg-surface-alt text-foreground-subtle hover:text-foreground transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="px-6 py-6 space-y-5">
          {/* Nome */}
          <div className="space-y-2">
            <label className="text-xs font-medium text-foreground-subtle uppercase tracking-wider">
              Nome do Caso <span className="text-error">*</span>
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Ex: Silva vs. Banco Nacional"
              className="w-full bg-surface-elevated border border-border rounded-md px-4 py-2.5 text-sm text-foreground placeholder:text-foreground-subtle focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent"
              autoFocus
            />
          </div>

          {/* Numero do Processo */}
          <div className="space-y-2">
            <label className="text-xs font-medium text-foreground-subtle uppercase tracking-wider">
              Numero do Processo
            </label>
            <input
              type="text"
              value={number}
              onChange={(e) => setNumber(e.target.value)}
              placeholder="Ex: 0001234-56.2024.8.26.0100"
              className="w-full bg-surface-elevated border border-border rounded-md px-4 py-2.5 text-sm text-foreground font-mono placeholder:text-foreground-subtle focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent"
            />
          </div>

          {/* Cliente */}
          <div className="space-y-2">
            <label className="text-xs font-medium text-foreground-subtle uppercase tracking-wider">
              Cliente
            </label>
            <input
              type="text"
              value={client}
              onChange={(e) => setClient(e.target.value)}
              placeholder="Nome do cliente"
              list="clients-list"
              className="w-full bg-surface-elevated border border-border rounded-md px-4 py-2.5 text-sm text-foreground placeholder:text-foreground-subtle focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent"
            />
            {existingClients.length > 0 && (
              <datalist id="clients-list">
                {existingClients.map(c => (
                  <option key={c} value={c} />
                ))}
              </datalist>
            )}
            <p className="text-[10px] text-foreground-subtle">
              Casos do mesmo cliente serao agrupados na mesma pasta
            </p>
          </div>

          {/* Descricao */}
          <div className="space-y-2">
            <label className="text-xs font-medium text-foreground-subtle uppercase tracking-wider">
              Descricao
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Breve descricao do caso..."
              rows={2}
              className="w-full bg-surface-elevated border border-border rounded-md px-4 py-2.5 text-sm text-foreground placeholder:text-foreground-subtle focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent resize-none"
            />
          </div>

          {/* Tags */}
          <div className="space-y-2">
            <label className="text-xs font-medium text-foreground-subtle uppercase tracking-wider">
              Tags
            </label>
            <div className="flex flex-wrap gap-2">
              {COMMON_TAGS.map(tag => (
                <button
                  key={tag}
                  type="button"
                  onClick={() => toggleTag(tag)}
                  className={`
                    px-2.5 py-1 rounded text-[10px] uppercase tracking-wider font-medium transition-all
                    ${selectedTags.includes(tag)
                      ? 'bg-accent text-white'
                      : 'bg-surface-elevated text-foreground-subtle hover:text-foreground border border-border hover:border-accent/30'
                    }
                  `}
                >
                  {tag}
                </button>
              ))}
            </div>
          </div>

          {/* Error */}
          {error && (
            <div className="bg-error/10 border border-error/30 rounded-md px-4 py-3 text-sm text-error">
              {error}
            </div>
          )}
        </form>

        {/* Footer */}
        <div className="bg-surface-alt/30 px-6 py-4 border-t border-border flex justify-end gap-3">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-md text-sm text-foreground-muted hover:text-foreground transition-colors"
          >
            Cancelar
          </button>

          <button
            onClick={handleSubmit}
            disabled={isCreating || !name.trim()}
            className={`
              px-6 py-2 rounded-md font-medium text-sm transition-all flex items-center gap-2
              ${isCreating || !name.trim()
                ? 'bg-surface-elevated text-foreground-subtle cursor-not-allowed'
                : 'bg-accent text-white hover:bg-accent/90'
              }
            `}
          >
            {isCreating ? (
              <>
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                <span>Criando...</span>
              </>
            ) : (
              <span>Criar Caso</span>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default NewCaseModal;
