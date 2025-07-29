// Déclarations de types pour smaApi.js
export interface ChatResponse {
  message?: string;
  answer?: string;
  agent_used?: string;
  confidence?: number;
  sources?: any[];
}

export interface ChatRequest {
  message: string;
  context?: Record<string, any>;
}

export async function sendChatMessage(message: string): Promise<ChatResponse>; 