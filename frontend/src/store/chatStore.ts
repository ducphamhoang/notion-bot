// Chat state management with Zustand

import { create } from 'zustand';
import type { Message, MessageData } from '../types/message';
import type { ApiError } from '../types/api';
import type {
  CreateTaskResponse,
  ListTasksResponse,
  UpdateTaskResponse,
} from '../types/task';
import { parseCommand, validateParams } from '../lib/commandParser';
import { commandToApiRequest } from '../lib/apiMapper';
import { apiClient } from '../api/client';

interface ChatState {
  // State
  messages: Message[];
  isLoading: boolean;
  databaseId: string | null;
  selectedTokenId: string | null;
  
  // Actions
  setDatabaseId: (id: string) => void;
  setSelectedTokenId: (id: string | null) => void;
  addMessage: (message: Omit<Message, 'id'>) => void;
  sendCommand: (text: string) => Promise<void>;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  // Initial state
  messages: [],
  isLoading: false,
  databaseId: null,
  selectedTokenId: localStorage.getItem('selectedTokenId') || null,

  // Set Notion database ID
  setDatabaseId: (id: string) => {
    set({ databaseId: id });
  },

  // Set selected token ID with localStorage persistence
  setSelectedTokenId: (id: string | null) => {
    if (id) {
      localStorage.setItem('selectedTokenId', id);
    } else {
      localStorage.removeItem('selectedTokenId');
    }
    set({ selectedTokenId: id });
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
    const { addMessage, databaseId, selectedTokenId } = get();

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

      // Add token_id to request if selected
      if (selectedTokenId) {
        if (apiRequest.method === 'GET') {
          // For GET requests, add to params object
          apiRequest.params = {
            ...apiRequest.params,
            token_id: selectedTokenId,
          };
        } else {
          // For POST/PATCH/DELETE, append to endpoint URL
          const separator = apiRequest.endpoint.includes('?') ? '&' : '?';
          apiRequest.endpoint = `${apiRequest.endpoint}${separator}token_id=${selectedTokenId}`;
        }
      }

      // Execute API call
      let response: CommandResponse | null = null;
      switch (apiRequest.method) {
        case 'GET':
          response = await apiClient.get<ListTasksResponse>(
            apiRequest.endpoint,
            apiRequest.params
          );
          break;
        case 'POST':
          response = await apiClient.post<CreateTaskResponse>(
            apiRequest.endpoint,
            apiRequest.body
          );
          break;
        case 'PATCH':
          response = await apiClient.patch<UpdateTaskResponse>(
            apiRequest.endpoint,
            apiRequest.body
          );
          break;
        case 'DELETE':
          response = await apiClient.delete<Record<string, unknown>>(
            apiRequest.endpoint
          );
          break;
      }

      // Add success response
      const messageData = mapResponseToMessageData(response);

      addMessage({
        role: 'bot',
        content: formatSuccessResponse(parsed.command, response),
        timestamp: new Date(),
        data: messageData,
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
type CommandResponse =
  | ListTasksResponse
  | CreateTaskResponse
  | UpdateTaskResponse
  | Record<string, unknown>
  | null;

function mapResponseToMessageData(response: CommandResponse): MessageData | undefined {
  if (isListTasksResponse(response)) {
    return { data: response.data };
  }
  return undefined;
}

function isListTasksResponse(
  response: CommandResponse
): response is ListTasksResponse {
  return Boolean(response && 'data' in response && Array.isArray(response.data));
}

function formatSuccessResponse(command: string, data: CommandResponse): string {
  switch (command) {
    case 'create':
      if (data && 'notion_task_id' in data && 'notion_task_url' in data) {
        return `✅ Task created successfully!\n\nTask ID: ${String(
          data.notion_task_id
        )}\nURL: ${String(data.notion_task_url)}`;
      }
      return '✅ Task created successfully!';
    
    case 'list':
      if (data && 'total' in data && typeof data.total === 'number') {
        if (data.total === 0) {
          return '📝 No tasks found matching your filters.';
        }
        const hasMore = 'has_more' in data && Boolean(data.has_more);
        return `📝 Found ${data.total} task(s)${hasMore ? ' (showing first page)' : ''}`;
      }
      return '📝 Command executed successfully!';
    
    case 'update':
      if (data && 'notion_task_id' in data && 'notion_task_url' in data) {
        return `✅ Task updated successfully!\n\nTask ID: ${String(
          data.notion_task_id
        )}\nURL: ${String(data.notion_task_url)}`;
      }
      return '✅ Task updated successfully!';
    
    case 'delete':
      return '✅ Task deleted successfully!';
    
    default:
      return '✅ Command executed successfully!';
  }
}
