---
trigger: keywords
keywords: [file picker, save file, notification, clipboard, tauri api, dialog, filesystem]
description: APIs nativas do Tauri - uso obrigatorio em projetos Tauri
---

# Tauri Native APIs - Referencia Obrigatoria

## REGRA FUNDAMENTAL
> Sempre usar APIs nativas. Web fallback so com justificativa explicita.

## Dialog (Arquivos)

### Selecionar Arquivo
```typescript
import { open } from '@tauri-apps/plugin-dialog';

const path = await open({
  multiple: false,
  filters: [{
    name: 'Audio',
    extensions: ['wav', 'mp3', 'webm']
  }]
});
```

**PROIBIDO:** `<input type="file">`

### Salvar Arquivo
```typescript
import { save } from '@tauri-apps/plugin-dialog';
import { writeFile } from '@tauri-apps/plugin-fs';

const path = await save({
  filters: [{ name: 'Text', extensions: ['txt'] }]
});
if (path) {
  await writeFile(path, content);
}
```

**PROIBIDO:** Download via `<a href="data:...">`

## Filesystem

```typescript
import {
  readFile,
  writeFile,
  readDir,
  createDir,
  exists
} from '@tauri-apps/plugin-fs';

// Ler arquivo
const content = await readFile(path);

// Escrever arquivo
await writeFile(path, new TextEncoder().encode(text));

// Listar diretorio
const entries = await readDir(path);
```

**PROIBIDO:** FileReader API do browser

## Notifications

```typescript
import {
  sendNotification,
  requestPermission,
  isPermissionGranted
} from '@tauri-apps/plugin-notification';

// Verificar/solicitar permissao
let permitted = await isPermissionGranted();
if (!permitted) {
  const permission = await requestPermission();
  permitted = permission === 'granted';
}

// Enviar notificacao
if (permitted) {
  sendNotification({
    title: 'Processo Concluido',
    body: 'Arquivo salvo com sucesso!'
  });
}
```

**PROIBIDO:** `alert()`, toasts web-only

## Clipboard

```typescript
import { writeText, readText } from '@tauri-apps/plugin-clipboard-manager';

// Copiar
await writeText('Hello, World!');

// Colar
const text = await readText();
```

**PROIBIDO:** `navigator.clipboard` (menos capabilities)

## Shell (Links Externos)

```typescript
import { open } from '@tauri-apps/plugin-shell';

// Abrir URL no browser padrao
await open('https://tauri.app');

// Abrir arquivo com app padrao
await open('/path/to/document.pdf');
```

**PROIBIDO:** `window.open()` (comportamento inconsistente)

## Store (Persistencia)

```typescript
import { Store } from '@tauri-apps/plugin-store';

const store = new Store('settings.json');

// Salvar
await store.set('theme', 'dark');
await store.save();

// Carregar
const theme = await store.get<string>('theme');
```

**PROIBIDO:** `localStorage` (sem criptografia, sem sync)

## Tabela de Referencia Rapida

| Necessidade | API Tauri | Web Fallback PROIBIDO |
|-------------|-----------|----------------------|
| Selecao arquivo | `dialog.open()` | `<input type="file">` |
| Salvar arquivo | `dialog.save()` + `fs.writeFile()` | Download link |
| Notificacoes | `notification` plugin | `alert()` |
| Clipboard | `clipboard` plugin | `navigator.clipboard` |
| Links externos | `shell.open()` | `window.open()` |
| Persistencia | `store` plugin | `localStorage` |
