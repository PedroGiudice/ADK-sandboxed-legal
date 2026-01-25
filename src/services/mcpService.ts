import { MCPServer } from '../types';
import { generateId } from '../constants';

/**
 * Creates a new MCP Server configuration
 */
export const createMCPServer = (name: string, url: string): MCPServer => {
  return {
    id: generateId(),
    name,
    url,
    tools: [],
    enabled: true,
    status: 'unknown',
  };
};

/**
 * Validates MCP server URL format
 */
export const validateMCPUrl = (url: string): boolean => {
  try {
    const parsed = new URL(url);
    return ['http:', 'https:', 'ws:', 'wss:'].includes(parsed.protocol);
  } catch {
    return false;
  }
};

/**
 * Performs a health check on an MCP server
 */
export const checkMCPHealth = async (server: MCPServer): Promise<MCPServer> => {
  try {
    // MCP servers typically respond to a simple GET or have a health endpoint
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);

    const response = await fetch(`${server.url}/health`, {
      method: 'GET',
      signal: controller.signal,
    }).catch(() => null);

    clearTimeout(timeoutId);

    const isOnline = response?.ok ?? false;

    return {
      ...server,
      status: isOnline ? 'online' : 'offline',
      lastHealthCheck: new Date(),
    };
  } catch {
    return {
      ...server,
      status: 'offline',
      lastHealthCheck: new Date(),
    };
  }
};

/**
 * Checks health of all MCP servers
 */
export const checkAllMCPHealth = async (servers: MCPServer[]): Promise<MCPServer[]> => {
  const results = await Promise.all(servers.map(checkMCPHealth));
  return results;
};

/**
 * Converts MCP servers config to environment variable format for Python agents
 */
export const mcpServersToEnv = (servers: MCPServer[]): Record<string, string> => {
  const enabledServers = servers.filter(s => s.enabled);

  if (enabledServers.length === 0) {
    return {};
  }

  return {
    MCP_SERVERS: JSON.stringify(
      enabledServers.map(s => ({
        name: s.name,
        url: s.url,
        tools: s.tools,
      }))
    ),
    MCP_SERVER_COUNT: String(enabledServers.length),
  };
};

/**
 * Parses tools from MCP server discovery
 */
export const discoverMCPTools = async (server: MCPServer): Promise<string[]> => {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000);

    const response = await fetch(`${server.url}/tools`, {
      method: 'GET',
      signal: controller.signal,
      headers: {
        'Accept': 'application/json',
      },
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      return [];
    }

    const data = await response.json();

    // MCP typically returns tools in a specific format
    if (Array.isArray(data.tools)) {
      return data.tools.map((t: { name: string }) => t.name);
    }

    if (Array.isArray(data)) {
      return data.map((t: { name: string }) => t.name);
    }

    return [];
  } catch {
    return [];
  }
};

/**
 * Discovers tools for all MCP servers
 */
export const discoverAllMCPTools = async (servers: MCPServer[]): Promise<MCPServer[]> => {
  const results = await Promise.all(
    servers.map(async (server) => {
      const tools = await discoverMCPTools(server);
      return {
        ...server,
        tools,
      };
    })
  );
  return results;
};
