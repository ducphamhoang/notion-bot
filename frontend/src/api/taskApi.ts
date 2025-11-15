// Task API functions

import { apiClient } from './client';
import type {
  CreateTaskRequest,
  CreateTaskResponse,
  ListTasksRequest,
  ListTasksResponse,
  UpdateTaskRequest,
  UpdateTaskResponse,
} from '../types/task';

export async function createTask(data: CreateTaskRequest): Promise<CreateTaskResponse> {
  return apiClient.post<CreateTaskResponse>('/tasks/', data);
}

export async function listTasks(params: ListTasksRequest): Promise<ListTasksResponse> {
  // Convert params to string record for query parameters
  const queryParams: Record<string, string> = {
    notion_database_id: params.notion_database_id,
  };

  if (params.status) queryParams.status = params.status;
  if (params.assignee) queryParams.assignee = params.assignee;
  if (params.due_date_from) queryParams.due_date_from = params.due_date_from;
  if (params.due_date_to) queryParams.due_date_to = params.due_date_to;
  if (params.priority) queryParams.priority = params.priority;
  if (params.project_id) queryParams.project_id = params.project_id;
  if (params.page) queryParams.page = params.page.toString();
  if (params.limit) queryParams.limit = params.limit.toString();
  if (params.sort_by) queryParams.sort_by = params.sort_by;
  if (params.order) queryParams.order = params.order;

  return apiClient.get<ListTasksResponse>('/tasks/', queryParams);
}

export async function updateTask(
  taskId: string,
  data: UpdateTaskRequest
): Promise<UpdateTaskResponse> {
  return apiClient.patch<UpdateTaskResponse>(`/tasks/${taskId}`, data);
}

export async function deleteTask(taskId: string): Promise<void> {
  return apiClient.delete<void>(`/tasks/${taskId}`);
}
