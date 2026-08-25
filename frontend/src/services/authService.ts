import { API_BASE_URL } from '@/lib/api';

export interface AuthPayload {
  username: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  username: string;
}

async function handleAuthResponse(
  response: Response,
  fallback: string,
): Promise<AuthResponse> {
  if (!response.ok) {
    let detail = fallback;
    try {
      const data = await response.json();
      if (typeof data?.detail === 'string' && data.detail.trim()) {
        detail = data.detail;
      } else if (Array.isArray(data?.detail) && data.detail.length > 0) {
        const first = data.detail[0] as { msg?: unknown } | null;
        if (first && typeof first.msg === 'string') {
          detail = first.msg;
        }
      }
    } catch {
      // use fallback
    }
    throw new Error(detail);
  }
  return response.json();
}

export async function registerUser(
  payload: AuthPayload,
): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return handleAuthResponse(response, 'Registration failed.');
}

export async function loginUser(
  payload: AuthPayload,
): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return handleAuthResponse(response, 'Login failed.');
}
