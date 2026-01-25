import React, { useCallback, useMemo, KeyboardEvent } from 'react';
import { createEditor, Descendant, Editor, Transforms, Element as SlateElement } from 'slate';
import { Slate, Editable, withReact, RenderElementProps, RenderLeafProps } from 'slate-react';
import { withHistory } from 'slate-history';
import { CustomElement, CustomText, MarkType } from '../../types/slate';
import { isEditorEmpty } from './utils/serializer';
import EditorToolbar from './EditorToolbar';

/**
 * Initial value for empty editor
 */
export const initialValue: Descendant[] = [
  {
    type: 'paragraph',
    children: [{ text: '' }],
  },
];

interface SlateEditorProps {
  value: Descendant[];
  onChange: (value: Descendant[]) => void;
  onSubmit: () => void;
  disabled?: boolean;
  placeholder?: string;
}

/**
 * Custom element renderer
 */
const Element = ({ attributes, children, element }: RenderElementProps) => {
  const customElement = element as CustomElement;

  switch (customElement.type) {
    case 'heading':
      const HeadingTag = `h${customElement.level}` as 'h1' | 'h2' | 'h3';
      const headingClasses = {
        1: 'text-xl font-bold mb-2',
        2: 'text-lg font-semibold mb-1.5',
        3: 'text-base font-medium mb-1',
      };
      return (
        <HeadingTag {...attributes} className={headingClasses[customElement.level]}>
          {children}
        </HeadingTag>
      );
    case 'bulleted-list':
      return (
        <ul {...attributes} className="list-disc list-inside ml-4 space-y-1">
          {children}
        </ul>
      );
    case 'numbered-list':
      return (
        <ol {...attributes} className="list-decimal list-inside ml-4 space-y-1">
          {children}
        </ol>
      );
    case 'list-item':
      return <li {...attributes}>{children}</li>;
    case 'blockquote':
      return (
        <blockquote
          {...attributes}
          className="border-l-4 border-accent/40 pl-4 py-1 italic text-foreground-muted bg-surface-alt/30 rounded-r"
        >
          {children}
        </blockquote>
      );
    case 'paragraph':
    default:
      return <p {...attributes} className="min-h-[1.5em]">{children}</p>;
  }
};

/**
 * Custom leaf renderer for text formatting
 */
const Leaf = ({ attributes, children, leaf }: RenderLeafProps) => {
  const customLeaf = leaf as CustomText;

  if (customLeaf.bold) {
    children = <strong className="font-semibold">{children}</strong>;
  }
  if (customLeaf.italic) {
    children = <em className="italic">{children}</em>;
  }
  if (customLeaf.underline) {
    children = <u className="underline">{children}</u>;
  }
  if (customLeaf.code) {
    children = (
      <code className="px-1.5 py-0.5 bg-surface-elevated rounded text-[0.9em] font-mono text-accent">
        {children}
      </code>
    );
  }

  return <span {...attributes}>{children}</span>;
};

/**
 * Toggle a mark (bold, italic, etc.)
 */
export const toggleMark = (editor: Editor, format: MarkType) => {
  const isActive = isMarkActive(editor, format);

  if (isActive) {
    Editor.removeMark(editor, format);
  } else {
    Editor.addMark(editor, format, true);
  }
};

/**
 * Check if a mark is active
 */
export const isMarkActive = (editor: Editor, format: MarkType): boolean => {
  const marks = Editor.marks(editor);
  return marks ? marks[format] === true : false;
};

/**
 * Toggle a block type
 */
export const toggleBlock = (editor: Editor, format: CustomElement['type'], level?: number) => {
  const isActive = isBlockActive(editor, format, level);
  const isList = format === 'bulleted-list' || format === 'numbered-list';

  Transforms.unwrapNodes(editor, {
    match: n =>
      !Editor.isEditor(n) &&
      SlateElement.isElement(n) &&
      (n.type === 'bulleted-list' || n.type === 'numbered-list'),
    split: true,
  });

  let newProperties: Partial<CustomElement>;

  if (isActive) {
    newProperties = { type: 'paragraph' };
  } else if (isList) {
    newProperties = { type: 'list-item' };
  } else if (format === 'heading') {
    newProperties = { type: 'heading', level: (level || 1) as 1 | 2 | 3 };
  } else {
    newProperties = { type: format };
  }

  Transforms.setNodes(editor, newProperties as Partial<SlateElement>);

  if (!isActive && isList) {
    const block = { type: format, children: [] } as CustomElement;
    Transforms.wrapNodes(editor, block);
  }
};

/**
 * Check if a block type is active
 */
export const isBlockActive = (editor: Editor, format: CustomElement['type'], level?: number): boolean => {
  const { selection } = editor;
  if (!selection) return false;

  const [match] = Array.from(
    Editor.nodes(editor, {
      at: Editor.unhangRange(editor, selection),
      match: n => {
        if (!SlateElement.isElement(n)) return false;
        if (n.type !== format) return false;
        if (format === 'heading' && level !== undefined) {
          return (n as any).level === level;
        }
        return true;
      },
    })
  );

  return !!match;
};

/**
 * Main Slate Editor component
 */
const SlateEditor: React.FC<SlateEditorProps> = ({
  value,
  onChange,
  onSubmit,
  disabled = false,
  placeholder = 'Digite sua consulta juridica...',
}) => {
  const editor = useMemo(() => withHistory(withReact(createEditor())), []);

  const renderElement = useCallback((props: RenderElementProps) => <Element {...props} />, []);
  const renderLeaf = useCallback((props: RenderLeafProps) => <Leaf {...props} />, []);

  const handleKeyDown = useCallback(
    (event: KeyboardEvent<HTMLDivElement>) => {
      // Ctrl/Cmd + Enter to submit
      if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
        event.preventDefault();
        if (!isEditorEmpty(value) && !disabled) {
          onSubmit();
        }
        return;
      }

      // Format shortcuts
      if (event.ctrlKey || event.metaKey) {
        switch (event.key) {
          case 'b':
            event.preventDefault();
            toggleMark(editor, 'bold');
            break;
          case 'i':
            event.preventDefault();
            toggleMark(editor, 'italic');
            break;
          case 'u':
            event.preventDefault();
            toggleMark(editor, 'underline');
            break;
          case '`':
            event.preventDefault();
            toggleMark(editor, 'code');
            break;
        }
      }
    },
    [editor, onSubmit, disabled, value]
  );

  return (
    <div className="slate-editor-container">
      <Slate editor={editor} initialValue={value} onValueChange={onChange}>
        <EditorToolbar editor={editor} />
        <Editable
          renderElement={renderElement}
          renderLeaf={renderLeaf}
          placeholder={disabled ? 'Processando resposta...' : placeholder}
          disabled={disabled}
          onKeyDown={handleKeyDown}
          className={`
            w-full p-4 bg-transparent text-foreground placeholder-foreground-muted
            focus:outline-none resize-none min-h-[80px] max-h-[200px] overflow-y-auto
            text-[15px] leading-relaxed
            ${disabled ? 'cursor-not-allowed opacity-70' : ''}
          `}
          style={{ outline: 'none' }}
          spellCheck
          autoFocus
        />
      </Slate>
    </div>
  );
};

export default SlateEditor;
