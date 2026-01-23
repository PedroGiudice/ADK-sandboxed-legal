---
trigger: keywords
keywords: [tauri, desktop app, native app, rust frontend, tauri init, tauri setup]
description: Conceitos fundamentais de Tauri para desenvolvimento
---

# Tauri Core Concepts

## O que e Tauri
Framework para criar apps desktop/mobile usando web technologies (HTML/CSS/JS)
com backend em Rust. Diferente de Electron, usa WebView do sistema (nao Chromium).

## Arquitetura

```
Frontend (WebView)          Backend (Rust)
+---------------+           +---------------+
|   React/TS    |<--------->|    Tauri      |
|               |   IPC     |    Core       |
|  UI/Events    |           |   Commands    |
+---------------+           +---------------+
```

## IPC (Inter-Process Communication)

### Definindo Commands (Rust)
```rust
#[tauri::command]
fn greet(name: String) -> String {
    format!("Hello, {}!", name)
}

// Com error handling
#[tauri::command]
fn read_file(path: String) -> Result<String, String> {
    std::fs::read_to_string(&path)
        .map_err(|e| e.to_string())
}
```

### Chamando Commands (TypeScript)
```typescript
import { invoke } from '@tauri-apps/api/core';

// Sem type safety (evitar)
const greeting = await invoke<string>('greet', { name: 'World' });

// Com tauri-specta (preferido)
import { commands } from './bindings';
const greeting = await commands.greet('World');
```

## Plugins Oficiais Principais

| Plugin | Funcionalidade |
|--------|---------------|
| `@tauri-apps/plugin-dialog` | Dialogos nativos (open, save, message) |
| `@tauri-apps/plugin-fs` | Filesystem access |
| `@tauri-apps/plugin-notification` | Notificacoes do sistema |
| `@tauri-apps/plugin-clipboard` | Clipboard read/write |
| `@tauri-apps/plugin-shell` | Executar comandos, abrir URLs |
| `@tauri-apps/plugin-store` | Persistencia key-value |

## Configuracao (tauri.conf.json)

```json
{
  "productName": "My App",
  "version": "0.1.0",
  "identifier": "com.mycompany.myapp",
  "build": {
    "frontendDist": "../dist"
  },
  "app": {
    "withGlobalTauri": false,
    "security": {
      "csp": "default-src 'self'; script-src 'self'"
    }
  }
}
```

## Recursos

- Documentacao completa: https://tauri.app/llms.txt
- Plugins oficiais: https://github.com/tauri-apps/plugins-workspace
