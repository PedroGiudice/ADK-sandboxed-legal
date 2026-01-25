import { Descendant, Text, Element as SlateElement } from 'slate';
import { CustomElement, CustomText } from '../../../types/slate';

/**
 * Serialize Slate nodes to plain text
 */
export const serializeToText = (nodes: Descendant[]): string => {
  return nodes.map(node => serializeNodeToText(node)).join('\n');
};

const serializeNodeToText = (node: Descendant): string => {
  if (Text.isText(node)) {
    return node.text;
  }

  const children = node.children.map(child => serializeNodeToText(child)).join('');

  switch ((node as CustomElement).type) {
    case 'paragraph':
      return children;
    case 'heading':
      return children;
    case 'bulleted-list':
    case 'numbered-list':
      return children;
    case 'list-item':
      return `- ${children}`;
    case 'blockquote':
      return `> ${children}`;
    default:
      return children;
  }
};

/**
 * Serialize Slate nodes to Markdown
 */
export const serializeToMarkdown = (nodes: Descendant[]): string => {
  return nodes.map(node => serializeNodeToMarkdown(node)).join('\n');
};

const serializeNodeToMarkdown = (node: Descendant): string => {
  if (Text.isText(node)) {
    let text = node.text;
    const customText = node as CustomText;

    if (customText.code) {
      text = `\`${text}\``;
    }
    if (customText.bold) {
      text = `**${text}**`;
    }
    if (customText.italic) {
      text = `*${text}*`;
    }
    // Underline has no standard Markdown, skip or use HTML

    return text;
  }

  const element = node as CustomElement;
  const children = element.children.map(child => serializeNodeToMarkdown(child)).join('');

  switch (element.type) {
    case 'paragraph':
      return children;
    case 'heading':
      const prefix = '#'.repeat(element.level);
      return `${prefix} ${children}`;
    case 'bulleted-list':
      return element.children.map(child => serializeNodeToMarkdown(child)).join('\n');
    case 'numbered-list':
      return element.children.map((child, i) => {
        const content = serializeNodeToMarkdown(child).replace(/^- /, '');
        return `${i + 1}. ${content}`;
      }).join('\n');
    case 'list-item':
      return `- ${children}`;
    case 'blockquote':
      return `> ${children}`;
    default:
      return children;
  }
};

/**
 * Deserialize plain text to Slate nodes
 */
export const deserializeFromText = (text: string): Descendant[] => {
  const lines = text.split('\n');

  if (lines.length === 0 || (lines.length === 1 && lines[0] === '')) {
    return [{ type: 'paragraph', children: [{ text: '' }] }];
  }

  return lines.map(line => ({
    type: 'paragraph' as const,
    children: [{ text: line }],
  }));
};

/**
 * Deserialize Markdown to Slate nodes
 * Basic implementation - handles common patterns
 */
export const deserializeFromMarkdown = (markdown: string): Descendant[] => {
  const lines = markdown.split('\n');
  const nodes: Descendant[] = [];
  let currentList: Descendant[] | null = null;
  let listType: 'bulleted-list' | 'numbered-list' | null = null;

  const parseInlineFormatting = (text: string): Descendant[] => {
    const children: Descendant[] = [];
    let remaining = text;

    // Simple inline parsing - handles **bold**, *italic*, `code`
    const regex = /(\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`)/g;
    let lastIndex = 0;
    let match;

    while ((match = regex.exec(remaining)) !== null) {
      // Add plain text before match
      if (match.index > lastIndex) {
        children.push({ text: remaining.slice(lastIndex, match.index) });
      }

      if (match[2]) {
        // Bold **text**
        children.push({ text: match[2], bold: true });
      } else if (match[3]) {
        // Italic *text*
        children.push({ text: match[3], italic: true });
      } else if (match[4]) {
        // Code `text`
        children.push({ text: match[4], code: true });
      }

      lastIndex = regex.lastIndex;
    }

    // Add remaining text
    if (lastIndex < remaining.length) {
      children.push({ text: remaining.slice(lastIndex) });
    }

    // If no children, add empty text
    if (children.length === 0) {
      children.push({ text: '' });
    }

    return children;
  };

  const flushList = () => {
    if (currentList && listType) {
      nodes.push({
        type: listType,
        children: currentList,
      } as Descendant);
      currentList = null;
      listType = null;
    }
  };

  for (const line of lines) {
    // Heading
    const headingMatch = line.match(/^(#{1,3})\s+(.+)$/);
    if (headingMatch) {
      flushList();
      const level = headingMatch[1].length as 1 | 2 | 3;
      nodes.push({
        type: 'heading',
        level,
        children: parseInlineFormatting(headingMatch[2]),
      });
      continue;
    }

    // Bulleted list item
    const bulletMatch = line.match(/^[-*]\s+(.+)$/);
    if (bulletMatch) {
      if (listType !== 'bulleted-list') {
        flushList();
        currentList = [];
        listType = 'bulleted-list';
      }
      currentList!.push({
        type: 'list-item',
        children: parseInlineFormatting(bulletMatch[1]),
      });
      continue;
    }

    // Numbered list item
    const numberedMatch = line.match(/^\d+\.\s+(.+)$/);
    if (numberedMatch) {
      if (listType !== 'numbered-list') {
        flushList();
        currentList = [];
        listType = 'numbered-list';
      }
      currentList!.push({
        type: 'list-item',
        children: parseInlineFormatting(numberedMatch[1]),
      });
      continue;
    }

    // Blockquote
    const quoteMatch = line.match(/^>\s*(.*)$/);
    if (quoteMatch) {
      flushList();
      nodes.push({
        type: 'blockquote',
        children: parseInlineFormatting(quoteMatch[1]),
      });
      continue;
    }

    // Empty line or paragraph
    flushList();
    if (line.trim() === '') {
      // Skip empty lines between blocks
      continue;
    }

    nodes.push({
      type: 'paragraph',
      children: parseInlineFormatting(line),
    });
  }

  flushList();

  // Return at least one empty paragraph
  if (nodes.length === 0) {
    return [{ type: 'paragraph', children: [{ text: '' }] }];
  }

  return nodes;
};

/**
 * Check if editor content is empty
 */
export const isEditorEmpty = (nodes: Descendant[]): boolean => {
  if (nodes.length === 0) return true;
  if (nodes.length === 1) {
    const node = nodes[0];
    if (SlateElement.isElement(node) && node.type === 'paragraph') {
      const children = node.children;
      if (children.length === 1 && Text.isText(children[0]) && children[0].text === '') {
        return true;
      }
    }
  }
  return false;
};
