import { Command } from '@tauri-apps/plugin-shell';
import { IntegrationsConfig, MCPServer, LocalFolder } from '../types';
import { loadIntegrationsConfig } from '../constants';
import { mcpServersToEnv } from './mcpService';

interface AgentResult {
  success: boolean;
  output?: string;
  error?: string;
  outputPath?: string;
}

interface AgentOptions {
  integrationsConfig?: IntegrationsConfig;
  onProgress?: (data: string) => void;
}

/**
 * Converts filesystem config to environment variables for Python agents
 */
const filesystemToEnv = (folders: LocalFolder[], mode: 'whitelist' | 'unrestricted'): Record<string, string> => {
  const enabledFolders = folders.filter(f => f.enabled);

  if (enabledFolders.length === 0 && mode === 'whitelist') {
    return {};
  }

  return {
    FILESYSTEM_MODE: mode,
    FILESYSTEM_FOLDERS: JSON.stringify(
      enabledFolders.map(f => ({
        path: f.path,
        alias: f.alias,
        readOnly: f.readOnly,
      }))
    ),
    FILESYSTEM_FOLDER_COUNT: String(enabledFolders.length),
  };
};

/**
 * Builds environment variables from integrations config
 */
const buildEnvFromConfig = (config: IntegrationsConfig): Record<string, string> => {
  const env: Record<string, string> = {};

  // Add MCP servers
  const mcpEnv = mcpServersToEnv(config.mcpServers || []);
  Object.assign(env, mcpEnv);

  // Add filesystem config
  const fsEnv = filesystemToEnv(
    config.filesystem?.whitelistedFolders || [],
    config.filesystem?.mode || 'whitelist'
  );
  Object.assign(env, fsEnv);

  // Add Google Drive token if available (for Python agents that need it)
  if (config.googleDrive?.accessToken) {
    env.GOOGLE_DRIVE_TOKEN = config.googleDrive.accessToken;
  }

  return env;
};

export const runJurisprudenceAgent = async (
  topic: string,
  onProgress?: (data: string) => void
): Promise<AgentResult> => {
  // Load integrations config
  const integrationsConfig = loadIntegrationsConfig();
  const envVars = buildEnvFromConfig(integrationsConfig);

  console.log(`Starting Jurisprudence Agent for topic: ${topic}`);
  console.log(`Integrations: ${Object.keys(envVars).length} env vars configured`);

  try {
    const command = Command.create('python', [
      'adk-agents/jurisprudence_agent/agent.py',
      topic
    ], {
      env: envVars,
    });

    let fullOutput = '';
    let outputPath = '';

    command.on('close', (data) => {
      console.log(`command finished with code ${data.code} and signal ${data.signal}`);
    });

    command.on('error', (error) => {
      console.error(`command error: "${error}"`);
    });

    command.stdout.on('data', (line) => {
      fullOutput += line + '\n';
      console.log(`[PY]: ${line}`);
      if (onProgress) onProgress(line);

      // Try to detect output path
      if (line.includes('Output salvo em:')) {
        outputPath = line.split('Output salvo em:')[1].trim();
      }
    });

    command.stderr.on('data', (line) => {
      console.error(`[PY-ERR]: ${line}`);
      if (onProgress) onProgress(`ERROR: ${line}`);
    });

    const child = await command.execute();

    if (child.code === 0) {
      return {
        success: true,
        output: fullOutput,
        outputPath: outputPath
      };
    } else {
      return {
        success: false,
        error: `Agent exited with code ${child.code}`,
        output: fullOutput
      };
    }

  } catch (e) {
    console.error('Failed to run agent:', e);
    return {
      success: false,
      error: String(e)
    };
  }
};

/**
 * Generic agent runner that accepts custom script path and args
 */
export const runPythonAgent = async (
  scriptPath: string,
  args: string[],
  options?: AgentOptions
): Promise<AgentResult> => {
  // Load integrations config
  const integrationsConfig = options?.integrationsConfig || loadIntegrationsConfig();
  const envVars = buildEnvFromConfig(integrationsConfig);

  console.log(`Starting Python Agent: ${scriptPath}`);
  console.log(`Args: ${args.join(', ')}`);
  console.log(`Integrations: ${Object.keys(envVars).length} env vars configured`);

  try {
    const command = Command.create('python', [scriptPath, ...args], {
      env: envVars,
    });

    let fullOutput = '';
    let outputPath = '';

    command.on('close', (data) => {
      console.log(`command finished with code ${data.code} and signal ${data.signal}`);
    });

    command.on('error', (error) => {
      console.error(`command error: "${error}"`);
    });

    command.stdout.on('data', (line) => {
      fullOutput += line + '\n';
      console.log(`[PY]: ${line}`);
      if (options?.onProgress) options.onProgress(line);

      // Try to detect output path
      if (line.includes('Output salvo em:')) {
        outputPath = line.split('Output salvo em:')[1].trim();
      }
    });

    command.stderr.on('data', (line) => {
      console.error(`[PY-ERR]: ${line}`);
      if (options?.onProgress) options.onProgress(`ERROR: ${line}`);
    });

    const child = await command.execute();

    if (child.code === 0) {
      return {
        success: true,
        output: fullOutput,
        outputPath: outputPath
      };
    } else {
      return {
        success: false,
        error: `Agent exited with code ${child.code}`,
        output: fullOutput
      };
    }

  } catch (e) {
    console.error('Failed to run agent:', e);
    return {
      success: false,
      error: String(e)
    };
  }
};
