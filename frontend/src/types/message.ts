// Chat message types

export type MessageRole = 'user' | 'bot' | 'error';

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  error?: boolean;
  data?: any; // Optional structured data for bot responses (e.g., task list)
}
