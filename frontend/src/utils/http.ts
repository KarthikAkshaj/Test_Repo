/**
 * Configured Axios instance for TaskFlow API calls.
 * Always use `apiClient` from this module — never construct raw axios instances in feature code.
 */

import axios, { AxiosError, AxiosInstance } from 'axios';

const BASE_URL = process.env.TASKFLOW_API_URL ?? 'http://localhost:5000/api/v1';

export const apiClient: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 10_000,
});

/** Attach a JWT Bearer token to all subsequent requests. */
export function setAuthToken(token: string): void {
  apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
}

/** Remove the JWT Bearer token (e.g. on logout). */
export function clearAuthToken(): void {
  delete apiClient.defaults.headers.common['Authorization'];
}

/** Extract the `error` string from an API error response envelope. */
export function getApiErrorMessage(err: unknown): string {
  if (err instanceof AxiosError && err.response?.data?.error) {
    return err.response.data.error as string;
  }
  if (err instanceof Error) return err.message;
  return 'An unexpected error occurred';
}
