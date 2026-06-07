import { apiClient } from '../utils/http';
import type { Task, CreateTaskPayload, UpdateTaskPayload, PaginatedResponse } from '../types';

export interface ListTasksParams {
  page?: number;
  per_page?: number;
  project_id?: number;
  status?: string;
  assignee_id?: number;
}

/** Fetch a paginated list of tasks. */
export async function listTasks(params?: ListTasksParams): Promise<PaginatedResponse<Task>> {
  const { data } = await apiClient.get<PaginatedResponse<Task>>('/tasks', { params });
  return data;
}

/** Fetch a single task by ID. */
export async function getTask(taskId: number): Promise<Task> {
  const { data } = await apiClient.get<Task>(`/tasks/${taskId}`);
  return data;
}

/**
 * Create a new task.
 * due_date must be an ISO 8601 datetime string if provided.
 */
export async function createTask(payload: CreateTaskPayload): Promise<Task> {
  const { data } = await apiClient.post<Task>('/tasks', payload);
  return data;
}

/**
 * Partially update a task.
 * due_date must be an ISO 8601 datetime string or null if provided.
 */
export async function updateTask(taskId: number, payload: UpdateTaskPayload): Promise<Task> {
  const { data } = await apiClient.patch<Task>(`/tasks/${taskId}`, payload);
  return data;
}

/** Delete a task. */
export async function deleteTask(taskId: number): Promise<void> {
  await apiClient.delete(`/tasks/${taskId}`);
}
