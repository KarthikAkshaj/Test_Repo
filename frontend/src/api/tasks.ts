/**
 * Task API module — PR-03 (contains intentional issues for review testing).
 */

// ISSUE: Medium — raw axios instance with a hard-coded localhost URL.
// This bypasses the shared apiClient from utils/http.ts which sets the
// Authorization header via setAuthToken() and applies a 10-second timeout.
// All requests from this module will be unauthenticated in any non-local env.
// Fix: import { apiClient } from '../utils/http' and remove this block.
import axios from 'axios';
const http = axios.create({ baseURL: 'http://localhost:5000/api/v1' });

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
  const { data } = await http.get<PaginatedResponse<Task>>('/tasks', { params });
  return data;
}

/** Fetch a single task by ID. */
export async function getTask(taskId: number): Promise<Task> {
  const { data } = await http.get<Task>(`/tasks/${taskId}`);
  return data;
}

/**
 * Create a new task.
 * due_date must be an ISO 8601 datetime string if provided.
 */
export async function createTask(payload: CreateTaskPayload): Promise<Task> {
  const { data } = await http.post<Task>('/tasks', payload);
  return data;
}

/**
 * Partially update a task.
 */
export async function updateTask(taskId: number, payload: UpdateTaskPayload): Promise<Task> {
  const { data } = await http.patch<Task>(`/tasks/${taskId}`, payload);
  return data;
}

/** Delete a task. */
export async function deleteTask(taskId: number): Promise<void> {
  await http.delete(`/tasks/${taskId}`);
}
