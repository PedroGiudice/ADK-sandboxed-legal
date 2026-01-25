import { BaseEditor, Descendant } from 'slate';
import { ReactEditor } from 'slate-react';
import { HistoryEditor } from 'slate-history';

/**
 * Custom element types for the Slate editor
 */
export type ParagraphElement = {
  type: 'paragraph';
  children: Descendant[];
};

export type HeadingElement = {
  type: 'heading';
  level: 1 | 2 | 3;
  children: Descendant[];
};

export type BulletListElement = {
  type: 'bulleted-list';
  children: Descendant[];
};

export type NumberedListElement = {
  type: 'numbered-list';
  children: Descendant[];
};

export type ListItemElement = {
  type: 'list-item';
  children: Descendant[];
};

export type BlockquoteElement = {
  type: 'blockquote';
  children: Descendant[];
};

export type CustomElement =
  | ParagraphElement
  | HeadingElement
  | BulletListElement
  | NumberedListElement
  | ListItemElement
  | BlockquoteElement;

/**
 * Custom text formatting marks
 */
export type CustomText = {
  text: string;
  bold?: boolean;
  italic?: boolean;
  code?: boolean;
  underline?: boolean;
};

/**
 * Type aliases for convenience
 */
export type CustomEditor = BaseEditor & ReactEditor & HistoryEditor;
export type ElementType = CustomElement['type'];
export type MarkType = keyof Omit<CustomText, 'text'>;

/**
 * Augment the Slate module with custom types
 */
declare module 'slate' {
  interface CustomTypes {
    Editor: CustomEditor;
    Element: CustomElement;
    Text: CustomText;
  }
}

