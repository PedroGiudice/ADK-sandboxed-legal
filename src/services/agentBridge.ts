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

// === Case Context para Sandboxing ===

export interface CaseContext {
  casePath: string;
  caseId: string;
  sessionId?: string;
}

export interface ADKEvent {
  type: string;
  data: Record<string, unknown>;
  timestamp: string;
}

export interface SessionResult {
  success: boolean;
  sessionId?: string;
  data?: Record<string, unknown>;
  error?: string;
}

export interface PipelineProgress {
  state: string;
  currentPhase: string;
  progressPercent: number;
  lastCheckpoint?: string;
}

// === Parser de eventos ADK ===

/**
 * Parseia linha de output procurando eventos __ADK_EVENT__
 */
export const parseADKEvent = (line: string): ADKEvent | null => {
  const eventPattern = /__ADK_EVENT__(.+?)__ADK_EVENT__/;
  const match = line.match(eventPattern);

  if (match && match[1]) {
    try {
      return JSON.parse(match[1]) as ADKEvent;
    } catch (e) {
      console.warn('Erro ao parsear evento ADK:', e);
      return null;
    }
  }

  return null;
};

/**
 * Extrai texto puro removendo eventos ADK
 */
export const stripADKEvents = (output: string): string => {
  return output.replace(/__ADK_EVENT__.+?__ADK_EVENT__/g, '').trim();
};

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

// === Session Management para Sandboxing ===

export interface SessionOptions {
  onEvent?: (event: ADKEvent) => void;
  onProgress?: (progress: PipelineProgress) => void;
  onOutput?: (line: string) => void;
}

/**
 * Inicia uma sessao de caso (cria estrutura e inicializa Git)
 */
export const startCaseSession = async (
  casePath: string,
  caseId: string,
  options?: SessionOptions
): Promise<SessionResult> => {
  console.log(`Starting case session: ${caseId} at ${casePath}`);

  // Carregar config de integracoes e adicionar ADK_WORKSPACE
  const integrationsConfig = loadIntegrationsConfig();
  const envVars = buildEnvFromConfig(integrationsConfig);
  envVars.ADK_WORKSPACE = casePath; // Sandboxing: agente so acessa este diretorio

  try {
    const command = Command.create('python', [
      '-m', 'brazilian_legal_pipeline.session_cli',
      'start',
      '--case-path', casePath,
      '--case-id', caseId
    ], {
      cwd: 'adk-agents',
      env: envVars
    });

    let sessionId: string | undefined;
    let resultData: Record<string, unknown> | undefined;
    let error: string | undefined;

    command.stdout.on('data', (line) => {
      console.log(`[SESSION]: ${line}`);

      const event = parseADKEvent(line);
      if (event) {
        if (options?.onEvent) {
          options.onEvent(event);
        }

        if (event.type === 'cli_result') {
          const data = event.data as { success: boolean; data?: Record<string, unknown>; error?: string };
          if (data.success && data.data) {
            sessionId = (data.data as { session_id?: string }).session_id;
            resultData = data.data;
          } else if (data.error) {
            error = data.error;
          }
        }
      }

      if (options?.onOutput) {
        options.onOutput(stripADKEvents(line));
      }
    });

    command.stderr.on('data', (line) => {
      console.error(`[SESSION-ERR]: ${line}`);
    });

    const child = await command.execute();

    if (child.code === 0 && sessionId) {
      return { success: true, sessionId, data: resultData };
    } else {
      return { success: false, error: error || `Session start failed with code ${child.code}` };
    }

  } catch (e) {
    console.error('Failed to start session:', e);
    return { success: false, error: String(e) };
  }
};

/**
 * Executa pipeline em uma sessao existente
 */
