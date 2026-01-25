import { Plugin } from 'vite';
import { parse } from 'smol-toml';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { resolve } from 'path';

interface ThemeColors {
  surface: string;
  surface_alt: string;
  surface_elevated: string;
  foreground: string;
  foreground_muted: string;
  foreground_subtle: string;
  border: string;
  border_subtle: string;
  accent: string;
  accent_hover: string;
  accent_muted: string;
  success: string;
  warning: string;
  error: string;
}

interface ThemeScrollbar {
  track: string;
  thumb: string;
  thumb_hover: string;
}

interface ThemeDefinition {
  name: string;
  description: string;
  colors: ThemeColors;
  scrollbar: ThemeScrollbar;
}

interface ThemeConfig {
  meta: { version: string; default_theme: string };
  themes: Record<string, ThemeDefinition>;
}

function generateCssVariables(theme: ThemeDefinition, themeId: string): string {
  const colorVars = Object.entries(theme.colors)
    .map(([key, value]) => `  --color-${key.replace(/_/g, '-')}: ${value};`)
    .join('\n');
  const scrollbarVars = Object.entries(theme.scrollbar)
    .map(([key, value]) => `  --scrollbar-${key.replace(/_/g, '-')}: ${value};`)
    .join('\n');
  return `.theme-${themeId} {\n${colorVars}\n${scrollbarVars}\n}`;
}

function generateThemeCSS(config: ThemeConfig): string {
  const themesCSS = Object.entries(config.themes)
    .map(([id, theme]) => generateCssVariables(theme, id))
    .join('\n\n');
  return `/* Auto-generated from themes.toml - DO NOT EDIT */\n\n${themesCSS}`;
}

export default function tomlThemesPlugin(): Plugin {
  const themesPath = resolve(process.cwd(), 'themes/themes.toml');
  const outputDir = resolve(process.cwd(), 'themes');

  function generateThemes() {
    if (!existsSync(themesPath)) {
      console.warn('[toml-themes] themes/themes.toml not found, skipping');
      return;
    }

    const tomlContent = readFileSync(themesPath, 'utf-8');
    const config = parse(tomlContent) as unknown as ThemeConfig;

    // Generate CSS
    const css = generateThemeCSS(config);
    writeFileSync(resolve(outputDir, 'generated-themes.css'), css);

    // Generate JSON metadata
    const themesJson = {
      defaultTheme: config.meta.default_theme,
      themes: Object.fromEntries(
        Object.entries(config.themes).map(([id, theme]) => [
          id,
          { name: theme.name, description: theme.description }
        ])
      )
    };
    writeFileSync(resolve(outputDir, 'themes-metadata.json'), JSON.stringify(themesJson, null, 2));

    console.log(`[toml-themes] Generated CSS and metadata for ${Object.keys(config.themes).length} themes`);
  }

  return {
    name: 'vite-plugin-toml-themes',

    buildStart() {
      generateThemes();
    },

    configureServer(server) {
      server.watcher.add(themesPath);
    },

    handleHotUpdate({ file, server }) {
      if (file.endsWith('themes.toml')) {
        generateThemes();
        server.ws.send({ type: 'full-reload' });
      }
    }
  };
}
