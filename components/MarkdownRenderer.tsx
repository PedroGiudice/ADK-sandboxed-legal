import React from 'react';

/**
 * Enhanced Markdown Renderer
 * Supports: headings, lists, blockquotes, bold, italic, code, links
 */

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

/**
 * Parse inline formatting (bold, italic, code, links)
 */
const parseInline = (text: string, keyPrefix: string = ''): React.ReactNode[] => {
  const elements: React.ReactNode[] = [];

  // Regex for inline elements: **bold**, *italic*, `code`, [link](url)
  const regex = /(\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`|\[(.+?)\]\((.+?)\))/g;
  let lastIndex = 0;
  let match;
  let partKey = 0;

  while ((match = regex.exec(text)) !== null) {
    // Add plain text before match
    if (match.index > lastIndex) {
      elements.push(text.slice(lastIndex, match.index));
    }

    const key = `${keyPrefix}-${partKey++}`;

    if (match[2]) {
      // Bold **text**
      elements.push(
        <strong key={key} className="font-semibold">
          {match[2]}
        </strong>
      );
    } else if (match[3]) {
      // Italic *text*
      elements.push(
        <em key={key} className="italic">
          {match[3]}
        </em>
      );
    } else if (match[4]) {
      // Code `text`
      elements.push(
        <code key={key} className="px-1.5 py-0.5 bg-surface-elevated rounded text-[0.9em] font-mono text-accent">
          {match[4]}
        </code>
      );
    } else if (match[5] && match[6]) {
      // Link [text](url)
      elements.push(
        <a
          key={key}
          href={match[6]}
          target="_blank"
          rel="noopener noreferrer"
          className="text-accent hover:underline"
        >
          {match[5]}
        </a>
      );
    }

    lastIndex = regex.lastIndex;
  }

  // Add remaining text
  if (lastIndex < text.length) {
    elements.push(text.slice(lastIndex));
  }

  return elements.length > 0 ? elements : [text];
};

/**
 * Parse a single line and determine its type
 */
interface ParsedLine {
  type: 'heading' | 'bullet-list' | 'numbered-list' | 'blockquote' | 'paragraph' | 'empty';
  level?: number;
  content: string;
  number?: number;
}

const parseLine = (line: string): ParsedLine => {
  const trimmed = line.trim();

  if (!trimmed) {
    return { type: 'empty', content: '' };
  }

  // Heading: # ## ### etc
  const headingMatch = trimmed.match(/^(#{1,6})\s+(.+)$/);
  if (headingMatch) {
    return {
      type: 'heading',
      level: headingMatch[1].length,
      content: headingMatch[2],
    };
  }

  // Numbered list: 1. 2. etc
  const numberedMatch = trimmed.match(/^(\d+)\.\s+(.+)$/);
  if (numberedMatch) {
    return {
      type: 'numbered-list',
      number: parseInt(numberedMatch[1], 10),
      content: numberedMatch[2],
    };
  }

  // Bullet list: - or *
  const bulletMatch = trimmed.match(/^[-*]\s+(.+)$/);
  if (bulletMatch) {
    return {
      type: 'bullet-list',
      content: bulletMatch[1],
    };
  }

  // Blockquote: >
  const quoteMatch = trimmed.match(/^>\s*(.*)$/);
  if (quoteMatch) {
    return {
      type: 'blockquote',
      content: quoteMatch[1],
    };
  }

  // Regular paragraph
  return {
    type: 'paragraph',
    content: trimmed,
  };
};

/**
 * Group consecutive list items
 */
interface Block {
  type: 'heading' | 'bullet-list' | 'numbered-list' | 'blockquote' | 'paragraph';
  items: ParsedLine[];
  level?: number;
}

const groupBlocks = (lines: ParsedLine[]): Block[] => {
  const blocks: Block[] = [];
  let currentBlock: Block | null = null;

  for (const line of lines) {
    if (line.type === 'empty') {
      currentBlock = null;
      continue;
    }

    const isList = line.type === 'bullet-list' || line.type === 'numbered-list';

    if (currentBlock && currentBlock.type === line.type && isList) {
      // Continue same list
      currentBlock.items.push(line);
    } else {
      // Start new block
      currentBlock = {
        type: line.type,
        items: [line],
        level: line.level,
      };
      blocks.push(currentBlock);
    }
  }

  return blocks;
};

/**
 * Render a block
 */
const renderBlock = (block: Block, blockIdx: number): React.ReactNode => {
  const key = `block-${blockIdx}`;

  switch (block.type) {
    case 'heading': {
      const item = block.items[0];
      const level = item.level || 1;
      const headingClasses: Record<number, string> = {
        1: 'text-xl font-bold mt-4 mb-2',
        2: 'text-lg font-semibold mt-3 mb-2',
        3: 'text-base font-semibold mt-2 mb-1',
        4: 'text-sm font-semibold mt-2 mb-1',
        5: 'text-sm font-medium mt-1 mb-1',
        6: 'text-xs font-medium mt-1 mb-1 uppercase tracking-wide',
      };
      const Tag = `h${level}` as keyof JSX.IntrinsicElements;
      return (
        <Tag key={key} className={headingClasses[level] || headingClasses[3]}>
          {parseInline(item.content, key)}
        </Tag>
      );
    }

    case 'numbered-list':
      return (
        <ol key={key} className="list-decimal list-outside ml-6 my-2 space-y-1">
          {block.items.map((item, idx) => (
            <li key={`${key}-${idx}`} className="pl-1">
              {parseInline(item.content, `${key}-${idx}`)}
            </li>
          ))}
        </ol>
      );

    case 'bullet-list':
      return (
        <ul key={key} className="list-disc list-outside ml-6 my-2 space-y-1">
          {block.items.map((item, idx) => (
            <li key={`${key}-${idx}`} className="pl-1">
              {parseInline(item.content, `${key}-${idx}`)}
            </li>
          ))}
        </ul>
      );

    case 'blockquote':
      return (
        <blockquote
          key={key}
          className="border-l-4 border-accent/40 pl-4 py-2 my-2 italic text-foreground-muted bg-surface-alt/30 rounded-r"
        >
          {block.items.map((item, idx) => (
            <p key={`${key}-${idx}`}>
              {parseInline(item.content, `${key}-${idx}`)}
            </p>
          ))}
        </blockquote>
      );

    case 'paragraph':
    default:
      return (
        <p key={key} className="my-1.5">
          {parseInline(block.items[0].content, key)}
        </p>
      );
  }
};

/**
 * Main Markdown Renderer component
 */
const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content, className = '' }) => {
  if (!content) return null;

  // Parse lines
  const lines = content.split('\n').map(parseLine);

  // Group into blocks
  const blocks = groupBlocks(lines);

  return (
    <div className={`markdown-content leading-relaxed ${className}`}>
      {blocks.map((block, idx) => renderBlock(block, idx))}
    </div>
  );
};

export default MarkdownRenderer;

/**
 * Legacy function for compatibility - wraps the component
 */
export const renderMarkdown = (text: string): React.ReactNode => {
  return <MarkdownRenderer content={text} />;
};
