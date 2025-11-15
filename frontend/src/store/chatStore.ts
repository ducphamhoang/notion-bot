// Chat state management with Zustand

import { create } from 'zustand';
import type { Message } from '../types/message';
import type { ApiError } from '../types/api';
import { parseCommand, validateParams } from '../lib/commandParser';
import { commandToApiRequest } from '../lib/apiMapper';
import { apiClient } from '../api/client';

interface ChatState {
  // State
  messages: Message[];
  isLoading: boolean;
  databaseId: string | null;
  
  // Actions
  setDatabaseId: (id: string) => void;
  addMessage: (message: Omit<Message, 'id'>) => void;
  sendCommand: (text: string) => Promise<void>;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  // Initial state
  messages: [],
  isLoading: false,
  databaseId: null,

  // Set Notion database ID
  setDatabaseId: (id: string) => {
    set({ databaseId: id });
  },

  // Add a message to the chat
  addMessage: (message: Omit<Message, 'id'>) => {
    const newMessage: Message = {
      ...message,
      id: crypto.randomUUID(),
    };
    set((state) => ({
      messages: [...state.messages, newMessage],
    }));
  },

  // Send a command and handle the response
  sendCommand: async (text: string) => {
    const { addMessage, databaseId } = get();

    // Add user message
    addMessage({
      role: 'user',
      content: text,
      timestamp: new Date(),
    });

    // Set loading state
    set({ isLoading: true });

    try {
      // Parse the command
      const { result: parsed, error: parseError } = parseCommand(text);

      if (parseError) {
        addMessage({
          role: 'error',
          content: parseError.message,
          timestamp: new Date(),
          error: true,
        });
        set({ isLoading: false });
        return;
      }

      if (!parsed) {
        throw new Error('Failed to parse command');
      }

      // Validate parameters
      const validationError = validateParams(parsed.command, parsed.params);
      if (validationError) {
        addMessage({
          role: 'error',
          content: validationError.message,
          timestamp: new Date(),
          error: true,
        });
        set({ isLoading: false });
        return;
      }

      // Check if database ID is set
      if (!databaseId) {
        addMessage({
          role: 'error',
          content: 'Please set a Notion database ID first. Use the settings to configure it.',
          timestamp: new Date(),
          error: true,
        });
        set({ isLoading: false });
        return;
      }

      // Convert to API request
      const apiRequest = commandToApiRequest(parsed, databaseId);

      // Execute API call
      let response: any;
      switch (apiRequest.method) {
        case 'GET':
          response = await apiClient.get(apiRequest.endpoint, apiRequest.params);
          break;
        case 'POST':
          response = await apiClient.post(apiRequest.endpoint, apiRequest.body);
          break;
        case 'PATCH':
          response = await apiClient.patch(apiRequest.endpoint, apiRequest.body);
          break;
        case 'DELETE':
          response = await apiClient.delete(apiRequest.endpoint);
          break;
      }

      // Add success response
      addMessage({
        role: 'bot',
        content: formatSuccessResponse(parsed.command, response),
        timestamp: new Date(),
        data: response,
      });

    } catch (error) {
      // Handle API errors
      const apiError = error as ApiError;
      addMessage({
        role: 'error',
        content: apiError.message || 'An unexpected error occurred',
        timestamp: new Date(),
        error: true,
      });
    } finally {
      set({ isLoading: false });
    }
  },

  // Clear all messages
  clearMessages: () => {
    set({ messages: [] });
  },
}));

/**
 * Format success response based on command type
 */
function formatSuccessResponse(command: string, data: any): string {
  switch (command) {
    case 'create':
      return `✅ Task created successfully!\n\nTask ID: ${data.notion_task_id}\nURL: ${data.notion_task_url}`;
    
    case 'list':
      if (data.total === 0) {
        return '📝 No tasks found matching your filters.';
      }
      return `📝 Found ${data.total} task(s)${data.has_more ? ' (showing first page)' : ''}`;
    
    case 'update':
      return `✅ Task updated successfully!\n\nTask ID: ${data.notion_task_id}\nURL: ${data.notion_task_url}`;
    
    case 'delete':
      return '✅ Task deleted successfully!';
    
    default:
      return '✅ Command executed successfully!';
  }
}
