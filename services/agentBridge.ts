import { Command } from '@tauri-apps/plugin-shell';

interface AgentResult {
  success: boolean;
  output?: string;
  error?: string;
  outputPath?: string;
}

export const runJurisprudenceAgent = async (topic: string, onProgress?: (data: string) => void): Promise<AgentResult> => {
  console.log(`Starting Jurisprudence Agent for topic: ${topic}`);
  
  try {
    const command = Command.create('python', [
      'adk-agents/jurisprudence_agent/agent.py',
      topic
    ]);

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
