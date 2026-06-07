import { apiClient, setAuthToken } from '../utils/http';
import type { AuthResponse } from '../types';

/**
 * Register a new user account.
 * Sets the auth token on success.
 */
export async function register(
  email: string,
  password: string,
  fullName: string,
): Promise<AuthResponse> {
  const { data } = await apiClient.post<AuthResponse>('/auth/register', {
    email,
    password,
    full_name: fullName,
  });
  setAuthToken(data.token);
  return data;
}

/**
 * Authenticate with email and password.
 * Sets the auth token on success.
 */
export async function login(email: string, password: string): Promise<AuthResponse> {
  const { data } = await apiClient.post<AuthResponse>('/auth/login', { email, password });
  setAuthToken(data.token);
  return data;
}
