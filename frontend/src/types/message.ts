// Chat message types

import type { TaskSummary } from './task';

export type MessageRole = 'user' | 'bot' | 'error';

export interface MessageData {
  data?: TaskSummary[];
  [key: string]: unknown;
}

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  error?: boolean;
  data?: MessageData; // Optional structured data for bot responses (e.g., task list)
}