export const runCaseSession = async (
  sessionId: string,
  consultation: Record<string, unknown>,
  casePath?: string,
  options?: SessionOptions
): Promise<SessionResult> => {
  console.log(`Running pipeline in session: ${sessionId}`);

  // Carregar config de integracoes
  const integrationsConfig = loadIntegrationsConfig();
  const envVars = buildEnvFromConfig(integrationsConfig);
  if (casePath) {
    envVars.ADK_WORKSPACE = casePath; // Sandboxing
  }

  try {
    const command = Command.create('python', [
      '-m', 'brazilian_legal_pipeline.session_cli',
      'run',
      '--session-id', sessionId,
      '--consultation', JSON.stringify(consultation)
    ], {
      cwd: 'adk-agents',
      env: envVars
    });

    let resultData: Record<string, unknown> | undefined;
    let error: string | undefined;

    command.stdout.on('data', (line) => {
      console.log(`[PIPELINE]: ${line}`);

      const event = parseADKEvent(line);
      if (event) {
        if (options?.onEvent) {
          options.onEvent(event);
        }

        if (event.type === 'loop_status' && options?.onProgress) {
          const data = event.data as {
            state: string;
            current_phase: string;
            progress_percent: number;
            last_checkpoint?: { checkpoint_path: string };
          };
          options.onProgress({
            state: data.state,
            currentPhase: data.current_phase,
            progressPercent: data.progress_percent,
            lastCheckpoint: data.last_checkpoint?.checkpoint_path
          });
        }

        if (event.type === 'cli_result') {
          const data = event.data as { success: boolean; data?: Record<string, unknown>; error?: string };
          if (data.success) {
            resultData = data.data;
          } else {
            error = data.error;
          }
        }
      }

      if (options?.onOutput) {
        options.onOutput(stripADKEvents(line));
      }
    });

    command.stderr.on('data', (line) => {
      console.error(`[PIPELINE-ERR]: ${line}`);
    });

    const child = await command.execute();

    if (child.code === 0) {
      return { success: true, sessionId, data: resultData };
    } else {
      return { success: false, sessionId, error: error || `Pipeline failed with code ${child.code}` };
    }

  } catch (e) {
    console.error('Failed to run pipeline:', e);
    return { success: false, sessionId, error: String(e) };
  }
};

/**
 * Inicia sessao e executa pipeline em um comando
 */
export const startAndRunCaseSession = async (
  casePath: string,
  caseId: string,
  consultation: Record<string, unknown>,
  options?: SessionOptions
): Promise<SessionResult> => {
  console.log(`Starting and running case session: ${caseId}`);

  // Carregar config de integracoes e adicionar ADK_WORKSPACE
  const integrationsConfig = loadIntegrationsConfig();
  const envVars = buildEnvFromConfig(integrationsConfig);
  envVars.ADK_WORKSPACE = casePath; // Sandboxing: agente so acessa este diretorio

  console.log(`ADK_WORKSPACE set to: ${casePath}`);

  try {
    const command = Command.create('python', [
      '-m', 'brazilian_legal_pipeline.session_cli',
      'start-and-run',
      '--case-path', casePath,
      '--case-id', caseId,
      '--consultation', JSON.stringify(consultation)
    ], {
      cwd: 'adk-agents',
      env: envVars
    });

    let sessionId: string | undefined;
    let resultData: Record<string, unknown> | undefined;
    let error: string | undefined;

    command.stdout.on('data', (line) => {
      console.log(`[SESSION+PIPELINE]: ${line}`);

      const event = parseADKEvent(line);
      if (event) {
        if (options?.onEvent) {
          options.onEvent(event);
        }

        if (event.type === 'loop_status' && options?.onProgress) {
          const data = event.data as {
            state: string;
            current_phase: string;
            progress_percent: number;
          };
          options.onProgress({
            state: data.state,
            currentPhase: data.current_phase,
            progressPercent: data.progress_percent
          });
        }

        if (event.type === 'session_created') {
          sessionId = (event.data as { session_id: string }).session_id;
        }

        if (event.type === 'cli_result') {
          const data = event.data as { success: boolean; data?: Record<string, unknown>; error?: string };
          if (data.success) {
            resultData = data.data;
            if (!sessionId && data.data?.session) {
              sessionId = ((data.data.session as Record<string, unknown>).session_id as string);
            }
          } else {
            error = data.error;
          }
        }
      }

      if (options?.onOutput) {
        options.onOutput(stripADKEvents(line));
      }
    });

    command.stderr.on('data', (line) => {
      console.error(`[SESSION+PIPELINE-ERR]: ${line}`);
    });

    const child = await command.execute();

    if (child.code === 0 && sessionId) {
      return { success: true, sessionId, data: resultData };
    } else {
      return { success: false, sessionId, error: error || `Session+Pipeline failed with code ${child.code}` };
    }

  } catch (e) {
    console.error('Failed to start and run session:', e);
    return { success: false, error: String(e) };
  }
};

/**
 * Obtem status Git de um caso
 */
export const getCaseGitStatus = async (casePath: string): Promise<SessionResult> => {
  try {
    const command = Command.create('python', [
      '-m', 'brazilian_legal_pipeline.session_cli',
      'git-status',
      '--case-path', casePath
    ], {
      cwd: 'adk-agents'
    });

    let resultData: Record<string, unknown> | undefined;
    let error: string | undefined;

    command.stdout.on('data', (line) => {
      const event = parseADKEvent(line);
      if (event && event.type === 'cli_result') {
        const data = event.data as { success: boolean; data?: Record<string, unknown>; error?: string };
        if (data.success) {
          resultData = data.data;
        } else {
          error = data.error;
        }
      }
    });

    const child = await command.execute();

    if (child.code === 0 && resultData) {
      return { success: true, data: resultData };
    } else {
      return { success: false, error: error || 'Failed to get git status' };
    }

  } catch (e) {
    return { success: false, error: String(e) };
  }
};
