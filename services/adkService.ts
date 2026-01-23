
import { RuntimeConfig, AgentProfile } from '../types';
import { GoogleGenAI } from "@google/genai";

/**
 * ADK Service Layer
 * 
 * This service is responsible for handling communication between the frontend shell
 * and the Google ADK Agent backend using the Google GenAI SDK.
 */

/** Fix: Implementation of sendPromptToAgent using the latest Google GenAI SDK */
export const sendPromptToAgent = async (
  prompt: string, 
  agent: AgentProfile, 
  config: RuntimeConfig
): Promise<string> => {
  
  // Use named parameter to initialize SDK
  const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
  
  // Select 'gemini-3-pro-preview' for complex legal reasoning tasks
  const modelName = 'gemini-3-pro-preview';

  try {
    const response = await ai.models.generateContent({
      model: modelName,
      contents: prompt,
      config: {
        systemInstruction: `You are a world-class legal expert operating as ${agent.name}. Specialization: ${agent.specialization}. Description: ${agent.description}. Provide detailed analysis in a ${config.outputStyle} style.`,
        temperature: config.temperature,
        topK: config.topK,
        // High thinking budget for complex legal analysis
        thinkingConfig: { thinkingBudget: 32768 },
        // Conditionally enable Google Search grounding
        tools: config.enableGrounding ? [{ googleSearch: {} }] : undefined,
      },
    });

    // Access text property directly as per guidelines
    return response.text || "AGENT_ERROR: Null Response Output.";
  } catch (error) {
    console.error('--- ADK AGENT ERROR ---', error);
    throw error;
  }
};

export const validateConfig = (config: RuntimeConfig): boolean => {
  // Logic to validate configuration parameters before execution
  return config.temperature >= 0 && config.temperature <= 1;
};
