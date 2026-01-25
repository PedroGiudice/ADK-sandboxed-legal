import React from 'react';
import { Editor } from 'slate';
import { useSlate } from 'slate-react';
import { toggleMark, isMarkActive, toggleBlock, isBlockActive } from './SlateEditor';
import { MarkType, CustomElement } from '../../types/slate';

interface ToolbarButtonProps {
  format: MarkType | CustomElement['type'];
  icon: React.ReactNode;
  isBlock?: boolean;
  level?: number;
  title: string;
}

const ToolbarButton: React.FC<ToolbarButtonProps> = ({ format, icon, isBlock = false, level, title }) => {
  const editor = useSlate();

  const isActive = isBlock
    ? isBlockActive(editor, format as CustomElement['type'], level)
    : isMarkActive(editor, format as MarkType);

  const handleMouseDown = (event: React.MouseEvent) => {
    event.preventDefault();
    if (isBlock) {
      toggleBlock(editor, format as CustomElement['type'], level);
    } else {
      toggleMark(editor, format as MarkType);
    }
  };

  return (
    <button
      type="button"
      onMouseDown={handleMouseDown}
      title={title}
      className={`
        p-1.5 rounded transition-all duration-150
        ${isActive
          ? 'bg-accent/20 text-accent'
          : 'text-foreground-muted hover:text-foreground hover:bg-surface-elevated'
        }
      `}
    >
      {icon}
    </button>
  );
};

// Icons as inline SVGs
const BoldIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M6 4h8a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z"/>
    <path d="M6 12h9a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z"/>
  </svg>
);

const ItalicIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="19" y1="4" x2="10" y2="4"/>
    <line x1="14" y1="20" x2="5" y2="20"/>
    <line x1="15" y1="4" x2="9" y2="20"/>
  </svg>
);

const UnderlineIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M6 3v7a6 6 0 0 0 6 6 6 6 0 0 0 6-6V3"/>
    <line x1="4" y1="21" x2="20" y2="21"/>
  </svg>
);

const CodeIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="16 18 22 12 16 6"/>
    <polyline points="8 6 2 12 8 18"/>
  </svg>
);

const HeadingIcon = ({ level }: { level: number }) => (
  <span className="font-bold text-xs">H{level}</span>
);

const ListBulletIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="8" y1="6" x2="21" y2="6"/>
    <line x1="8" y1="12" x2="21" y2="12"/>
    <line x1="8" y1="18" x2="21" y2="18"/>
    <circle cx="4" cy="6" r="1" fill="currentColor"/>
    <circle cx="4" cy="12" r="1" fill="currentColor"/>
    <circle cx="4" cy="18" r="1" fill="currentColor"/>
  </svg>
);

const ListNumberIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="10" y1="6" x2="21" y2="6"/>
    <line x1="10" y1="12" x2="21" y2="12"/>
    <line x1="10" y1="18" x2="21" y2="18"/>
    <text x="3" y="8" fontSize="8" fill="currentColor" fontFamily="monospace">1</text>
    <text x="3" y="14" fontSize="8" fill="currentColor" fontFamily="monospace">2</text>
    <text x="3" y="20" fontSize="8" fill="currentColor" fontFamily="monospace">3</text>
  </svg>
);

const QuoteIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V21z"/>
    <path d="M15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2h.75c0 2.25.25 4-2.75 4v3z"/>
  </svg>
);

const Separator = () => (
  <div className="w-px h-4 bg-border mx-1" />
);

interface EditorToolbarProps {
  editor: Editor;
}

const EditorToolbar: React.FC<EditorToolbarProps> = () => {
  return (
    <div className="flex items-center gap-0.5 px-2 py-1.5 border-b border-border bg-surface-alt/50">
      {/* Text formatting */}
      <ToolbarButton format="bold" icon={<BoldIcon />} title="Negrito (Ctrl+B)" />
      <ToolbarButton format="italic" icon={<ItalicIcon />} title="Italico (Ctrl+I)" />
      <ToolbarButton format="underline" icon={<UnderlineIcon />} title="Sublinhado (Ctrl+U)" />
      <ToolbarButton format="code" icon={<CodeIcon />} title="Codigo (Ctrl+`)" />

      <Separator />

      {/* Headings */}
      <ToolbarButton format="heading" isBlock level={1} icon={<HeadingIcon level={1} />} title="Titulo 1" />
      <ToolbarButton format="heading" isBlock level={2} icon={<HeadingIcon level={2} />} title="Titulo 2" />
      <ToolbarButton format="heading" isBlock level={3} icon={<HeadingIcon level={3} />} title="Titulo 3" />

      <Separator />

      {/* Lists */}
      <ToolbarButton format="bulleted-list" isBlock icon={<ListBulletIcon />} title="Lista com marcadores" />
      <ToolbarButton format="numbered-list" isBlock icon={<ListNumberIcon />} title="Lista numerada" />

      <Separator />

      {/* Blockquote */}
      <ToolbarButton format="blockquote" isBlock icon={<QuoteIcon />} title="Citacao" />

      {/* Keyboard hints */}
      <div className="ml-auto text-[10px] text-foreground-subtle font-mono">
        Ctrl+Enter para enviar
      </div>
    </div>
  );
};

export default EditorToolbar;
