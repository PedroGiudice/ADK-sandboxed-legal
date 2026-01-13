import { RuntimeConfig, AgentProfile } from '../types';

/**
 * ADK Service Layer
 * 
 * This service is responsible for handling communication between the frontend shell
 * and the Google ADK Agent backend.
 * 
 * NOTE: Currently operating in UI-only mode. Backend integration pending.
 */

// This function acts as a stub for where the actual Gemini API or custom ADK backend call would go.
// Per requirements, we do not mock responses, but we provide the function signature.
export const sendPromptToAgent = async (
  prompt: string, 
  agent: AgentProfile, 
  config: RuntimeConfig
): Promise<void> => {
  
  console.log('--- ADK REQUEST OUTBOUND ---');
  console.log(`Agent: ${agent.id}`);
  console.log(`Config: ${JSON.stringify(config)}`);
  console.log(`Payload: ${prompt}`);
  console.log('----------------------------');

  // Future integration point:
  // const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
  // const response = await ai.models.generateContent({ ... });
  
  return Promise.resolve();
};

export const validateConfig = (config: RuntimeConfig): boolean => {
  // Logic to validate configuration parameters before execution
  return config.temperature >= 0 && config.temperature <= 1;
};