---
trigger: keywords
keywords: [tauri component, tauri react, tauri ui, desktop ui, tauri styling, tanstack query, tauri data fetching]
description: Padroes de frontend para apps Tauri - desktop-first com TanStack Query
---

# Frontend Patterns para Tauri

## Stack 2026
- React 19 + TypeScript 5.8+
- Vite 6.x para build
- **TanStack Query para data fetching (OBRIGATORIO)**
- TanStack Router para navegacao (opcional)
- Tailwind CSS 4.x
- tauri-specta para IPC type-safe

## Filosofia
Apps Tauri sao DESKTOP apps, nao sites. O frontend deve:
- Aproveitar capacidades desktop (hover, keyboard, etc.)
- Usar CSS moderno sem restricoes de "browser compatibility"
- Integrar-se com o sistema (tray, menus, shortcuts)
- **NUNCA fazer fetch direto - sempre TanStack Query**

## Estrutura de Componentes

```
src/
  components/
    ui/              # Componentes base (Button, Input, etc.)
    native/          # Wrappers para APIs nativas
      FilePicker.tsx
      Notification.tsx
      ThemeSync.tsx
    features/        # Componentes de feature/dominio
  hooks/
    useTauriEvent.ts # Subscribe a eventos Tauri
    useFileSystem.ts # Wrapper para fs plugin
    useNativeTheme.ts# Sync com tema do sistema
    queries/         # TanStack Query hooks
      useUserQuery.ts
      useDataQuery.ts
  lib/
    tauri/           # Bindings e helpers
    api.ts           # Configuracao cliente API
  types/             # Definicoes TypeScript globais
  App.tsx
  main.tsx           # QueryClient setup
```

## TanStack Query Setup

```tsx
// main.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 min
      retry: 1,
    },
  },
});

createRoot(document.getElementById('root')!).render(
  <QueryClientProvider client={queryClient}>
    <App />
  </QueryClientProvider>
);
```

## Hook Pattern: Data Fetching com Tauri

```tsx
// hooks/queries/useUserData.ts
import { useQuery } from '@tanstack/react-query';
import { invoke } from '@tauri-apps/api/core';

export function useUserData(userId: string) {
  return useQuery({
    queryKey: ['user', userId],
    queryFn: () => invoke<User>('get_user', { userId }),
    enabled: !!userId,
  });
}
```

## Componente: FilePicker (Exemplo Golden Path)

```tsx
// components/native/FilePicker.tsx
import { open } from '@tauri-apps/plugin-dialog';
import { readFile } from '@tauri-apps/plugin-fs';

interface FilePickerProps {
  onSelect: (content: Uint8Array, path: string) => void;
  accept?: string[];
  label?: string;
}

export function FilePicker({ onSelect, accept, label = 'Select File' }: FilePickerProps) {
  const handleClick = async () => {
    const path = await open({
      multiple: false,
      filters: accept ? [{ name: 'Files', extensions: accept }] : undefined,
    });

    if (path && typeof path === 'string') {
      const content = await readFile(path);
      onSelect(content, path);
    }
  };

  return (
    <button
      onClick={handleClick}
      className="
        px-4 py-2 rounded-lg
        bg-white/10 hover:bg-white/20
        backdrop-blur-xl
        border border-white/20
        transition-all duration-200
        focus:outline-none focus:ring-2 focus:ring-indigo-500
      "
    >
      {label}
    </button>
  );
}
```

## Hook: useTauriEvent

```tsx
import { useEffect } from 'react';
import { listen, UnlistenFn } from '@tauri-apps/api/event';

export function useTauriEvent<T>(
  event: string,
  handler: (payload: T) => void
) {
  useEffect(() => {
    let unlisten: UnlistenFn;

    listen<T>(event, (e) => handler(e.payload))
      .then((fn) => { unlisten = fn; });

    return () => { unlisten?.(); };
  }, [event, handler]);
}
```

## Hook: useNativeTheme

```tsx
import { useEffect, useState } from 'react';
import { getCurrentWindow, Theme } from '@tauri-apps/api/window';

export function useNativeTheme() {
  const [theme, setTheme] = useState<'light' | 'dark'>('dark');

  useEffect(() => {
    const window = getCurrentWindow();

    window.theme().then((t) => {
      setTheme(t === Theme.Light ? 'light' : 'dark');
    });

    const unlisten = window.onThemeChanged(({ payload }) => {
      setTheme(payload === Theme.Light ? 'light' : 'dark');
    });

    return () => { unlisten.then((fn) => fn()); };
  }, []);

  return theme;
}
```

## Hook: useKeyboardShortcut

```tsx
import { useEffect } from 'react';

type Modifier = 'ctrl' | 'alt' | 'shift' | 'meta';

export function useKeyboardShortcut(
  key: string,
  callback: () => void,
  modifiers: Modifier[] = []
) {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const modifiersMatch =
        modifiers.includes('ctrl') === e.ctrlKey &&
        modifiers.includes('alt') === e.altKey &&
        modifiers.includes('shift') === e.shiftKey &&
        modifiers.includes('meta') === e.metaKey;

      if (e.key.toLowerCase() === key.toLowerCase() && modifiersMatch) {
        e.preventDefault();
        callback();
      }
    };

    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [key, callback, modifiers]);
}

// Uso
// useKeyboardShortcut('s', handleSave, ['ctrl']); // Ctrl+S
// useKeyboardShortcut('n', handleNew, ['ctrl']);  // Ctrl+N
```

## Styling: Desktop-First

```css
/* Aproveitar capacidades desktop */

/* Hover states ricos (desktop tem mouse) */
.card:hover {
  transform: translateY(-2px) scale(1.01);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

/* Backdrop blur (WebView moderno suporta) */
.glass {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
}

/* Custom scrollbar (desktop) */
::-webkit-scrollbar {
  width: 8px;
}
::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
}

/* Keyboard focus visible */
:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}
```

## Regras Absolutas

### NUNCA Fazer
- Usar `<input type="file">` (sempre `dialog.open()`)
- Usar `localStorage` (sempre `store` plugin)
- Usar `alert()` ou toasts web (sempre `notification` plugin)
- Simplificar CSS por "compatibilidade" (WebView e moderno)
- Fazer fetch direto (sempre TanStack Query)
- Usar `any` em tipos (TypeScript strict)
- Usar `window.open()` (sempre `shell.open()`)
- Usar `navigator.clipboard` (sempre `clipboard` plugin)

### SEMPRE Fazer
- Usar APIs nativas para file, clipboard, notification
- Usar TanStack Query para data fetching
- Implementar hover states ricos (desktop tem mouse)
- Adicionar keyboard shortcuts para acoes principais
- Usar backdrop-filter, gradients complexos
- Sincronizar com tema do sistema
- Type-safe IPC via tauri-specta
- Focus states visiveis para acessibilidade
