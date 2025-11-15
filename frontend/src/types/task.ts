// TypeScript types matching backend DTOs from src/features/tasks/dto/

export type Priority = 'Low' | 'Medium' | 'High';

// Matches CreateTaskRequest from src/features/tasks/dto/create_task_request.py
export interface CreateTaskRequest {
  title: string;
  notion_database_id: string;
  assignee_id?: string;
  due_date?: string; // ISO 8601 datetime string
  priority?: Priority;
  properties?: Record<string, unknown>;
}
export interface CreateTaskResponse {
  notion_task_id: string;
  notion_task_url: string;
  created_at: string; // ISO 8601 datetime string
}

// Matches ListTasksRequest from src/features/tasks/dto/list_tasks_request.py
export interface ListTasksRequest {
  notion_database_id: string;
  status?: string;
  assignee?: string;
  due_date_from?: string; // ISO 8601 datetime string
  due_date_to?: string; // ISO 8601 datetime string
  priority?: Priority;
  project_id?: string;
  page?: number;
  limit?: number;
  sort_by?: string;
  order?: 'asc' | 'desc';
}

// Matches TaskSummary from src/features/tasks/dto/list_tasks_response.py
export interface TaskSummary {
  notion_task_id: string;
  title: string;
  status?: string;
  priority?: Priority;
  due_date?: string; // ISO 8601 datetime string
  assignees: string[];
  created_time: string; // ISO 8601 datetime string
  last_edited_time: string; // ISO 8601 datetime string
  url: string;
}

// Matches ListTasksResponse from src/features/tasks/dto/list_tasks_response.py
export interface ListTasksResponse {
  data: TaskSummary[];
  page: number;
  limit: number;
  total: number;
  has_more: boolean;
}

// Matches UpdateTaskRequest from src/features/tasks/dto/update_task_request.py
export interface UpdateTaskRequest {
  status?: string;
  assignee_id?: string;
  due_date?: string; // ISO 8601 datetime string
  priority?: Priority;
  properties?: Record<string, unknown>;
}

// Matches UpdateTaskResponse from src/features/tasks/dto/update_task_response.py
export interface UpdateTaskResponse {
  notion_task_id: string;
  notion_task_url: string;
  updated_at: string; // ISO 8601 datetime string
  status?: string;
  priority?: Priority;
  due_date?: string; // ISO 8601 datetime string
}
